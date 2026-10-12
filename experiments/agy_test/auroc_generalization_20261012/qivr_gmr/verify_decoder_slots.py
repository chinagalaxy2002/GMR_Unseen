"""Real native with/no-SA parity, attention masks and slot artifact checks."""
import copy
import importlib
import json
import tempfile
from pathlib import Path

import numpy as np
import torch

import run_decoder_experiment as experiment
from decoder_slot_monitor import DecoderSlotMonitor, pairwise_iou
from mechanism_monitor import save_json


def main():
    torch.set_num_threads(2)
    boxes = torch.tensor([[[.1, .3], [.1, .3], [.5, .6]]])
    iou = pairwise_iou(boxes)
    assert iou[0, 0, 1] == 1 and iou[0, 0, 2] == 0
    results = []
    for backbone in ('moment', 'qd'):
        paths = experiment.diagnostics.registry.paths('soccer', 'A1_soccer', backbone)
        paths['dataset'] = 'soccer'
        opt = copy.deepcopy(torch.load(paths['checkpoint'], map_location='cpu', weights_only=False)['opt'])
        opt.device, opt.eval_bsz = 'cpu', 2
        package = 'moment_detr_gmr' if backbone == 'moment' else 'qd_detr_gmr'
        module = importlib.import_module(f'training.{package}.dataset')
        build = importlib.import_module(f"models.{package}.{'moment_detr' if backbone == 'moment' else 'model'}").build_model
        dataset = experiment.make_dataset(paths, opt, module, 'train', True)
        dataset.data = [next(r for r in dataset.data if len(r['relevant_windows']) >= 2),
                        next(r for r in dataset.data if not r['relevant_windows'])]
        metadata, batch = next(iter(experiment.loader(dataset, module, 2, 0)))
        inputs, targets = module.prepare_batch_inputs(batch, 'cpu')
        for variant in ('with_sa', 'no_sa'):
            experiment.seed_everything(3407)
            model, criterion = build(opt)
            for layer in model.transformer.decoder.layers:
                layer.rm_self_attn_decoder = variant == 'no_sa'
            assert model.exist_head is not None and not hasattr(model, "qivr_head")
            assert "loss_evidence" not in criterion.weight_dict
            model.train()
            initial_rng = torch.get_rng_state().clone()
            expected = model(**inputs)
            baseline_losses = criterion(expected, targets)
            total = sum(v*criterion.weight_dict[k] for k,v in baseline_losses.items() if k in criterion.weight_dict)
            parameters = list(model.parameters())
            baseline_grads = torch.autograd.grad(total, parameters, allow_unused=True)
            baseline_rng = torch.get_rng_state().clone()
            torch.set_rng_state(initial_rng)
            with tempfile.TemporaryDirectory(prefix='decoder_check_') as temporary:
                monitor = DecoderSlotMonitor(model, temporary, 1)
                monitor.begin('train', 1, 1, 1)
                observed = model(**inputs)
                losses = criterion(observed, targets)
                indices = criterion.matcher(observed, targets)
                monitor.observe(observed, targets, metadata, inputs, indices)
                for key in ('pred_spans', 'pred_logits', 'pred_exist_logits', 'hs'):
                    torch.testing.assert_close(observed[key], expected[key], rtol=0, atol=0)
                loss = sum(v*criterion.weight_dict[k] for k,v in losses.items() if k in criterion.weight_dict)
                loss.backward()
                assert torch.equal(baseline_rng, torch.get_rng_state())
                for parameter, grad in zip(parameters, baseline_grads):
                    if grad is None:
                        assert parameter.grad is None
                    else:
                        torch.testing.assert_close(parameter.grad, grad, rtol=0, atol=0)
                folder = Path(temporary)/'decoder_slots'
                raw = dict(np.load(next(folder.glob('train_*.npz')), allow_pickle=False))
                assert raw['hs'].shape[:3] == (len(model.transformer.decoder.layers), 2, opt.num_queries)
                assert (raw['final_gt_assignment'][1] == -1).all()
                assert np.isnan(raw['best_gt_iou'][:, 1]).all()
                for layer in range(len(model.transformer.decoder.layers)):
                    key = f'attention_self_layer_{layer}'
                    assert (key in raw) == (variant == 'with_sa')
                    cross = raw[f'attention_cross_layer_{layer}']
                    expected_mask = raw['video_mask'] if backbone == 'qd' else np.concatenate([raw['video_mask'], raw['text_mask']], -1)
                    assert cross.shape == (2, opt.num_queries, expected_mask.shape[-1])
                    assert np.all(cross[np.broadcast_to(~expected_mask[:, None], cross.shape)] == 0)
                records = json.loads((folder/'train_slots.jsonl').read_text())['records']
                assert len(records) == len(model.transformer.decoder.layers)*2
                assert all(r['self_attention_status'] == ('observed' if variant == 'with_sa' else 'disabled') for r in records)
                # A skipped batch must not produce a record or capture a tensor.
                monitor.every = 50
                monitor.begin('train', 1, 2, 2)
                assert not monitor.enabled
                monitor.close()
            results.append(f'{backbone}/{variant}: outputs, gradients and RNG bitwise unchanged; actual layer/slot/attention shapes, masked tokens, multi-GT and negative NA, no-SA absence and native baseline without QIVR verified')
    save_json(experiment.ROOT/'monitoring/DECODER_SLOT_TEST_RESULTS.json', dict(passed=True, tests=results))
    print(json.dumps(dict(passed=True, tests=results), indent=2))


if __name__ == '__main__':
    main()
