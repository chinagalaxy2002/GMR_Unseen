"""Data augmentation strategy for generalized video-moment retrieval, reproducing Kim et al. AAAI 2026."""
import random
import copy
import torch

def apply_kim_augmentation(model_inputs, targets, metadata, tau_no=0.08, tau_mul=0.05):
    """Synthetic No-Target and Multi-Target Data Augmentation (Kim et al. AAAI 2026 Section 3.3).
    
    1. No-target sample generation:
       With probability tau_no, swap text features with another sample from the batch
       and clear all GT windows (setting exist_label = 0).
    2. Multi-target sample generation:
       With probability tau_mul (among remaining positive samples), combine spans from another
       positive sample to reinforce multi-moment localization and set multi_label = 1.
    """
    if tau_no <= 0.0 and tau_mul <= 0.0:
        return model_inputs, targets, metadata, 0, 0
    
    device = model_inputs['src_txt'].device
    B = model_inputs['src_txt'].shape[0]
    pos_indices = [i for i in range(B) if targets['exist_label'][i] > 0.5]
    if len(pos_indices) < 2:
        return model_inputs, targets, metadata, 0, 0

    aug_no_count = 0
    aug_mul_count = 0
    processed_no = set()

    # Step 1: Synthetic No-Target Augmentation
    if tau_no > 0.0:
        for i in pos_indices:
            if random.random() < tau_no:
                candidate_pool = [j for j in range(B) if j != i]
                j = random.choice(candidate_pool)
                
                # Replace text features and mask with sample j's text
                model_inputs['src_txt'][i] = model_inputs['src_txt'][j].clone()
                model_inputs['src_txt_mask'][i] = model_inputs['src_txt_mask'][j].clone()
                
                # Clear ground truth targets
                targets['exist_label'][i] = 0.0
                targets['span_labels'][i] = {
                    'spans': torch.zeros((0, 2), dtype=torch.float32, device=device)
                }
                
                # Update metadata
                metadata[i] = copy.deepcopy(metadata[i])
                metadata[i]['relevant_windows'] = []
                metadata[i]['synthetic_no_target'] = True
                if 'query' in metadata[j]:
                    metadata[i]['query'] = metadata[j]['query']
                processed_no.add(i)
                aug_no_count += 1

    # Step 2: Synthetic Multi-Target Augmentation
    if tau_mul > 0.0:
        remaining_pos = [i for i in pos_indices if i not in processed_no]
        for i in remaining_pos:
            if random.random() < tau_mul:
                other_pos = [j for j in remaining_pos if j != i]
                if other_pos:
                    j = random.choice(other_pos)
                    spans_i = targets['span_labels'][i]['spans']
                    spans_j = targets['span_labels'][j]['spans']
                    if len(spans_i) > 0 and len(spans_j) > 0:
                        combined_spans = torch.cat([spans_i, spans_j], dim=0)
                        targets['span_labels'][i] = {'spans': combined_spans}
                        metadata[i] = copy.deepcopy(metadata[i])
                        metadata[i]['relevant_windows'] = metadata[i].get('relevant_windows', []) + metadata[j].get('relevant_windows', [])
                        metadata[i]['synthetic_multi_target'] = True
                        aug_mul_count += 1

    return model_inputs, targets, metadata, aug_no_count, aug_mul_count
