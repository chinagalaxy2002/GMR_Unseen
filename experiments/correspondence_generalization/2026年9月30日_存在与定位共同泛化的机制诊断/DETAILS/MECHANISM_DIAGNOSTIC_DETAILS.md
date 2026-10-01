# D0/D3/D1/D2全部诊断记录

## diagnostics/ASSET_AND_COVERAGE.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "true_U_access": false,
  "families": {
    "throw": {
      "purpose": "training-internal pseudo-unseen diagnostic only; not official full-S training",
      "code_commit": "bc88348e0e6b7b629a77d884fe66efe8c87b2774",
      "code_sha256": "864614ee1f09a6336448f9aaf4ce3c0111537560f7f648f8af90e78bcf2d1876",
      "seed": 3407,
      "held_action": "throw",
      "source_train_sha256": "0cd951d33e1429d1cecf4ce0a661fc290dc4997b995abba362f76545bb486a14",
      "source_val_seen_sha256": "da227548ea5eb9f35b54e785cb6158a3b739cd88e76d6cd1d713e211e9f7e7a4",
      "derived": {
        "train.jsonl": {
          "path": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/pseudo_unseen_a1_throw_strict/train.jsonl",
          "sha256": "358a1d0a00c97ebb27395df96535b51ab74249793395373ceae94691c59dd0ef",
          "rows": 7559,
          "labels": {
            "0": 1307,
            "1": 6252
          }
        },
        "pseudo_unseen_dev.jsonl": {
          "path": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/pseudo_unseen_a1_throw_strict/pseudo_unseen_dev.jsonl",
          "sha256": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
          "rows": 570,
          "labels": {
            "0": 106,
            "1": 464
          }
        },
        "val_seen.jsonl": {
          "path": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/pseudo_unseen_a1_throw_strict/val_seen.jsonl",
          "sha256": "29166e4d694480fd41184bd4ff5802d1251103f4a042cdcbd9ac25ab7ddb6685",
          "rows": 1185,
          "labels": {
            "0": 476,
            "1": 709
          }
        }
      },
      "held_videos": 394,
      "train_dev_video_overlap": 0,
      "train_dev_qid_overlap": 0,
      "sampling": "Original row order retained; no altered rows, added queries, or new labels. All held-action videos excluded from derived train.",
      "semantic_audit": "Annotated primary throw family plus lexical throw/toss/hurl/fling/lob inflections; all extra matching training videos excluded.",
      "lexical_pattern": "\\b(?:throw|throws|throwing|threw|thrown|toss|tosses|tossing|tossed|hurl|hurls|hurling|hurled|fling|flings|flinging|flung|lob|lobs|lobbing|lobbed)\\b",
      "extra_excluded_videos": [
        "3EDV7",
        "HJJ32",
        "KU2T0",
        "TPSUY",
        "X5YL3"
      ],
      "extra_lexical_rows": [
        {
          "annotation_provenance": "Charades-STA positive via GMR pos_only export",
          "construction_type": "original_positive",
          "duration": 31.46770773735402,
          "exist_label": 1,
          "existence_status": "present",
          "novelty_type": "seen_composition",
          "partition": "S+",
          "qid": "train1819",
          "query": "person packing his bag thrown in the bed.",
          "relevant_windows": [
            [
              15.9,
              21.0
            ]
          ],
          "semantic_graph": {
            "action": "pack",
            "action_base": "pack",
            "action_class": "pack",
            "action_span": [
              7,
              14
            ],
            "action_wordnet_sense": "pack.v.01",
            "agent": "person",
            "canonicalization_confidence": "high",
            "location": null,
            "object": "bag",
            "object_concept": "bag",
            "object_role": "theme",
            "object_span": [
              19,
              22
            ],
            "object_wordnet_sense": "bag.n.01",
            "particle_span": null,
            "relation": null,
            "temporal_relation": null,
            "verbnet_classes": []
          },
          "semantic_status": "seen",
          "source_qid": "train1819",
          "source_split": "train",
          "verification_status": "human_temporal_annotation",
          "vid": "HJJ32",
          "video_id": "HJJ32"
        },
        {
          "annotation_provenance": "Charades-STA positive via GMR pos_only export",
          "construction_type": "original_positive",
          "duration": 31.8,
          "exist_label": 1,
          "existence_status": "present",
          "novelty_type": "seen_composition",
          "partition": "S+",
          "qid": "train4705",
          "query": "a person holding a broom throws it.",
          "relevant_windows": [
            [
              6.7,
              11.9
            ]
          ],
          "semantic_graph": {
            "action": "hold",
            "action_base": "hold",
            "action_class": "hold",
            "action_span": [
              9,
              16
            ],
            "action_wordnet_sense": "keep.v.01",
            "agent": "person",
            "canonicalization_confidence": "high",
            "location": null,
            "object": "broom",
            "object_concept": "broom",
            "object_role": "theme",
            "object_span": [
              19,
              24
            ],
            "object_wordnet_sense": "broom.n.01",
            "particle_span": null,
            "relation": null,
            "temporal_relation": null,
            "verbnet_classes": [
              "body_motion-49.2",
              "conduct-111.1",
              "conjecture-29.5",
              "contain-15.4",
              "exist-47.1",
              "fit-54.3",
              "keep-15.2",
              "own-100.1",
              "support-15.3",
              "sustain-55.6"
            ]
          },
          "semantic_status": "seen",
          "source_qid": "train4705",
          "source_split": "train",
          "verification_status": "human_temporal_annotation",
          "vid": "TPSUY",
          "video_id": "TPSUY"
        },
        {
          "annotation_provenance": "Charades-STA positive via GMR pos_only export",
          "construction_type": "original_positive",
          "duration": 18.44460570875665,
          "exist_label": 1,
          "existence_status": "present",
          "novelty_type": "seen_composition",
          "partition": "S+",
          "qid": "train5053",
          "query": "a person holding a bag throws food into a refrigerator.",
          "relevant_windows": [
            [
              0.0,
              2.8
            ]
          ],
          "semantic_graph": {
            "action": "hold",
            "action_base": "hold",
            "action_class": "hold",
            "action_span": [
              9,
              16
            ],
            "action_wordnet_sense": "keep.v.01",
            "agent": "person",
            "canonicalization_confidence": "high",
            "location": null,
            "object": "bag",
            "object_concept": "bag",
            "object_role": "theme",
            "object_span": [
              19,
              22
            ],
            "object_wordnet_sense": "bag.n.01",
            "particle_span": null,
            "relation": null,
            "temporal_relation": null,
            "verbnet_classes": [
              "body_motion-49.2",
              "conduct-111.1",
              "conjecture-29.5",
              "contain-15.4",
              "exist-47.1",
              "fit-54.3",
              "keep-15.2",
              "own-100.1",
              "support-15.3",
              "sustain-55.6"
            ]
          },
          "semantic_status": "seen",
          "source_qid": "train5053",
          "source_split": "train",
          "verification_status": "human_temporal_annotation",
          "vid": "X5YL3",
          "video_id": "X5YL3"
        },
        {
          "annotation_provenance": "Charades-STA positive via GMR pos_only export",
          "construction_type": "original_positive",
          "duration": 30.433333333333334,
          "exist_label": 1,
          "existence_status": "present",
          "novelty_type": "seen_composition",
          "partition": "S+",
          "qid": "train10983",
          "query": "one person is sitting in a chair tossing a pillow.",
          "relevant_windows": [
            [
              0.0,
              8.2
            ]
          ],
          "semantic_graph": {
            "action": "sit",
            "action_base": "sit",
            "action_class": "sit",
            "action_span": [
              14,
              21
            ],
            "action_wordnet_sense": "sit.v.01",
            "agent": "person",
            "canonicalization_confidence": "high",
            "location": "chair",
            "object": "chair",
            "object_concept": "chair",
            "object_role": "location",
            "object_span": [
              27,
              32
            ],
            "object_wordnet_sense": "chair.n.01",
            "particle_span": null,
            "relation": "in",
            "temporal_relation": null,
            "verbnet_classes": [
              "assuming_position-50",
              "put_spatial-9.2"
            ]
          },
          "semantic_status": "seen",
          "source_qid": "train10983",
          "source_split": "train",
          "verification_status": "human_temporal_annotation",
          "vid": "KU2T0",
          "video_id": "KU2T0"
        },
        {
          "annotation_provenance": "Charades-STA positive via GMR pos_only export",
          "construction_type": "original_positive",
          "duration": 30.291666666666668,
          "exist_label": 1,
          "existence_status": "present",
          "novelty_type": "seen_composition",
          "partition": "S+",
          "qid": "train12015",
          "query": "a person tosses clothes into their washer.",
          "relevant_windows": [
            [
              2.6,
              10.4
            ]
          ],
          "semantic_graph": {
            "action": "toss",
            "action_base": "toss",
            "action_class": "toss",
            "action_span": [
              9,
              15
            ],
            "action_wordnet_sense": "flip.v.06",
            "agent": "person",
            "canonicalization_confidence": "high",
            "location": null,
            "object": "clothe",
            "object_concept": "clothe",
            "object_role": "theme",
            "object_span": [
              16,
              23
            ],
            "object_wordnet_sense": null,
            "particle_span": null,
            "relation": null,
            "temporal_relation": null,
            "verbnet_classes": [
              "crane-40.3.2"
            ]
          },
          "semantic_status": "seen",
          "source_qid": "train12015",
          "source_split": "train",
          "verification_status": "human_temporal_annotation",
          "vid": "3EDV7",
          "video_id": "3EDV7"
        }
      ],
      "predecessor_manifest_sha256": "8f222c327fcbf8901e1018c9ea8849cf8d975740c2f584ca7bddc040c4b5690d",
      "limitations": "Lexical/annotated-family isolation is audited; no claim of complete conceptual separation or no pretrained exposure. Extra video exclusions introduce a distribution shift. Official full-S train unchanged."
    },
    "open_close": {
      "seed": 3407,
      "family": "open_close",
      "actions": [
        "open",
        "close"
      ],
      "lexical_pattern": "\\b(?:open|opens|opening|opened|close|closes|closing|closed|shut|shuts|shutting)\\b",
      "excluded_video_count": 1276,
      "source_train_sha256": "0cd951d33e1429d1cecf4ce0a661fc290dc4997b995abba362f76545bb486a14",
      "source_seen_sha256": "da227548ea5eb9f35b54e785cb6158a3b739cd88e76d6cd1d713e211e9f7e7a4",
      "derived": {
        "train.jsonl": {
          "sha256": "0ceef8a6e83977cef15b50f322115410792b83d1e2c04a3bf29bb3d745c2b672",
          "rows": 4625,
          "labels": {
            "1": 4188,
            "0": 437
          },
          "videos": 2442
        },
        "pseudo_unseen_dev.jsonl": {
          "sha256": "2866d727777b1c43a8f8eb6394c985b966c7300bb2693f950f4457f92c506a2e",
          "rows": 2827,
          "labels": {
            "1": 1888,
            "0": 939
          },
          "videos": 1236
        },
        "val_seen.jsonl": {
          "sha256": "4e8dcb029c0e7e8c9f550ea568077d49fc1842ba64493f090aca8f2ee55c2a56",
          "rows": 722,
          "labels": {
            "1": 516,
            "0": 206
          },
          "videos": 299
        }
      },
      "isolation": "annotated primary action and lexical family, not complete conceptual isolation",
      "original_rows_unchanged": true,
      "train_dev_video_overlap": 0
    },
    "sit": {
      "seed": 3407,
      "family": "sit",
      "actions": [
        "sit"
      ],
      "lexical_pattern": "\\b(?:sit|sits|sitting|sat|seat|seats|seated|seating)\\b",
      "excluded_video_count": 465,
      "source_train_sha256": "0cd951d33e1429d1cecf4ce0a661fc290dc4997b995abba362f76545bb486a14",
      "source_seen_sha256": "da227548ea5eb9f35b54e785cb6158a3b739cd88e76d6cd1d713e211e9f7e7a4",
      "derived": {
        "train.jsonl": {
          "sha256": "c5961e670d9fe9155cba6c98935b972de05f5ca54c86be908cb8ea3918377f7b",
          "rows": 6978,
          "labels": {
            "1": 5920,
            "0": 1058
          },
          "videos": 3253
        },
        "pseudo_unseen_dev.jsonl": {
          "sha256": "f1ee87f31d4e0257a2e3eb0d794b1ab55aa8024c51aa2967508d15d35d95b43c",
          "rows": 976,
          "labels": {
            "1": 625,
            "0": 351
          },
          "videos": 452
        },
        "val_seen.jsonl": {
          "sha256": "7af69ae2bdca9d5b9ce9367db036f9ce308f537727882cb616e586ed3d0837d5",
          "rows": 1065,
          "labels": {
            "1": 676,
            "0": 389
          },
          "videos": 370
        }
      },
      "isolation": "annotated primary action and lexical family, not complete conceptual isolation",
      "original_rows_unchanged": true,
      "train_dev_video_overlap": 0
    }
  }
}
```

## diagnostics/ASSET_REVALIDATION.json

```json
{
  "checked_at": "2026-10-01T00:00:00.905711+08:00",
  "source_train_sha256": "0cd951d33e1429d1cecf4ce0a661fc290dc4997b995abba362f76545bb486a14",
  "true_U_access": false,
  "families": {
    "throw": {
      "train_rows": 7559,
      "pseudo_rows": 570,
      "train_pseudo_video_overlap": 0,
      "original_row_bytes_unchanged": true,
      "training_lexical_family_leak_rows": 0,
      "derived_hashes": {
        "train.jsonl": "358a1d0a00c97ebb27395df96535b51ab74249793395373ceae94691c59dd0ef",
        "pseudo_unseen_dev.jsonl": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
        "val_seen.jsonl": "29166e4d694480fd41184bd4ff5802d1251103f4a042cdcbd9ac25ab7ddb6685"
      }
    },
    "open_close": {
      "train_rows": 4625,
      "pseudo_rows": 2827,
      "train_pseudo_video_overlap": 0,
      "original_row_bytes_unchanged": true,
      "training_lexical_family_leak_rows": 0,
      "derived_hashes": {
        "train.jsonl": "0ceef8a6e83977cef15b50f322115410792b83d1e2c04a3bf29bb3d745c2b672",
        "pseudo_unseen_dev.jsonl": "2866d727777b1c43a8f8eb6394c985b966c7300bb2693f950f4457f92c506a2e",
        "val_seen.jsonl": "4e8dcb029c0e7e8c9f550ea568077d49fc1842ba64493f090aca8f2ee55c2a56"
      }
    },
    "sit": {
      "train_rows": 6978,
      "pseudo_rows": 976,
      "train_pseudo_video_overlap": 0,
      "original_row_bytes_unchanged": true,
      "training_lexical_family_leak_rows": 0,
      "derived_hashes": {
        "train.jsonl": "c5961e670d9fe9155cba6c98935b972de05f5ca54c86be908cb8ea3918377f7b",
        "pseudo_unseen_dev.jsonl": "f1ee87f31d4e0257a2e3eb0d794b1ab55aa8024c51aa2967508d15d35d95b43c",
        "val_seen.jsonl": "7af69ae2bdca9d5b9ce9367db036f9ce308f537727882cb616e586ed3d0837d5"
      }
    }
  }
}
```

## diagnostics/BASELINE_METRICS.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "true_U_access": false,
  "seed": 3407,
  "resamples": 1000,
  "original_video_union": 2302,
  "bootstrap": "sample union of original videos once per replicate; reuse common multiplicities across all families and splits; equal family means",
  "intervals": "baseline absolute uncertainty only, not paired candidate gains or seed stability",
  "source_sha256": "69a70d8f6f4794e6588d4de50d4310d2cbd04eacad25b3e4baf750224ea5aef1",
  "families": {
    "throw": {
      "pseudo": {
        "metrics": {
          "AUROC": {
            "point": 0.5731030416395576,
            "ci_level": 0.975,
            "ci": [
              0.5014817007096817,
              0.6426058418525862
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.2672413793103448,
            "ci_level": 0.975,
            "ci": [
              0.2154702328404326,
              0.3193473625660518
            ],
            "valid_resamples": 1000
          },
          "gated_R1_05": {
            "point": 0.26939655172413796,
            "ci_level": 0.95,
            "ci": [
              0.2242085350939119,
              0.3164726925442714
            ],
            "valid_resamples": 1000
          },
          "FRR": {
            "point": 0.08836206896551724,
            "ci_level": 0.95,
            "ci": [
              0.059319246208742196,
              0.12025351695751459
            ],
            "valid_resamples": 1000
          },
          "RR": {
            "point": 0.1320754716981132,
            "ci_level": 0.95,
            "ci": [
              0.05677387406171814,
              0.22324617346938774
            ],
            "valid_resamples": 1000
          },
          "raw_correct_rejected_rate": {
            "point": 0.12096774193548387,
            "ci_level": 0.95,
            "ci": [
              0.05981481481481483,
              0.19205934793683138
            ],
            "valid_resamples": 1000
          }
        },
        "threshold": 0.9973,
        "source_hashes": {
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/views/pseudo.jsonl": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/pseudo_predictions.jsonl": "a5c4d5c0d3a5ee7bb4cb517a0af0c829868ddef9dd249964b7feb8230685501f",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/threshold_frozen.json": "c628ee3e943be5f110ff9f86eb77176ae55f733d73493a98b4ce5710b278c85e"
        },
        "raw_correct_rejected_denominator": 124
      },
      "seen": {
        "metrics": {
          "AUROC": {
            "point": 0.7996112408291949,
            "ci_level": 0.975,
            "ci": [
              0.7589208836216105,
              0.8356382418764773
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.4400564174894217,
            "ci_level": 0.975,
            "ci": [
              0.3880043354049719,
              0.48991202013014334
            ],
            "valid_resamples": 1000
          },
          "gated_R1_05": {
            "point": 0.4414668547249647,
            "ci_level": 0.95,
            "ci": [
              0.3974242424242424,
              0.48402960946141405
            ],
            "valid_resamples": 1000
          },
          "FRR": {
            "point": 0.2073342736248237,
            "ci_level": 0.95,
            "ci": [
              0.172505719097504,
              0.24428801670593273
            ],
            "valid_resamples": 1000
          },
          "RR": {
            "point": 0.7037815126050421,
            "ci_level": 0.95,
            "ci": [
              0.6525251185596013,
              0.7465353342799899
            ],
            "valid_resamples": 1000
          },
          "raw_correct_rejected_rate": {
            "point": 0.18269230769230768,
            "ci_level": 0.95,
            "ci": [
              0.13239077995175558,
              0.23077586206896553
            ],
            "valid_resamples": 1000
          }
        },
        "threshold": 0.9973,
        "source_hashes": {
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/views/val_seen.jsonl": "29166e4d694480fd41184bd4ff5802d1251103f4a042cdcbd9ac25ab7ddb6685",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/best_seen_predictions.jsonl": "606dd34aa6a38cacb278b767183719efa483a0fba24aa782806cb34798461d1f",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/threshold_frozen.json": "c628ee3e943be5f110ff9f86eb77176ae55f733d73493a98b4ce5710b278c85e"
        },
        "raw_correct_rejected_denominator": 312
      }
    },
    "open_close": {
      "pseudo": {
        "metrics": {
          "AUROC": {
            "point": 0.5346313130629411,
            "ci_level": 0.975,
            "ci": [
              0.5135996390069768,
              0.5573282193642973
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.2632415254237288,
            "ci_level": 0.975,
            "ci": [
              0.23531583987240087,
              0.2924013157894737
            ],
            "valid_resamples": 1000
          },
          "gated_R1_05": {
            "point": 0.2664194915254237,
            "ci_level": 0.95,
            "ci": [
              0.2432376533720898,
              0.29118475682482015
            ],
            "valid_resamples": 1000
          },
          "FRR": {
            "point": 0.14565677966101695,
            "ci_level": 0.95,
            "ci": [
              0.1277669139278901,
              0.16507083333333333
            ],
            "valid_resamples": 1000
          },
          "RR": {
            "point": 0.16826411075612355,
            "ci_level": 0.95,
            "ci": [
              0.14148847343560592,
              0.19486666236968817
            ],
            "valid_resamples": 1000
          },
          "raw_correct_rejected_rate": {
            "point": 0.1267605633802817,
            "ci_level": 0.95,
            "ci": [
              0.09356585643498058,
              0.15864016146050597
            ],
            "valid_resamples": 1000
          }
        },
        "threshold": 0.9977,
        "source_hashes": {
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/views/pseudo.jsonl": "2866d727777b1c43a8f8eb6394c985b966c7300bb2693f950f4457f92c506a2e",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/pseudo_predictions.jsonl": "7c28e4de9e2164a344c83784e4534715c8a90921529612116e3226e36990fbbf",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/threshold_frozen.json": "1379fca89be53a0a8654ccc8a752ffb5c0a0d18ecb718a5ca32fe8757eefb5b3"
        },
        "raw_correct_rejected_denominator": 497
      },
      "seen": {
        "metrics": {
          "AUROC": {
            "point": 0.8560905396251975,
            "ci_level": 0.975,
            "ci": [
              0.8094918427640889,
              0.8922124864331086
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.32945736434108525,
            "ci_level": 0.975,
            "ci": [
              0.2818796641791045,
              0.38156638294862427
            ],
            "valid_resamples": 1000
          },
          "gated_R1_05": {
            "point": 0.34108527131782945,
            "ci_level": 0.95,
            "ci": [
              0.29803823529411766,
              0.388548359772994
            ],
            "valid_resamples": 1000
          },
          "FRR": {
            "point": 0.18992248062015504,
            "ci_level": 0.95,
            "ci": [
              0.15176737483758604,
              0.22874864224350744
            ],
            "valid_resamples": 1000
          },
          "RR": {
            "point": 0.7961165048543689,
            "ci_level": 0.95,
            "ci": [
              0.7242979772225056,
              0.8526628214371544
            ],
            "valid_resamples": 1000
          },
          "raw_correct_rejected_rate": {
            "point": 0.18235294117647058,
            "ci_level": 0.95,
            "ci": [
              0.12039579834699861,
              0.2431021009014248
            ],
            "valid_resamples": 1000
          }
        },
        "threshold": 0.9977,
        "source_hashes": {
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/views/val_seen.jsonl": "4e8dcb029c0e7e8c9f550ea568077d49fc1842ba64493f090aca8f2ee55c2a56",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/best_seen_predictions.jsonl": "c847d74492c9ecf0d8022e233b8a1340ada6025e2535a0e0e7ba7be353400573",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/threshold_frozen.json": "1379fca89be53a0a8654ccc8a752ffb5c0a0d18ecb718a5ca32fe8757eefb5b3"
        },
        "raw_correct_rejected_denominator": 170
      }
    },
    "sit": {
      "pseudo": {
        "metrics": {
          "AUROC": {
            "point": 0.6540216524216524,
            "ci_level": 0.975,
            "ci": [
              0.6073986537625757,
              0.6993250743427879
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.3504,
            "ci_level": 0.975,
            "ci": [
              0.29718870538845166,
              0.40527039531877257
            ],
            "valid_resamples": 1000
          },
          "gated_R1_05": {
            "point": 0.3536,
            "ci_level": 0.95,
            "ci": [
              0.305259374474525,
              0.3981257520320212
            ],
            "valid_resamples": 1000
          },
          "FRR": {
            "point": 0.064,
            "ci_level": 0.95,
            "ci": [
              0.04454042485466822,
              0.08591962522302472
            ],
            "valid_resamples": 1000
          },
          "RR": {
            "point": 0.23076923076923078,
            "ci_level": 0.95,
            "ci": [
              0.18356164383561643,
              0.2788250040732896
            ],
            "valid_resamples": 1000
          },
          "raw_correct_rejected_rate": {
            "point": 0.0821917808219178,
            "ci_level": 0.95,
            "ci": [
              0.04625883529855519,
              0.12684035476718403
            ],
            "valid_resamples": 1000
          }
        },
        "threshold": 0.955,
        "source_hashes": {
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/views/pseudo.jsonl": "f1ee87f31d4e0257a2e3eb0d794b1ab55aa8024c51aa2967508d15d35d95b43c",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/pseudo_predictions.jsonl": "7deaad795715181e45bf4fcb2ceab641bea0920d8f402184e805551c437a7861",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/threshold_frozen.json": "badcb1c6921b4126f059d286f99cc1c3114e295a18ae5ee135c3da9a659d5b66"
        },
        "raw_correct_rejected_denominator": 219
      },
      "seen": {
        "metrics": {
          "AUROC": {
            "point": 0.8432142802817115,
            "ci_level": 0.975,
            "ci": [
              0.8166176245444142,
              0.8691409545365121
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.3254437869822485,
            "ci_level": 0.975,
            "ci": [
              0.280035502751609,
              0.36845463318511396
            ],
            "valid_resamples": 1000
          },
          "gated_R1_05": {
            "point": 0.3224852071005917,
            "ci_level": 0.95,
            "ci": [
              0.28074815593225844,
              0.35901489875398856
            ],
            "valid_resamples": 1000
          },
          "FRR": {
            "point": 0.3668639053254438,
            "ci_level": 0.95,
            "ci": [
              0.31816620402498264,
              0.4116113754232566
            ],
            "valid_resamples": 1000
          },
          "RR": {
            "point": 0.9125964010282777,
            "ci_level": 0.95,
            "ci": [
              0.8810710995085995,
              0.9382438068254676
            ],
            "valid_resamples": 1000
          },
          "raw_correct_rejected_rate": {
            "point": 0.35,
            "ci_level": 0.95,
            "ci": [
              0.278937154530161,
              0.42411052489177486
            ],
            "valid_resamples": 1000
          }
        },
        "threshold": 0.955,
        "source_hashes": {
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/views/val_seen.jsonl": "7af69ae2bdca9d5b9ce9367db036f9ce308f537727882cb616e586ed3d0837d5",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/best_seen_predictions.jsonl": "e8ec2c706ec1bc9f407ac71759f99f95e861806fe59209a3569031ffca391364",
          "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/threshold_frozen.json": "badcb1c6921b4126f059d286f99cc1c3114e295a18ae5ee135c3da9a659d5b66"
        },
        "raw_correct_rejected_denominator": 220
      }
    }
  },
  "equal_family_mean": {
    "pseudo": {
      "AUROC": {
        "point": 0.5872520023747171,
        "ci_level": 0.975,
        "ci": [
          0.5572876304308823,
          0.6145576836895199
        ],
        "valid_resamples": 1000
      },
      "raw_R1_05": {
        "point": 0.29362763491135785,
        "ci_level": 0.975,
        "ci": [
          0.2669078661192343,
          0.3192471166072328
        ],
        "valid_resamples": 1000
      },
      "gated_R1_05": {
        "point": 0.29647201441652055,
        "ci_level": 0.95,
        "ci": [
          0.27316907179657124,
          0.32047290598556566
        ],
        "valid_resamples": 1000
      },
      "FRR": {
        "point": 0.09933961620884472,
        "ci_level": 0.95,
        "ci": [
          0.08585090709500365,
          0.11363597699227673
        ],
        "valid_resamples": 1000
      },
      "RR": {
        "point": 0.1770362710744892,
        "ci_level": 0.95,
        "ci": [
          0.14721402519652557,
          0.21125314461025033
        ],
        "valid_resamples": 1000
      },
      "raw_correct_rejected_rate": {
        "point": 0.10997336204589446,
        "ci_level": 0.95,
        "ci": [
          0.08263200112853764,
          0.1385865749682349
        ],
        "valid_resamples": 1000
      }
    },
    "seen": {
      "AUROC": {
        "point": 0.8329720202453679,
        "ci_level": 0.975,
        "ci": [
          0.8054962791657936,
          0.856512982969963
        ],
        "valid_resamples": 1000
      },
      "raw_R1_05": {
        "point": 0.3649858562709185,
        "ci_level": 0.975,
        "ci": [
          0.32859277104133455,
          0.4007940410343201
        ],
        "valid_resamples": 1000
      },
      "gated_R1_05": {
        "point": 0.3683457777144619,
        "ci_level": 0.95,
        "ci": [
          0.33585731757420884,
          0.4002539550407898
        ],
        "valid_resamples": 1000
      },
      "FRR": {
        "point": 0.2547068865234742,
        "ci_level": 0.95,
        "ci": [
          0.22431897286649857,
          0.2820221023463264
        ],
        "valid_resamples": 1000
      },
      "RR": {
        "point": 0.8041648061625629,
        "ci_level": 0.95,
        "ci": [
          0.7631524300797349,
          0.8370285813665417
        ],
        "valid_resamples": 1000
      },
      "raw_correct_rejected_rate": {
        "point": 0.23834841628959272,
        "ci_level": 0.95,
        "ci": [
          0.19922023790582932,
          0.28025786147228077
        ],
        "valid_resamples": 1000
      }
    }
  },
  "training_scope": "Saved seen-selected checkpoints; throw/open_close trained 100 epochs, sit stopped after 77 logged epochs. No new training; cross-family mean descriptive, not uniform completed-budget evidence."
}
```

## diagnostics/FAMILY_MANIFEST.json

```json
{
  "seed": 3407,
  "families": [
    "throw",
    "open_close",
    "sit"
  ],
  "selection": "original training coverage only; no U/test or method outcomes",
  "source_train_sha256": "0cd951d33e1429d1cecf4ce0a661fc290dc4997b995abba362f76545bb486a14",
  "views": {
    "throw": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/pseudo_unseen_a1_throw_strict",
    "open_close": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/views/open_close",
    "sit": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/views/sit"
  }
}
```

## diagnostics/open_close/baseline/CONTROLLED_QUERY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "query_groups": 158,
  "rows": 1598,
  "pairs": 7367,
  "pairacc": 0.5469662006244062,
  "video_endpoint_bootstrap_ci95": [
    0.5067282248928595,
    0.5883323923471798
  ],
  "text_input": "same normalized cached feature and mask per identical query, canonical lexicographically smallest qid; original video and labels unchanged",
  "pure_text_pairacc_control": 0.5,
  "checkpoint_sha256": "7c0e74c81535fc3371772c9706331b09c2b43f0c16c0d0504ca3d2244ab415ea",
  "scores": {
    "train16": 0.9999871253967285,
    "train34": 0.999545156955719,
    "train53": 0.9999475479125977,
    "train54": 0.9999381303787231,
    "train57": 0.9999847412109375,
    "train72": 0.9999533891677856,
    "train73": 0.9999216794967651,
    "train74": 0.9998881816864014,
    "train92": 0.9325682520866394,
    "train94": 0.8802449107170105,
    "train95": 0.9999902248382568,
    "train109": 0.9999467134475708,
    "train134": 0.9999756813049316,
    "train142": 0.9998877048492432,
    "train169": 0.9999498128890991,
    "train174": 0.9007682800292969,
    "train206": 0.999442994594574,
    "train208": 0.3095126748085022,
    "train248": 0.9998335838317871,
    "train256": 0.9996747970581055,
    "train287": 0.999984860420227,
    "train299": 0.9999978542327881,
    "train309": 0.9998389482498169,
    "train310": 0.9998815059661865,
    "train387": 0.9999350309371948,
    "train424": 0.9999871253967285,
    "train457": 0.8766962289810181,
    "train460": 0.9999438524246216,
    "train469": 0.9999508857727051,
    "train470": 0.9999682903289795,
    "train483": 0.9637911915779114,
    "train501": 0.9251239895820618,
    "train510": 0.9995379447937012,
    "train511": 0.999508261680603,
    "train532": 0.9999628067016602,
    "train534": 0.9999514818191528,
    "train550": 0.17961323261260986,
    "train570": 0.9999309778213501,
    "train585": 0.9999343156814575,
    "train592": 0.9999676942825317,
    "train595": 0.9999570846557617,
    "train603": 0.9998242259025574,
    "train608": 0.9998248219490051,
    "train666": 0.9982851147651672,
    "train672": 0.7973620891571045,
    "train675": 0.9999834299087524,
    "train701": 0.99996018409729,
    "train703": 0.9999628067016602,
    "train734": 0.9999234676361084,
    "train737": 0.9999419450759888,
    "train743": 0.9986329674720764,
    "train763": 0.999990701675415,
    "train776": 0.9997708201408386,
    "train790": 0.9997581839561462,
    "train830": 0.9999275207519531,
    "train831": 0.9997619986534119,
    "train832": 0.9997718930244446,
    "train835": 0.999764621257782,
    "train852": 0.9994698166847229,
    "train900": 0.9999810457229614,
    "train907": 0.9999490976333618,
    "train921": 0.9965499639511108,
    "train922": 0.9839199185371399,
    "train926": 0.9998651742935181,
    "train936": 0.7568463683128357,
    "train969": 0.9998912811279297,
    "train975": 0.9999700784683228,
    "train976": 0.9999938011169434,
    "train977": 0.999994158744812,
    "train981": 0.9997264742851257,
    "train983": 0.9999815225601196,
    "train999": 0.9999901056289673,
    "train1004": 0.9999016523361206,
    "train1023": 0.9994457364082336,
    "train1030": 0.997509241104126,
    "train1043": 0.9997785687446594,
    "train1057": 0.9826206564903259,
    "train1063": 0.9999052286148071,
    "train1082": 0.9998304843902588,
    "train1102": 0.9995970129966736,
    "train1124": 0.999980092048645,
    "train1127": 0.9999901056289673,
    "train1140": 0.9999085664749146,
    "train1141": 0.9999659061431885,
    "train1158": 0.9999786615371704,
    "train1165": 0.9999624490737915,
    "train1174": 0.9907124638557434,
    "train1180": 0.9997072815895081,
    "train1185": 0.9945135116577148,
    "train1186": 0.9999229907989502,
    "train1187": 0.9995760321617126,
    "train1188": 0.9992951154708862,
    "train1194": 0.9999818801879883,
    "train1206": 0.9988766312599182,
    "train1216": 0.9898797273635864,
    "train1237": 0.9999808073043823,
    "train1244": 0.999810516834259,
    "train1246": 0.9999377727508545,
    "train1265": 0.9995612502098083,
    "train1332": 0.9999912977218628,
    "train1338": 0.9998683929443359,
    "train1340": 0.9999732971191406,
    "train1346": 0.999943733215332,
    "train1356": 0.9999887943267822,
    "train1372": 0.9998155236244202,
    "train1373": 0.9998098015785217,
    "train1383": 0.9998213648796082,
    "train1430": 0.999826967716217,
    "train1450": 0.999276340007782,
    "train1473": 0.9999336004257202,
    "train1487": 0.9994567036628723,
    "train1489": 0.9998644590377808,
    "train1494": 0.9999784231185913,
    "train1527": 0.9999542236328125,
    "train1534": 0.9989822506904602,
    "train1559": 0.9999490976333618,
    "train1578": 0.9992345571517944,
    "train1593": 0.9999626874923706,
    "train1595": 0.9999920129776001,
    "train1596": 0.9999686479568481,
    "train1613": 0.9999730587005615,
    "train1625": 0.26694223284721375,
    "train1629": 0.9999582767486572,
    "train1641": 0.9999970197677612,
    "train1649": 0.9996867179870605,
    "train1654": 0.9999340772628784,
    "train1661": 0.9999499320983887,
    "train1668": 0.9939743876457214,
    "train1673": 0.9999393224716187,
    "train1695": 0.9999645948410034,
    "train1703": 0.9997878670692444,
    "train1705": 0.9995772242546082,
    "train1706": 0.9994379878044128,
    "train1717": 0.9887802600860596,
    "train1738": 0.9997655749320984,
    "train1766": 0.9987389445304871,
    "train1775": 0.9999785423278809,
    "train1816": 0.9998360872268677,
    "train1823": 0.9994205236434937,
    "train1825": 0.9998961687088013,
    "train1841": 0.9988352656364441,
    "train1848": 0.9981070756912231,
    "train1851": 0.9999845027923584,
    "train1854": 0.9999573230743408,
    "train1882": 0.9994632601737976,
    "train1888": 0.9999247789382935,
    "train1889": 0.9999390840530396,
    "train1903": 0.9999175071716309,
    "train1910": 0.999929666519165,
    "train1919": 0.9999650716781616,
    "train1947": 0.9999948740005493,
    "train1954": 0.9999184608459473,
    "train1966": 0.999974250793457,
    "train1970": 0.9999403953552246,
    "train1971": 0.9999091625213623,
    "train1983": 0.9992873072624207,
    "train1990": 0.9999958276748657,
    "train1994": 0.999624490737915,
    "train1997": 0.9997699856758118,
    "train1999": 0.9995170831680298,
    "train2028": 0.9999970197677612,
    "train2058": 0.9995552897453308,
    "train2065": 0.9996247291564941,
    "train2080": 0.9999175071716309,
    "train2103": 0.9998353719711304,
    "train2106": 0.9996811151504517,
    "train2141": 0.9999475479125977,
    "train2142": 0.999956488609314,
    "train2150": 0.9999574422836304,
    "train2157": 0.9999942779541016,
    "train2164": 0.9999935626983643,
    "train2196": 0.9999312162399292,
    "train2197": 0.999828577041626,
    "train2198": 0.9999390840530396,
    "train2199": 0.9999505281448364,
    "train2207": 0.9976905584335327,
    "train2212": 0.9541795253753662,
    "train2219": 0.9997182488441467,
    "train2220": 0.9998949766159058,
    "train2234": 0.9999516010284424,
    "train2237": 0.9999716281890869,
    "train2244": 0.9990835189819336,
    "train2246": 0.9987503290176392,
    "train2254": 0.9992595314979553,
    "train2304": 0.9999047517776489,
    "train2308": 0.854141116142273,
    "train2309": 0.9999105930328369,
    "train2310": 0.9999567270278931,
    "train2318": 0.9993429780006409,
    "train2336": 0.9999724626541138,
    "train2350": 0.9999932050704956,
    "train2376": 0.9973642230033875,
    "train2390": 0.99873286485672,
    "train2454": 0.9999926090240479,
    "train2467": 0.9994377493858337,
    "train2492": 0.9993345141410828,
    "train2497": 0.0020691403187811375,
    "train2498": 0.9994572997093201,
    "train2499": 0.9998906850814819,
    "train2521": 0.9999810457229614,
    "train2537": 0.999197781085968,
    "train2561": 0.9999892711639404,
    "train2563": 0.9997276663780212,
    "train2573": 0.9998925924301147,
    "train2577": 0.999972939491272,
    "train2583": 0.9990515112876892,
    "train2584": 0.9968902468681335,
    "train2614": 0.9999924898147583,
    "train2618": 0.9999004602432251,
    "train2633": 0.9999979734420776,
    "train2639": 0.999911904335022,
    "train2641": 0.9999110698699951,
    "train2651": 0.9998801946640015,
    "train2653": 0.9998472929000854,
    "train2661": 0.003818654455244541,
    "train2662": 0.99992835521698,
    "train2664": 0.43566060066223145,
    "train2677": 0.9999810457229614,
    "train2711": 0.9997430443763733,
    "train2712": 0.9998840093612671,
    "train2713": 0.9999227523803711,
    "train2718": 0.99988853931427,
    "train2720": 0.9999303817749023,
    "train2726": 0.9998025298118591,
    "train2741": 0.9999741315841675,
    "train2747": 0.999983549118042,
    "train2748": 0.9999833106994629,
    "train2752": 0.9996777772903442,
    "train2755": 0.999946117401123,
    "train2820": 0.9999504089355469,
    "train2829": 0.996996283531189,
    "train2835": 0.9999823570251465,
    "train2840": 0.9999600648880005,
    "train2845": 0.9997945427894592,
    "train2856": 0.9999212026596069,
    "train2863": 0.9999727010726929,
    "train2864": 0.9999616146087646,
    "train2871": 0.9999902248382568,
    "train2899": 0.9995965361595154,
    "train2901": 0.9991316199302673,
    "train2927": 0.001593441003933549,
    "train2933": 0.9999550580978394,
    "train2960": 0.999783456325531,
    "train2962": 0.999821126461029,
    "train2972": 0.9999982118606567,
    "train2981": 0.9999877214431763,
    "train2983": 0.9999769926071167,
    "train2984": 0.9999779462814331,
    "train2992": 0.9999597072601318,
    "train3013": 0.9995232820510864,
    "train3029": 0.9999661445617676,
    "train3034": 0.9999884366989136,
    "train3045": 0.9995179176330566,
    "train3049": 0.9999245405197144,
    "train3053": 0.7822617888450623,
    "train3073": 0.9992280006408691,
    "train3092": 0.999975323677063,
    "train3111": 0.9999146461486816,
    "train3113": 0.9998805522918701,
    "train3123": 0.9996718168258667,
    "train3128": 0.9996522665023804,
    "train3140": 0.9998831748962402,
    "train3158": 0.999786913394928,
    "train3160": 0.9998977184295654,
    "train3162": 0.9999972581863403,
    "train3164": 0.999997615814209,
    "train3175": 0.9999520778656006,
    "train3192": 0.9999681711196899,
    "train3193": 0.9998661279678345,
    "train3195": 0.9999468326568604,
    "train3218": 0.9999552965164185,
    "train3224": 0.8881950378417969,
    "train3241": 0.9999754428863525,
    "train3279": 0.9999748468399048,
    "train3281": 0.9999854564666748,
    "train3284": 0.8256863951683044,
    "train3312": 0.9998787641525269,
    "train3326": 0.999800980091095,
    "train3338": 0.9999648332595825,
    "train3341": 0.9999861717224121,
    "train3360": 0.06143728271126747,
    "train3385": 0.9999868869781494,
    "train3387": 0.9999576807022095,
    "train3403": 0.9997661709785461,
    "train3404": 0.9999680519104004,
    "train3407": 0.9998632669448853,
    "train3414": 0.9999948740005493,
    "train3442": 0.9999655485153198,
    "train3444": 0.9999450445175171,
    "train3463": 0.9999804496765137,
    "train3466": 0.9999860525131226,
    "train3482": 0.9990745782852173,
    "train3514": 0.9999737739562988,
    "train3530": 0.9997594952583313,
    "train3583": 0.8486394882202148,
    "train3617": 0.9999951124191284,
    "train3621": 0.9999873638153076,
    "train3630": 0.999243974685669,
    "train3631": 0.9999274015426636,
    "train3689": 0.9978421926498413,
    "train3694": 0.9999821186065674,
    "train3696": 0.9998592138290405,
    "train3697": 0.999638557434082,
    "train3699": 0.9999395608901978,
    "train3702": 0.999997615814209,
    "train3709": 0.9996331930160522,
    "train3754": 0.007811075542122126,
    "train3755": 0.08630659431219101,
    "train3761": 0.9998704195022583,
    "train3769": 0.9999011754989624,
    "train3770": 0.9999924898147583,
    "train3771": 0.9998992681503296,
    "train3773": 0.9999269247055054,
    "train3775": 0.999970555305481,
    "train3777": 0.9999814033508301,
    "train3807": 0.9964959025382996,
    "train3811": 0.9999829530715942,
    "train3813": 0.9999719858169556,
    "train3814": 0.3040091395378113,
    "train3833": 0.9999735355377197,
    "train3846": 0.9999938011169434,
    "train3878": 0.9998637437820435,
    "train3890": 0.9995157718658447,
    "train3893": 0.999333918094635,
    "train3894": 0.9999825954437256,
    "train3919": 0.9999547004699707,
    "train3933": 0.9995443224906921,
    "train3935": 0.9999572038650513,
    "train3936": 0.999947190284729,
    "train3948": 0.938634991645813,
    "train3958": 0.9995672106742859,
    "train3959": 0.9992347955703735,
    "train4005": 0.9975979924201965,
    "train4017": 0.9999752044677734,
    "train4027": 0.9999855756759644,
    "train4031": 0.9997149109840393,
    "train4044": 0.9999967813491821,
    "train4046": 0.9999959468841553,
    "train4051": 0.9999879598617554,
    "train4079": 0.9997145533561707,
    "train4080": 0.9999669790267944,
    "train4081": 0.9999827146530151,
    "train4084": 0.9849048852920532,
    "train4085": 0.9955582618713379,
    "train4110": 0.9999711513519287,
    "train4124": 0.9999071359634399,
    "train4125": 0.9998542070388794,
    "train4126": 0.9999430179595947,
    "train4132": 0.9998677968978882,
    "train4141": 0.9999856948852539,
    "train4161": 0.9996172189712524,
    "train4171": 0.9997988343238831,
    "train4172": 0.999984622001648,
    "train4186": 0.9999607801437378,
    "train4212": 0.9998550415039062,
    "train4239": 0.9999619722366333,
    "train4241": 0.999913215637207,
    "train4250": 0.9992724061012268,
    "train4251": 0.9994694590568542,
    "train4263": 0.9990764856338501,
    "train4288": 0.9991075396537781,
    "train4306": 0.9999666213989258,
    "train4307": 0.9991974234580994,
    "train4362": 0.9999674558639526,
    "train4380": 0.9999970197677612,
    "train4383": 0.9998887777328491,
    "train4394": 0.9996875524520874,
    "train4415": 0.0007520914077758789,
    "train4450": 0.9996721744537354,
    "train4455": 0.9999309778213501,
    "train4457": 0.9998825788497925,
    "train4464": 0.9999432563781738,
    "train4474": 0.9645893573760986,
    "train4515": 0.9999246597290039,
    "train4534": 0.9914171099662781,
    "train4536": 0.9783292412757874,
    "train4541": 0.9999372959136963,
    "train4548": 0.9993146657943726,
    "train4554": 0.9999374151229858,
    "train4604": 0.8353203535079956,
    "train4634": 0.9999779462814331,
    "train4637": 0.9999101161956787,
    "train4639": 0.9999887943267822,
    "train4644": 0.713748037815094,
    "train4653": 0.9999086856842041,
    "train4654": 0.9997919201850891,
    "train4686": 0.6584964394569397,
    "train4688": 0.8079342842102051,
    "train4692": 0.9997250437736511,
    "train4698": 0.9999088048934937,
    "train4701": 0.9999364614486694,
    "train4737": 0.9997560381889343,
    "train4742": 0.9996402263641357,
    "train4748": 0.9976479411125183,
    "train4764": 0.9993890523910522,
    "train4791": 0.9999346733093262,
    "train4833": 0.9999339580535889,
    "train4834": 0.9998874664306641,
    "train4849": 0.9999969005584717,
    "train4870": 0.9998243451118469,
    "train4904": 0.993118405342102,
    "train4909": 0.9999724626541138,
    "train4924": 0.9998613595962524,
    "train4982": 0.5205544829368591,
    "train4990": 0.9965498447418213,
    "train4999": 0.9999657869338989,
    "train5000": 0.9999667406082153,
    "train5003": 0.9999799728393555,
    "train5022": 0.9998156428337097,
    "train5040": 0.9999858140945435,
    "train5056": 0.99950110912323,
    "train5057": 0.999699592590332,
    "train5060": 0.9999895095825195,
    "train5061": 0.9999881982803345,
    "train5077": 0.9992507100105286,
    "train5080": 0.999958872795105,
    "train5081": 0.9999874830245972,
    "train5090": 0.9999222755432129,
    "train5108": 0.999805748462677,
    "train5139": 0.9999176263809204,
    "train5140": 0.9999120235443115,
    "train5143": 0.8626994490623474,
    "train5152": 0.9999792575836182,
    "train5162": 0.9996408224105835,
    "train5163": 0.99928879737854,
    "train5182": 0.9999462366104126,
    "train5187": 0.9999817609786987,
    "train5206": 0.9987654685974121,
    "train5218": 0.9988940358161926,
    "train5231": 0.9999816417694092,
    "train5256": 0.9998829364776611,
    "train5272": 0.9996253252029419,
    "train5275": 0.9996294975280762,
    "train5279": 0.9998546838760376,
    "train5284": 0.9987574815750122,
    "train5291": 0.9999542236328125,
    "train5293": 0.999932050704956,
    "train5309": 0.9998642206192017,
    "train5356": 0.9999912977218628,
    "train5388": 0.8389112949371338,
    "train5389": 0.933426022529602,
    "train5398": 0.9999669790267944,
    "train5408": 0.39289167523384094,
    "train5438": 0.9999796152114868,
    "train5444": 0.9999327659606934,
    "train5460": 0.9998190999031067,
    "train5499": 0.9999535083770752,
    "train5517": 0.9958874583244324,
    "train5554": 0.9996384382247925,
    "train5556": 0.9998113512992859,
    "train5621": 0.9998769760131836,
    "train5623": 0.9998722076416016,
    "train5633": 0.9998743534088135,
    "train5674": 0.9998607635498047,
    "train5675": 0.9983684420585632,
    "train5709": 0.9999241828918457,
    "train5710": 0.9999639987945557,
    "train5754": 0.9996479749679565,
    "train5815": 0.9990715980529785,
    "train5860": 0.9998154044151306,
    "train5861": 0.9999856948852539,
    "train5885": 0.9888258576393127,
    "train5898": 0.999881386756897,
    "train5938": 0.9998494386672974,
    "train5940": 0.10005112737417221,
    "train5950": 0.9999176263809204,
    "train5981": 0.9699095487594604,
    "train5983": 0.9832563400268555,
    "train6001": 0.9997486472129822,
    "train6010": 0.9999635219573975,
    "train6026": 0.9994902610778809,
    "train6045": 0.9998713731765747,
    "train6048": 0.9999983310699463,
    "train6055": 0.9998503923416138,
    "train6068": 0.9995532631874084,
    "train6089": 0.9997184872627258,
    "train6109": 0.9997479319572449,
    "train6110": 0.9996826648712158,
    "train6113": 0.9998888969421387,
    "train6118": 0.9997351765632629,
    "train6119": 0.99949049949646,
    "train6123": 0.9999147653579712,
    "train6125": 0.9997929930686951,
    "train6159": 0.9999971389770508,
    "train6161": 0.9999319314956665,
    "train6173": 0.9999815225601196,
    "train6180": 0.9993622899055481,
    "train6181": 0.9999562501907349,
    "train6182": 0.9999202489852905,
    "train6194": 0.9999234676361084,
    "train6217": 0.7408170104026794,
    "train6228": 0.99985671043396,
    "train6229": 0.9993023872375488,
    "train6230": 0.9992685914039612,
    "train6231": 0.9998761415481567,
    "train6236": 0.9999616146087646,
    "train6263": 0.9999798536300659,
    "train6269": 0.999921441078186,
    "train6270": 0.9999394416809082,
    "train6276": 0.9999411106109619,
    "train6292": 0.999988317489624,
    "train6302": 0.9999580383300781,
    "train6307": 0.9997432827949524,
    "train6308": 0.9999487400054932,
    "train6311": 0.9997876286506653,
    "train6318": 0.9957255125045776,
    "train6339": 0.9997084736824036,
    "train6346": 0.9999812841415405,
    "train6347": 0.9999847412109375,
    "train6399": 0.9997033476829529,
    "train6407": 0.9999847412109375,
    "train6420": 0.9999017715454102,
    "train6421": 0.9999109506607056,
    "train6438": 0.9999184608459473,
    "train6443": 0.999953031539917,
    "train6463": 0.9999493360519409,
    "train6500": 0.9976237416267395,
    "train6503": 0.999984622001648,
    "train6506": 0.9997299313545227,
    "train6529": 0.9999717473983765,
    "train6541": 0.9999762773513794,
    "train6549": 0.9998648166656494,
    "train6553": 0.9999818801879883,
    "train6557": 0.9999231100082397,
    "train6576": 0.9997274279594421,
    "train6578": 0.9999823570251465,
    "train6616": 0.999894380569458,
    "train6619": 0.9998791217803955,
    "train6626": 0.9988666772842407,
    "train6635": 0.9999746084213257,
    "train6650": 0.9997503161430359,
    "train6651": 0.9999843835830688,
    "train6655": 0.9997656941413879,
    "train6679": 0.9999754428863525,
    "train6680": 0.9996097683906555,
    "train6691": 0.9999089241027832,
    "train6695": 0.9978873133659363,
    "train6744": 0.9999148845672607,
    "train6753": 0.9999349117279053,
    "train6783": 0.27445223927497864,
    "train6788": 0.9852702617645264,
    "train6794": 0.9994346499443054,
    "train6829": 0.999950647354126,
    "train6841": 0.9995054006576538,
    "train6845": 0.998993456363678,
    "train6851": 0.897700846195221,
    "train6855": 0.9998281002044678,
    "train6859": 0.9999878406524658,
    "train6888": 0.9999860525131226,
    "train6890": 0.9999862909317017,
    "train6891": 0.9999855756759644,
    "train6926": 0.9999864101409912,
    "train6927": 0.999944806098938,
    "train6945": 0.9997305274009705,
    "train6946": 0.9996746778488159,
    "train6947": 0.9999567270278931,
    "train6951": 0.9998939037322998,
    "train6966": 0.9997003078460693,
    "train6974": 0.999980092048645,
    "train6977": 0.9995397329330444,
    "train6986": 0.999970555305481,
    "train6988": 0.7979075312614441,
    "train7041": 0.9995474219322205,
    "train7044": 0.999913215637207,
    "train7065": 0.9999856948852539,
    "train7066": 0.9999827146530151,
    "train7084": 0.9999779462814331,
    "train7086": 0.9999690055847168,
    "train7108": 0.9992278814315796,
    "train7113": 0.9997316002845764,
    "train7134": 0.961463451385498,
    "train7136": 0.999969482421875,
    "train7152": 0.8512306213378906,
    "train7153": 0.9992654919624329,
    "train7159": 0.9988731741905212,
    "train7164": 0.999946117401123,
    "train7166": 0.9999548196792603,
    "train7176": 0.9929585456848145,
    "train7195": 0.9999340772628784,
    "train7201": 0.9998832941055298,
    "train7202": 0.9999291896820068,
    "train7225": 0.9999463558197021,
    "train7226": 0.9999160766601562,
    "train7230": 0.9998124241828918,
    "train7233": 0.9999490976333618,
    "train7238": 0.9998453855514526,
    "train7242": 0.9999598264694214,
    "train7248": 0.9999809265136719,
    "train7269": 0.9998492002487183,
    "train7273": 0.999991774559021,
    "train7300": 0.9999831914901733,
    "train7304": 0.9997890591621399,
    "train7326": 0.9999858140945435,
    "train7332": 0.9996131062507629,
    "train7335": 0.9999921321868896,
    "train7336": 0.9999914169311523,
    "train7337": 0.9999915361404419,
    "train7342": 0.9997269511222839,
    "train7361": 0.9999207258224487,
    "train7362": 0.9999593496322632,
    "train7369": 0.999970555305481,
    "train7402": 0.9974251985549927,
    "train7424": 0.9996433258056641,
    "train7432": 0.9999785423278809,
    "train7433": 0.9999524354934692,
    "train7451": 0.9997417330741882,
    "train7453": 0.9996320009231567,
    "train7460": 0.9994754195213318,
    "train7466": 0.9994908571243286,
    "train7467": 0.9995939135551453,
    "train7470": 0.9999898672103882,
    "train7499": 0.999969482421875,
    "train7534": 0.9999446868896484,
    "train7536": 0.9999620914459229,
    "train7562": 0.8344854116439819,
    "train7577": 0.9999104738235474,
    "train7588": 0.9983080625534058,
    "train7594": 0.9999376535415649,
    "train7608": 0.9999086856842041,
    "train7653": 0.9977248311042786,
    "train7657": 0.9999862909317017,
    "train7658": 0.9999847412109375,
    "train7660": 0.9999953508377075,
    "train7665": 0.9999536275863647,
    "train7669": 0.7012219429016113,
    "train7717": 0.999935507774353,
    "train7719": 0.9994309544563293,
    "train7728": 0.999886155128479,
    "train7731": 0.9999717473983765,
    "train7739": 0.9995645880699158,
    "train7753": 0.9994966983795166,
    "train7762": 0.9993959665298462,
    "train7763": 0.9998725652694702,
    "train7776": 0.9996196031570435,
    "train7782": 0.9999277591705322,
    "train7783": 0.9999231100082397,
    "train7786": 0.9982784986495972,
    "train7792": 0.9992807507514954,
    "train7803": 0.9999932050704956,
    "train7805": 0.9997197985649109,
    "train7808": 0.9996703863143921,
    "train7815": 0.9999306201934814,
    "train7816": 0.999921441078186,
    "train7823": 0.9993205070495605,
    "train7825": 0.9946820139884949,
    "train7865": 0.9999747276306152,
    "train7880": 0.9998525381088257,
    "train7888": 0.9998107552528381,
    "train7889": 0.9997490048408508,
    "train7908": 0.9997541308403015,
    "train7909": 0.9998674392700195,
    "train7913": 0.999758780002594,
    "train7927": 0.9999932050704956,
    "train7946": 0.9999809265136719,
    "train7954": 0.9999910593032837,
    "train7955": 0.9999885559082031,
    "train7963": 0.9993582367897034,
    "train7972": 0.9999581575393677,
    "train7977": 0.9998390674591064,
    "train7978": 0.9999908208847046,
    "train8002": 0.9995879530906677,
    "train8018": 0.9999892711639404,
    "train8034": 0.9623679518699646,
    "train8036": 0.9999815225601196,
    "train8047": 0.9998482465744019,
    "train8062": 0.9994484782218933,
    "train8108": 0.9980019927024841,
    "train8111": 0.9971131086349487,
    "train8113": 0.9997424483299255,
    "train8128": 0.004804786294698715,
    "train8133": 0.9999736547470093,
    "train8136": 0.9999809265136719,
    "train8149": 0.9998501539230347,
    "train8150": 0.999991774559021,
    "train8159": 0.9988767504692078,
    "train8176": 0.9999707937240601,
    "train8183": 0.9997290968894958,
    "train8184": 0.9998190999031067,
    "train8238": 0.9962407350540161,
    "train8240": 0.995586633682251,
    "train8291": 0.9998076558113098,
    "train8297": 0.976428747177124,
    "train8300": 0.999822199344635,
    "train8350": 0.9998843669891357,
    "train8351": 0.9998960494995117,
    "train8358": 0.9999105930328369,
    "train8386": 0.9998990297317505,
    "train8390": 0.9998812675476074,
    "train8402": 0.9998886585235596,
    "train8408": 0.1353117972612381,
    "train8409": 0.13149811327457428,
    "train8449": 0.9998699426651001,
    "train8450": 0.999447762966156,
    "train8451": 0.9998736381530762,
    "train8475": 0.999972939491272,
    "train8477": 0.9989169836044312,
    "train8484": 0.9999239444732666,
    "train8492": 0.9993250370025635,
    "train8511": 0.9999582767486572,
    "train8533": 0.9984277486801147,
    "train8569": 0.9991692304611206,
    "train8574": 0.9999645948410034,
    "train8575": 0.9999603033065796,
    "train8579": 0.9996947050094604,
    "train8613": 0.9991990923881531,
    "train8641": 0.9997698664665222,
    "train8643": 0.9995278120040894,
    "train8678": 0.9999610185623169,
    "train8679": 0.9992501139640808,
    "train8690": 0.9990718364715576,
    "train8697": 0.9998815059661865,
    "train8698": 0.9998947381973267,
    "train8735": 0.9997720122337341,
    "train8740": 0.9999263286590576,
    "train8755": 0.9999890327453613,
    "train8774": 0.9999774694442749,
    "train8775": 0.9999740123748779,
    "train8776": 0.9998418092727661,
    "train8779": 0.9999735355377197,
    "train8780": 0.9999821186065674,
    "train8799": 0.9976455569267273,
    "train8800": 0.999915361404419,
    "train8809": 0.9995623230934143,
    "train8813": 0.9997760653495789,
    "train8829": 0.9999741315841675,
    "train8849": 0.9980175495147705,
    "train8854": 0.9999732971191406,
    "train8856": 0.9997697472572327,
    "train8892": 0.9999876022338867,
    "train8924": 0.9991185069084167,
    "train8932": 0.9998267292976379,
    "train8941": 0.999963641166687,
    "train8944": 0.9999344348907471,
    "train8945": 0.9999511241912842,
    "train8951": 0.9999920129776001,
    "train8952": 0.9999899864196777,
    "train8954": 0.9995086193084717,
    "train8955": 0.9994683861732483,
    "train8962": 0.9999828338623047,
    "train8983": 0.999984860420227,
    "train9007": 0.999927282333374,
    "train9009": 0.9999561309814453,
    "train9010": 0.9999351501464844,
    "train9037": 0.9999891519546509,
    "train9054": 0.9998769760131836,
    "train9058": 0.9999681711196899,
    "train9066": 0.999975323677063,
    "train9087": 0.9996830224990845,
    "train9094": 0.9995833039283752,
    "train9100": 0.9999556541442871,
    "train9101": 0.9999829530715942,
    "train9104": 0.9999891519546509,
    "train9105": 0.9999382495880127,
    "train9114": 0.9249520897865295,
    "train9135": 0.9996923208236694,
    "train9156": 0.9998944997787476,
    "train9211": 0.9999747276306152,
    "train9216": 0.9999436140060425,
    "train9217": 0.9999237060546875,
    "train9237": 0.9999222755432129,
    "train9298": 0.9413610100746155,
    "train9333": 0.9996931552886963,
    "train9334": 0.9999711513519287,
    "train9349": 0.9998670816421509,
    "train9371": 0.9970992803573608,
    "train9384": 0.9996065497398376,
    "train9388": 0.9999665021896362,
    "train9401": 0.9999814033508301,
    "train9412": 0.99901282787323,
    "train9443": 0.9983198046684265,
    "train9444": 0.9913177490234375,
    "train9449": 0.9999475479125977,
    "train9455": 0.9999204874038696,
    "train9469": 0.9999829530715942,
    "train9499": 0.9996820688247681,
    "train9526": 0.9999803304672241,
    "train9530": 0.9993749260902405,
    "train9583": 0.9999228715896606,
    "train9587": 0.9999549388885498,
    "train9611": 0.9999456405639648,
    "train9619": 0.9998677968978882,
    "train9624": 0.9989379048347473,
    "train9636": 0.9999455213546753,
    "train9643": 0.9999349117279053,
    "train9645": 0.9999346733093262,
    "train9653": 0.9998672008514404,
    "train9676": 0.999937891960144,
    "train9692": 0.9999828338623047,
    "train9703": 0.9998553991317749,
    "train9709": 0.9999490976333618,
    "train9784": 0.3529961109161377,
    "train9822": 0.9999829530715942,
    "train9830": 0.9995538592338562,
    "train9831": 0.9997212290763855,
    "train9853": 0.9999949932098389,
    "train9872": 0.9999403953552246,
    "train9876": 0.9978127479553223,
    "train9886": 0.9999144077301025,
    "train9896": 0.9965437054634094,
    "train9907": 0.999948263168335,
    "train9944": 0.9999693632125854,
    "train9971": 0.9999052286148071,
    "train9989": 0.9977443218231201,
    "train9995": 0.9979619979858398,
    "train10000": 0.9995985627174377,
    "train10001": 0.9999655485153198,
    "train10076": 0.9995200634002686,
    "train10082": 0.9996757507324219,
    "train10089": 0.9998144507408142,
    "train10108": 0.9982104301452637,
    "train10122": 0.9999452829360962,
    "train10136": 0.9997244477272034,
    "train10137": 0.9997379183769226,
    "train10147": 0.999992847442627,
    "train10169": 0.9999059438705444,
    "train10172": 0.9998596906661987,
    "train10178": 0.9999626874923706,
    "train10181": 0.9999855756759644,
    "train10183": 0.9999806880950928,
    "train10202": 0.9998935461044312,
    "train10208": 0.9993401169776917,
    "train10209": 0.9997934699058533,
    "train10210": 0.999902606010437,
    "train10228": 0.9999959468841553,
    "train10233": 0.9999803304672241,
    "train10264": 0.9999706745147705,
    "train10273": 0.9999902248382568,
    "train10276": 0.897529125213623,
    "train10282": 0.9996224641799927,
    "train10283": 0.9997074007987976,
    "train10293": 0.9999047517776489,
    "train10319": 0.9999127388000488,
    "train10320": 0.9999767541885376,
    "train10326": 0.9998787641525269,
    "train10329": 0.9999433755874634,
    "train10345": 0.9999216794967651,
    "train10349": 0.9999817609786987,
    "train10366": 0.8938173651695251,
    "train10372": 0.9999479055404663,
    "train10373": 0.9999696016311646,
    "train10383": 0.9999600648880005,
    "train10384": 0.9999467134475708,
    "train10388": 0.999967098236084,
    "train10390": 0.9999526739120483,
    "train10392": 0.9999397993087769,
    "train10395": 0.9999371767044067,
    "train10401": 0.9994907379150391,
    "train10403": 0.9995235204696655,
    "train10404": 0.9991262555122375,
    "train10410": 0.43977320194244385,
    "train10416": 0.9993280172348022,
    "train10420": 0.9981986880302429,
    "train10422": 0.9991389513015747,
    "train10435": 0.9991934895515442,
    "train10445": 0.9996660947799683,
    "train10450": 0.999937891960144,
    "train10463": 0.9999966621398926,
    "train10466": 0.9999479055404663,
    "train10467": 0.9999181032180786,
    "train10485": 0.9999918937683105,
    "train10489": 0.9999866485595703,
    "train10490": 0.9999896287918091,
    "train10491": 0.9999901056289673,
    "train10494": 0.9998794794082642,
    "train10503": 0.9996738433837891,
    "train10505": 0.9998102784156799,
    "train10516": 0.9989609718322754,
    "train10550": 0.9989233613014221,
    "train10568": 0.9997262358665466,
    "train10595": 0.9998338222503662,
    "train10600": 0.9999737739562988,
    "train10619": 0.9986191987991333,
    "train10624": 0.9989246726036072,
    "train10637": 0.9998940229415894,
    "train10643": 0.9997989535331726,
    "train10679": 0.9999935626983643,
    "train10695": 0.9999990463256836,
    "train10728": 0.9989577531814575,
    "train10734": 0.9999812841415405,
    "train10772": 0.9999579191207886,
    "train10774": 0.9999430179595947,
    "train10825": 0.9998816251754761,
    "train10839": 0.9947254061698914,
    "train10840": 0.9987984895706177,
    "train10862": 0.9992882609367371,
    "train10899": 0.9317632913589478,
    "train10932": 0.9999462366104126,
    "train10967": 0.999990701675415,
    "train10991": 0.9999785423278809,
    "train10993": 0.9999172687530518,
    "train10995": 0.9999648332595825,
    "train11006": 0.9997419714927673,
    "train11019": 0.9998980760574341,
    "train11024": 0.9997695088386536,
    "train11030": 0.987043559551239,
    "train11060": 0.9998691082000732,
    "train11127": 0.9999938011169434,
    "train11148": 0.9999734163284302,
    "train11173": 0.9987232089042664,
    "train11228": 0.9980849027633667,
    "train11232": 0.9999594688415527,
    "train11235": 0.9999276399612427,
    "train11284": 0.9999771118164062,
    "train11285": 0.9999716281890869,
    "train11293": 0.9987195730209351,
    "train11295": 0.99319988489151,
    "train11296": 0.9993808269500732,
    "train11297": 0.9999436140060425,
    "train11299": 0.9999791383743286,
    "train11331": 0.9998983144760132,
    "train11337": 0.9999382495880127,
    "train11376": 0.988735020160675,
    "train11428": 0.9999877214431763,
    "train11487": 0.9995724558830261,
    "train11490": 0.9996335506439209,
    "train11491": 0.9999918937683105,
    "train11492": 0.9999498128890991,
    "train11511": 0.9999804496765137,
    "train11512": 0.9999715089797974,
    "train11517": 0.9995001554489136,
    "train11520": 0.9998365640640259,
    "train11527": 0.9999179840087891,
    "train11536": 0.9971073269844055,
    "train11575": 0.634107232093811,
    "train11600": 0.999915599822998,
    "train11603": 0.9999270439147949,
    "train11605": 0.9998478889465332,
    "train11613": 0.9999711513519287,
    "train11643": 0.9961923360824585,
    "train11650": 0.9996466636657715,
    "train11659": 0.9979593753814697,
    "train11665": 0.999992847442627,
    "train11675": 0.9997678399085999,
    "train11679": 0.9999923706054688,
    "train11711": 0.999936580657959,
    "train11719": 0.9998857975006104,
    "train11720": 0.9999725818634033,
    "train11732": 0.999697208404541,
    "train11782": 0.999305248260498,
    "train11786": 0.9998906850814819,
    "train11791": 0.9994450211524963,
    "train11801": 0.9999645948410034,
    "train11803": 0.9999632835388184,
    "train11813": 0.999972939491272,
    "train11839": 0.9999566078186035,
    "train11852": 0.9999467134475708,
    "train11866": 0.9999169111251831,
    "train11871": 0.9999749660491943,
    "train11903": 0.9999638795852661,
    "train11904": 0.999963641166687,
    "train11910": 0.9999878406524658,
    "train11933": 0.9999340772628784,
    "train11945": 0.9992604851722717,
    "train11956": 0.9999840259552002,
    "train11959": 0.9999793767929077,
    "train11969": 0.9919496774673462,
    "train12048": 0.9997649788856506,
    "train12066": 0.9999707937240601,
    "train12069": 0.9998778104782104,
    "train12099": 0.9999369382858276,
    "train12101": 0.9985517859458923,
    "train12102": 0.9999887943267822,
    "train12138": 0.9989321827888489,
    "train12139": 0.9993894100189209,
    "train12165": 0.9999772310256958,
    "train12170": 0.9999492168426514,
    "train12180": 0.9999688863754272,
    "train12181": 0.9992823004722595,
    "train12189": 0.9999696016311646,
    "train12204": 0.999943733215332,
    "train12226": 0.9996247291564941,
    "train12294": 0.9999500513076782,
    "train12297": 0.9999384880065918,
    "train12298": 0.9996060729026794,
    "train12300": 0.999900221824646,
    "train12324": 0.9999964237213135,
    "train12327": 0.9999290704727173,
    "train12330": 0.9996334314346313,
    "train12331": 0.999916672706604,
    "train12334": 0.9999872446060181,
    "train12343": 0.3665638267993927,
    "train12348": 0.9998729228973389,
    "train12377": 0.9999876022338867,
    "train12380": 0.999988317489624,
    "train12391": 0.9999438524246216,
    "neg_006467e6e5b4b68e": 0.9999706745147705,
    "neg_006ba24c315cc155": 0.997866690158844,
    "neg_00a6e28e6b0f8c47": 0.9976003766059875,
    "neg_00ded655948d5fe3": 0.9998170733451843,
    "neg_016794ce831a0291": 0.9995379447937012,
    "neg_0182642363344e95": 0.9998244643211365,
    "neg_019962b0c82cfcb2": 0.988125205039978,
    "neg_01b4ed78d8d463ac": 0.9999098777770996,
    "neg_0216ffd7ae8a678b": 0.9993589520454407,
    "neg_0233e231575605fb": 0.9995991587638855,
    "neg_02c4e7d79261479a": 0.999985933303833,
    "neg_03752164fd749b96": 0.9999932050704956,
    "neg_03af0f25d46964ec": 0.9999521970748901,
    "neg_03c7e3b8cc42cf87": 0.9999498128890991,
    "neg_047a5bcb4fa9ddae": 0.999188244342804,
    "neg_052e47fb330a440a": 0.9881014823913574,
    "neg_053ab678b409da1a": 0.9991092085838318,
    "neg_053d73f1b80ecfda": 0.9999268054962158,
    "neg_0588f9c88a2f7af7": 0.2693493366241455,
    "neg_069d79e51ee1a011": 0.9996114373207092,
    "neg_073863262ebdb99a": 0.9999611377716064,
    "neg_075510130610b682": 0.999875545501709,
    "neg_07ba81a4bd49c277": 0.9997026324272156,
    "neg_07efd4e6c0175a53": 0.999574601650238,
    "neg_082d049c1ad9a338": 0.9990246295928955,
    "neg_082efa42fa9534ac": 0.9999591112136841,
    "neg_084d01d1782d116f": 0.999755322933197,
    "neg_092002f139655621": 0.9999344348907471,
    "neg_0a07dc0b4d373e4a": 0.9994969367980957,
    "neg_0a23ebe4b2b886e6": 0.9997250437736511,
    "neg_0b86f1eb6dbe1afe": 0.9996594190597534,
    "neg_0b96eb2f66d44c67": 0.9993844032287598,
    "neg_0bd3be4327e50338": 0.999657154083252,
    "neg_0dbed496ae47da32": 0.9999005794525146,
    "neg_0e5d44a0176e2cb3": 0.9986805319786072,
    "neg_0e8d32149e630abc": 0.9998675584793091,
    "neg_0eb16feed31f29af": 0.9995139837265015,
    "neg_0ebf3e6559a995f9": 0.9999810457229614,
    "neg_0f5ea743233e5ab9": 0.9999885559082031,
    "neg_0fb73ec4cec575c7": 0.44888198375701904,
    "neg_0fec21d6ec72ef03": 0.999920129776001,
    "neg_1011152a94d6959d": 0.9998866319656372,
    "neg_10417ea9da459036": 0.8867287039756775,
    "neg_1148cee1a8de4b07": 0.9999752044677734,
    "neg_1193ff25d6316c7f": 0.9997357726097107,
    "neg_11c171abdb15323b": 0.999975323677063,
    "neg_12784d670432dad7": 0.9999867677688599,
    "neg_13476f7d133670f3": 0.998969316482544,
    "neg_1365d94f3dc62431": 0.9999622106552124,
    "neg_1373a69ed2b0ccd9": 0.9999734163284302,
    "neg_13d0f7c4f7f2cc36": 0.9999579191207886,
    "neg_145abf5104b2daac": 0.9999697208404541,
    "neg_148225005b038446": 0.9985017776489258,
    "neg_14cd44b595c8408b": 0.9999359846115112,
    "neg_14e5b8b1ff4fe5a1": 0.9964220523834229,
    "neg_152f203387e39547": 0.9999432563781738,
    "neg_15c920c79778c07c": 0.9991543292999268,
    "neg_16957e499406d811": 0.999544084072113,
    "neg_16a119eef88c7416": 0.998770534992218,
    "neg_16a5e3d613f355df": 0.999408483505249,
    "neg_16d10028d9988a7e": 0.9985817670822144,
    "neg_16ddfe813ea2f158": 0.9994932413101196,
    "neg_16e15305011a146b": 0.9986981153488159,
    "neg_1709e43acff76b3d": 0.9999464750289917,
    "neg_171f6ac8de91d6d7": 0.9999178647994995,
    "neg_185303da40e25f5c": 0.9998015761375427,
    "neg_18575141e3f8b7ff": 0.9998902082443237,
    "neg_18d210cdc329d363": 0.9999024868011475,
    "neg_1aaf23e8e1c54920": 0.9997597336769104,
    "neg_1bcb0e5be62e0062": 0.9998756647109985,
    "neg_1c03cd7d1fd154d8": 0.9561047554016113,
    "neg_1c4740e932ae0419": 0.999901533126831,
    "neg_1c893841044336b3": 0.9999045133590698,
    "neg_1cdd94bf6543c51f": 0.9998302459716797,
    "neg_1d2f8e2cccd8f65a": 0.9943166375160217,
    "neg_1f47cb85a351bebc": 0.9999338388442993,
    "neg_1f5fc6ec74fd8a1f": 0.9932109713554382,
    "neg_2058df8afb3795bc": 0.9996423721313477,
    "neg_20e0f3ed14b3ffcc": 0.9999628067016602,
    "neg_20fba20a7bf298c1": 0.9999668598175049,
    "neg_22219ce5a29629ed": 0.9999613761901855,
    "neg_222907f58f069a6b": 0.9999836683273315,
    "neg_2238d2dd6ff8f706": 0.9998955726623535,
    "neg_224ada1c786c9701": 0.9997451901435852,
    "neg_22d3bfe6747b4a31": 0.9999055862426758,
    "neg_22d5b61cbcf52394": 0.999931812286377,
    "neg_233fc5f946908fdd": 0.9999691247940063,
    "neg_23795de9f9d1c1c6": 0.9999591112136841,
    "neg_243841a2fb2e998e": 0.9995150566101074,
    "neg_244cc81685eada46": 0.9996997117996216,
    "neg_2592a47021c3dd83": 0.9999768733978271,
    "neg_264f32dfc11dc433": 0.9999916553497314,
    "neg_27112a0b95ffd900": 0.9998642206192017,
    "neg_2753a8b05faa5147": 0.9999713897705078,
    "neg_2781b3c60911139f": 0.9976654052734375,
    "neg_27d94d63435a6ad1": 0.9999794960021973,
    "neg_27da80e1f9d90726": 0.9999847412109375,
    "neg_284ce7e5f9f31af4": 0.8486827611923218,
    "neg_294b80815ba7afe1": 0.9988561868667603,
    "neg_2b3140d840e271a9": 0.9995630383491516,
    "neg_2b4ee1e65ed8246e": 0.9999784231185913,
    "neg_2c062d090d328778": 0.9999526739120483,
    "neg_2c30f11f8692fe0a": 0.999954342842102,
    "neg_2cb7c9578c6ad3aa": 0.9999253749847412,
    "neg_2cba5441eb7bdcbd": 0.9999862909317017,
    "neg_2d0e0e67eea50c01": 0.999915599822998,
    "neg_2da9185e4238c03e": 0.9999935626983643,
    "neg_2e59d4480d580f51": 0.9990038275718689,
    "neg_2e7a020b0ae2e15c": 0.9992176294326782,
    "neg_2ea69396a29411bb": 0.9999614953994751,
    "neg_2f79def84a5659e4": 0.9995012283325195,
    "neg_30afef82b9a61d61": 0.999581515789032,
    "neg_3127263cfc1ab4e3": 0.9999889135360718,
    "neg_313f10ce8b32e46a": 0.9988716244697571,
    "neg_31847bdfdd8a5c24": 0.9998922348022461,
    "neg_31e86e7e752f1870": 0.9998952150344849,
    "neg_334861d24b737b7f": 0.9999444484710693,
    "neg_3372d5a65245c941": 0.9999642372131348,
    "neg_3381f73246bd2e6a": 0.9998069405555725,
    "neg_33e157f521e2937d": 0.9984716773033142,
    "neg_343f7c439684e555": 0.9997712969779968,
    "neg_34e57ba141e157fd": 0.999915599822998,
    "neg_34f0d7605bb45551": 0.950508713722229,
    "neg_34fba977a943a120": 0.9997449517250061,
    "neg_36a016b256bc355e": 0.9988206028938293,
    "neg_36de902b5668849e": 0.9999232292175293,
    "neg_36dfcc6b8071ccb2": 0.9999867677688599,
    "neg_370eb1e6494f4fd1": 0.9998477697372437,
    "neg_3798481899bcd2f0": 0.9621339440345764,
    "neg_37cace9b6506d2b6": 0.9983150959014893,
    "neg_37cf5fde614ad3a0": 0.9985476136207581,
    "neg_3a5fcb2ff0241fba": 0.9992663264274597,
    "neg_3a8f00ab6623393d": 0.9996688365936279,
    "neg_3aa26dd5456d49b1": 0.9998495578765869,
    "neg_3b08bcadf1c72484": 0.9997487664222717,
    "neg_3b25894a4d11e9f5": 0.9999501705169678,
    "neg_3bde7f3bb4310613": 0.9996293783187866,
    "neg_3c2f72af1f1772d9": 0.99842369556427,
    "neg_3ca723222d01f8ae": 0.9998904466629028,
    "neg_3d6c6088d2c3eed7": 0.9999856948852539,
    "neg_3dd40b30097d3f3c": 0.9999980926513672,
    "neg_3df9e2ffda6eb161": 0.9999383687973022,
    "neg_3e072fdb85104816": 0.9998598098754883,
    "neg_3f78079237ac20f9": 0.9999692440032959,
    "neg_3fbd037ae43ff27e": 0.9999736547470093,
    "neg_3fcc667dae6090cd": 0.9998865127563477,
    "neg_4016d576ad9666a7": 0.9999817609786987,
    "neg_403b1b7387b7513f": 0.9867396354675293,
    "neg_4140c9a44fbd5a29": 0.7202152013778687,
    "neg_41742129e0fb8a29": 0.9999085664749146,
    "neg_425286edda822db2": 0.9999252557754517,
    "neg_42ad34dde74225b6": 0.9999313354492188,
    "neg_42b23b90d5e77ce1": 0.9998478889465332,
    "neg_440b7d741239bf05": 0.9999198913574219,
    "neg_45c5bf43ac193962": 0.9999840259552002,
    "neg_460ecf44c9da7749": 0.9998865127563477,
    "neg_466fdf13cb24b64c": 0.9996730089187622,
    "neg_46adbd1787a14be1": 0.9945500493049622,
    "neg_46b5b7885b46bfc4": 0.9996556043624878,
    "neg_478342c85335cb4f": 0.9991484880447388,
    "neg_47a217416e1ce476": 0.9997496008872986,
    "neg_47b934f2ad98082c": 0.9999196529388428,
    "neg_47ef8af68125fd5f": 0.9983306527137756,
    "neg_480f9461d9c89eee": 0.9989504814147949,
    "neg_483284a26361428e": 0.9999533891677856,
    "neg_48b1c3e207e63ef8": 0.9999979734420776,
    "neg_48c6707771ccabc3": 0.9999401569366455,
    "neg_48f36859f3e280be": 0.9997488856315613,
    "neg_4933819f1ec01b4f": 0.9998027682304382,
    "neg_493d06357d12e77e": 0.99779212474823,
    "neg_4a03b0d87d12991d": 0.9998218417167664,
    "neg_4a1d6fbebd1f015a": 0.9999159574508667,
    "neg_4a71b2dec65e4c56": 0.9995077848434448,
    "neg_4b20936675551afb": 0.9980496168136597,
    "neg_4b78b35ce134a809": 0.9999865293502808,
    "neg_4baad2bfd7ced016": 0.9985526204109192,
    "neg_4d417b7850bb23fc": 0.9982726573944092,
    "neg_4da2c032aceada66": 0.9986479878425598,
    "neg_4dbfbee9f328c815": 0.9998911619186401,
    "neg_4dc4c41d42a86c7f": 0.9995206594467163,
    "neg_4de1f8b0fcad48b7": 0.999568521976471,
    "neg_4e097b6b21351bb1": 0.999980092048645,
    "neg_4e6f4756d2514118": 0.9999488592147827,
    "neg_4e8790093dea5d1f": 0.9994240999221802,
    "neg_4ed5747a11115802": 0.9998626708984375,
    "neg_4efc2fac6374745f": 0.9998266100883484,
    "neg_4f084886976ae346": 0.9998486042022705,
    "neg_4f3296da178a79f0": 0.9998853206634521,
    "neg_4f3c8ee03f7f7e49": 0.9996125102043152,
    "neg_4f6a7a1989fcd3e7": 0.9999449253082275,
    "neg_4f989bdef4d865c0": 0.9999728202819824,
    "neg_4ff2d4bf3a6e34ad": 0.9999580383300781,
    "neg_509a635a898a1e46": 0.9999880790710449,
    "neg_50b5073b0055f1fd": 0.999997615814209,
    "neg_511d9f5ce771833d": 0.9989474415779114,
    "neg_51593cb0343d0d79": 0.9995354413986206,
    "neg_51fd98f90ccea95e": 0.9998828172683716,
    "neg_54cc6c0e77575553": 0.9905619025230408,
    "neg_5508c3715464a26d": 0.999951958656311,
    "neg_55c73860c7c65c49": 0.9987623691558838,
    "neg_55f96e7c29daeb0a": 0.9999911785125732,
    "neg_5685068c0a04ae54": 0.999976396560669,
    "neg_5699a8ff7a7463ad": 0.9999486207962036,
    "neg_582d2d0553cad2fc": 0.9999103546142578,
    "neg_582db5594fbc0b41": 0.9996969699859619,
    "neg_585ea6bbf5804d2e": 0.999997615814209,
    "neg_594e84fedd34961b": 0.9999878406524658,
    "neg_5a1aaf4fc71e9bc0": 0.9994584918022156,
    "neg_5a209bfbe270ad9a": 0.918921172618866,
    "neg_5a55c5528ae81a92": 0.999272882938385,
    "neg_5a5f0f9e54148f2d": 0.9998773336410522,
    "neg_5af3b50176fe5d57": 0.9929884076118469,
    "neg_5b3b03e4eaea1a5e": 0.9977657794952393,
    "neg_5ce873ab18524ad6": 0.9996305704116821,
    "neg_5d315a1d32683dcd": 0.9915832877159119,
    "neg_5dd5d6e8614612a2": 0.9995556473731995,
    "neg_5ea6639c2a60fad2": 0.9999798536300659,
    "neg_5fa9c1688f2d8c2c": 0.999813973903656,
    "neg_601ce8cf7d3fc426": 0.40692660212516785,
    "neg_60379e06646eeac1": 0.9943304061889648,
    "neg_609d3578e1fb8dce": 0.9999641180038452,
    "neg_60aadf222fb0c01b": 0.9955124258995056,
    "neg_60b1c4f402f0ccd0": 0.9991279244422913,
    "neg_6202cae62c6f525c": 0.9996658563613892,
    "neg_620818f7b1118969": 0.9991350769996643,
    "neg_62132b569964f0a4": 0.9998959302902222,
    "neg_6243932716829b36": 0.9978961944580078,
    "neg_62a0d7874fb24fe6": 0.9999581575393677,
    "neg_62fa242327a4a668": 0.9998966455459595,
    "neg_6348a675793e98a0": 0.9840405583381653,
    "neg_635aec84553f84f5": 0.9759878516197205,
    "neg_6391030bf0f862e3": 0.9999926090240479,
    "neg_64722f71c57b94b9": 0.9951627254486084,
    "neg_64a32cb927a50de1": 0.9997081160545349,
    "neg_64d89bacca158b0a": 0.9996874332427979,
    "neg_6510db8f3255a9f7": 0.9998610019683838,
    "neg_65453d7eac20803a": 0.99192214012146,
    "neg_65b8e84a91fec3fc": 0.9997873902320862,
    "neg_65f1428cf66cbed3": 0.9999312162399292,
    "neg_65fc4b56c995fed0": 0.9976934790611267,
    "neg_66894d708c91369a": 0.9992533326148987,
    "neg_66b5eb2fb4846906": 0.9999958276748657,
    "neg_66bd94ab22e5a14e": 0.7037752270698547,
    "neg_67789090299bd8e3": 0.9999933242797852,
    "neg_678b19dbcb490d0e": 0.6719712615013123,
    "neg_67c2cbdc2b223421": 0.9999727010726929,
    "neg_67d8c1404b81d9bd": 0.9994421601295471,
    "neg_693cd288351c34b6": 0.9999786615371704,
    "neg_696010f6c1c9bb42": 0.9992115497589111,
    "neg_6aacc607213618ff": 0.9996473789215088,
    "neg_6ab8cb027e87d917": 0.9998511075973511,
    "neg_6abb77437c165180": 0.9999349117279053,
    "neg_6b3a75aa962a1418": 0.9996620416641235,
    "neg_6bb7e1beb8bf78e9": 0.9999741315841675,
    "neg_6be65482e49ce5cc": 0.9999865293502808,
    "neg_6bef0639997bda28": 0.9999228715896606,
    "neg_6c2240e88371905e": 0.9999059438705444,
    "neg_6c89722191ea14fe": 0.9991868138313293,
    "neg_6d45c01739645cfd": 0.9997281432151794,
    "neg_6d6b92226b0bce7c": 0.9999876022338867,
    "neg_6dd6b61503130abe": 0.9814945459365845,
    "neg_6e42ec88199aff9c": 0.9999477863311768,
    "neg_6e78a31f60fea0d6": 0.9993427395820618,
    "neg_6f9cb2b42d0b6dba": 0.9589124321937561,
    "neg_6fad94fbb4ba48c4": 0.998028576374054,
    "neg_70d631f6cc19a2b3": 0.9999697208404541,
    "neg_7247072603e31c50": 0.9969356060028076,
    "neg_72a591d5f7dcedd5": 0.9998517036437988,
    "neg_72b7537ecdbfddf0": 0.9996052384376526,
    "neg_735e0758ebf83db5": 0.9998466968536377,
    "neg_7380b430b5ede3ce": 0.3350085914134979,
    "neg_73f1aab9eedf8d69": 0.999455988407135,
    "neg_74454b986aad3ca8": 0.9999779462814331,
    "neg_74c67fe60442a188": 0.9990912675857544,
    "neg_74e5e2b29c8ef349": 0.9994204044342041,
    "neg_75367dcf0f764d4d": 0.9999719858169556,
    "neg_764fb16d6b34955e": 0.999956488609314,
    "neg_76c00177a38fb10e": 0.999948263168335,
    "neg_76d457bb9b048004": 0.9959057569503784,
    "neg_78fa7089ac303501": 0.9996548891067505,
    "neg_79009580266d7c10": 0.9998039603233337,
    "neg_796c53cdbf350b7d": 0.9997946619987488,
    "neg_796c5f12bfed819e": 0.9998705387115479,
    "neg_7971b90a1c596ff3": 0.9998520612716675,
    "neg_7a4db1070ed9b20c": 0.9999715089797974,
    "neg_7a7d8909902dcf57": 0.9998929500579834,
    "neg_7ad4b0637c110387": 0.9992803931236267,
    "neg_7aec9eb9614f17df": 0.9999951124191284,
    "neg_7b371dfa2a710c24": 0.9999144077301025,
    "neg_7b4163fe929d4e67": 0.9999847412109375,
    "neg_7bf0167ddf760aa0": 0.9994710087776184,
    "neg_7cd453a0f425a82f": 0.9999583959579468,
    "neg_7cd5eb915c3f7c85": 0.99983811378479,
    "neg_7d1ebe0b41048c05": 0.9999916553497314,
    "neg_7d3121083da46aa7": 0.898059070110321,
    "neg_7e1c1f55d8ecbeaa": 0.9996094107627869,
    "neg_7e3e483ac196c4eb": 0.9996089339256287,
    "neg_7ea04f65e805cddd": 0.0003941197937820107,
    "neg_7ebc1264e72e39c5": 0.9998958110809326,
    "neg_7ee81d7d7517c335": 0.9999938011169434,
    "neg_7ee856d9f1ab9e1d": 0.9987300038337708,
    "neg_7f5bdfc12cf2c498": 0.9987015724182129,
    "neg_7f68ac4e001d2017": 0.9992688298225403,
    "neg_7fe6d3859f788b48": 0.9973963499069214,
    "neg_800e09504333c615": 0.9953442215919495,
    "neg_800ea0900165de96": 0.9989109039306641,
    "neg_80421cc4b54c10ab": 0.9999505281448364,
    "neg_819e6e88c055a80f": 0.9999680519104004,
    "neg_81daf1cb84b3f9ce": 0.0011032834881916642,
    "neg_81edb4a335bc88a9": 0.9998728036880493,
    "neg_8216a2e55cd38af8": 0.9999388456344604,
    "neg_8249e3bc542e5654": 0.9999891519546509,
    "neg_82a80dbd45ea767b": 0.9884364604949951,
    "neg_832fa1bac3206132": 0.9999074935913086,
    "neg_83908617f6117201": 0.9998098015785217,
    "neg_83c0b6dafebc14b7": 0.9961816072463989,
    "neg_83f5c70a29a56d2d": 0.9998868703842163,
    "neg_8473183be2203b45": 0.9998557567596436,
    "neg_84a203bef2c5ddab": 0.9999822378158569,
    "neg_84a87a7b4accaea8": 0.9999784231185913,
    "neg_84f71561858a842c": 0.9959980249404907,
    "neg_84ffcb62f913f2a3": 0.9999690055847168,
    "neg_85ac28459e18ae2c": 0.9998745918273926,
    "neg_85d222c731890929": 0.9877168536186218,
    "neg_868df6e1dd5db501": 0.9452924132347107,
    "neg_86af7b612c1cbd0e": 0.9977490305900574,
    "neg_87463e00db8211d6": 0.9997809529304504,
    "neg_881ed8bda77a5f38": 0.9999890327453613,
    "neg_89de18175c00fcc8": 0.998162567615509,
    "neg_89f42f048eb29655": 0.999962329864502,
    "neg_8ad772c57949c4a0": 0.9999415874481201,
    "neg_8b4aa7349018ed38": 0.9999873638153076,
    "neg_8b8f0a5dcd7619bd": 0.9999340772628784,
    "neg_8ba78e62b15b614a": 0.9999634027481079,
    "neg_8bbccc456b7fbd4c": 0.999651312828064,
    "neg_8c8ab7e3dbd58b61": 0.9999803304672241,
    "neg_8ce22fd3e8079bfa": 0.999909520149231,
    "neg_8d54dcca33197511": 0.9999688863754272,
    "neg_8db54daf3dc8d818": 0.9806421399116516,
    "neg_8e730efda26faea5": 0.999987006187439,
    "neg_8eb6a7b2f7e06417": 0.999981164932251,
    "neg_8f1ad81530586ac2": 0.9994450211524963,
    "neg_8f465cf68a064ad6": 0.9999953508377075,
    "neg_8facd896b054cd90": 0.9996364116668701,
    "neg_9041cd18aab756d8": 0.9999305009841919,
    "neg_91160c761f7fa922": 0.003303182078525424,
    "neg_9184a51be39a5e82": 0.9997321963310242,
    "neg_91a957c48307a9bd": 0.9999152421951294,
    "neg_91e4436644afed50": 0.9995505213737488,
    "neg_9241cc192a0437b7": 0.9989584684371948,
    "neg_926d311dbd529492": 0.9989256262779236,
    "neg_9307b20167fb01a9": 0.9971309304237366,
    "neg_93b178cc3ec99ff3": 0.9985283613204956,
    "neg_93cfedb1120092ba": 0.9999145269393921,
    "neg_93eb2458ecf868a4": 0.9997308850288391,
    "neg_957aebe76624a9d2": 0.9999772310256958,
    "neg_95a7ee986e7e7e19": 0.9663755893707275,
    "neg_95c94dad7a703bac": 0.9999614953994751,
    "neg_95efd41e16aefe3a": 0.9995169639587402,
    "neg_962f0e40f2e7dc70": 0.9981572031974792,
    "neg_97561c0403ce7252": 0.9998886585235596,
    "neg_9764fb97ed16e64f": 0.9999146461486816,
    "neg_97e82acf153899e4": 0.9951017498970032,
    "neg_989771602d6cb9cb": 0.9496616125106812,
    "neg_98d991e3202dc178": 0.9988573789596558,
    "neg_9904528156abb072": 0.9999819993972778,
    "neg_990fa86a6bd8437a": 0.9998433589935303,
    "neg_9941e065f920ac34": 0.9999982118606567,
    "neg_9976589a0d2c5abf": 0.9999157190322876,
    "neg_99af107d90e9430f": 0.9995958209037781,
    "neg_99bfd0e193c8db57": 0.999998927116394,
    "neg_99cbac2c318af141": 0.9997304081916809,
    "neg_9a3e7a0804ab3e10": 0.4485492408275604,
    "neg_9a5a9c97bab52aa3": 0.9999932050704956,
    "neg_9a69d203c9d90946": 0.9999955892562866,
    "neg_9bd64cd8fb2951d3": 0.9994412064552307,
    "neg_9bf2b39d70aaf0de": 0.9999737739562988,
    "neg_9c507ed792c1098b": 0.9997838139533997,
    "neg_9c7172600fcb2c3a": 0.9997987151145935,
    "neg_9cc25f245394a29d": 0.9999362230300903,
    "neg_9ce8f8ba64322bf2": 0.9950101375579834,
    "neg_9d80f35d332f642a": 0.9994720816612244,
    "neg_9f036f8ae29791a4": 0.9999912977218628,
    "neg_9f89a719b061e98f": 0.9822127819061279,
    "neg_9f8b5931dd71aa49": 0.9992926120758057,
    "neg_9fa520c179c2eb06": 0.9998935461044312,
    "neg_a1906167f5becc8a": 0.9998249411582947,
    "neg_a2308f9f35f7efa4": 0.9993878602981567,
    "neg_a2f2ceee681780e4": 0.9986535310745239,
    "neg_a365c32665840ab4": 0.9995274543762207,
    "neg_a3a5f40c4fcf0c97": 0.9999583959579468,
    "neg_a454744a777a7ac2": 0.999957799911499,
    "neg_a4a1b60fa117fa2e": 0.9999014139175415,
    "neg_a5929e6c50ae8355": 0.982196569442749,
    "neg_a5c7deac8964e92d": 0.9977868795394897,
    "neg_a62584538a61124f": 0.9994080066680908,
    "neg_a62bed1b81944d9a": 0.9998931884765625,
    "neg_a6648a0a03fdefb4": 0.9992164373397827,
    "neg_a74ec4abf6279f0e": 0.9995145797729492,
    "neg_a77e6e05e82398de": 0.9999639987945557,
    "neg_a7d1121549cf27ea": 0.9998292922973633,
    "neg_a8773e73b10d63f6": 0.9999295473098755,
    "neg_a8cc0ef13867b0cc": 0.9998844861984253,
    "neg_aa1cf9d3831907a3": 0.9997947812080383,
    "neg_aa6b46f7b216ecd7": 0.9998548030853271,
    "neg_aaefe29515f43d28": 0.9999092817306519,
    "neg_abc815d3ab181651": 0.9998408555984497,
    "neg_ac7a839c638700f8": 0.99998939037323,
    "neg_ad8a9862fbf53fa6": 0.0024015125818550587,
    "neg_add105f33f6c5c87": 0.9997908473014832,
    "neg_ae05050318ab6249": 0.9999693632125854,
    "neg_ae2023b2929f9ea1": 0.9999862909317017,
    "neg_aeca0e0858c1c3dc": 0.9996428489685059,
    "neg_af28e4884bf33693": 0.9979777932167053,
    "neg_af32f13e783d9fe8": 0.9999768733978271,
    "neg_af902fb31ad355dc": 0.9995728135108948,
    "neg_b0b9956e45b90382": 0.999541163444519,
    "neg_b0d7116ade290da6": 0.9778335094451904,
    "neg_b11ab332736cb2c8": 0.9999749660491943,
    "neg_b27b43f8f789a101": 0.918994665145874,
    "neg_b2a633870454fa92": 0.999669075012207,
    "neg_b2e1945b86283631": 0.9996774196624756,
    "neg_b323a8b0e1a583a6": 0.9996461868286133,
    "neg_b36971a89782f57e": 0.9986787438392639,
    "neg_b375349338ef98a1": 0.9998745918273926,
    "neg_b389b8afe999a475": 0.9996906518936157,
    "neg_b41461efbecf83d7": 0.9999886751174927,
    "neg_b43a429763aae863": 0.9999353885650635,
    "neg_b603a6e76a8f9eca": 0.999914288520813,
    "neg_b62a236f176a16eb": 0.9999788999557495,
    "neg_b62be593be2dd3c6": 0.9998531341552734,
    "neg_b655c4c582456e94": 0.9997095465660095,
    "neg_b6cf2813acd1cda9": 0.9951202273368835,
    "neg_b7777d25abdede00": 0.999945878982544,
    "neg_b7ab10d6bb3b2977": 0.9999687671661377,
    "neg_b843cae4b5a3d8b8": 0.9999274015426636,
    "neg_b87de8a8302947bf": 0.9937933683395386,
    "neg_b8d22baf50764725": 0.9999661445617676,
    "neg_b8e81509b3c36355": 0.9996664524078369,
    "neg_b95d545bed9d4a9d": 0.999860405921936,
    "neg_b961786817512a66": 0.9998743534088135,
    "neg_b987df89a326a950": 0.9999867677688599,
    "neg_b991979a057b554e": 0.8792358636856079,
    "neg_b9f81130a3c9d2c5": 0.9998190999031067,
    "neg_bac22b6e778ba010": 0.9999197721481323,
    "neg_bac7b31d25f2185b": 0.9997134804725647,
    "neg_bb5c900f9a8f10ed": 0.9999531507492065,
    "neg_bb660219e7908e4c": 0.9998606443405151,
    "neg_bb75740e47b943db": 0.9999644756317139,
    "neg_bc4be17aafc99fa4": 0.9996715784072876,
    "neg_bc91d47afbf006b1": 0.9996261596679688,
    "neg_bcd0e3db5c3a51d2": 0.9979947805404663,
    "neg_bdecdad615912554": 0.9999505281448364,
    "neg_bea0cbb0c8437e3f": 0.9997653365135193,
    "neg_bf4a3cfac36e3e1e": 0.9999667406082153,
    "neg_bf865e1d96aa4184": 0.9998136162757874,
    "neg_bfecee4ebf80a8e8": 0.9999722242355347,
    "neg_c03e168ac695a93f": 0.9874628186225891,
    "neg_c047d42aca34a42d": 0.9999808073043823,
    "neg_c07222e0001c5ed6": 0.999725878238678,
    "neg_c09b8425face4b3a": 0.9995131492614746,
    "neg_c10b20ef07f8c9cc": 0.9992423057556152,
    "neg_c150e209b86e1dad": 0.9998282194137573,
    "neg_c2d4dc4a817678a5": 0.9995734095573425,
    "neg_c2edd416956ace1c": 0.9998264908790588,
    "neg_c316e35903bdab83": 0.9999476671218872,
    "neg_c36ead1037d018ce": 0.9999483823776245,
    "neg_c3bd53c04a056f3b": 0.9992135763168335,
    "neg_c3fd23607ef85aa6": 0.9995489716529846,
    "neg_c43aea14d4348fce": 0.9955131411552429,
    "neg_c44eb9dc14ae9962": 0.9999834299087524,
    "neg_c454c40e7bf13285": 0.9998593330383301,
    "neg_c555bc6b729dbeb7": 0.9997009038925171,
    "neg_c5bc7d4826db6f6a": 0.9716372489929199,
    "neg_c628f5c1f40005eb": 0.9997493624687195,
    "neg_c6405cbb3d63fd5c": 0.9999946355819702,
    "neg_c6bf152cc3a24a06": 0.9999243021011353,
    "neg_c770ccd597b86aaa": 0.9998714923858643,
    "neg_c7fd7593681f84fc": 0.9995998740196228,
    "neg_c88d1bb7d239ca25": 0.9999685287475586,
    "neg_c8ae0ea9fcb6da7c": 0.9999518394470215,
    "neg_c8ed42a1ce8473e0": 0.9990078806877136,
    "neg_cb0188d8a55f049f": 0.9997982382774353,
    "neg_cd234285dc3dc3d6": 0.9864055514335632,
    "neg_cdc975b56fc0add5": 0.999901294708252,
    "neg_ce01fe7bb4f8532b": 0.9999496936798096,
    "neg_cf2d6fb4a56cf92a": 0.9999411106109619,
    "neg_cf2e209ea51d810e": 0.9998127818107605,
    "neg_cf6a3ad771b070eb": 0.9344472885131836,
    "neg_cfb9612894a8093c": 0.999879002571106,
    "neg_cfd7da5acb80dc77": 0.5870731472969055,
    "neg_cfe0342f02f04b87": 0.9998722076416016,
    "neg_d01eb29db7d65791": 0.9985248446464539,
    "neg_d0669d06ae21b723": 0.999902606010437,
    "neg_d165a07f899a1dcf": 0.9999784231185913,
    "neg_d183a7983860e182": 0.9999630451202393,
    "neg_d19f1e45d0484905": 0.99628746509552,
    "neg_d21abe7c950876d9": 0.9996734857559204,
    "neg_d22d9d3d549eab02": 0.9999966621398926,
    "neg_d3837df40e80624b": 0.9995779395103455,
    "neg_d3a5f3592bc98ddc": 0.9999672174453735,
    "neg_d3fc83b2892bc9a7": 0.9957934617996216,
    "neg_d40cb5b43817deb7": 0.9999973773956299,
    "neg_d41fc9264805edb4": 0.0003720385138876736,
    "neg_d42bdaebf117aa61": 0.9513081908226013,
    "neg_d43e40e721609377": 0.9993900060653687,
    "neg_d495215a19de3cf2": 0.999872088432312,
    "neg_d4f4165c6d2f1b74": 0.9995142221450806,
    "neg_d5589354241f7953": 0.9998996257781982,
    "neg_d5cea4a1185a1521": 0.9999582767486572,
    "neg_d66752978a50c6ac": 0.9999772310256958,
    "neg_d67ca84274883161": 0.9994171857833862,
    "neg_d6a5e603ce308b1e": 0.9999557733535767,
    "neg_d74de26ca5475bfe": 0.9998230338096619,
    "neg_d763a8b6f45e67fd": 0.9998739957809448,
    "neg_d77bff206db64a36": 0.9999351501464844,
    "neg_d83c97e89abb57fa": 0.999957799911499,
    "neg_d85073a672fb44df": 0.9990504384040833,
    "neg_d8e80f76dabd44c1": 0.9998573064804077,
    "neg_d90e7f8a539b1ad6": 0.9994593262672424,
    "neg_d9a8287632edc26b": 0.9987545013427734,
    "neg_da52a928ad0e561a": 0.9999762773513794,
    "neg_dac6769efa9460e4": 0.9999394416809082,
    "neg_dafb14935f6a759b": 0.6922739744186401,
    "neg_dbb950da7b648c22": 0.9603893160820007,
    "neg_dc1f8e55fa3d1f1c": 0.9999580383300781,
    "neg_dc60093779bbb72f": 0.9995693564414978,
    "neg_dd255c84c0b226b7": 0.999990701675415,
    "neg_dd49d55dcf4bba56": 0.99997878074646,
    "neg_dd78ef35d2ee8c89": 0.9996076226234436,
    "neg_ddae7042b1563889": 0.9999856948852539,
    "neg_ddd0039a79af3ded": 0.9975838661193848,
    "neg_de392cd5cfe3f589": 0.9992721676826477,
    "neg_de9d25f4dc880c0e": 0.9999905824661255,
    "neg_dea75233a677422f": 0.9999098777770996,
    "neg_dec386f946aea6d0": 0.9972118735313416,
    "neg_dec8f8d73bdbb6b7": 0.9999710321426392,
    "neg_decdade8ed4aa14d": 0.9997231364250183,
    "neg_df72b0355d683195": 0.9990203380584717,
    "neg_dfb9772202cb11bf": 0.9999736547470093,
    "neg_e04e999b7b37b502": 0.9883739948272705,
    "neg_e05f6a87c4de0e39": 0.9999847412109375,
    "neg_e153e40f5ddabd72": 0.9999643564224243,
    "neg_e1739a84606c6894": 0.9998002648353577,
    "neg_e1c79b3aa42d30a6": 0.9999492168426514,
    "neg_e1ed5c7ee8ce1f9b": 0.9994480013847351,
    "neg_e24177b1796b131f": 0.999114453792572,
    "neg_e339300ca83776ea": 0.9631563425064087,
    "neg_e3e6cec3183cf8b1": 0.9998440742492676,
    "neg_e57c8c10ab7f2be0": 0.9997724890708923,
    "neg_e61ad6ec5ff3b525": 0.9999862909317017,
    "neg_e74106b661032ac9": 0.9989601373672485,
    "neg_e746064210daedea": 0.9999934434890747,
    "neg_e787258152d51315": 0.9987666606903076,
    "neg_e7ea959975319930": 0.997093915939331,
    "neg_e84bc292395c0541": 0.998474657535553,
    "neg_e8e32c792a288230": 0.9998770952224731,
    "neg_e9c54ab66416dc71": 0.9999837875366211,
    "neg_ea1fd43cd35027c3": 0.9996250867843628,
    "neg_eb07413ff5cbf278": 0.9998832941055298,
    "neg_eb2831a51d9b34c8": 0.008798524737358093,
    "neg_eb5744e19a478290": 0.9999403953552246,
    "neg_eb57d965f598505b": 0.9997581839561462,
    "neg_eb9580698a9a0640": 0.8446848392486572,
    "neg_ebd665b8fe574e98": 0.9906745553016663,
    "neg_ecc315b7d893b778": 0.9998754262924194,
    "neg_ed35619e71da7eb8": 0.999542236328125,
    "neg_edf51e12ab5a4d56": 0.9999045133590698,
    "neg_eef65cb60225693b": 0.9999634027481079,
    "neg_ef8be80c7cda8d84": 0.9927425384521484,
    "neg_f1055b9c80e30e84": 0.9685419797897339,
    "neg_f1270f7481f91f9b": 0.9999567270278931,
    "neg_f25f425a07664152": 0.9979839324951172,
    "neg_f27684664c62b8ed": 0.9953529834747314,
    "neg_f368e412460f1f04": 0.9992203712463379,
    "neg_f39c264563a8363e": 0.9998767375946045,
    "neg_f422a75d568177e2": 0.9999775886535645,
    "neg_f431d674e0d1378a": 0.9999825954437256,
    "neg_f4ace10d811f63db": 0.9999589920043945,
    "neg_f528d7bb813e36c2": 0.9999481439590454,
    "neg_f5292c7bb3cbc828": 0.999702513217926,
    "neg_f5887bd3bf26c4e6": 0.999964714050293,
    "neg_f6474b537d97ff05": 0.9986781477928162,
    "neg_f66f3fbd17e33e4a": 0.9999915361404419,
    "neg_f6eab77440b65455": 0.9998576641082764,
    "neg_f705c7b0363f8603": 0.9996076226234436,
    "neg_f7e113edd72cd509": 0.9999603033065796,
    "neg_f816199a34df0deb": 0.9997894167900085,
    "neg_f8314701ebc2e188": 0.9999624490737915,
    "neg_f8374a1283da14ba": 0.999895453453064,
    "neg_f8634244ea9f9356": 0.9999282360076904,
    "neg_f8742084d8d90352": 0.9980182647705078,
    "neg_f8999293e5f802eb": 0.9995465874671936,
    "neg_f8c84b154795459a": 0.999866247177124,
    "neg_f961c4e167bb1a1f": 0.9999731779098511,
    "neg_f9c9f6454e050ef8": 0.999948263168335,
    "neg_fa9324161cc2ca50": 0.9997435212135315,
    "neg_fb1cc678ee3763bb": 0.9974011182785034,
    "neg_fb426c25ad05a6db": 0.999976634979248,
    "neg_fb92a6fa4a5ac880": 0.9998660087585449,
    "neg_fbae94b28f494891": 0.9997770190238953,
    "neg_fbc15e2a52c6b185": 0.9999052286148071,
    "neg_fbcbe4258f25020c": 0.9973021745681763,
    "neg_fc010c391d287f6b": 0.8539267778396606,
    "neg_fc14dc2cb6cd5eda": 0.9999079704284668,
    "neg_fc303473458e44c6": 0.9999368190765381,
    "neg_fd19a0154ba04497": 0.9999768733978271,
    "neg_fd1fcd37ce87e23a": 0.5838569402694702,
    "neg_fd7e5e245ecdc986": 0.9995881915092468,
    "neg_fe287044f7baf220": 0.99956876039505,
    "neg_feb5e834667ae879": 0.9918404817581177,
    "neg_ff89beca6a2df00c": 0.9997209906578064,
    "neg_ffeee581cdec4ab0": 0.9999047517776489
  },
  "limitations": "original labels only; sparse correlated pairs, endpoint video bootstrap; not a causal proof or full-sample metric"
}
```

## diagnostics/open_close/baseline/FAILURE_DECOMPOSITION.json

```json
{
  "pseudo": {
    "AUROC": 0.5346313130629411,
    "raw_R1_05": 0.2632415254237288,
    "gated_R1_05": 0.2664194915254237,
    "FRR": 0.14565677966101695,
    "RR": 0.16826411075612357,
    "counts": {
      "positive": 1888,
      "raw_incorrect": 1391,
      "positive_rejected": 275,
      "official_gated_correct": 503,
      "raw_correct_gated_wrong": 12,
      "raw_wrong_gated_correct": 18,
      "official_empty": 0,
      "raw_correct": 497,
      "raw_correct_accepted": 434,
      "raw_correct_rejected": 63,
      "negative": 939,
      "negative_accepted": 781
    },
    "raw_correct_rejected_over_positives": 0.03336864406779661,
    "raw_correct_rejected_over_raw_correct": 0.1267605633802817,
    "raw_errors_over_hard_failures": 0.9566712517193948,
    "threshold": 0.9977,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.5904159132007233,
    "same_video_pairs": 1659,
    "cross_video_pairacc": 0.5345790614468491,
    "exact_query_cross_video_pairacc": 0.5416044522872269,
    "exact_query_cross_video_pairs": 7367,
    "exact_query_groups": 158,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 664,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/pseudo.jsonl": "2866d727777b1c43a8f8eb6394c985b966c7300bb2693f950f4457f92c506a2e",
      "pseudo_predictions.jsonl": "7c28e4de9e2164a344c83784e4534715c8a90921529612116e3226e36990fbbf"
    }
  },
  "seen": {
    "AUROC": 0.8560905396251977,
    "raw_R1_05": 0.32945736434108525,
    "gated_R1_05": 0.34108527131782945,
    "FRR": 0.18992248062015504,
    "RR": 0.7961165048543689,
    "counts": {
      "positive": 516,
      "raw_incorrect": 346,
      "positive_rejected": 98,
      "official_gated_correct": 176,
      "raw_correct_gated_wrong": 1,
      "raw_wrong_gated_correct": 7,
      "official_empty": 0,
      "raw_correct": 170,
      "raw_correct_rejected": 31,
      "raw_correct_accepted": 139,
      "negative": 206,
      "negative_accepted": 42
    },
    "raw_correct_rejected_over_positives": 0.060077519379844964,
    "raw_correct_rejected_over_raw_correct": 0.18235294117647058,
    "raw_errors_over_hard_failures": 0.9177718832891246,
    "threshold": 0.9977,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.7944214876033058,
    "same_video_pairs": 484,
    "cross_video_pairacc": 0.8563726231429328,
    "exact_query_cross_video_pairacc": 0.625,
    "exact_query_cross_video_pairs": 12,
    "exact_query_groups": 9,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 104,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/val_seen.jsonl": "4e8dcb029c0e7e8c9f550ea568077d49fc1842ba64493f090aca8f2ee55c2a56",
      "best_seen_predictions.jsonl": "c847d74492c9ecf0d8022e233b8a1340ada6025e2535a0e0e7ba7be353400573"
    }
  }
}
```

## diagnostics/open_close/baseline/GATE_POSTPROCESS_AUDIT.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "results": {
    "pseudo": {
      "rows": 2827,
      "positive": 1888,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train263",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train469",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train470",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train509",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train510",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train511",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train969",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train981",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2498",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2711",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train3029",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train3341",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train3700",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train3702",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train4169",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train4186",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train5140",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train5633",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train6089",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train6113",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train6191",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train6829",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train7531",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train7753",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train8779",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train8829",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train9567",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train11487",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train11786",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train12226",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.2664194915254237,
      "official_gated_R1_05": 0.2664194915254237,
      "prediction_sha256": "7c28e4de9e2164a344c83784e4534715c8a90921529612116e3226e36990fbbf"
    },
    "seen": {
      "rows": 722,
      "positive": 516,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train1126",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train1411",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train1916",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2481",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train3563",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train6674",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train7600",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train10356",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.34108527131782945,
      "official_gated_R1_05": 0.34108527131782945,
      "prediction_sha256": "c847d74492c9ecf0d8022e233b8a1340ada6025e2535a0e0e7ba7be353400573"
    }
  },
  "source_sha256": "e8f3da3638ebe09271ab1e32db99dd2ce36e12e5d52584165ea6d7310791f5f4",
  "official_evaluator_sha256": "b71f952fa6cfbfbaae1ca0b6bd1f476159c17c2448b87d55f82300fa97a50537",
  "official_postprocessor_sha256": "50e6501c642e77502f7a4d781e01e12bbd97521d3b0a8f47d793b3044be30046",
  "gate_sha256": "0e1235c8425f9c61883e88a57a8a1feec2c9ceb15046aeecd83563deb3cefc67",
  "interpretation": "Official soft gate is a per-row nonnegative scalar. Exact positive scalar scaling preserves within-row ranking. Saved gated coordinates alone receive clip_ts/round_multiple; frozen raw endpoint remains untouched. When aligned coordinates match, hit changes are explained by temporal postprocessing rather than gate veto or reranking. Aligned raw is auxiliary only, not a replacement co-primary endpoint."
}
```

## diagnostics/open_close/baseline/GRADIENT_DETAIL.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "source_sha256": "aa62ab661c26930186b53405490d723cc70e4c952e94a60596cd0584f7619473",
  "checkpoints": {
    "best": {
      "checkpoint_epoch_zero_based": 49,
      "checkpoint_sha256": "7c0e74c81535fc3371772c9706331b09c2b43f0c16c0d0504ca3d2244ab415ea",
      "model_tensor_sha256": "e1ae2e52c59731ef7df018d0ab87d78ec84be6024ce3df07a236f7b98f3a5b04",
      "original_diagnostic_sha256": "e948f07099d469306c7fbe4cc7bf3ca312374c0f7d8f127817f4b1a712bfa2f4",
      "qids": [
        [
          "train5809",
          "train1090",
          "train9396",
          "train8631",
          "train3994",
          "train1331",
          "train2066",
          "train3646",
          "train8820",
          "train1053",
          "train3703",
          "train5166",
          "train5020",
          "train5321",
          "train3802",
          "train3497"
        ],
        [
          "train8913",
          "train10559",
          "train2459",
          "train11118",
          "train11785",
          "train4761",
          "train2780",
          "train10189",
          "train6074",
          "train7542",
          "train2134",
          "train11582",
          "train3615",
          "train8041",
          "train8752",
          "train12083"
        ],
        [
          "train1845",
          "train4260",
          "train10581",
          "train7743",
          "train2724",
          "train12152",
          "train11164",
          "train4102",
          "train7745",
          "train6906",
          "train1873",
          "train6190",
          "train3859",
          "train1923",
          "train721",
          "train5386"
        ],
        [
          "train11276",
          "train6352",
          "train7891",
          "train8070",
          "train9618",
          "train10454",
          "train6568",
          "train3989",
          "train10370",
          "train2797",
          "train2300",
          "train11923",
          "train7126",
          "train5146",
          "train4297",
          "train10362"
        ],
        [
          "train10531",
          "train1081",
          "train8749",
          "train11773",
          "train8280",
          "train9489",
          "train5728",
          "train5838",
          "train11788",
          "train7160",
          "train3363",
          "train728",
          "train8670",
          "train3496",
          "train10911",
          "train431"
        ],
        [
          "train9193",
          "train3724",
          "train6368",
          "train5327",
          "train9829",
          "train9626",
          "train1087",
          "train8181",
          "train11893",
          "train2173",
          "train5665",
          "train3951",
          "train7712",
          "train8370",
          "train10268",
          "train12323"
        ],
        [
          "train10334",
          "train1240",
          "train8422",
          "train1614",
          "train3861",
          "train5072",
          "train12397",
          "train3518",
          "train11230",
          "train5606",
          "train3624",
          "train10655",
          "train4301",
          "train10881",
          "train3168",
          "train9486"
        ],
        [
          "train9903",
          "train9482",
          "train5094",
          "train10969",
          "train4439",
          "train9214",
          "train5262",
          "train6036",
          "train9899",
          "train7935",
          "train7573",
          "train9770",
          "train11274",
          "train4232",
          "train9250",
          "train8125"
        ],
        [
          "train12144",
          "train8872",
          "train452",
          "train9667",
          "train6087",
          "train8117",
          "train3054",
          "train4233",
          "train191",
          "train8748",
          "train3419",
          "train5867",
          "train11713",
          "train11912",
          "train2862",
          "train9654"
        ],
        [
          "train8458",
          "train6810",
          "train2182",
          "train1757",
          "train807",
          "train5744",
          "train11744",
          "train11847",
          "train10231",
          "train10376",
          "train12023",
          "train6081",
          "train1111",
          "train5842",
          "train11853",
          "train3524"
        ],
        [
          "train1615",
          "train7210",
          "train11494",
          "train6254",
          "train11136",
          "train3677",
          "train6481",
          "train6957",
          "train8180",
          "train2572",
          "train9772",
          "train1562",
          "train4511",
          "train8889",
          "train1605",
          "train4327"
        ],
        [
          "train7965",
          "train6134",
          "train10594",
          "train6246",
          "train2922",
          "train4685",
          "train2071",
          "train2807",
          "train3905",
          "train7575",
          "train11419",
          "train7932",
          "train5328",
          "train10569",
          "train8773",
          "train3344"
        ],
        [
          "train6769",
          "train9916",
          "train12355",
          "train7415",
          "train4099",
          "train9615",
          "train4476",
          "train1571",
          "train9850",
          "train5048",
          "train1645",
          "train4200",
          "train49",
          "train3762",
          "train4934",
          "train6588"
        ],
        [
          "train8321",
          "train12021",
          "train7051",
          "train6401",
          "train10050",
          "train6991",
          "train7709",
          "train4866",
          "train2804",
          "train10585",
          "train3988",
          "train9761",
          "train12075",
          "train1396",
          "train10224",
          "train10212"
        ],
        [
          "train10499",
          "train2407",
          "train410",
          "train86",
          "train11037",
          "train3774",
          "train5925",
          "train3206",
          "train6361",
          "train3757",
          "train1048",
          "train8515",
          "train7638",
          "train9845",
          "train12088",
          "train502"
        ],
        [
          "train8968",
          "train5376",
          "train11985",
          "train3681",
          "train646",
          "train7015",
          "train572",
          "train11185",
          "train9436",
          "train5025",
          "train4216",
          "train2384",
          "train407",
          "train8016",
          "train10045",
          "train961"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.13296785950660706
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 2.9086978435516357
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.003379684960236773,
          "negative_fraction": 0.5625
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.03590112365782261
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.13304877281189
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.004829645389690995,
          "negative_fraction": 0.1875
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.4028981477022171
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 12.258073806762695
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.01453825505450368,
          "negative_fraction": 0.375
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.024252358824014664
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2627745568752289
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.15999481081962585
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.048152290284633636
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4585481286048889
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.044541969895362854
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.007646919693797827
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4820882976055145
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2944025695323944
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4452918469905853
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10594090819358826
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.09449832886457443
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.30498969554901123
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.029673604294657707
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.19095396995544434
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.053222183138132095
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3609488010406494
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8234989643096924
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.7005016803741455
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.6425960063934326
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.7277045249938965
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.554649829864502
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.0499022006988525
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.933811664581299
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.444362163543701
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.8955070972442627
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.2618424892425537
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.062646389007568
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1664090156555176
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.993896722793579
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.633530378341675
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.680398941040039
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.013704197481274605
          },
          {
            "full_block_cosine": 0.06300074607133865
          },
          {
            "full_block_cosine": 0.03318788856267929
          },
          {
            "full_block_cosine": -0.10149714350700378
          },
          {
            "full_block_cosine": -0.08401469886302948
          },
          {
            "full_block_cosine": 0.14461910724639893
          },
          {
            "full_block_cosine": -0.03864748030900955
          },
          {
            "full_block_cosine": -0.06652744859457016
          },
          {
            "full_block_cosine": -0.12163563072681427
          },
          {
            "full_block_cosine": -0.009703070856630802
          },
          {
            "full_block_cosine": -0.1137566789984703
          },
          {
            "full_block_cosine": -0.006228995975106955
          },
          {
            "full_block_cosine": 0.03308628499507904
          },
          {
            "full_block_cosine": 0.038040321320295334
          },
          {
            "full_block_cosine": -0.0005303739453665912
          },
          {
            "full_block_cosine": 0.05817451700568199
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.008178362622857094
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06980583816766739
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03976045176386833
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01669178158044815
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1255771666765213
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.011763426475226879
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003847405780106783
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.11616978794336319
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10716382414102554
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.11035798490047455
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.027845576405525208
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.032041795551776886
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.09272338449954987
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.012979013845324516
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.052182212471961975
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01689695008099079
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.141683101654053
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.975966691970825
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3084018230438232
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.60990571975708
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.8310866355896
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.576303482055664
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.9485087394714355
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.852982521057129
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.8048667907714844
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.124414443969727
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.5697829723358154
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.8300557136535645
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.226622104644775
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3939311504364014
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.394975185394287
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.90088152885437
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": 0.01706174947321415
          },
          {
            "full_block_cosine": 0.011717271991074085
          },
          {
            "full_block_cosine": 0.012856715358793736
          },
          {
            "full_block_cosine": -0.0017206637421622872
          },
          {
            "full_block_cosine": 0.0024481031578034163
          },
          {
            "full_block_cosine": 0.005342015065252781
          },
          {
            "full_block_cosine": 0.02162918820977211
          },
          {
            "full_block_cosine": -0.001615774817764759
          },
          {
            "full_block_cosine": -0.009645610116422176
          },
          {
            "full_block_cosine": 0.02618938684463501
          },
          {
            "full_block_cosine": 0.0018979355227202177
          },
          {
            "full_block_cosine": 0.01566285267472267
          },
          {
            "full_block_cosine": 0.0043172757141292095
          },
          {
            "full_block_cosine": 0.004273494705557823
          },
          {
            "full_block_cosine": 0.0014657502761110663
          },
          {
            "full_block_cosine": 0.011303485371172428
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.08460374176502228
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7913247346878052
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4795946478843689
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.12675605714321136
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.5412967205047607
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.12035888433456421
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03188123553991318
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.5125172138214111
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.877757728099823
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.5275027751922607
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3262016475200653
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2520872950553894
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7623616456985474
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10304462909698486
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5592935085296631
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.15071816742420197
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 13.931081771850586
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.738646507263184
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.910552978515625
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.500717163085938
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.216901779174805
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 14.418591499328613
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.826735496520996
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 15.855842590332031
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.979207038879395
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 14.782048225402832
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.062363624572754
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 17.223005294799805
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.566006660461426
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 14.018831253051758
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.119955062866211
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.299245834350586
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": -0.00366835854947567
          },
          {
            "full_block_cosine": 0.06574186682701111
          },
          {
            "full_block_cosine": 0.08794097602367401
          },
          {
            "full_block_cosine": 0.054501086473464966
          },
          {
            "full_block_cosine": -0.06206084042787552
          },
          {
            "full_block_cosine": 0.059822723269462585
          },
          {
            "full_block_cosine": -0.07243253290653229
          },
          {
            "full_block_cosine": -0.02193646878004074
          },
          {
            "full_block_cosine": -0.06967031955718994
          },
          {
            "full_block_cosine": 0.017111150547862053
          },
          {
            "full_block_cosine": -0.08034057170152664
          },
          {
            "full_block_cosine": 0.011965359561145306
          },
          {
            "full_block_cosine": 0.11563274264335632
          },
          {
            "full_block_cosine": 0.06806225329637527
          },
          {
            "full_block_cosine": 0.0072436099871993065
          },
          {
            "full_block_cosine": 0.08561397343873978
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    },
    "latest": {
      "checkpoint_epoch_zero_based": 99,
      "checkpoint_sha256": "605f493e00783844fee0840d2b0151859dd7f732a815726fd29583014349be87",
      "model_tensor_sha256": "4bd6694f96a1a61f92c6a0f5754045e93c2f1fb04673eacedb67d67bcdb3afc4",
      "original_diagnostic_sha256": "49765d684703335af74da7eac3d8b6de6a1a06c66944ca031236e49b778338c1",
      "qids": [
        [
          "train5809",
          "train1090",
          "train9396",
          "train8631",
          "train3994",
          "train1331",
          "train2066",
          "train3646",
          "train8820",
          "train1053",
          "train3703",
          "train5166",
          "train5020",
          "train5321",
          "train3802",
          "train3497"
        ],
        [
          "train8913",
          "train10559",
          "train2459",
          "train11118",
          "train11785",
          "train4761",
          "train2780",
          "train10189",
          "train6074",
          "train7542",
          "train2134",
          "train11582",
          "train3615",
          "train8041",
          "train8752",
          "train12083"
        ],
        [
          "train1845",
          "train4260",
          "train10581",
          "train7743",
          "train2724",
          "train12152",
          "train11164",
          "train4102",
          "train7745",
          "train6906",
          "train1873",
          "train6190",
          "train3859",
          "train1923",
          "train721",
          "train5386"
        ],
        [
          "train11276",
          "train6352",
          "train7891",
          "train8070",
          "train9618",
          "train10454",
          "train6568",
          "train3989",
          "train10370",
          "train2797",
          "train2300",
          "train11923",
          "train7126",
          "train5146",
          "train4297",
          "train10362"
        ],
        [
          "train10531",
          "train1081",
          "train8749",
          "train11773",
          "train8280",
          "train9489",
          "train5728",
          "train5838",
          "train11788",
          "train7160",
          "train3363",
          "train728",
          "train8670",
          "train3496",
          "train10911",
          "train431"
        ],
        [
          "train9193",
          "train3724",
          "train6368",
          "train5327",
          "train9829",
          "train9626",
          "train1087",
          "train8181",
          "train11893",
          "train2173",
          "train5665",
          "train3951",
          "train7712",
          "train8370",
          "train10268",
          "train12323"
        ],
        [
          "train10334",
          "train1240",
          "train8422",
          "train1614",
          "train3861",
          "train5072",
          "train12397",
          "train3518",
          "train11230",
          "train5606",
          "train3624",
          "train10655",
          "train4301",
          "train10881",
          "train3168",
          "train9486"
        ],
        [
          "train9903",
          "train9482",
          "train5094",
          "train10969",
          "train4439",
          "train9214",
          "train5262",
          "train6036",
          "train9899",
          "train7935",
          "train7573",
          "train9770",
          "train11274",
          "train4232",
          "train9250",
          "train8125"
        ],
        [
          "train12144",
          "train8872",
          "train452",
          "train9667",
          "train6087",
          "train8117",
          "train3054",
          "train4233",
          "train191",
          "train8748",
          "train3419",
          "train5867",
          "train11713",
          "train11912",
          "train2862",
          "train9654"
        ],
        [
          "train8458",
          "train6810",
          "train2182",
          "train1757",
          "train807",
          "train5744",
          "train11744",
          "train11847",
          "train10231",
          "train10376",
          "train12023",
          "train6081",
          "train1111",
          "train5842",
          "train11853",
          "train3524"
        ],
        [
          "train1615",
          "train7210",
          "train11494",
          "train6254",
          "train11136",
          "train3677",
          "train6481",
          "train6957",
          "train8180",
          "train2572",
          "train9772",
          "train1562",
          "train4511",
          "train8889",
          "train1605",
          "train4327"
        ],
        [
          "train7965",
          "train6134",
          "train10594",
          "train6246",
          "train2922",
          "train4685",
          "train2071",
          "train2807",
          "train3905",
          "train7575",
          "train11419",
          "train7932",
          "train5328",
          "train10569",
          "train8773",
          "train3344"
        ],
        [
          "train6769",
          "train9916",
          "train12355",
          "train7415",
          "train4099",
          "train9615",
          "train4476",
          "train1571",
          "train9850",
          "train5048",
          "train1645",
          "train4200",
          "train49",
          "train3762",
          "train4934",
          "train6588"
        ],
        [
          "train8321",
          "train12021",
          "train7051",
          "train6401",
          "train10050",
          "train6991",
          "train7709",
          "train4866",
          "train2804",
          "train10585",
          "train3988",
          "train9761",
          "train12075",
          "train1396",
          "train10224",
          "train10212"
        ],
        [
          "train10499",
          "train2407",
          "train410",
          "train86",
          "train11037",
          "train3774",
          "train5925",
          "train3206",
          "train6361",
          "train3757",
          "train1048",
          "train8515",
          "train7638",
          "train9845",
          "train12088",
          "train502"
        ],
        [
          "train8968",
          "train5376",
          "train11985",
          "train3681",
          "train646",
          "train7015",
          "train572",
          "train11185",
          "train9436",
          "train5025",
          "train4216",
          "train2384",
          "train407",
          "train8016",
          "train10045",
          "train961"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.00967435771599412
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 2.883290410041809
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.0008159137796610594,
          "negative_fraction": 0.5
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.003583829733543098
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.628950834274292
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.002039250743109733,
          "negative_fraction": 0.4375
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.011870014481246471
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 7.505797624588013
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.030808533541858196,
          "negative_fraction": 0.3125
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004580750595778227
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03033412992954254
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0018363723065704107
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002658919896930456
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.005906508769840002
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.007695289328694344
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001653155661188066
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.011653426103293896
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3679269850254059
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01358573604375124
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.005336361937224865
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01494545303285122
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.019154133275151253
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.013132882304489613
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.015471744351089
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0022347334306687117
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.2034640312194824
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1337764263153076
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.373955488204956
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.896261215209961
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.9392170906066895
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.7201647758483887
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.4364283084869385
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.6528728008270264
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.102617025375366
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.9973692893981934
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.113520383834839
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8065741062164307
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8703196048736572
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.499891519546509
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.742544412612915
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.591747283935547
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.05367321893572807
          },
          {
            "full_block_cosine": -0.07242554426193237
          },
          {
            "full_block_cosine": 0.04558702930808067
          },
          {
            "full_block_cosine": -0.034159690141677856
          },
          {
            "full_block_cosine": 0.015485914424061775
          },
          {
            "full_block_cosine": 0.024932388216257095
          },
          {
            "full_block_cosine": -0.015657104551792145
          },
          {
            "full_block_cosine": 0.05948023498058319
          },
          {
            "full_block_cosine": 0.055167824029922485
          },
          {
            "full_block_cosine": -0.007067072670906782
          },
          {
            "full_block_cosine": 0.005435245111584663
          },
          {
            "full_block_cosine": -0.03844951093196869
          },
          {
            "full_block_cosine": -0.11343131214380264
          },
          {
            "full_block_cosine": -0.010123956948518753
          },
          {
            "full_block_cosine": 0.0568598248064518
          },
          {
            "full_block_cosine": -0.06712163239717484
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0022624842822551727
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.009262153878808022
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0010893611470237374
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0013423659838736057
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0026354596484452486
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0030510115902870893
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0009721482638269663
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00516491150483489
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.14599454402923584
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004116647876799107
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002531577367335558
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.005275161005556583
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.006840053014457226
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.005211875308305025
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.006098118145018816
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0010842534247785807
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.742668628692627
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.01959753036499
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.592333793640137
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.480158805847168
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.0982866287231445
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.906676292419434
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.340618133544922
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.665567874908447
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.540380954742432
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.994267463684082
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.383302211761475
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.744746208190918
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.6808221340179443
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.227295875549316
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.4036946296691895
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.770404100418091
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": 0.015794066712260246
          },
          {
            "full_block_cosine": 0.008665237575769424
          },
          {
            "full_block_cosine": 0.01205704640597105
          },
          {
            "full_block_cosine": 0.005191104952245951
          },
          {
            "full_block_cosine": -0.0015627347165718675
          },
          {
            "full_block_cosine": 0.0018289556028321385
          },
          {
            "full_block_cosine": -0.0011946003651246428
          },
          {
            "full_block_cosine": 0.002249545883387327
          },
          {
            "full_block_cosine": -0.005791413597762585
          },
          {
            "full_block_cosine": -0.0035503103863447905
          },
          {
            "full_block_cosine": 0.007987462915480137
          },
          {
            "full_block_cosine": 0.009061865508556366
          },
          {
            "full_block_cosine": 0.0053105042316019535
          },
          {
            "full_block_cosine": -0.0016248018946498632
          },
          {
            "full_block_cosine": -0.003066800534725189
          },
          {
            "full_block_cosine": -0.006825269665569067
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0048688617534935474
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06354984641075134
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002161559881642461
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0038144816644489765
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.008792915381491184
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.010482613928616047
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0026336507871747017
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.013257415033876896
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6401935815811157
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03969555348157883
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.009494734928011894
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03903048112988472
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.030898721888661385
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01746072992682457
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.034187838435173035
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0026743581984192133
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.82196569442749
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.5077433586120605
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.5660014152526855
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.297260284423828
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.986258506774902
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.502167701721191
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.41684341430664
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.417232990264893
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.838071346282959
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.490605354309082
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.791769981384277
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.731849670410156
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.503851890563965
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.916468143463135
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.392426490783691
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.653759002685547
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": 0.19344519078731537
          },
          {
            "full_block_cosine": -0.13733036816120148
          },
          {
            "full_block_cosine": 0.22773604094982147
          },
          {
            "full_block_cosine": 0.11277096718549728
          },
          {
            "full_block_cosine": 0.03893477842211723
          },
          {
            "full_block_cosine": -0.012152692303061485
          },
          {
            "full_block_cosine": 0.022142469882965088
          },
          {
            "full_block_cosine": -0.004496516659855843
          },
          {
            "full_block_cosine": 0.03208091855049133
          },
          {
            "full_block_cosine": 0.02647186443209648
          },
          {
            "full_block_cosine": 0.02953614853322506
          },
          {
            "full_block_cosine": 0.06789322942495346
          },
          {
            "full_block_cosine": -0.027431858703494072
          },
          {
            "full_block_cosine": 0.03984150290489197
          },
          {
            "full_block_cosine": 0.13539938628673553
          },
          {
            "full_block_cosine": -0.09216383099555969
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    }
  },
  "interpretation": "S+ only, eval mode local geometry; unused tensors treated as zero in full-block cosine. Original norms used only the jointly differentiable tensor intersection; detail fixes interpretation without overwriting original output. Inactive saliency is unavailable, not agreement. No S- localization gradient is inferred."
}
```

## diagnostics/open_close/baseline/GRADIENT_RELATIONS_best.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/best.ckpt",
  "checkpoint_sha256": "7c0e74c81535fc3371772c9706331b09c2b43f0c16c0d0504ca3d2244ab415ea",
  "checkpoint_epoch_zero_based": 49,
  "executed_source_sha256": "0cefac0e2209e91c37897790ccc595c159083f570579c9996f2663d10a5af524",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train5809",
      "train1090",
      "train9396",
      "train8631",
      "train3994",
      "train1331",
      "train2066",
      "train3646",
      "train8820",
      "train1053",
      "train3703",
      "train5166",
      "train5020",
      "train5321",
      "train3802",
      "train3497"
    ],
    [
      "train8913",
      "train10559",
      "train2459",
      "train11118",
      "train11785",
      "train4761",
      "train2780",
      "train10189",
      "train6074",
      "train7542",
      "train2134",
      "train11582",
      "train3615",
      "train8041",
      "train8752",
      "train12083"
    ],
    [
      "train1845",
      "train4260",
      "train10581",
      "train7743",
      "train2724",
      "train12152",
      "train11164",
      "train4102",
      "train7745",
      "train6906",
      "train1873",
      "train6190",
      "train3859",
      "train1923",
      "train721",
      "train5386"
    ],
    [
      "train11276",
      "train6352",
      "train7891",
      "train8070",
      "train9618",
      "train10454",
      "train6568",
      "train3989",
      "train10370",
      "train2797",
      "train2300",
      "train11923",
      "train7126",
      "train5146",
      "train4297",
      "train10362"
    ],
    [
      "train10531",
      "train1081",
      "train8749",
      "train11773",
      "train8280",
      "train9489",
      "train5728",
      "train5838",
      "train11788",
      "train7160",
      "train3363",
      "train728",
      "train8670",
      "train3496",
      "train10911",
      "train431"
    ],
    [
      "train9193",
      "train3724",
      "train6368",
      "train5327",
      "train9829",
      "train9626",
      "train1087",
      "train8181",
      "train11893",
      "train2173",
      "train5665",
      "train3951",
      "train7712",
      "train8370",
      "train10268",
      "train12323"
    ],
    [
      "train10334",
      "train1240",
      "train8422",
      "train1614",
      "train3861",
      "train5072",
      "train12397",
      "train3518",
      "train11230",
      "train5606",
      "train3624",
      "train10655",
      "train4301",
      "train10881",
      "train3168",
      "train9486"
    ],
    [
      "train9903",
      "train9482",
      "train5094",
      "train10969",
      "train4439",
      "train9214",
      "train5262",
      "train6036",
      "train9899",
      "train7935",
      "train7573",
      "train9770",
      "train11274",
      "train4232",
      "train9250",
      "train8125"
    ],
    [
      "train12144",
      "train8872",
      "train452",
      "train9667",
      "train6087",
      "train8117",
      "train3054",
      "train4233",
      "train191",
      "train8748",
      "train3419",
      "train5867",
      "train11713",
      "train11912",
      "train2862",
      "train9654"
    ],
    [
      "train8458",
      "train6810",
      "train2182",
      "train1757",
      "train807",
      "train5744",
      "train11744",
      "train11847",
      "train10231",
      "train10376",
      "train12023",
      "train6081",
      "train1111",
      "train5842",
      "train11853",
      "train3524"
    ],
    [
      "train1615",
      "train7210",
      "train11494",
      "train6254",
      "train11136",
      "train3677",
      "train6481",
      "train6957",
      "train8180",
      "train2572",
      "train9772",
      "train1562",
      "train4511",
      "train8889",
      "train1605",
      "train4327"
    ],
    [
      "train7965",
      "train6134",
      "train10594",
      "train6246",
      "train2922",
      "train4685",
      "train2071",
      "train2807",
      "train3905",
      "train7575",
      "train11419",
      "train7932",
      "train5328",
      "train10569",
      "train8773",
      "train3344"
    ],
    [
      "train6769",
      "train9916",
      "train12355",
      "train7415",
      "train4099",
      "train9615",
      "train4476",
      "train1571",
      "train9850",
      "train5048",
      "train1645",
      "train4200",
      "train49",
      "train3762",
      "train4934",
      "train6588"
    ],
    [
      "train8321",
      "train12021",
      "train7051",
      "train6401",
      "train10050",
      "train6991",
      "train7709",
      "train4866",
      "train2804",
      "train10585",
      "train3988",
      "train9761",
      "train12075",
      "train1396",
      "train10224",
      "train10212"
    ],
    [
      "train10499",
      "train2407",
      "train410",
      "train86",
      "train11037",
      "train3774",
      "train5925",
      "train3206",
      "train6361",
      "train3757",
      "train1048",
      "train8515",
      "train7638",
      "train9845",
      "train12088",
      "train502"
    ],
    [
      "train8968",
      "train5376",
      "train11985",
      "train3681",
      "train646",
      "train7015",
      "train572",
      "train11185",
      "train9436",
      "train5025",
      "train4216",
      "train2384",
      "train407",
      "train8016",
      "train10045",
      "train961"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.0033796851930674165,
      "negative_fraction": 0.5625,
      "cosines": [
        0.013704193755984306,
        0.06300074607133865,
        0.03318788483738899,
        -0.10149716585874557,
        -0.08401472121477127,
        0.14461912214756012,
        -0.03864748030900955,
        -0.06652743369340897,
        -0.12163562327623367,
        -0.009703068993985653,
        -0.1137566864490509,
        -0.006228998769074678,
        0.03308629244565964,
        0.03804032504558563,
        -0.0005303716170601547,
        0.05817451700568199
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.024252358824014664,
          "other_norm": 3.3609488010406494
        },
        {
          "exist_norm": 0.26277458667755127,
          "other_norm": 2.8234989643096924
        },
        {
          "exist_norm": 0.15999481081962585,
          "other_norm": 2.7005014419555664
        },
        {
          "exist_norm": 0.048152294009923935,
          "other_norm": 2.6425960063934326
        },
        {
          "exist_norm": 0.45854809880256653,
          "other_norm": 2.7277045249938965
        },
        {
          "exist_norm": 0.04454196244478226,
          "other_norm": 3.554649829864502
        },
        {
          "exist_norm": 0.007646919693797827,
          "other_norm": 3.0499022006988525
        },
        {
          "exist_norm": 0.4820883274078369,
          "other_norm": 3.933811664581299
        },
        {
          "exist_norm": 0.2944025993347168,
          "other_norm": 2.444362163543701
        },
        {
          "exist_norm": 0.44529181718826294,
          "other_norm": 3.8955070972442627
        },
        {
          "exist_norm": 0.10594090819358826,
          "other_norm": 2.2618422508239746
        },
        {
          "exist_norm": 0.09449835121631622,
          "other_norm": 4.062646389007568
        },
        {
          "exist_norm": 0.30498966574668884,
          "other_norm": 3.1664092540740967
        },
        {
          "exist_norm": 0.029673604294657707,
          "other_norm": 2.993896484375
        },
        {
          "exist_norm": 0.19095396995544434,
          "other_norm": 2.633530616760254
        },
        {
          "exist_norm": 0.053222183138132095,
          "other_norm": 2.680398941040039
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.015532387420535088,
      "negative_fraction": 0.1875,
      "cosines": [
        0.03790551796555519,
        0.029235048219561577,
        0.03238779678940773,
        -0.006638216320425272,
        0.011329744011163712,
        0.01731172949075699,
        0.07306808978319168,
        -0.005817083176225424,
        -0.033009909093379974,
        0.062295667827129364,
        0.004551268182694912,
        0.06632006913423538,
        0.013753045350313187,
        0.010192958638072014,
        0.0039004916325211525,
        0.02852764166891575
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.008178362622857094,
          "other_norm": 1.8642234802246094
        },
        {
          "exist_norm": 0.06980583816766739,
          "other_norm": 1.1927536725997925
        },
        {
          "exist_norm": 0.03976045548915863,
          "other_norm": 1.3133089542388916
        },
        {
          "exist_norm": 0.016691779717803,
          "other_norm": 1.4541200399398804
        },
        {
          "exist_norm": 0.1255771666765213,
          "other_norm": 1.0438894033432007
        },
        {
          "exist_norm": 0.011763425543904305,
          "other_norm": 1.7207231521606445
        },
        {
          "exist_norm": 0.0038474055472761393,
          "other_norm": 1.4648284912109375
        },
        {
          "exist_norm": 0.11616978794336319,
          "other_norm": 1.9035098552703857
        },
        {
          "exist_norm": 0.10716382414102554,
          "other_norm": 1.111795425415039
        },
        {
          "exist_norm": 0.11035798490047455,
          "other_norm": 1.7339224815368652
        },
        {
          "exist_norm": 0.02784557454288006,
          "other_norm": 1.0716313123703003
        },
        {
          "exist_norm": 0.032041795551776886,
          "other_norm": 1.6130589246749878
        },
        {
          "exist_norm": 0.09272336959838867,
          "other_norm": 1.6407109498977661
        },
        {
          "exist_norm": 0.012979013845324516,
          "other_norm": 1.4229378700256348
        },
        {
          "exist_norm": 0.05218220874667168,
          "other_norm": 1.2757840156555176
        },
        {
          "exist_norm": 0.016896948218345642,
          "other_norm": 1.5456433296203613
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.014538254123181105,
      "negative_fraction": 0.375,
      "cosines": [
        -0.0036683594807982445,
        0.06574186682701111,
        0.08794097602367401,
        0.05450107529759407,
        -0.06206084042787552,
        0.05982271954417229,
        -0.07243254035711288,
        -0.021936463192105293,
        -0.06967030465602875,
        0.017111148685216904,
        -0.08034055680036545,
        0.011965359561145306,
        0.11563275754451752,
        0.06806225329637527,
        0.007243606727570295,
        0.08561398833990097
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.08460374176502228,
          "other_norm": 13.931081771850586
        },
        {
          "exist_norm": 0.7913246750831604,
          "other_norm": 11.7386474609375
        },
        {
          "exist_norm": 0.4795946478843689,
          "other_norm": 11.910552978515625
        },
        {
          "exist_norm": 0.12675605714321136,
          "other_norm": 11.500718116760254
        },
        {
          "exist_norm": 1.5412967205047607,
          "other_norm": 12.216901779174805
        },
        {
          "exist_norm": 0.12035888433456421,
          "other_norm": 14.418591499328613
        },
        {
          "exist_norm": 0.03188123553991318,
          "other_norm": 12.82673454284668
        },
        {
          "exist_norm": 1.5125172138214111,
          "other_norm": 15.855843544006348
        },
        {
          "exist_norm": 0.8777576684951782,
          "other_norm": 10.979207038879395
        },
        {
          "exist_norm": 1.5275027751922607,
          "other_norm": 14.782047271728516
        },
        {
          "exist_norm": 0.3262016475200653,
          "other_norm": 11.06236457824707
        },
        {
          "exist_norm": 0.2520872950553894,
          "other_norm": 17.223005294799805
        },
        {
          "exist_norm": 0.7623616456985474,
          "other_norm": 11.56600570678711
        },
        {
          "exist_norm": 0.10304462909698486,
          "other_norm": 14.018831253051758
        },
        {
          "exist_norm": 0.5592935085296631,
          "other_norm": 11.119956016540527
        },
        {
          "exist_norm": 0.15071815252304077,
          "other_norm": 12.29924488067627
        }
      ]
    }
  },
  "state": "completed",
  "interpretation": "cross-checkpoint and cross-family evidence required; duplicated best/latest epoch is not independent evidence"
}
```

## diagnostics/open_close/baseline/GRADIENT_RELATIONS_latest.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/runs/open_close_qd_gmr_baseline_s3407_attempt1/latest.ckpt",
  "checkpoint_sha256": "605f493e00783844fee0840d2b0151859dd7f732a815726fd29583014349be87",
  "checkpoint_epoch_zero_based": 99,
  "executed_source_sha256": "0cefac0e2209e91c37897790ccc595c159083f570579c9996f2663d10a5af524",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train5809",
      "train1090",
      "train9396",
      "train8631",
      "train3994",
      "train1331",
      "train2066",
      "train3646",
      "train8820",
      "train1053",
      "train3703",
      "train5166",
      "train5020",
      "train5321",
      "train3802",
      "train3497"
    ],
    [
      "train8913",
      "train10559",
      "train2459",
      "train11118",
      "train11785",
      "train4761",
      "train2780",
      "train10189",
      "train6074",
      "train7542",
      "train2134",
      "train11582",
      "train3615",
      "train8041",
      "train8752",
      "train12083"
    ],
    [
      "train1845",
      "train4260",
      "train10581",
      "train7743",
      "train2724",
      "train12152",
      "train11164",
      "train4102",
      "train7745",
      "train6906",
      "train1873",
      "train6190",
      "train3859",
      "train1923",
      "train721",
      "train5386"
    ],
    [
      "train11276",
      "train6352",
      "train7891",
      "train8070",
      "train9618",
      "train10454",
      "train6568",
      "train3989",
      "train10370",
      "train2797",
      "train2300",
      "train11923",
      "train7126",
      "train5146",
      "train4297",
      "train10362"
    ],
    [
      "train10531",
      "train1081",
      "train8749",
      "train11773",
      "train8280",
      "train9489",
      "train5728",
      "train5838",
      "train11788",
      "train7160",
      "train3363",
      "train728",
      "train8670",
      "train3496",
      "train10911",
      "train431"
    ],
    [
      "train9193",
      "train3724",
      "train6368",
      "train5327",
      "train9829",
      "train9626",
      "train1087",
      "train8181",
      "train11893",
      "train2173",
      "train5665",
      "train3951",
      "train7712",
      "train8370",
      "train10268",
      "train12323"
    ],
    [
      "train10334",
      "train1240",
      "train8422",
      "train1614",
      "train3861",
      "train5072",
      "train12397",
      "train3518",
      "train11230",
      "train5606",
      "train3624",
      "train10655",
      "train4301",
      "train10881",
      "train3168",
      "train9486"
    ],
    [
      "train9903",
      "train9482",
      "train5094",
      "train10969",
      "train4439",
      "train9214",
      "train5262",
      "train6036",
      "train9899",
      "train7935",
      "train7573",
      "train9770",
      "train11274",
      "train4232",
      "train9250",
      "train8125"
    ],
    [
      "train12144",
      "train8872",
      "train452",
      "train9667",
      "train6087",
      "train8117",
      "train3054",
      "train4233",
      "train191",
      "train8748",
      "train3419",
      "train5867",
      "train11713",
      "train11912",
      "train2862",
      "train9654"
    ],
    [
      "train8458",
      "train6810",
      "train2182",
      "train1757",
      "train807",
      "train5744",
      "train11744",
      "train11847",
      "train10231",
      "train10376",
      "train12023",
      "train6081",
      "train1111",
      "train5842",
      "train11853",
      "train3524"
    ],
    [
      "train1615",
      "train7210",
      "train11494",
      "train6254",
      "train11136",
      "train3677",
      "train6481",
      "train6957",
      "train8180",
      "train2572",
      "train9772",
      "train1562",
      "train4511",
      "train8889",
      "train1605",
      "train4327"
    ],
    [
      "train7965",
      "train6134",
      "train10594",
      "train6246",
      "train2922",
      "train4685",
      "train2071",
      "train2807",
      "train3905",
      "train7575",
      "train11419",
      "train7932",
      "train5328",
      "train10569",
      "train8773",
      "train3344"
    ],
    [
      "train6769",
      "train9916",
      "train12355",
      "train7415",
      "train4099",
      "train9615",
      "train4476",
      "train1571",
      "train9850",
      "train5048",
      "train1645",
      "train4200",
      "train49",
      "train3762",
      "train4934",
      "train6588"
    ],
    [
      "train8321",
      "train12021",
      "train7051",
      "train6401",
      "train10050",
      "train6991",
      "train7709",
      "train4866",
      "train2804",
      "train10585",
      "train3988",
      "train9761",
      "train12075",
      "train1396",
      "train10224",
      "train10212"
    ],
    [
      "train10499",
      "train2407",
      "train410",
      "train86",
      "train11037",
      "train3774",
      "train5925",
      "train3206",
      "train6361",
      "train3757",
      "train1048",
      "train8515",
      "train7638",
      "train9845",
      "train12088",
      "train502"
    ],
    [
      "train8968",
      "train5376",
      "train11985",
      "train3681",
      "train646",
      "train7015",
      "train572",
      "train11185",
      "train9436",
      "train5025",
      "train4216",
      "train2384",
      "train407",
      "train8016",
      "train10045",
      "train961"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.0008159161079674959,
      "negative_fraction": 0.5,
      "cosines": [
        0.05367322638630867,
        -0.07242552936077118,
        0.04558701813220978,
        -0.03415968641638756,
        0.01548592746257782,
        0.0249323733150959,
        -0.015657098963856697,
        0.059480223804712296,
        0.05516782030463219,
        -0.007067082449793816,
        0.005435250233858824,
        -0.03844951465725899,
        -0.11343130469322205,
        -0.010123958811163902,
        0.0568598210811615,
        -0.06712162494659424
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.004580750595778227,
          "other_norm": 2.2034640312194824
        },
        {
          "exist_norm": 0.03033412992954254,
          "other_norm": 3.1337766647338867
        },
        {
          "exist_norm": 0.0018363723065704107,
          "other_norm": 2.373955249786377
        },
        {
          "exist_norm": 0.002658919896930456,
          "other_norm": 2.896261215209961
        },
        {
          "exist_norm": 0.005906508304178715,
          "other_norm": 2.9392168521881104
        },
        {
          "exist_norm": 0.007695289328694344,
          "other_norm": 3.7201650142669678
        },
        {
          "exist_norm": 0.0016531557776033878,
          "other_norm": 3.4364285469055176
        },
        {
          "exist_norm": 0.01165342703461647,
          "other_norm": 2.6528728008270264
        },
        {
          "exist_norm": 0.36792701482772827,
          "other_norm": 3.102617025375366
        },
        {
          "exist_norm": 0.013585737906396389,
          "other_norm": 2.9973697662353516
        },
        {
          "exist_norm": 0.005336361937224865,
          "other_norm": 3.113520383834839
        },
        {
          "exist_norm": 0.014945453964173794,
          "other_norm": 2.8065741062164307
        },
        {
          "exist_norm": 0.019154131412506104,
          "other_norm": 2.870319366455078
        },
        {
          "exist_norm": 0.013132879510521889,
          "other_norm": 2.4998912811279297
        },
        {
          "exist_norm": 0.015471743419766426,
          "other_norm": 2.742544651031494
        },
        {
          "exist_norm": 0.0022347334306687117,
          "other_norm": 2.5917470455169678
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.0077070805709809065,
      "negative_fraction": 0.4375,
      "cosines": [
        0.0706130787730217,
        0.02373858354985714,
        0.05756107717752457,
        0.023143576458096504,
        -0.005629108287394047,
        0.005400998052209616,
        -0.004997734911739826,
        0.010013163089752197,
        -0.0241593848913908,
        -0.014121941290795803,
        0.025785168632864952,
        0.031200341880321503,
        0.015912555158138275,
        -0.00819351151585579,
        -0.010839404538273811,
        -0.021181337535381317
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.0022624842822551727,
          "other_norm": 1.0607954263687134
        },
        {
          "exist_norm": 0.009262153878808022,
          "other_norm": 1.4672644138336182
        },
        {
          "exist_norm": 0.0010893611470237374,
          "other_norm": 0.9619343280792236
        },
        {
          "exist_norm": 0.0013423659838736057,
          "other_norm": 1.2291995286941528
        },
        {
          "exist_norm": 0.0026354596484452486,
          "other_norm": 1.1377530097961426
        },
        {
          "exist_norm": 0.0030510113574564457,
          "other_norm": 1.661562204360962
        },
        {
          "exist_norm": 0.0009721483220346272,
          "other_norm": 1.2765589952468872
        },
        {
          "exist_norm": 0.00516491150483489,
          "other_norm": 1.0481611490249634
        },
        {
          "exist_norm": 0.14599454402923584,
          "other_norm": 1.0884063243865967
        },
        {
          "exist_norm": 0.004116647876799107,
          "other_norm": 1.2555779218673706
        },
        {
          "exist_norm": 0.002531577367335558,
          "other_norm": 1.3578139543533325
        },
        {
          "exist_norm": 0.005275161005556583,
          "other_norm": 1.3780698776245117
        },
        {
          "exist_norm": 0.0068400525487959385,
          "other_norm": 1.2284024953842163
        },
        {
          "exist_norm": 0.005211874842643738,
          "other_norm": 1.43319833278656
        },
        {
          "exist_norm": 0.006098118610680103,
          "other_norm": 1.2459399700164795
        },
        {
          "exist_norm": 0.0010842534247785807,
          "other_norm": 1.2149386405944824
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.030808529816567898,
      "negative_fraction": 0.3125,
      "cosines": [
        0.19344519078731537,
        -0.13733038306236267,
        0.22773604094982147,
        0.11277098208665848,
        0.038934774696826935,
        -0.012152694165706635,
        0.02214246243238449,
        -0.004496521782130003,
        0.03208091855049133,
        0.02647186629474163,
        0.029536141082644463,
        0.06789323687553406,
        -0.027431856840848923,
        0.03984151780605316,
        0.13539940118789673,
        -0.09216383844614029
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.00486886128783226,
          "other_norm": 6.82196569442749
        },
        {
          "exist_norm": 0.06354984641075134,
          "other_norm": 7.5077433586120605
        },
        {
          "exist_norm": 0.0021615601144731045,
          "other_norm": 6.5660014152526855
        },
        {
          "exist_norm": 0.003814481431618333,
          "other_norm": 8.297260284423828
        },
        {
          "exist_norm": 0.008792915381491184,
          "other_norm": 8.986259460449219
        },
        {
          "exist_norm": 0.010482613928616047,
          "other_norm": 9.502166748046875
        },
        {
          "exist_norm": 0.0026336507871747017,
          "other_norm": 9.41684341430664
        },
        {
          "exist_norm": 0.013257415033876896,
          "other_norm": 6.417232990264893
        },
        {
          "exist_norm": 0.6401935815811157,
          "other_norm": 7.838070869445801
        },
        {
          "exist_norm": 0.039695557206869125,
          "other_norm": 7.490605354309082
        },
        {
          "exist_norm": 0.009494734928011894,
          "other_norm": 7.791769981384277
        },
        {
          "exist_norm": 0.03903047740459442,
          "other_norm": 6.731849193572998
        },
        {
          "exist_norm": 0.030898721888661385,
          "other_norm": 7.503851890563965
        },
        {
          "exist_norm": 0.01746072992682457,
          "other_norm": 5.916468143463135
        },
        {
          "exist_norm": 0.034187838435173035,
          "other_norm": 7.392426490783691
        },
        {
          "exist_norm": 0.0026743581984192133,
          "other_norm": 9.653759002685547
        }
      ]
    }
  },
  "state": "completed",
  "interpretation": "cross-checkpoint and cross-family evidence required; duplicated best/latest epoch is not independent evidence"
}
```

## diagnostics/open_close/baseline/INPUT_SENSITIVITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "rows": 2827,
  "videos": 1236,
  "manifest_sha256": "aaabf8eb0ef81362e844c28c1e8f7ca8c15ae8d0a298d2b91050f6fa8313bc75",
  "identity_max_abs_error": 0.0,
  "summaries": {
    "identity": {
      "exist_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      }
    },
    "zero_visual": {
      "exist_abs_delta": {
        "row_mean": 0.02428787410828187,
        "video_mean": 0.03164228679252281,
        "video_bootstrap_ci95": [
          0.02572860962502534,
          0.03816355980789038
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.20870180403254332,
        "video_mean": 0.21260530641598605,
        "video_bootstrap_ci95": [
          0.19080352327014954,
          0.233589391662814
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.16043993408736046,
        "video_mean": 0.16221237746122602,
        "video_bootstrap_ci95": [
          0.15084535444413358,
          0.17311866194965328
        ]
      }
    },
    "shuffle_time": {
      "exist_abs_delta": {
        "row_mean": 0.00661922296973902,
        "video_mean": 0.007406949166900704,
        "video_bootstrap_ci95": [
          0.00592774948407457,
          0.009095710450582745
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.10364343827378847,
        "video_mean": 0.10695921302717419,
        "video_bootstrap_ci95": [
          0.0923985141521549,
          0.12172212911593977
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.06842222081996081,
        "video_mean": 0.07078153627440038,
        "video_bootstrap_ci95": [
          0.06242217547372871,
          0.0783724083008694
        ]
      }
    },
    "zero_clip": {
      "exist_abs_delta": {
        "row_mean": 0.01994725466692434,
        "video_mean": 0.02389516509453074,
        "video_bootstrap_ci95": [
          0.019369256040974652,
          0.029041562443723985
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.17226742129465866,
        "video_mean": 0.17631183541377718,
        "video_bootstrap_ci95": [
          0.15878472222222229,
          0.19428292109724152
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.11980537345964326,
        "video_mean": 0.12234092774694652,
        "video_bootstrap_ci95": [
          0.11300152728253512,
          0.1328505997397894
        ]
      }
    },
    "zero_slowfast": {
      "exist_abs_delta": {
        "row_mean": 0.022708491366272603,
        "video_mean": 0.027793265622271898,
        "video_bootstrap_ci95": [
          0.022293481310220208,
          0.0342862367319134
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.3180049522461974,
        "video_mean": 0.3178295320285611,
        "video_bootstrap_ci95": [
          0.2935734512251503,
          0.3431853746083114
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.2070658327052966,
        "video_mean": 0.20813375238666498,
        "video_bootstrap_ci95": [
          0.19586713133134875,
          0.2210326398720668
        ]
      }
    }
  },
  "limitations": "Sensitivity of frozen model, not necessity/causal proof. Zeroing is out of distribution; shuffle preserves positions. No perturbed-label AUROC, R1, FRR or RR computed. Raw top span before official temporal postprocessing; original official gate is a scalar per row and does not change exact-precision slot ranking."
}
```

## diagnostics/open_close/baseline/INPUT_SENSITIVITY_MANIFEST.json

```json
{
  "state": "frozen_before_inference",
  "seed": 3407,
  "training_updates": 0,
  "checkpoint_sha256": "7c0e74c81535fc3371772c9706331b09c2b43f0c16c0d0504ca3d2244ab415ea",
  "checkpoint_epoch_zero_based": 49,
  "source_sha256": "d980356f74f3bed35178abf6120b6ea99e8ac23aaef7748dd2e8a4f42f38dec8",
  "view_sha256": "2866d727777b1c43a8f8eb6394c985b966c7300bb2693f950f4457f92c506a2e",
  "qids": [
    "train16",
    "train28",
    "train34",
    "train35",
    "train36",
    "train38",
    "train53",
    "train54",
    "train57",
    "train60",
    "train72",
    "train73",
    "train74",
    "train92",
    "train94",
    "train95",
    "train97",
    "train103",
    "train106",
    "train109",
    "train121",
    "train133",
    "train134",
    "train138",
    "train141",
    "train142",
    "train152",
    "train168",
    "train169",
    "train172",
    "train173",
    "train174",
    "train206",
    "train208",
    "train248",
    "train249",
    "train250",
    "train256",
    "train263",
    "train287",
    "train289",
    "train294",
    "train298",
    "train299",
    "train307",
    "train309",
    "train310",
    "train330",
    "train331",
    "train378",
    "train387",
    "train424",
    "train425",
    "train444",
    "train445",
    "train446",
    "train448",
    "train455",
    "train457",
    "train458",
    "train459",
    "train460",
    "train469",
    "train470",
    "train483",
    "train490",
    "train501",
    "train507",
    "train509",
    "train510",
    "train511",
    "train526",
    "train530",
    "train532",
    "train533",
    "train534",
    "train548",
    "train550",
    "train552",
    "train554",
    "train570",
    "train585",
    "train592",
    "train595",
    "train603",
    "train608",
    "train647",
    "train656",
    "train658",
    "train666",
    "train667",
    "train672",
    "train674",
    "train675",
    "train676",
    "train683",
    "train701",
    "train703",
    "train713",
    "train714",
    "train734",
    "train737",
    "train739",
    "train743",
    "train763",
    "train776",
    "train788",
    "train789",
    "train790",
    "train815",
    "train830",
    "train831",
    "train832",
    "train834",
    "train835",
    "train852",
    "train900",
    "train902",
    "train907",
    "train921",
    "train922",
    "train926",
    "train936",
    "train938",
    "train969",
    "train974",
    "train975",
    "train976",
    "train977",
    "train981",
    "train982",
    "train983",
    "train999",
    "train1003",
    "train1004",
    "train1023",
    "train1030",
    "train1043",
    "train1045",
    "train1054",
    "train1055",
    "train1056",
    "train1057",
    "train1063",
    "train1072",
    "train1082",
    "train1098",
    "train1102",
    "train1117",
    "train1124",
    "train1127",
    "train1128",
    "train1135",
    "train1138",
    "train1139",
    "train1140",
    "train1141",
    "train1144",
    "train1158",
    "train1165",
    "train1170",
    "train1174",
    "train1178",
    "train1180",
    "train1185",
    "train1186",
    "train1187",
    "train1188",
    "train1194",
    "train1195",
    "train1206",
    "train1207",
    "train1216",
    "train1236",
    "train1237",
    "train1238",
    "train1244",
    "train1245",
    "train1246",
    "train1257",
    "train1264",
    "train1265",
    "train1267",
    "train1268",
    "train1287",
    "train1297",
    "train1299",
    "train1316",
    "train1317",
    "train1322",
    "train1332",
    "train1338",
    "train1340",
    "train1346",
    "train1348",
    "train1349",
    "train1356",
    "train1359",
    "train1372",
    "train1373",
    "train1374",
    "train1383",
    "train1399",
    "train1429",
    "train1430",
    "train1431",
    "train1448",
    "train1450",
    "train1473",
    "train1475",
    "train1487",
    "train1489",
    "train1493",
    "train1494",
    "train1504",
    "train1506",
    "train1508",
    "train1510",
    "train1527",
    "train1528",
    "train1534",
    "train1558",
    "train1559",
    "train1566",
    "train1569",
    "train1578",
    "train1593",
    "train1595",
    "train1596",
    "train1612",
    "train1613",
    "train1618",
    "train1619",
    "train1621",
    "train1622",
    "train1623",
    "train1625",
    "train1629",
    "train1631",
    "train1635",
    "train1637",
    "train1639",
    "train1641",
    "train1647",
    "train1649",
    "train1654",
    "train1660",
    "train1661",
    "train1668",
    "train1673",
    "train1693",
    "train1695",
    "train1697",
    "train1703",
    "train1705",
    "train1706",
    "train1717",
    "train1718",
    "train1738",
    "train1744",
    "train1749",
    "train1766",
    "train1775",
    "train1792",
    "train1793",
    "train1794",
    "train1816",
    "train1817",
    "train1823",
    "train1825",
    "train1841",
    "train1842",
    "train1846",
    "train1847",
    "train1848",
    "train1850",
    "train1851",
    "train1854",
    "train1882",
    "train1888",
    "train1889",
    "train1903",
    "train1904",
    "train1910",
    "train1919",
    "train1947",
    "train1948",
    "train1954",
    "train1966",
    "train1970",
    "train1971",
    "train1983",
    "train1990",
    "train1994",
    "train1997",
    "train1999",
    "train2001",
    "train2028",
    "train2031",
    "train2032",
    "train2034",
    "train2044",
    "train2046",
    "train2058",
    "train2065",
    "train2076",
    "train2080",
    "train2085",
    "train2086",
    "train2103",
    "train2106",
    "train2120",
    "train2141",
    "train2142",
    "train2150",
    "train2157",
    "train2158",
    "train2164",
    "train2196",
    "train2197",
    "train2198",
    "train2199",
    "train2203",
    "train2207",
    "train2212",
    "train2215",
    "train2219",
    "train2220",
    "train2232",
    "train2234",
    "train2237",
    "train2244",
    "train2246",
    "train2253",
    "train2254",
    "train2258",
    "train2267",
    "train2281",
    "train2304",
    "train2305",
    "train2307",
    "train2308",
    "train2309",
    "train2310",
    "train2311",
    "train2318",
    "train2321",
    "train2336",
    "train2349",
    "train2350",
    "train2362",
    "train2371",
    "train2376",
    "train2388",
    "train2390",
    "train2395",
    "train2397",
    "train2402",
    "train2414",
    "train2415",
    "train2417",
    "train2426",
    "train2428",
    "train2429",
    "train2448",
    "train2454",
    "train2466",
    "train2467",
    "train2486",
    "train2487",
    "train2492",
    "train2497",
    "train2498",
    "train2499",
    "train2514",
    "train2521",
    "train2537",
    "train2538",
    "train2539",
    "train2556",
    "train2561",
    "train2562",
    "train2563",
    "train2573",
    "train2577",
    "train2580",
    "train2583",
    "train2584",
    "train2602",
    "train2613",
    "train2614",
    "train2618",
    "train2620",
    "train2633",
    "train2639",
    "train2641",
    "train2651",
    "train2653",
    "train2661",
    "train2662",
    "train2664",
    "train2677",
    "train2711",
    "train2712",
    "train2713",
    "train2718",
    "train2719",
    "train2720",
    "train2726",
    "train2728",
    "train2729",
    "train2730",
    "train2733",
    "train2740",
    "train2741",
    "train2745",
    "train2747",
    "train2748",
    "train2752",
    "train2753",
    "train2755",
    "train2772",
    "train2773",
    "train2775",
    "train2777",
    "train2820",
    "train2822",
    "train2825",
    "train2827",
    "train2829",
    "train2833",
    "train2835",
    "train2840",
    "train2845",
    "train2856",
    "train2857",
    "train2858",
    "train2863",
    "train2864",
    "train2867",
    "train2868",
    "train2869",
    "train2870",
    "train2871",
    "train2889",
    "train2899",
    "train2901",
    "train2902",
    "train2903",
    "train2926",
    "train2927",
    "train2930",
    "train2931",
    "train2932",
    "train2933",
    "train2946",
    "train2951",
    "train2960",
    "train2962",
    "train2972",
    "train2973",
    "train2974",
    "train2981",
    "train2983",
    "train2984",
    "train2992",
    "train3004",
    "train3005",
    "train3006",
    "train3013",
    "train3014",
    "train3021",
    "train3029",
    "train3034",
    "train3045",
    "train3046",
    "train3049",
    "train3053",
    "train3055",
    "train3073",
    "train3080",
    "train3090",
    "train3092",
    "train3095",
    "train3109",
    "train3110",
    "train3111",
    "train3113",
    "train3118",
    "train3120",
    "train3121",
    "train3123",
    "train3128",
    "train3129",
    "train3140",
    "train3142",
    "train3143",
    "train3158",
    "train3160",
    "train3162",
    "train3164",
    "train3165",
    "train3166",
    "train3175",
    "train3192",
    "train3193",
    "train3195",
    "train3205",
    "train3218",
    "train3224",
    "train3240",
    "train3241",
    "train3279",
    "train3281",
    "train3282",
    "train3284",
    "train3292",
    "train3294",
    "train3312",
    "train3318",
    "train3326",
    "train3338",
    "train3341",
    "train3353",
    "train3354",
    "train3360",
    "train3385",
    "train3387",
    "train3403",
    "train3404",
    "train3407",
    "train3409",
    "train3413",
    "train3414",
    "train3415",
    "train3424",
    "train3426",
    "train3442",
    "train3443",
    "train3444",
    "train3449",
    "train3450",
    "train3451",
    "train3463",
    "train3466",
    "train3467",
    "train3482",
    "train3514",
    "train3530",
    "train3531",
    "train3576",
    "train3577",
    "train3583",
    "train3585",
    "train3587",
    "train3609",
    "train3617",
    "train3618",
    "train3621",
    "train3627",
    "train3629",
    "train3630",
    "train3631",
    "train3635",
    "train3636",
    "train3649",
    "train3689",
    "train3694",
    "train3695",
    "train3696",
    "train3697",
    "train3699",
    "train3700",
    "train3702",
    "train3709",
    "train3742",
    "train3743",
    "train3754",
    "train3755",
    "train3761",
    "train3769",
    "train3770",
    "train3771",
    "train3773",
    "train3775",
    "train3776",
    "train3777",
    "train3797",
    "train3807",
    "train3811",
    "train3813",
    "train3814",
    "train3824",
    "train3833",
    "train3846",
    "train3848",
    "train3876",
    "train3877",
    "train3878",
    "train3889",
    "train3890",
    "train3893",
    "train3894",
    "train3914",
    "train3915",
    "train3919",
    "train3928",
    "train3929",
    "train3930",
    "train3931",
    "train3933",
    "train3935",
    "train3936",
    "train3948",
    "train3958",
    "train3959",
    "train3961",
    "train3967",
    "train3969",
    "train4005",
    "train4006",
    "train4017",
    "train4027",
    "train4031",
    "train4043",
    "train4044",
    "train4046",
    "train4047",
    "train4048",
    "train4049",
    "train4051",
    "train4059",
    "train4064",
    "train4079",
    "train4080",
    "train4081",
    "train4084",
    "train4085",
    "train4106",
    "train4110",
    "train4124",
    "train4125",
    "train4126",
    "train4132",
    "train4133",
    "train4139",
    "train4140",
    "train4141",
    "train4148",
    "train4152",
    "train4154",
    "train4161",
    "train4169",
    "train4171",
    "train4172",
    "train4173",
    "train4186",
    "train4187",
    "train4212",
    "train4214",
    "train4239",
    "train4241",
    "train4250",
    "train4251",
    "train4259",
    "train4263",
    "train4266",
    "train4286",
    "train4288",
    "train4290",
    "train4294",
    "train4306",
    "train4307",
    "train4317",
    "train4318",
    "train4321",
    "train4354",
    "train4362",
    "train4380",
    "train4383",
    "train4385",
    "train4393",
    "train4394",
    "train4404",
    "train4415",
    "train4432",
    "train4445",
    "train4450",
    "train4455",
    "train4457",
    "train4462",
    "train4464",
    "train4470",
    "train4474",
    "train4475",
    "train4479",
    "train4480",
    "train4489",
    "train4497",
    "train4504",
    "train4515",
    "train4534",
    "train4536",
    "train4541",
    "train4543",
    "train4548",
    "train4554",
    "train4555",
    "train4591",
    "train4592",
    "train4604",
    "train4607",
    "train4608",
    "train4609",
    "train4618",
    "train4634",
    "train4637",
    "train4639",
    "train4643",
    "train4644",
    "train4653",
    "train4654",
    "train4686",
    "train4688",
    "train4690",
    "train4692",
    "train4693",
    "train4698",
    "train4701",
    "train4727",
    "train4737",
    "train4741",
    "train4742",
    "train4747",
    "train4748",
    "train4760",
    "train4762",
    "train4763",
    "train4764",
    "train4783",
    "train4790",
    "train4791",
    "train4794",
    "train4833",
    "train4834",
    "train4849",
    "train4850",
    "train4856",
    "train4864",
    "train4870",
    "train4877",
    "train4881",
    "train4882",
    "train4901",
    "train4902",
    "train4904",
    "train4909",
    "train4924",
    "train4936",
    "train4949",
    "train4970",
    "train4982",
    "train4990",
    "train4999",
    "train5000",
    "train5003",
    "train5006",
    "train5014",
    "train5021",
    "train5022",
    "train5023",
    "train5040",
    "train5044",
    "train5054",
    "train5056",
    "train5057",
    "train5060",
    "train5061",
    "train5073",
    "train5076",
    "train5077",
    "train5078",
    "train5080",
    "train5081",
    "train5090",
    "train5092",
    "train5107",
    "train5108",
    "train5139",
    "train5140",
    "train5141",
    "train5143",
    "train5152",
    "train5153",
    "train5162",
    "train5163",
    "train5178",
    "train5181",
    "train5182",
    "train5187",
    "train5206",
    "train5218",
    "train5219",
    "train5231",
    "train5246",
    "train5255",
    "train5256",
    "train5272",
    "train5275",
    "train5279",
    "train5283",
    "train5284",
    "train5285",
    "train5291",
    "train5292",
    "train5293",
    "train5303",
    "train5305",
    "train5309",
    "train5310",
    "train5320",
    "train5356",
    "train5372",
    "train5388",
    "train5389",
    "train5393",
    "train5398",
    "train5399",
    "train5400",
    "train5407",
    "train5408",
    "train5411",
    "train5416",
    "train5423",
    "train5438",
    "train5443",
    "train5444",
    "train5460",
    "train5470",
    "train5488",
    "train5494",
    "train5497",
    "train5498",
    "train5499",
    "train5500",
    "train5517",
    "train5518",
    "train5520",
    "train5525",
    "train5526",
    "train5534",
    "train5539",
    "train5554",
    "train5556",
    "train5557",
    "train5566",
    "train5589",
    "train5621",
    "train5623",
    "train5633",
    "train5636",
    "train5640",
    "train5645",
    "train5649",
    "train5656",
    "train5672",
    "train5674",
    "train5675",
    "train5677",
    "train5678",
    "train5691",
    "train5699",
    "train5707",
    "train5709",
    "train5710",
    "train5735",
    "train5752",
    "train5753",
    "train5754",
    "train5755",
    "train5761",
    "train5806",
    "train5807",
    "train5815",
    "train5822",
    "train5847",
    "train5860",
    "train5861",
    "train5868",
    "train5878",
    "train5885",
    "train5887",
    "train5896",
    "train5897",
    "train5898",
    "train5934",
    "train5938",
    "train5940",
    "train5950",
    "train5956",
    "train5960",
    "train5961",
    "train5981",
    "train5983",
    "train5986",
    "train5987",
    "train5992",
    "train6001",
    "train6010",
    "train6011",
    "train6026",
    "train6028",
    "train6040",
    "train6045",
    "train6048",
    "train6049",
    "train6055",
    "train6060",
    "train6068",
    "train6089",
    "train6105",
    "train6106",
    "train6109",
    "train6110",
    "train6112",
    "train6113",
    "train6118",
    "train6119",
    "train6121",
    "train6123",
    "train6125",
    "train6159",
    "train6161",
    "train6167",
    "train6168",
    "train6170",
    "train6173",
    "train6180",
    "train6181",
    "train6182",
    "train6191",
    "train6194",
    "train6216",
    "train6217",
    "train6219",
    "train6225",
    "train6228",
    "train6229",
    "train6230",
    "train6231",
    "train6236",
    "train6263",
    "train6269",
    "train6270",
    "train6276",
    "train6289",
    "train6292",
    "train6302",
    "train6307",
    "train6308",
    "train6311",
    "train6318",
    "train6324",
    "train6331",
    "train6332",
    "train6334",
    "train6339",
    "train6346",
    "train6347",
    "train6355",
    "train6364",
    "train6365",
    "train6392",
    "train6399",
    "train6407",
    "train6408",
    "train6410",
    "train6420",
    "train6421",
    "train6438",
    "train6442",
    "train6443",
    "train6448",
    "train6458",
    "train6463",
    "train6476",
    "train6500",
    "train6503",
    "train6506",
    "train6514",
    "train6515",
    "train6519",
    "train6528",
    "train6529",
    "train6541",
    "train6549",
    "train6553",
    "train6556",
    "train6557",
    "train6562",
    "train6576",
    "train6577",
    "train6578",
    "train6579",
    "train6584",
    "train6615",
    "train6616",
    "train6618",
    "train6619",
    "train6626",
    "train6635",
    "train6644",
    "train6650",
    "train6651",
    "train6652",
    "train6653",
    "train6655",
    "train6679",
    "train6680",
    "train6685",
    "train6691",
    "train6694",
    "train6695",
    "train6734",
    "train6744",
    "train6752",
    "train6753",
    "train6762",
    "train6770",
    "train6783",
    "train6788",
    "train6794",
    "train6807",
    "train6814",
    "train6815",
    "train6824",
    "train6829",
    "train6831",
    "train6840",
    "train6841",
    "train6844",
    "train6845",
    "train6851",
    "train6855",
    "train6859",
    "train6862",
    "train6868",
    "train6869",
    "train6871",
    "train6872",
    "train6876",
    "train6878",
    "train6888",
    "train6889",
    "train6890",
    "train6891",
    "train6908",
    "train6909",
    "train6922",
    "train6924",
    "train6926",
    "train6927",
    "train6933",
    "train6945",
    "train6946",
    "train6947",
    "train6949",
    "train6951",
    "train6966",
    "train6971",
    "train6974",
    "train6976",
    "train6977",
    "train6984",
    "train6985",
    "train6986",
    "train6988",
    "train7027",
    "train7034",
    "train7041",
    "train7044",
    "train7065",
    "train7066",
    "train7084",
    "train7086",
    "train7108",
    "train7113",
    "train7120",
    "train7121",
    "train7134",
    "train7136",
    "train7137",
    "train7152",
    "train7153",
    "train7159",
    "train7164",
    "train7166",
    "train7170",
    "train7176",
    "train7177",
    "train7195",
    "train7201",
    "train7202",
    "train7203",
    "train7225",
    "train7226",
    "train7230",
    "train7231",
    "train7233",
    "train7235",
    "train7238",
    "train7242",
    "train7248",
    "train7268",
    "train7269",
    "train7273",
    "train7285",
    "train7293",
    "train7300",
    "train7304",
    "train7310",
    "train7325",
    "train7326",
    "train7331",
    "train7332",
    "train7334",
    "train7335",
    "train7336",
    "train7337",
    "train7342",
    "train7361",
    "train7362",
    "train7369",
    "train7376",
    "train7384",
    "train7401",
    "train7402",
    "train7424",
    "train7425",
    "train7432",
    "train7433",
    "train7434",
    "train7447",
    "train7451",
    "train7453",
    "train7457",
    "train7460",
    "train7465",
    "train7466",
    "train7467",
    "train7470",
    "train7478",
    "train7497",
    "train7498",
    "train7499",
    "train7531",
    "train7534",
    "train7535",
    "train7536",
    "train7546",
    "train7550",
    "train7562",
    "train7577",
    "train7578",
    "train7586",
    "train7588",
    "train7594",
    "train7598",
    "train7604",
    "train7607",
    "train7608",
    "train7609",
    "train7623",
    "train7653",
    "train7654",
    "train7656",
    "train7657",
    "train7658",
    "train7660",
    "train7665",
    "train7666",
    "train7669",
    "train7670",
    "train7674",
    "train7692",
    "train7706",
    "train7717",
    "train7719",
    "train7728",
    "train7730",
    "train7731",
    "train7738",
    "train7739",
    "train7740",
    "train7753",
    "train7762",
    "train7763",
    "train7776",
    "train7778",
    "train7781",
    "train7782",
    "train7783",
    "train7786",
    "train7789",
    "train7792",
    "train7793",
    "train7800",
    "train7803",
    "train7804",
    "train7805",
    "train7808",
    "train7815",
    "train7816",
    "train7818",
    "train7823",
    "train7825",
    "train7827",
    "train7828",
    "train7856",
    "train7865",
    "train7866",
    "train7876",
    "train7880",
    "train7882",
    "train7884",
    "train7885",
    "train7888",
    "train7889",
    "train7908",
    "train7909",
    "train7912",
    "train7913",
    "train7927",
    "train7946",
    "train7948",
    "train7949",
    "train7954",
    "train7955",
    "train7963",
    "train7972",
    "train7975",
    "train7976",
    "train7977",
    "train7978",
    "train8002",
    "train8018",
    "train8021",
    "train8023",
    "train8034",
    "train8036",
    "train8046",
    "train8047",
    "train8061",
    "train8062",
    "train8063",
    "train8064",
    "train8071",
    "train8080",
    "train8081",
    "train8106",
    "train8107",
    "train8108",
    "train8111",
    "train8113",
    "train8115",
    "train8127",
    "train8128",
    "train8133",
    "train8136",
    "train8142",
    "train8147",
    "train8149",
    "train8150",
    "train8153",
    "train8159",
    "train8171",
    "train8176",
    "train8183",
    "train8184",
    "train8188",
    "train8190",
    "train8237",
    "train8238",
    "train8239",
    "train8240",
    "train8247",
    "train8257",
    "train8258",
    "train8273",
    "train8274",
    "train8291",
    "train8292",
    "train8297",
    "train8300",
    "train8303",
    "train8314",
    "train8350",
    "train8351",
    "train8357",
    "train8358",
    "train8386",
    "train8390",
    "train8395",
    "train8399",
    "train8400",
    "train8402",
    "train8405",
    "train8408",
    "train8409",
    "train8426",
    "train8449",
    "train8450",
    "train8451",
    "train8472",
    "train8475",
    "train8477",
    "train8480",
    "train8483",
    "train8484",
    "train8492",
    "train8496",
    "train8511",
    "train8513",
    "train8518",
    "train8533",
    "train8546",
    "train8569",
    "train8574",
    "train8575",
    "train8579",
    "train8587",
    "train8588",
    "train8602",
    "train8613",
    "train8625",
    "train8634",
    "train8635",
    "train8636",
    "train8640",
    "train8641",
    "train8643",
    "train8664",
    "train8678",
    "train8679",
    "train8689",
    "train8690",
    "train8692",
    "train8694",
    "train8697",
    "train8698",
    "train8713",
    "train8727",
    "train8735",
    "train8737",
    "train8740",
    "train8755",
    "train8774",
    "train8775",
    "train8776",
    "train8779",
    "train8780",
    "train8799",
    "train8800",
    "train8806",
    "train8807",
    "train8809",
    "train8813",
    "train8815",
    "train8829",
    "train8839",
    "train8848",
    "train8849",
    "train8854",
    "train8855",
    "train8856",
    "train8858",
    "train8870",
    "train8885",
    "train8892",
    "train8902",
    "train8904",
    "train8923",
    "train8924",
    "train8932",
    "train8941",
    "train8944",
    "train8945",
    "train8950",
    "train8951",
    "train8952",
    "train8954",
    "train8955",
    "train8959",
    "train8962",
    "train8963",
    "train8983",
    "train9007",
    "train9009",
    "train9010",
    "train9037",
    "train9046",
    "train9053",
    "train9054",
    "train9058",
    "train9065",
    "train9066",
    "train9071",
    "train9087",
    "train9091",
    "train9093",
    "train9094",
    "train9099",
    "train9100",
    "train9101",
    "train9103",
    "train9104",
    "train9105",
    "train9114",
    "train9135",
    "train9136",
    "train9156",
    "train9162",
    "train9164",
    "train9165",
    "train9173",
    "train9211",
    "train9216",
    "train9217",
    "train9237",
    "train9251",
    "train9260",
    "train9261",
    "train9263",
    "train9274",
    "train9277",
    "train9298",
    "train9333",
    "train9334",
    "train9349",
    "train9357",
    "train9371",
    "train9372",
    "train9379",
    "train9380",
    "train9384",
    "train9388",
    "train9400",
    "train9401",
    "train9412",
    "train9414",
    "train9416",
    "train9423",
    "train9426",
    "train9440",
    "train9443",
    "train9444",
    "train9449",
    "train9451",
    "train9452",
    "train9455",
    "train9459",
    "train9460",
    "train9464",
    "train9469",
    "train9470",
    "train9473",
    "train9488",
    "train9499",
    "train9526",
    "train9527",
    "train9530",
    "train9532",
    "train9533",
    "train9561",
    "train9567",
    "train9569",
    "train9570",
    "train9572",
    "train9573",
    "train9583",
    "train9587",
    "train9599",
    "train9600",
    "train9602",
    "train9608",
    "train9610",
    "train9611",
    "train9619",
    "train9624",
    "train9634",
    "train9636",
    "train9643",
    "train9645",
    "train9648",
    "train9653",
    "train9659",
    "train9675",
    "train9676",
    "train9689",
    "train9690",
    "train9692",
    "train9703",
    "train9704",
    "train9709",
    "train9710",
    "train9736",
    "train9752",
    "train9753",
    "train9754",
    "train9784",
    "train9790",
    "train9792",
    "train9822",
    "train9825",
    "train9826",
    "train9830",
    "train9831",
    "train9853",
    "train9859",
    "train9860",
    "train9866",
    "train9868",
    "train9872",
    "train9876",
    "train9886",
    "train9887",
    "train9889",
    "train9892",
    "train9896",
    "train9900",
    "train9905",
    "train9907",
    "train9918",
    "train9920",
    "train9921",
    "train9928",
    "train9938",
    "train9939",
    "train9944",
    "train9948",
    "train9971",
    "train9975",
    "train9989",
    "train9995",
    "train10000",
    "train10001",
    "train10003",
    "train10008",
    "train10009",
    "train10076",
    "train10082",
    "train10083",
    "train10087",
    "train10089",
    "train10091",
    "train10093",
    "train10094",
    "train10108",
    "train10116",
    "train10122",
    "train10136",
    "train10137",
    "train10147",
    "train10148",
    "train10154",
    "train10155",
    "train10156",
    "train10169",
    "train10171",
    "train10172",
    "train10178",
    "train10181",
    "train10183",
    "train10185",
    "train10193",
    "train10198",
    "train10202",
    "train10208",
    "train10209",
    "train10210",
    "train10227",
    "train10228",
    "train10233",
    "train10261",
    "train10262",
    "train10264",
    "train10265",
    "train10273",
    "train10274",
    "train10275",
    "train10276",
    "train10278",
    "train10282",
    "train10283",
    "train10289",
    "train10292",
    "train10293",
    "train10294",
    "train10299",
    "train10300",
    "train10319",
    "train10320",
    "train10326",
    "train10329",
    "train10330",
    "train10333",
    "train10342",
    "train10345",
    "train10349",
    "train10350",
    "train10351",
    "train10366",
    "train10367",
    "train10372",
    "train10373",
    "train10374",
    "train10383",
    "train10384",
    "train10388",
    "train10390",
    "train10392",
    "train10395",
    "train10400",
    "train10401",
    "train10403",
    "train10404",
    "train10410",
    "train10416",
    "train10420",
    "train10422",
    "train10424",
    "train10434",
    "train10435",
    "train10440",
    "train10441",
    "train10445",
    "train10450",
    "train10462",
    "train10463",
    "train10466",
    "train10467",
    "train10485",
    "train10489",
    "train10490",
    "train10491",
    "train10494",
    "train10496",
    "train10503",
    "train10505",
    "train10516",
    "train10549",
    "train10550",
    "train10568",
    "train10574",
    "train10576",
    "train10595",
    "train10596",
    "train10600",
    "train10619",
    "train10620",
    "train10624",
    "train10625",
    "train10637",
    "train10643",
    "train10679",
    "train10686",
    "train10688",
    "train10695",
    "train10697",
    "train10728",
    "train10733",
    "train10734",
    "train10736",
    "train10748",
    "train10749",
    "train10751",
    "train10772",
    "train10774",
    "train10782",
    "train10807",
    "train10810",
    "train10825",
    "train10833",
    "train10836",
    "train10839",
    "train10840",
    "train10845",
    "train10854",
    "train10855",
    "train10860",
    "train10862",
    "train10864",
    "train10890",
    "train10893",
    "train10899",
    "train10932",
    "train10951",
    "train10967",
    "train10984",
    "train10985",
    "train10990",
    "train10991",
    "train10993",
    "train10995",
    "train10996",
    "train10998",
    "train11006",
    "train11011",
    "train11019",
    "train11023",
    "train11024",
    "train11025",
    "train11030",
    "train11032",
    "train11045",
    "train11055",
    "train11060",
    "train11062",
    "train11063",
    "train11072",
    "train11100",
    "train11127",
    "train11128",
    "train11129",
    "train11140",
    "train11148",
    "train11173",
    "train11175",
    "train11178",
    "train11193",
    "train11228",
    "train11229",
    "train11232",
    "train11235",
    "train11244",
    "train11275",
    "train11284",
    "train11285",
    "train11290",
    "train11293",
    "train11294",
    "train11295",
    "train11296",
    "train11297",
    "train11298",
    "train11299",
    "train11327",
    "train11331",
    "train11337",
    "train11354",
    "train11364",
    "train11376",
    "train11379",
    "train11391",
    "train11417",
    "train11418",
    "train11426",
    "train11427",
    "train11428",
    "train11478",
    "train11487",
    "train11490",
    "train11491",
    "train11492",
    "train11511",
    "train11512",
    "train11517",
    "train11519",
    "train11520",
    "train11527",
    "train11536",
    "train11539",
    "train11548",
    "train11556",
    "train11575",
    "train11600",
    "train11603",
    "train11604",
    "train11605",
    "train11609",
    "train11611",
    "train11613",
    "train11615",
    "train11643",
    "train11650",
    "train11659",
    "train11665",
    "train11675",
    "train11676",
    "train11679",
    "train11711",
    "train11712",
    "train11718",
    "train11719",
    "train11720",
    "train11732",
    "train11748",
    "train11769",
    "train11782",
    "train11783",
    "train11786",
    "train11791",
    "train11801",
    "train11803",
    "train11813",
    "train11822",
    "train11835",
    "train11839",
    "train11840",
    "train11851",
    "train11852",
    "train11866",
    "train11868",
    "train11870",
    "train11871",
    "train11872",
    "train11879",
    "train11903",
    "train11904",
    "train11906",
    "train11910",
    "train11929",
    "train11933",
    "train11943",
    "train11945",
    "train11946",
    "train11956",
    "train11958",
    "train11959",
    "train11964",
    "train11969",
    "train11981",
    "train11989",
    "train12004",
    "train12044",
    "train12048",
    "train12049",
    "train12066",
    "train12069",
    "train12092",
    "train12093",
    "train12094",
    "train12099",
    "train12101",
    "train12102",
    "train12104",
    "train12121",
    "train12130",
    "train12137",
    "train12138",
    "train12139",
    "train12165",
    "train12168",
    "train12169",
    "train12170",
    "train12180",
    "train12181",
    "train12182",
    "train12189",
    "train12204",
    "train12226",
    "train12241",
    "train12258",
    "train12294",
    "train12297",
    "train12298",
    "train12300",
    "train12313",
    "train12324",
    "train12327",
    "train12328",
    "train12329",
    "train12330",
    "train12331",
    "train12333",
    "train12334",
    "train12342",
    "train12343",
    "train12348",
    "train12373",
    "train12374",
    "train12375",
    "train12377",
    "train12380",
    "train12387",
    "train12391",
    "train12394",
    "train12401",
    "neg_006467e6e5b4b68e",
    "neg_006ba24c315cc155",
    "neg_00a6e28e6b0f8c47",
    "neg_00ded655948d5fe3",
    "neg_016794ce831a0291",
    "neg_0182642363344e95",
    "neg_0196f4a13598469e",
    "neg_019962b0c82cfcb2",
    "neg_01b4ed78d8d463ac",
    "neg_0206122c18fb539e",
    "neg_0216ffd7ae8a678b",
    "neg_0233e231575605fb",
    "neg_02c4e7d79261479a",
    "neg_032671eb57572d10",
    "neg_03752164fd749b96",
    "neg_03af0f25d46964ec",
    "neg_03c7e3b8cc42cf87",
    "neg_040185722dc7cac4",
    "neg_047a5bcb4fa9ddae",
    "neg_04dd6f8345b7e995",
    "neg_052e47fb330a440a",
    "neg_0534caa9d718573c",
    "neg_053ab678b409da1a",
    "neg_053d73f1b80ecfda",
    "neg_0588f9c88a2f7af7",
    "neg_058dee0e9f5afe29",
    "neg_069d79e51ee1a011",
    "neg_073863262ebdb99a",
    "neg_075510130610b682",
    "neg_07ba81a4bd49c277",
    "neg_07efd4e6c0175a53",
    "neg_082d049c1ad9a338",
    "neg_082efa42fa9534ac",
    "neg_084d01d1782d116f",
    "neg_08d135db8d88cdcf",
    "neg_092002f139655621",
    "neg_092f3ad0345f18f7",
    "neg_09950b1000fe8070",
    "neg_09e6e0c9ce118dd7",
    "neg_0a07dc0b4d373e4a",
    "neg_0a23ebe4b2b886e6",
    "neg_0ab2f8fb56b8d444",
    "neg_0adb8f377f17586a",
    "neg_0b4308e1e541555c",
    "neg_0b79e0ec79c33ef5",
    "neg_0b868152e5701885",
    "neg_0b86f1eb6dbe1afe",
    "neg_0b96eb2f66d44c67",
    "neg_0bd3be4327e50338",
    "neg_0c0218fddc2e4e73",
    "neg_0c9b49c589befd0a",
    "neg_0dbed496ae47da32",
    "neg_0e5d44a0176e2cb3",
    "neg_0e8d32149e630abc",
    "neg_0eb16feed31f29af",
    "neg_0ebf3e6559a995f9",
    "neg_0f5ea743233e5ab9",
    "neg_0fb73ec4cec575c7",
    "neg_0fdb6812a2d29b59",
    "neg_0fec21d6ec72ef03",
    "neg_1011152a94d6959d",
    "neg_10417ea9da459036",
    "neg_10f549209a1bb5cf",
    "neg_1148cee1a8de4b07",
    "neg_1193ff25d6316c7f",
    "neg_11c171abdb15323b",
    "neg_120fbc2d08887e5f",
    "neg_12131761edca8cef",
    "neg_12784d670432dad7",
    "neg_12b7385127df9a18",
    "neg_13476f7d133670f3",
    "neg_1365d94f3dc62431",
    "neg_1373a69ed2b0ccd9",
    "neg_13afaa58cc04ab31",
    "neg_13d0f7c4f7f2cc36",
    "neg_145abf5104b2daac",
    "neg_148225005b038446",
    "neg_14cd44b595c8408b",
    "neg_14e5b8b1ff4fe5a1",
    "neg_152f203387e39547",
    "neg_156b3fe1d0ef4f25",
    "neg_15c920c79778c07c",
    "neg_16957e499406d811",
    "neg_16a119eef88c7416",
    "neg_16a5e3d613f355df",
    "neg_16d10028d9988a7e",
    "neg_16ddfe813ea2f158",
    "neg_16e15305011a146b",
    "neg_1709e43acff76b3d",
    "neg_171f6ac8de91d6d7",
    "neg_17303cebdb318a1f",
    "neg_176b0f35dd39c537",
    "neg_1793f6333acdb3c0",
    "neg_180b597c73a6e3cb",
    "neg_183b6ce265960372",
    "neg_185303da40e25f5c",
    "neg_18575141e3f8b7ff",
    "neg_18d210cdc329d363",
    "neg_19381c37aaa05f0f",
    "neg_1aa05c747f4cfad0",
    "neg_1aaf23e8e1c54920",
    "neg_1ab76b2ddcb87be4",
    "neg_1bcb0e5be62e0062",
    "neg_1bdd75eecf7ebe04",
    "neg_1c03cd7d1fd154d8",
    "neg_1c4740e932ae0419",
    "neg_1c893841044336b3",
    "neg_1cdd94bf6543c51f",
    "neg_1cf301f7de69fc72",
    "neg_1d2f8e2cccd8f65a",
    "neg_1f47cb85a351bebc",
    "neg_1f5fc6ec74fd8a1f",
    "neg_2058df8afb3795bc",
    "neg_2092643b486acf94",
    "neg_20e0f3ed14b3ffcc",
    "neg_20fba20a7bf298c1",
    "neg_21152a393eb3dd06",
    "neg_218aba84545d462b",
    "neg_219d7388716c6ec8",
    "neg_22219ce5a29629ed",
    "neg_222907f58f069a6b",
    "neg_2238d2dd6ff8f706",
    "neg_224ada1c786c9701",
    "neg_22bca1e8a4de3ea7",
    "neg_22d3bfe6747b4a31",
    "neg_22d5b61cbcf52394",
    "neg_233fc5f946908fdd",
    "neg_23795de9f9d1c1c6",
    "neg_23b1846c32b588e9",
    "neg_243841a2fb2e998e",
    "neg_244cc81685eada46",
    "neg_255508883bb9ba2b",
    "neg_258f91a98b5faad0",
    "neg_2592a47021c3dd83",
    "neg_264f32dfc11dc433",
    "neg_26b2755e5e3c52b5",
    "neg_26d7a3f150bff4d5",
    "neg_27108bcf52e39b4f",
    "neg_27112a0b95ffd900",
    "neg_27271020681de9eb",
    "neg_2753a8b05faa5147",
    "neg_2781b3c60911139f",
    "neg_279602d1825ffbaf",
    "neg_27d94d63435a6ad1",
    "neg_27da80e1f9d90726",
    "neg_284ce7e5f9f31af4",
    "neg_2896eafeb51772bd",
    "neg_291376a9f52bb37f",
    "neg_294b80815ba7afe1",
    "neg_2b3140d840e271a9",
    "neg_2b4ee1e65ed8246e",
    "neg_2b6a635e61b64ffc",
    "neg_2c062d090d328778",
    "neg_2c30f11f8692fe0a",
    "neg_2cb7c9578c6ad3aa",
    "neg_2cba5441eb7bdcbd",
    "neg_2ce1251dcb30bf12",
    "neg_2d0e0e67eea50c01",
    "neg_2d57934538b9c56c",
    "neg_2d80693bbf7439b4",
    "neg_2da9185e4238c03e",
    "neg_2dd7c39b8c55cf01",
    "neg_2e59d4480d580f51",
    "neg_2e7a020b0ae2e15c",
    "neg_2ea69396a29411bb",
    "neg_2f22a5a389e33e1e",
    "neg_2f79def84a5659e4",
    "neg_2f8d72b2f97a2082",
    "neg_30afef82b9a61d61",
    "neg_3127263cfc1ab4e3",
    "neg_313f10ce8b32e46a",
    "neg_31847bdfdd8a5c24",
    "neg_31d8261de210533d",
    "neg_31e86e7e752f1870",
    "neg_322abb967d50d505",
    "neg_334247b231f5ce25",
    "neg_33474c3c0c0ca162",
    "neg_334861d24b737b7f",
    "neg_3372d5a65245c941",
    "neg_3381f73246bd2e6a",
    "neg_33e157f521e2937d",
    "neg_343f7c439684e555",
    "neg_34944d959ec5ee22",
    "neg_34e57ba141e157fd",
    "neg_34f0d7605bb45551",
    "neg_34fba977a943a120",
    "neg_35459637342577f8",
    "neg_357acf520770c1eb",
    "neg_35dbc3618d48e74d",
    "neg_3603bd6d8ba3c6e4",
    "neg_36a016b256bc355e",
    "neg_36de902b5668849e",
    "neg_36dfcc6b8071ccb2",
    "neg_370eb1e6494f4fd1",
    "neg_3798481899bcd2f0",
    "neg_37b711086f6ebbd7",
    "neg_37cace9b6506d2b6",
    "neg_37cf5fde614ad3a0",
    "neg_37d327031f875fd6",
    "neg_387e2260cf918a73",
    "neg_391bd7ae11debd42",
    "neg_39386b3c851e9991",
    "neg_39aada3649e2dfd8",
    "neg_39b7e89633317516",
    "neg_3a5fcb2ff0241fba",
    "neg_3a8f00ab6623393d",
    "neg_3aa26dd5456d49b1",
    "neg_3aa8084b86585dc3",
    "neg_3ab255e483626a5b",
    "neg_3b08bcadf1c72484",
    "neg_3b0ae8b997639f3e",
    "neg_3b1e62dc029e037c",
    "neg_3b25894a4d11e9f5",
    "neg_3bde7f3bb4310613",
    "neg_3c2f72af1f1772d9",
    "neg_3c6b3d11522330a8",
    "neg_3ca723222d01f8ae",
    "neg_3d2298ac003a11eb",
    "neg_3d6c6088d2c3eed7",
    "neg_3d7186074e81956b",
    "neg_3dd40b30097d3f3c",
    "neg_3df9e2ffda6eb161",
    "neg_3e072fdb85104816",
    "neg_3f78079237ac20f9",
    "neg_3f96367cc60eb413",
    "neg_3fbd037ae43ff27e",
    "neg_3fcc667dae6090cd",
    "neg_3fd4effd46fe12c0",
    "neg_4016d576ad9666a7",
    "neg_402402841466b227",
    "neg_403b1b7387b7513f",
    "neg_4140c9a44fbd5a29",
    "neg_41742129e0fb8a29",
    "neg_425286edda822db2",
    "neg_42ad34dde74225b6",
    "neg_42b23b90d5e77ce1",
    "neg_432c4d8e7b23f52e",
    "neg_440b7d741239bf05",
    "neg_4468afb48a01f9a9",
    "neg_44d0ea08892f7ab5",
    "neg_44e1b29fc7be86fd",
    "neg_4543c51aeee1f60f",
    "neg_4555976c0f156318",
    "neg_45c5bf43ac193962",
    "neg_45f3114e1fc718f4",
    "neg_460ecf44c9da7749",
    "neg_466fdf13cb24b64c",
    "neg_46adbd1787a14be1",
    "neg_46b5b7885b46bfc4",
    "neg_478342c85335cb4f",
    "neg_47a217416e1ce476",
    "neg_47b934f2ad98082c",
    "neg_47ef8af68125fd5f",
    "neg_480f9461d9c89eee",
    "neg_483284a26361428e",
    "neg_48483a1fbaed3b44",
    "neg_48b1c3e207e63ef8",
    "neg_48c6707771ccabc3",
    "neg_48f36859f3e280be",
    "neg_4933819f1ec01b4f",
    "neg_493d06357d12e77e",
    "neg_4a03b0d87d12991d",
    "neg_4a1d6fbebd1f015a",
    "neg_4a71b2dec65e4c56",
    "neg_4b20936675551afb",
    "neg_4b2a6aec4d4cf93b",
    "neg_4b78b35ce134a809",
    "neg_4b955f730f56d276",
    "neg_4baad2bfd7ced016",
    "neg_4bf0e1ba03e696e6",
    "neg_4d417b7850bb23fc",
    "neg_4d72786677788f46",
    "neg_4da2c032aceada66",
    "neg_4dbfbee9f328c815",
    "neg_4dc4c41d42a86c7f",
    "neg_4de1f8b0fcad48b7",
    "neg_4e097b6b21351bb1",
    "neg_4e6f4756d2514118",
    "neg_4e8790093dea5d1f",
    "neg_4ed5747a11115802",
    "neg_4ee361d175cbc7c2",
    "neg_4efc2fac6374745f",
    "neg_4f084886976ae346",
    "neg_4f3296da178a79f0",
    "neg_4f3c8ee03f7f7e49",
    "neg_4f651ca71c1d2dfd",
    "neg_4f6a7a1989fcd3e7",
    "neg_4f8646330fb4a767",
    "neg_4f989bdef4d865c0",
    "neg_4ff2d4bf3a6e34ad",
    "neg_504f1cdd4fa9d259",
    "neg_509a635a898a1e46",
    "neg_50a00b4914b28f60",
    "neg_50b5073b0055f1fd",
    "neg_511d9f5ce771833d",
    "neg_51593cb0343d0d79",
    "neg_5179fcfac9e26f9e",
    "neg_51fd98f90ccea95e",
    "neg_53fa038272670ffc",
    "neg_543a09bc410e689a",
    "neg_547058b212a96156",
    "neg_5479f6b5395e15bd",
    "neg_54cc6c0e77575553",
    "neg_5508c3715464a26d",
    "neg_55c73860c7c65c49",
    "neg_55f96e7c29daeb0a",
    "neg_5685068c0a04ae54",
    "neg_5699a8ff7a7463ad",
    "neg_56f704145fb26fa0",
    "neg_5799d4429bd6162e",
    "neg_579da6914397befe",
    "neg_580db1fb71a4b545",
    "neg_5824f00a3f7f670f",
    "neg_582d2d0553cad2fc",
    "neg_582db5594fbc0b41",
    "neg_585ea6bbf5804d2e",
    "neg_58d314071c7041d0",
    "neg_594e84fedd34961b",
    "neg_595d9d3550df8165",
    "neg_59b34d93f183d037",
    "neg_5a1aaf4fc71e9bc0",
    "neg_5a209bfbe270ad9a",
    "neg_5a55c5528ae81a92",
    "neg_5a5f0f9e54148f2d",
    "neg_5abcb9c92cc93d30",
    "neg_5af3b50176fe5d57",
    "neg_5b0503c55a244aad",
    "neg_5b0a5775bd7ef62d",
    "neg_5b3b03e4eaea1a5e",
    "neg_5ce873ab18524ad6",
    "neg_5d315a1d32683dcd",
    "neg_5d61bce292f36847",
    "neg_5dd5d6e8614612a2",
    "neg_5ea6639c2a60fad2",
    "neg_5eadd1b42f9e76ae",
    "neg_5f4483ce2a9bb669",
    "neg_5fa9c1688f2d8c2c",
    "neg_601ce8cf7d3fc426",
    "neg_60379e06646eeac1",
    "neg_603b4a4ab88504e9",
    "neg_609d3578e1fb8dce",
    "neg_60aadf222fb0c01b",
    "neg_60b1c4f402f0ccd0",
    "neg_6154303ee4f6520d",
    "neg_6202cae62c6f525c",
    "neg_620818f7b1118969",
    "neg_62132b569964f0a4",
    "neg_62223c3cc017724c",
    "neg_6243932716829b36",
    "neg_6252452c3b6c5f88",
    "neg_6292e2cbf9782ed8",
    "neg_62a0d7874fb24fe6",
    "neg_62fa242327a4a668",
    "neg_631dbbe5df26984f",
    "neg_632e4628d790b7e4",
    "neg_633bcaa99d18f890",
    "neg_6348a675793e98a0",
    "neg_635aec84553f84f5",
    "neg_6391030bf0f862e3",
    "neg_63e97739a1c55dec",
    "neg_64722f71c57b94b9",
    "neg_649be75a8d4b2420",
    "neg_64a32cb927a50de1",
    "neg_64b6cb1cad33ce38",
    "neg_64d89bacca158b0a",
    "neg_6510db8f3255a9f7",
    "neg_65453d7eac20803a",
    "neg_654e5e8ebe8d8606",
    "neg_65ab947cfe58f655",
    "neg_65b8e84a91fec3fc",
    "neg_65f1428cf66cbed3",
    "neg_65fc4b56c995fed0",
    "neg_66239826e0106b51",
    "neg_6681a4c8ffa8d2af",
    "neg_66894d708c91369a",
    "neg_66b5eb2fb4846906",
    "neg_66bd94ab22e5a14e",
    "neg_67789090299bd8e3",
    "neg_678b19dbcb490d0e",
    "neg_67c2cbdc2b223421",
    "neg_67c8bb16e919e519",
    "neg_67d8c1404b81d9bd",
    "neg_67f7a8af55cbcc37",
    "neg_6847e66332c54449",
    "neg_6857544e0cf5a8cc",
    "neg_68e746edcd822180",
    "neg_68ed8c2f80dc0e97",
    "neg_68fc109c634c29d0",
    "neg_693cd288351c34b6",
    "neg_696010f6c1c9bb42",
    "neg_6a249f939773f2a1",
    "neg_6a6755f5bdca262e",
    "neg_6aacc607213618ff",
    "neg_6ab8cb027e87d917",
    "neg_6abb77437c165180",
    "neg_6b3a75aa962a1418",
    "neg_6b46772a6ae18a2e",
    "neg_6b5374939e1b1652",
    "neg_6b7a4fd012423937",
    "neg_6b954d5bd9f16f42",
    "neg_6bb7e1beb8bf78e9",
    "neg_6be65482e49ce5cc",
    "neg_6bef0639997bda28",
    "neg_6c2240e88371905e",
    "neg_6c89722191ea14fe",
    "neg_6d45c01739645cfd",
    "neg_6d6b92226b0bce7c",
    "neg_6dd6b61503130abe",
    "neg_6e42ec88199aff9c",
    "neg_6e5ede9e2025fee1",
    "neg_6e78a31f60fea0d6",
    "neg_6e8132da6fd6eda3",
    "neg_6ee1526361418cfa",
    "neg_6f9cb2b42d0b6dba",
    "neg_6fad94fbb4ba48c4",
    "neg_7000664cc11af7b1",
    "neg_702a70b660c45339",
    "neg_70d631f6cc19a2b3",
    "neg_716bf6b34be248f6",
    "neg_71728071839f4574",
    "neg_71758d37513d72b1",
    "neg_71857d204b2cd47c",
    "neg_7247072603e31c50",
    "neg_72a591d5f7dcedd5",
    "neg_72b7537ecdbfddf0",
    "neg_735e0758ebf83db5",
    "neg_7380b430b5ede3ce",
    "neg_73f1aab9eedf8d69",
    "neg_74454b986aad3ca8",
    "neg_745308a0931ebe27",
    "neg_74c67fe60442a188",
    "neg_74e5e2b29c8ef349",
    "neg_75367dcf0f764d4d",
    "neg_761b0119111eb10f",
    "neg_764fb16d6b34955e",
    "neg_769295bba4edb29a",
    "neg_76c00177a38fb10e",
    "neg_76d457bb9b048004",
    "neg_778fcbfe8e9cff86",
    "neg_78052c5c02ee3097",
    "neg_785a7a4d479d2a81",
    "neg_789243ebded17180",
    "neg_78fa7089ac303501",
    "neg_79009580266d7c10",
    "neg_796c53cdbf350b7d",
    "neg_796c5f12bfed819e",
    "neg_7971b90a1c596ff3",
    "neg_7982238c5d3da4f0",
    "neg_7a4db1070ed9b20c",
    "neg_7a7d8909902dcf57",
    "neg_7ad0e2c9b867c329",
    "neg_7ad4b0637c110387",
    "neg_7aec9eb9614f17df",
    "neg_7b371dfa2a710c24",
    "neg_7b4163fe929d4e67",
    "neg_7b92276e6379ec7b",
    "neg_7bf0167ddf760aa0",
    "neg_7cd453a0f425a82f",
    "neg_7cd5eb915c3f7c85",
    "neg_7d1ebe0b41048c05",
    "neg_7d3121083da46aa7",
    "neg_7d316368a868190b",
    "neg_7e1c1f55d8ecbeaa",
    "neg_7e3e483ac196c4eb",
    "neg_7e6f6cf023322a86",
    "neg_7ea04f65e805cddd",
    "neg_7ebc1264e72e39c5",
    "neg_7ee81d7d7517c335",
    "neg_7ee856d9f1ab9e1d",
    "neg_7f5bdfc12cf2c498",
    "neg_7f68ac4e001d2017",
    "neg_7fc395fcd94402a9",
    "neg_7fe6d3859f788b48",
    "neg_800e09504333c615",
    "neg_800ea0900165de96",
    "neg_80421cc4b54c10ab",
    "neg_819002de5cc5a319",
    "neg_819e6e88c055a80f",
    "neg_81daf1cb84b3f9ce",
    "neg_81edb4a335bc88a9",
    "neg_8216a2e55cd38af8",
    "neg_8236fe331dd20fee",
    "neg_8249e3bc542e5654",
    "neg_82a80dbd45ea767b",
    "neg_832fa1bac3206132",
    "neg_833104c9f19f8bc7",
    "neg_83908617f6117201",
    "neg_83c0b6dafebc14b7",
    "neg_83f5c70a29a56d2d",
    "neg_8429ccb0230cabeb",
    "neg_8473183be2203b45",
    "neg_84a203bef2c5ddab",
    "neg_84a87a7b4accaea8",
    "neg_84bd6aee45bcbdea",
    "neg_84f71561858a842c",
    "neg_84ffcb62f913f2a3",
    "neg_85003e2ae141fa49",
    "neg_85ac28459e18ae2c",
    "neg_85d222c731890929",
    "neg_86491c2a5531ad84",
    "neg_868df6e1dd5db501",
    "neg_86aee1dc830fc0ec",
    "neg_86af7b612c1cbd0e",
    "neg_87463e00db8211d6",
    "neg_875991c35c01a2d4",
    "neg_8780bb28e8cb34b5",
    "neg_881ed8bda77a5f38",
    "neg_89de18175c00fcc8",
    "neg_89f42f048eb29655",
    "neg_8ad772c57949c4a0",
    "neg_8b06507e81d7d6ec",
    "neg_8b4aa7349018ed38",
    "neg_8b8f0a5dcd7619bd",
    "neg_8ba78e62b15b614a",
    "neg_8bbccc456b7fbd4c",
    "neg_8bcc3b3dab10d4c9",
    "neg_8c1001f6242e7239",
    "neg_8c8ab7e3dbd58b61",
    "neg_8cabb577e8be71bc",
    "neg_8ce22fd3e8079bfa",
    "neg_8cf9adfdbe8c8005",
    "neg_8d54dcca33197511",
    "neg_8db54daf3dc8d818",
    "neg_8e5addbcb60c7cf7",
    "neg_8e730efda26faea5",
    "neg_8eb6a7b2f7e06417",
    "neg_8f1ad81530586ac2",
    "neg_8f465cf68a064ad6",
    "neg_8facd896b054cd90",
    "neg_9041cd18aab756d8",
    "neg_91160c761f7fa922",
    "neg_915c78ce4d19f690",
    "neg_9184a51be39a5e82",
    "neg_918d4184605df892",
    "neg_91a957c48307a9bd",
    "neg_91e4436644afed50",
    "neg_922a2d5792f079a2",
    "neg_9241cc192a0437b7",
    "neg_925001435411ddff",
    "neg_926d311dbd529492",
    "neg_9307b20167fb01a9",
    "neg_932b81777cdbd4ad",
    "neg_935f8bec58df3e9a",
    "neg_938f76e96828972e",
    "neg_93b178cc3ec99ff3",
    "neg_93cfedb1120092ba",
    "neg_93eb2458ecf868a4",
    "neg_94b9056e1f05c016",
    "neg_94b9f74425cb893c",
    "neg_94f04609cc7f83fe",
    "neg_95221a66a7d71579",
    "neg_9534f1a97da2699d",
    "neg_957aebe76624a9d2",
    "neg_95a7ee986e7e7e19",
    "neg_95c94dad7a703bac",
    "neg_95efd41e16aefe3a",
    "neg_962f0e40f2e7dc70",
    "neg_97561c0403ce7252",
    "neg_9764fb97ed16e64f",
    "neg_97e82acf153899e4",
    "neg_989771602d6cb9cb",
    "neg_98d991e3202dc178",
    "neg_9904528156abb072",
    "neg_990fa86a6bd8437a",
    "neg_9941e065f920ac34",
    "neg_995cdfcb2de3ea71",
    "neg_9976589a0d2c5abf",
    "neg_99af107d90e9430f",
    "neg_99bfd0e193c8db57",
    "neg_99cbac2c318af141",
    "neg_9a3e7a0804ab3e10",
    "neg_9a5a9c97bab52aa3",
    "neg_9a69d203c9d90946",
    "neg_9a7ace7972e0af4e",
    "neg_9b14bc8e6390a0f5",
    "neg_9b766901cbc9dff8",
    "neg_9bbb1eb3276e3392",
    "neg_9bd64cd8fb2951d3",
    "neg_9be9ce1ad9511087",
    "neg_9beaa14eb0097f42",
    "neg_9bf2b39d70aaf0de",
    "neg_9c507ed792c1098b",
    "neg_9c7172600fcb2c3a",
    "neg_9cc25f245394a29d",
    "neg_9ce8f8ba64322bf2",
    "neg_9d7ecd8bf995ca1b",
    "neg_9d80f35d332f642a",
    "neg_9ddebb1fae7a2dce",
    "neg_9e103bdbeebacf94",
    "neg_9f036f8ae29791a4",
    "neg_9f0a905c0b2d2327",
    "neg_9f49a2c0577e3ebf",
    "neg_9f89a719b061e98f",
    "neg_9f8b5931dd71aa49",
    "neg_9fa520c179c2eb06",
    "neg_9fe35edcdad6c537",
    "neg_a07e2a4a497719e6",
    "neg_a0ed66998b29c6e2",
    "neg_a175c2e900418f85",
    "neg_a1906167f5becc8a",
    "neg_a1dfccb2ba03728c",
    "neg_a2308f9f35f7efa4",
    "neg_a279563213b3e1b9",
    "neg_a2f2ceee681780e4",
    "neg_a3050dc3a0b12c89",
    "neg_a365c32665840ab4",
    "neg_a3a5f40c4fcf0c97",
    "neg_a454744a777a7ac2",
    "neg_a456bfd3aeb70e67",
    "neg_a4a1b60fa117fa2e",
    "neg_a5396ce1ecf7227b",
    "neg_a5929e6c50ae8355",
    "neg_a59db725e7d8f2ad",
    "neg_a5c7deac8964e92d",
    "neg_a62584538a61124f",
    "neg_a62b4be46784fba2",
    "neg_a62bed1b81944d9a",
    "neg_a6648a0a03fdefb4",
    "neg_a722dda873879d03",
    "neg_a737df9fece0906c",
    "neg_a742572c77538568",
    "neg_a74ec4abf6279f0e",
    "neg_a77e6e05e82398de",
    "neg_a7d1121549cf27ea",
    "neg_a7e130ee739944aa",
    "neg_a8773e73b10d63f6",
    "neg_a8cc0ef13867b0cc",
    "neg_aa1cf9d3831907a3",
    "neg_aa6b46f7b216ecd7",
    "neg_aae74148845bef5d",
    "neg_aaefe29515f43d28",
    "neg_ab31d2df6d3311ac",
    "neg_abc815d3ab181651",
    "neg_ac13663d9a97e57a",
    "neg_ac61f4a0f3d3c8ed",
    "neg_ac7a839c638700f8",
    "neg_ad0d2d667705bbc6",
    "neg_ad5f70fedbf3fea2",
    "neg_ad7143ca3e4113c3",
    "neg_ad8a9862fbf53fa6",
    "neg_add105f33f6c5c87",
    "neg_ae05050318ab6249",
    "neg_ae2023b2929f9ea1",
    "neg_aead7e78d0bb9157",
    "neg_aeca0e0858c1c3dc",
    "neg_af28e4884bf33693",
    "neg_af32f13e783d9fe8",
    "neg_af3da466fdde9069",
    "neg_af902fb31ad355dc",
    "neg_b0b9956e45b90382",
    "neg_b0d7116ade290da6",
    "neg_b0fda56025405ac4",
    "neg_b11ab332736cb2c8",
    "neg_b27b43f8f789a101",
    "neg_b2a633870454fa92",
    "neg_b2e1945b86283631",
    "neg_b323a8b0e1a583a6",
    "neg_b36971a89782f57e",
    "neg_b375349338ef98a1",
    "neg_b389b8afe999a475",
    "neg_b392ded2f8267fc8",
    "neg_b3ed747d8845722a",
    "neg_b410506d2e13389c",
    "neg_b41461efbecf83d7",
    "neg_b43a429763aae863",
    "neg_b501396433efcfaf",
    "neg_b603a6e76a8f9eca",
    "neg_b616241112b57633",
    "neg_b62a236f176a16eb",
    "neg_b62be593be2dd3c6",
    "neg_b655c4c582456e94",
    "neg_b693c15931d09db3",
    "neg_b6cf2813acd1cda9",
    "neg_b6eaf8951d339194",
    "neg_b76cb19a26be0d75",
    "neg_b7777d25abdede00",
    "neg_b7ab10d6bb3b2977",
    "neg_b8105af69c24afdb",
    "neg_b843cae4b5a3d8b8",
    "neg_b8548d89164b7db0",
    "neg_b87de8a8302947bf",
    "neg_b8cd4f52b89f4837",
    "neg_b8d22baf50764725",
    "neg_b8e81509b3c36355",
    "neg_b8fb14cd5b2e0a30",
    "neg_b95d545bed9d4a9d",
    "neg_b95dd0be590b5e0e",
    "neg_b961786817512a66",
    "neg_b987df89a326a950",
    "neg_b991979a057b554e",
    "neg_b9f81130a3c9d2c5",
    "neg_ba0b2a657b8492aa",
    "neg_bac22b6e778ba010",
    "neg_bac7b31d25f2185b",
    "neg_bb5c900f9a8f10ed",
    "neg_bb660219e7908e4c",
    "neg_bb75740e47b943db",
    "neg_bc3af88238b812b2",
    "neg_bc4be17aafc99fa4",
    "neg_bc91d47afbf006b1",
    "neg_bcd0e3db5c3a51d2",
    "neg_bdce6c5fae98a25e",
    "neg_bdecdad615912554",
    "neg_be1982057a96e960",
    "neg_be19a5047add3f2c",
    "neg_be618bb440d2d00c",
    "neg_be88d9d499b238bf",
    "neg_bea0cbb0c8437e3f",
    "neg_bf4a3cfac36e3e1e",
    "neg_bf4a722b71681df1",
    "neg_bf7cfb5bdf649258",
    "neg_bf865e1d96aa4184",
    "neg_bfcffcb6e9135ca2",
    "neg_bfecee4ebf80a8e8",
    "neg_c03e168ac695a93f",
    "neg_c047d42aca34a42d",
    "neg_c07222e0001c5ed6",
    "neg_c09b8425face4b3a",
    "neg_c10b20ef07f8c9cc",
    "neg_c150e209b86e1dad",
    "neg_c1989f6d25194548",
    "neg_c1ac4f957e323d5c",
    "neg_c1b696097765ab16",
    "neg_c2d4dc4a817678a5",
    "neg_c2edd416956ace1c",
    "neg_c316e35903bdab83",
    "neg_c36ead1037d018ce",
    "neg_c3bd53c04a056f3b",
    "neg_c3fd23607ef85aa6",
    "neg_c42e919d3294fa82",
    "neg_c43aea14d4348fce",
    "neg_c44eb9dc14ae9962",
    "neg_c454c40e7bf13285",
    "neg_c4aa278809cdec0a",
    "neg_c4fc1d59a75fea23",
    "neg_c529ba513e5d5ca3",
    "neg_c555bc6b729dbeb7",
    "neg_c5bc7d4826db6f6a",
    "neg_c5cc7c29f1b9ab3c",
    "neg_c628f5c1f40005eb",
    "neg_c63d1a22c286cb74",
    "neg_c6405cbb3d63fd5c",
    "neg_c6bf152cc3a24a06",
    "neg_c6e0fd55fad770a1",
    "neg_c6f5097e41e308cf",
    "neg_c70af63843c32e60",
    "neg_c74f62a5bb6d82e8",
    "neg_c770ccd597b86aaa",
    "neg_c7fd7593681f84fc",
    "neg_c820734b380c1ab8",
    "neg_c88d1bb7d239ca25",
    "neg_c8ae0ea9fcb6da7c",
    "neg_c8ed42a1ce8473e0",
    "neg_cb0188d8a55f049f",
    "neg_cc1d8c3b6f4b5803",
    "neg_cd234285dc3dc3d6",
    "neg_cd44f4af049fe50e",
    "neg_cdc975b56fc0add5",
    "neg_ce01fe7bb4f8532b",
    "neg_ce4e2eb7c4e15488",
    "neg_cf2d6fb4a56cf92a",
    "neg_cf2e209ea51d810e",
    "neg_cf4fc3b8d4220d5f",
    "neg_cf6a3ad771b070eb",
    "neg_cfb0fe374a470706",
    "neg_cfb9612894a8093c",
    "neg_cfd7da5acb80dc77",
    "neg_cfe0342f02f04b87",
    "neg_d01eb29db7d65791",
    "neg_d0669d06ae21b723",
    "neg_d0788a1e5b7ba9e6",
    "neg_d0fe11605175c77f",
    "neg_d165a07f899a1dcf",
    "neg_d183a7983860e182",
    "neg_d19f1e45d0484905",
    "neg_d1b57bba5172c5a0",
    "neg_d21abe7c950876d9",
    "neg_d22d9d3d549eab02",
    "neg_d3837df40e80624b",
    "neg_d39829bf877cc8a8",
    "neg_d3a5f3592bc98ddc",
    "neg_d3b3dd816a954641",
    "neg_d3ea4ff312b2b596",
    "neg_d3fc83b2892bc9a7",
    "neg_d40cb5b43817deb7",
    "neg_d41fc9264805edb4",
    "neg_d42bdaebf117aa61",
    "neg_d43e40e721609377",
    "neg_d495215a19de3cf2",
    "neg_d4f4165c6d2f1b74",
    "neg_d531fa58f25aed66",
    "neg_d5589354241f7953",
    "neg_d598d6e78c1e23da",
    "neg_d5cea4a1185a1521",
    "neg_d66752978a50c6ac",
    "neg_d67ca84274883161",
    "neg_d6a5e603ce308b1e",
    "neg_d74de26ca5475bfe",
    "neg_d763a8b6f45e67fd",
    "neg_d77bff206db64a36",
    "neg_d83c97e89abb57fa",
    "neg_d85073a672fb44df",
    "neg_d8e80f76dabd44c1",
    "neg_d90e7f8a539b1ad6",
    "neg_d9a8287632edc26b",
    "neg_d9ab749fdf0c5b3b",
    "neg_da52a928ad0e561a",
    "neg_dac6769efa9460e4",
    "neg_dafb14935f6a759b",
    "neg_dbb950da7b648c22",
    "neg_dc1f8e55fa3d1f1c",
    "neg_dc60093779bbb72f",
    "neg_dccef6d1c3a704b1",
    "neg_dd255c84c0b226b7",
    "neg_dd49d55dcf4bba56",
    "neg_dd78ef35d2ee8c89",
    "neg_ddae7042b1563889",
    "neg_ddd0039a79af3ded",
    "neg_de392cd5cfe3f589",
    "neg_de9d25f4dc880c0e",
    "neg_dea75233a677422f",
    "neg_dec386f946aea6d0",
    "neg_dec8f8d73bdbb6b7",
    "neg_decdade8ed4aa14d",
    "neg_df1cbbb97092854d",
    "neg_df63eed281fdf8e5",
    "neg_df72b0355d683195",
    "neg_df7f857c6dbc674d",
    "neg_dfb9772202cb11bf",
    "neg_e04e999b7b37b502",
    "neg_e05f6a87c4de0e39",
    "neg_e153e40f5ddabd72",
    "neg_e1739a84606c6894",
    "neg_e17cacd15b08f8fd",
    "neg_e1c79b3aa42d30a6",
    "neg_e1ed5c7ee8ce1f9b",
    "neg_e2177117959b3a8a",
    "neg_e24177b1796b131f",
    "neg_e2423f5fe968d8f1",
    "neg_e2c15c919f713fb0",
    "neg_e339300ca83776ea",
    "neg_e3e6cec3183cf8b1",
    "neg_e472030ba15ce658",
    "neg_e57c8c10ab7f2be0",
    "neg_e5b4650fcbcbe883",
    "neg_e61ad6ec5ff3b525",
    "neg_e74106b661032ac9",
    "neg_e746064210daedea",
    "neg_e74c56d1a6d3062c",
    "neg_e75efc760ab9f6e7",
    "neg_e778bb2f80710d98",
    "neg_e787258152d51315",
    "neg_e7ea959975319930",
    "neg_e84bc292395c0541",
    "neg_e86ef2cbe02e6414",
    "neg_e8e32c792a288230",
    "neg_e977c141abae333f",
    "neg_e9c54ab66416dc71",
    "neg_ea1fd43cd35027c3",
    "neg_ea4f6df09cb20a05",
    "neg_eb07413ff5cbf278",
    "neg_eb2831a51d9b34c8",
    "neg_eb32f51b86aef278",
    "neg_eb5744e19a478290",
    "neg_eb57d965f598505b",
    "neg_eb9580698a9a0640",
    "neg_ebd665b8fe574e98",
    "neg_ecc315b7d893b778",
    "neg_ed35619e71da7eb8",
    "neg_edf51e12ab5a4d56",
    "neg_ee1fbbc273dcf2a8",
    "neg_eef65cb60225693b",
    "neg_ef8be80c7cda8d84",
    "neg_f02d2862648f5920",
    "neg_f1055b9c80e30e84",
    "neg_f1270f7481f91f9b",
    "neg_f14cfac80e94815e",
    "neg_f19a7b8858bdbf38",
    "neg_f206f506670039ff",
    "neg_f258ed8033d11818",
    "neg_f25f425a07664152",
    "neg_f27684664c62b8ed",
    "neg_f368e412460f1f04",
    "neg_f3808490c9abd498",
    "neg_f39c264563a8363e",
    "neg_f3af8bd1fa50dc83",
    "neg_f422a75d568177e2",
    "neg_f431d674e0d1378a",
    "neg_f4ace10d811f63db",
    "neg_f4d9b58a0cf5161b",
    "neg_f528d7bb813e36c2",
    "neg_f5292c7bb3cbc828",
    "neg_f56fe5da98f507f3",
    "neg_f57311a5ea8d4303",
    "neg_f5887bd3bf26c4e6",
    "neg_f6474b537d97ff05",
    "neg_f65c46952c4c2da4",
    "neg_f66f3fbd17e33e4a",
    "neg_f6eab77440b65455",
    "neg_f705c7b0363f8603",
    "neg_f7170e5d370200f3",
    "neg_f7e113edd72cd509",
    "neg_f806705936505939",
    "neg_f816199a34df0deb",
    "neg_f8314701ebc2e188",
    "neg_f8374a1283da14ba",
    "neg_f8634244ea9f9356",
    "neg_f8742084d8d90352",
    "neg_f885b380dff298e7",
    "neg_f8999293e5f802eb",
    "neg_f8c84b154795459a",
    "neg_f961c4e167bb1a1f",
    "neg_f9c9f6454e050ef8",
    "neg_fa9324161cc2ca50",
    "neg_fb1cc678ee3763bb",
    "neg_fb426c25ad05a6db",
    "neg_fb6d2db79220e01a",
    "neg_fb92a6fa4a5ac880",
    "neg_fbae94b28f494891",
    "neg_fbba7ae232d8c51d",
    "neg_fbc15e2a52c6b185",
    "neg_fbcbe4258f25020c",
    "neg_fc010c391d287f6b",
    "neg_fc02c8dea63237fa",
    "neg_fc14dc2cb6cd5eda",
    "neg_fc303473458e44c6",
    "neg_fc4f44fabf43e13b",
    "neg_fc61c8cf2fe41e35",
    "neg_fd19a0154ba04497",
    "neg_fd1fcd37ce87e23a",
    "neg_fd5c79bfbf9ac557",
    "neg_fd7e5e245ecdc986",
    "neg_fdd22869f75ed419",
    "neg_fe287044f7baf220",
    "neg_feaae78c8792ad94",
    "neg_feb5e834667ae879",
    "neg_fedc6ce40eb8573a",
    "neg_ff89beca6a2df00c",
    "neg_ffeee581cdec4ab0"
  ],
  "branches": [
    [
      "vid_clip",
      0,
      512
    ],
    [
      "vid_slowfast",
      512,
      2816
    ]
  ],
  "modes": [
    "identity",
    "zero_visual",
    "shuffle_time",
    "zero_clip",
    "zero_slowfast"
  ],
  "perturbation": "zero normalized visual channels; shuffle valid visual rows only; masks, padded rows, text and TEF preserved",
  "permutation": "same permutation for each video and all queries; CPU generator seeded by SHA256(seed|vid|length)",
  "selection": "all existing pseudo rows, original order; no outcome-based selection",
  "accuracy_under_perturbation": "not computed"
}
```

## diagnostics/open_close/baseline/LATEST_FAILURE_DECOMPOSITION.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "checkpoint_epoch_zero_based": 99,
  "checkpoint_sha256": "605f493e00783844fee0840d2b0151859dd7f732a815726fd29583014349be87",
  "source_sha256": "a4a8dc5c9317945a71a184eab08e9a7962137004e736c19e12dcc34ba62741d0",
  "same_model_tensors_as_best": false,
  "predictions_reused_from_best": false,
  "results": {
    "pseudo": {
      "AUROC": 0.5512465366148626,
      "raw_R1_05": 0.2590042372881356,
      "gated_R1_05": 0.2616525423728814,
      "FRR": 0.12182203389830508,
      "RR": 0.17891373801916932,
      "counts": {
        "positive": 1888,
        "raw_incorrect": 1399,
        "positive_rejected": 230,
        "official_gated_correct": 494,
        "raw_correct_gated_wrong": 12,
        "raw_wrong_gated_correct": 17,
        "official_empty": 0,
        "raw_correct": 489,
        "raw_correct_accepted": 436,
        "raw_correct_rejected": 53,
        "negative": 939,
        "negative_accepted": 771
      },
      "raw_correct_rejected_over_raw_correct": 0.1083844580777096,
      "raw_errors_over_hard_failures": 0.9634986225895317,
      "threshold": 0.9993,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "16b32022718a00f1e20901bf45f5e670c6799411eec206238f6e028109e30225"
    },
    "seen": {
      "AUROC": 0.8429432904342591,
      "raw_R1_05": 0.312015503875969,
      "gated_R1_05": 0.31007751937984496,
      "FRR": 0.13178294573643412,
      "RR": 0.7378640776699029,
      "counts": {
        "positive": 516,
        "raw_incorrect": 355,
        "positive_rejected": 68,
        "official_gated_correct": 160,
        "raw_correct_gated_wrong": 5,
        "raw_wrong_gated_correct": 4,
        "official_empty": 0,
        "raw_correct": 161,
        "raw_correct_accepted": 141,
        "raw_correct_rejected": 20,
        "negative": 206,
        "negative_accepted": 54
      },
      "raw_correct_rejected_over_raw_correct": 0.12422360248447205,
      "raw_errors_over_hard_failures": 0.9466666666666667,
      "threshold": 0.9993,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "78c31b90b22a34618d2b195979861d5cc6fdb6fb0a93afa6cb9682b2943f5713"
    }
  },
  "limitations": "Latest comparison is descriptive, not an alternative pseudo-based checkpoint selection or full training trajectory; unchanged official gate, diagnostic threshold fitted on latest seen only."
}
```

## diagnostics/open_close/baseline/SCORE_COMPARABILITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "splits": {
    "pseudo": {
      "same_video_pairacc": 0.5904159132007233,
      "same_video_pairs": 1659,
      "cross_video_pairacc": 0.5345790614468491,
      "exact_query_cross_video_pairacc": 0.5416044522872269,
      "exact_query_cross_video_pairs": 7367,
      "exact_query_groups": 158,
      "exact_query_feature_consistent_groups": 0,
      "mixed_label_videos": 664
    },
    "seen": {
      "same_video_pairacc": 0.7944214876033058,
      "same_video_pairs": 484,
      "cross_video_pairacc": 0.8563726231429328,
      "exact_query_cross_video_pairacc": 0.625,
      "exact_query_cross_video_pairs": 12,
      "exact_query_groups": 9,
      "exact_query_feature_consistent_groups": 0,
      "mixed_label_videos": 104
    }
  },
  "limitations": "Within/cross-video rank decomposition uses original queries and labels; differing compositions do not prove video bias. Identical string ranks before feature control are not a text tie control."
}
```

## diagnostics/open_close/baseline/VISUAL_INCREMENT.json

```json
{
  "pseudo": {
    "same_video_pairacc": 0.5904159132007233,
    "same_video_pairs": 1659,
    "cross_video_pairacc": 0.5345790614468491,
    "exact_query_cross_video_pairacc": 0.5416044522872269,
    "exact_query_cross_video_pairs": 7367,
    "exact_query_groups": 158,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 664
  },
  "seen": {
    "same_video_pairacc": 0.7944214876033058,
    "same_video_pairs": 484,
    "cross_video_pairacc": 0.8563726231429328,
    "exact_query_cross_video_pairacc": 0.625,
    "exact_query_cross_video_pairs": 12,
    "exact_query_groups": 9,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 104
  }
}
```

## diagnostics/sit/baseline/CONTROLLED_QUERY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "query_groups": 45,
  "rows": 229,
  "pairs": 359,
  "pairacc": 0.5682451253481894,
  "video_endpoint_bootstrap_ci95": [
    0.46262892549261087,
    0.6675488588125034
  ],
  "text_input": "same normalized cached feature and mask per identical query, canonical lexicographically smallest qid; original video and labels unchanged",
  "pure_text_pairacc_control": 0.5,
  "checkpoint_sha256": "67dadc67ff6018741578ed0a405d59c608b07d7161b9bbb7cbe76cc35557a6f3",
  "scores": {
    "train115": 0.9991255402565002,
    "train231": 0.9994077682495117,
    "train274": 0.9679696559906006,
    "train403": 0.9926924705505371,
    "train857": 0.8470232486724854,
    "train940": 0.9823088049888611,
    "train944": 0.9859920144081116,
    "train1146": 0.9954568147659302,
    "train1355": 0.9844451546669006,
    "train1441": 0.9862352013587952,
    "train1650": 0.9604767560958862,
    "train1656": 0.998116135597229,
    "train1716": 0.9760282039642334,
    "train1732": 0.9790394902229309,
    "train1870": 0.9912201762199402,
    "train1923": 0.9972143769264221,
    "train1924": 0.9972701668739319,
    "train2022": 0.9814456105232239,
    "train2139": 0.9948064684867859,
    "train2227": 0.9984740614891052,
    "train2374": 0.9447500705718994,
    "train2599": 0.9820038676261902,
    "train2643": 0.8385149240493774,
    "train2716": 0.9809734225273132,
    "train2879": 0.9985815286636353,
    "train3157": 0.9776778817176819,
    "train3181": 0.9985992312431335,
    "train3719": 0.9786797761917114,
    "train3737": 0.9979941844940186,
    "train3832": 0.9865065813064575,
    "train3977": 0.9987980127334595,
    "train4087": 0.9855256676673889,
    "train4174": 0.9940463304519653,
    "train4175": 0.9946547746658325,
    "train4403": 0.9987514019012451,
    "train4433": 0.8901109099388123,
    "train4443": 0.9818782210350037,
    "train4444": 0.9677770137786865,
    "train4486": 0.9967007040977478,
    "train4782": 0.9943317174911499,
    "train4932": 0.9768956899642944,
    "train5010": 0.9852347373962402,
    "train5012": 0.9821311235427856,
    "train5025": 0.9359399676322937,
    "train5058": 0.9979351758956909,
    "train5222": 0.9975023865699768,
    "train5233": 0.9912593960762024,
    "train5355": 0.973055362701416,
    "train5461": 0.9966429471969604,
    "train5596": 0.9985828399658203,
    "train5728": 0.9982183575630188,
    "train5852": 0.9979835748672485,
    "train5945": 0.9777071475982666,
    "train6015": 0.9969518184661865,
    "train6036": 0.9840371608734131,
    "train6282": 0.9725719094276428,
    "train6303": 0.9886748790740967,
    "train6305": 0.9858248233795166,
    "train6542": 0.9989631175994873,
    "train6668": 0.9992139339447021,
    "train6689": 0.9981632828712463,
    "train6713": 0.9708845019340515,
    "train6800": 0.990523636341095,
    "train6900": 0.9678282737731934,
    "train7042": 0.9720783233642578,
    "train7043": 0.9785005450248718,
    "train7131": 0.7056466937065125,
    "train7192": 0.9829604625701904,
    "train7214": 0.9985339641571045,
    "train7307": 0.9927948117256165,
    "train7308": 0.9910995364189148,
    "train7439": 0.9984539747238159,
    "train7442": 0.9941457509994507,
    "train7547": 0.9981322884559631,
    "train7571": 0.983925461769104,
    "train7858": 0.9959916472434998,
    "train7918": 0.9966313242912292,
    "train7929": 0.99628746509552,
    "train8055": 0.9896015524864197,
    "train8065": 0.9984056353569031,
    "train8339": 0.988093912601471,
    "train8367": 0.9924138188362122,
    "train8381": 0.99648118019104,
    "train8416": 0.9977085590362549,
    "train8600": 0.9977807402610779,
    "train8637": 0.9606397747993469,
    "train8642": 0.9979946613311768,
    "train8674": 0.9993438124656677,
    "train8718": 0.9397662281990051,
    "train8719": 0.917568027973175,
    "train8733": 0.9698800444602966,
    "train8777": 0.9988221526145935,
    "train8934": 0.9695640206336975,
    "train8935": 0.970701277256012,
    "train8940": 0.9887444972991943,
    "train8992": 0.9987377524375916,
    "train9083": 0.9983052015304565,
    "train9373": 0.9973112344741821,
    "train9683": 0.9806973934173584,
    "train9786": 0.9993126392364502,
    "train9787": 0.9971109628677368,
    "train9788": 0.999014139175415,
    "train9902": 0.9987183809280396,
    "train9992": 0.8586185574531555,
    "train10028": 0.9340201616287231,
    "train10117": 0.9459457397460938,
    "train10447": 0.9978196620941162,
    "train10451": 0.9954615235328674,
    "train10488": 0.9991425275802612,
    "train10501": 0.9976714253425598,
    "train10648": 0.9981879591941833,
    "train10815": 0.994925856590271,
    "train10887": 0.9485746622085571,
    "train10888": 0.9674619436264038,
    "train10946": 0.9981909394264221,
    "train10961": 0.9865791201591492,
    "train10969": 0.9535820484161377,
    "train11156": 0.9547908306121826,
    "train11157": 0.932482898235321,
    "train11172": 0.9987131357192993,
    "train11199": 0.9990664124488831,
    "train11242": 0.9968411922454834,
    "train11382": 0.9975895881652832,
    "train11705": 0.9730908870697021,
    "train11726": 0.9986802935600281,
    "train11753": 0.9973094463348389,
    "train11854": 0.9992181062698364,
    "train11858": 0.9964724779129028,
    "train12056": 0.9982110261917114,
    "train12271": 0.9966806769371033,
    "train12354": 0.9878639578819275,
    "neg_0123f49ff5c49869": 0.9967047572135925,
    "neg_018516587239cb1c": 0.998696506023407,
    "neg_08bf8191490ff14b": 0.9603098630905151,
    "neg_093f49e32e660dda": 0.8955864310264587,
    "neg_0a1d7592a95d522e": 0.7990871667861938,
    "neg_0be7cd21f34a0d80": 0.9577243328094482,
    "neg_0c30b2804e1f2b35": 0.9971005320549011,
    "neg_0c69bdf9e9ef754d": 0.9986741542816162,
    "neg_0cee474d8129f426": 0.9983336329460144,
    "neg_0eb9a33ee3b7772c": 0.9696383476257324,
    "neg_12c96add4a685924": 0.9987296462059021,
    "neg_14212ca99ab4e3e4": 0.8829060792922974,
    "neg_15cbf04e3ededaa6": 0.9917416572570801,
    "neg_1966eecfd919fc00": 0.9790915846824646,
    "neg_1ae0f1592adb24fa": 0.9963948130607605,
    "neg_20c8388f8c12a201": 0.9889973402023315,
    "neg_20ee5c66894dc837": 0.9970777034759521,
    "neg_23e811c843cfa55e": 0.9972254037857056,
    "neg_291b8ef6279fecb6": 0.8999795913696289,
    "neg_2e37350e54b34ae8": 0.9883611798286438,
    "neg_3234f8617aeb3af7": 0.8835545182228088,
    "neg_3441c9d1534a657e": 0.992756187915802,
    "neg_34a6d2b4a4ea7496": 0.9724535346031189,
    "neg_3bcc986551a5aeb2": 0.9960371851921082,
    "neg_3c6493a95421bd82": 0.9989594221115112,
    "neg_3e3426987ea6634f": 0.935077965259552,
    "neg_3f98fa4d030550ce": 0.9443029761314392,
    "neg_3fca1604924ccba3": 0.9984036087989807,
    "neg_4649ad6bd22070ea": 0.9221353530883789,
    "neg_4ce0a40cc56c338c": 0.634564995765686,
    "neg_506c831be5358f9e": 0.9977450966835022,
    "neg_51acc7bd980cd390": 0.9938896894454956,
    "neg_5246b16e4fa28b88": 0.9164864420890808,
    "neg_534516fc851403af": 0.9863808751106262,
    "neg_5900614ea23f191e": 0.9954889416694641,
    "neg_5abd1fca17f7f0fc": 0.9989603757858276,
    "neg_5d516740e70d0520": 0.9865168333053589,
    "neg_5fb1d10f005c9bc2": 0.9977788329124451,
    "neg_6141729953832709": 0.9928533434867859,
    "neg_6277d4aa84d44ae6": 0.9758840799331665,
    "neg_6b7c4468117cbb0f": 0.9991627931594849,
    "neg_6be90c5ef9b29a6c": 0.995270311832428,
    "neg_6c76729669e48779": 0.9976418018341064,
    "neg_6d5ad488966e43f2": 0.6258288621902466,
    "neg_73c3d94050ce6715": 0.9936010241508484,
    "neg_76299e312092ee7b": 0.997771143913269,
    "neg_7c1dce3afbcb6732": 0.8372911214828491,
    "neg_7ed05dbbd40de425": 0.9984170198440552,
    "neg_7f99369fef37f124": 0.8128705024719238,
    "neg_7f9ea4c914fbdac6": 0.9968282580375671,
    "neg_86c33ffac2a67983": 0.9988314509391785,
    "neg_8729e648a7e46ef9": 0.9714165925979614,
    "neg_87fce2824ed7bfcf": 0.9971330165863037,
    "neg_8b2e2116142f6e81": 0.9508174657821655,
    "neg_8d9edcdfcd54ec96": 0.9414225816726685,
    "neg_8ddf19655e0f88f2": 0.9959915280342102,
    "neg_8f6a7ca3c6786f2d": 0.821732759475708,
    "neg_9011ae82d3984518": 0.9986692667007446,
    "neg_9126b619bf00e3c2": 0.9967759251594543,
    "neg_92ece90fa8eb96f7": 0.9974226951599121,
    "neg_933b2475b417e910": 0.9874946475028992,
    "neg_96877b9835c4d75f": 0.9602041840553284,
    "neg_9997d1ad26b746e3": 0.997750461101532,
    "neg_9a5541e8fde83b53": 0.9984375834465027,
    "neg_9ea504aea4e7ab27": 0.9983793497085571,
    "neg_a67229aef624ffe8": 0.9814051985740662,
    "neg_aa339c9394106d34": 0.997463583946228,
    "neg_ac3b0848bb9dac97": 0.9946109056472778,
    "neg_afa2f514d25456a6": 0.9973104000091553,
    "neg_b152a99f6bbcccb9": 0.9604637622833252,
    "neg_b2f3b4fc99e427ad": 0.9973523616790771,
    "neg_b6926223119b8223": 0.9858986139297485,
    "neg_bf34a66fb14c51a6": 0.9904482960700989,
    "neg_c2754502fefd5f64": 0.9482119083404541,
    "neg_c2abbb0fd3b4ae0a": 0.9725687503814697,
    "neg_c5d9d2d16d63d2a7": 0.9954445362091064,
    "neg_c68027405dbb50c8": 0.9984500408172607,
    "neg_cb149f15f0923753": 0.9986060261726379,
    "neg_cf35375d6938f9b4": 0.9988440275192261,
    "neg_cfed810b0fb2f889": 0.8942828178405762,
    "neg_d266a047cfb8a590": 0.9934980869293213,
    "neg_d628ecfe25f97317": 0.9900984168052673,
    "neg_d96aafddcd1fa9b9": 0.9988817572593689,
    "neg_dbd771fd941a5e06": 0.9669554233551025,
    "neg_dc7c0d5569456d77": 0.8268681764602661,
    "neg_dd7517b74bfdf1fb": 0.9986178874969482,
    "neg_df44b76a89a0c8a5": 0.9988816380500793,
    "neg_e18b5b7a763ce088": 0.9095637202262878,
    "neg_e63632e0e5e95536": 0.998691737651825,
    "neg_e9e33492f1e76a57": 0.9934688806533813,
    "neg_eb01bfd54e3b7892": 0.9957279562950134,
    "neg_f01163afb31ece5c": 0.9977602958679199,
    "neg_f2f90e9752c02fb6": 0.9963933825492859,
    "neg_f3bf785b5cb4a0e4": 0.99577397108078,
    "neg_f4eeba73cba7f915": 0.9959701299667358,
    "neg_f63a4373f57e84cf": 0.9980706572532654,
    "neg_f6c8fcfdbb1b6ff9": 0.9985901713371277,
    "neg_f6ebb438089efc10": 0.9961826205253601
  },
  "limitations": "original labels only; sparse correlated pairs, endpoint video bootstrap; not a causal proof or full-sample metric"
}
```

## diagnostics/sit/baseline/FAILURE_DECOMPOSITION.json

```json
{
  "pseudo": {
    "AUROC": 0.6540216524216524,
    "raw_R1_05": 0.3504,
    "gated_R1_05": 0.3536,
    "FRR": 0.064,
    "RR": 0.23076923076923073,
    "counts": {
      "positive": 625,
      "raw_incorrect": 406,
      "positive_rejected": 40,
      "official_gated_correct": 221,
      "raw_correct_gated_wrong": 4,
      "raw_wrong_gated_correct": 6,
      "official_empty": 0,
      "raw_correct": 219,
      "raw_correct_accepted": 201,
      "raw_correct_rejected": 18,
      "negative": 351,
      "negative_accepted": 270
    },
    "raw_correct_rejected_over_positives": 0.0288,
    "raw_correct_rejected_over_raw_correct": 0.0821917808219178,
    "raw_errors_over_hard_failures": 0.9575471698113207,
    "threshold": 0.955,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.6943493150684932,
    "same_video_pairs": 584,
    "cross_video_pairacc": 0.6539140092599787,
    "exact_query_cross_video_pairacc": 0.564066852367688,
    "exact_query_cross_video_pairs": 359,
    "exact_query_groups": 45,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 229,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/pseudo.jsonl": "f1ee87f31d4e0257a2e3eb0d794b1ab55aa8024c51aa2967508d15d35d95b43c",
      "pseudo_predictions.jsonl": "7deaad795715181e45bf4fcb2ceab641bea0920d8f402184e805551c437a7861"
    }
  },
  "seen": {
    "AUROC": 0.8432142802817116,
    "raw_R1_05": 0.3254437869822485,
    "gated_R1_05": 0.3224852071005917,
    "FRR": 0.3668639053254438,
    "RR": 0.9125964010282777,
    "counts": {
      "positive": 676,
      "raw_correct": 220,
      "raw_correct_accepted": 143,
      "positive_rejected": 248,
      "official_gated_correct": 218,
      "raw_correct_gated_wrong": 6,
      "raw_wrong_gated_correct": 4,
      "official_empty": 0,
      "raw_incorrect": 456,
      "raw_correct_rejected": 77,
      "negative": 389,
      "negative_accepted": 34
    },
    "raw_correct_rejected_over_positives": 0.11390532544378698,
    "raw_correct_rejected_over_raw_correct": 0.35,
    "raw_errors_over_hard_failures": 0.8555347091932458,
    "threshold": 0.955,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.753968253968254,
    "same_video_pairs": 882,
    "cross_video_pairacc": 0.8435146251936418,
    "exact_query_cross_video_pairacc": 0.6573816155988857,
    "exact_query_cross_video_pairs": 359,
    "exact_query_groups": 45,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 185,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/val_seen.jsonl": "7af69ae2bdca9d5b9ce9367db036f9ce308f537727882cb616e586ed3d0837d5",
      "best_seen_predictions.jsonl": "e8ec2c706ec1bc9f407ac71759f99f95e861806fe59209a3569031ffca391364"
    }
  }
}
```

## diagnostics/sit/baseline/GATE_POSTPROCESS_AUDIT.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "results": {
    "pseudo": {
      "rows": 976,
      "positive": 625,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train4486",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train4835",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train4836",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train7059",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train7509",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train8276",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train9107",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train9994",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train11083",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train11922",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.3536,
      "official_gated_R1_05": 0.3536,
      "prediction_sha256": "7deaad795715181e45bf4fcb2ceab641bea0920d8f402184e805551c437a7861"
    },
    "seen": {
      "rows": 1065,
      "positive": 676,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train665",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train3147",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train4208",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train4584",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train5086",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train7189",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train7602",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train7984",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train10114",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train11937",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.3224852071005917,
      "official_gated_R1_05": 0.3224852071005917,
      "prediction_sha256": "e8ec2c706ec1bc9f407ac71759f99f95e861806fe59209a3569031ffca391364"
    }
  },
  "source_sha256": "e8f3da3638ebe09271ab1e32db99dd2ce36e12e5d52584165ea6d7310791f5f4",
  "official_evaluator_sha256": "b71f952fa6cfbfbaae1ca0b6bd1f476159c17c2448b87d55f82300fa97a50537",
  "official_postprocessor_sha256": "50e6501c642e77502f7a4d781e01e12bbd97521d3b0a8f47d793b3044be30046",
  "gate_sha256": "0e1235c8425f9c61883e88a57a8a1feec2c9ceb15046aeecd83563deb3cefc67",
  "interpretation": "Official soft gate is a per-row nonnegative scalar. Exact positive scalar scaling preserves within-row ranking. Saved gated coordinates alone receive clip_ts/round_multiple; frozen raw endpoint remains untouched. When aligned coordinates match, hit changes are explained by temporal postprocessing rather than gate veto or reranking. Aligned raw is auxiliary only, not a replacement co-primary endpoint."
}
```

## diagnostics/sit/baseline/GRADIENT_DETAIL.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "source_sha256": "aa62ab661c26930186b53405490d723cc70e4c952e94a60596cd0584f7619473",
  "checkpoints": {
    "best": {
      "checkpoint_epoch_zero_based": 11,
      "checkpoint_sha256": "67dadc67ff6018741578ed0a405d59c608b07d7161b9bbb7cbe76cc35557a6f3",
      "model_tensor_sha256": "46c8d98fd32af9b22aaff3085c3d012e90f0980aaccba78cec0c5a6a027e9268",
      "original_diagnostic_sha256": "9d4ed5c7e3e93a71cca6cdfb9e200c7be38c139e540d8efda2d926eb94e1f8c7",
      "qids": [
        [
          "train12379",
          "train714",
          "train5246",
          "train6874",
          "train10461",
          "train10087",
          "train1159",
          "train852",
          "train2384",
          "train1373",
          "train596",
          "train9855",
          "train724",
          "train7556",
          "train6878",
          "train10480"
        ],
        [
          "train9665",
          "train10386",
          "train6567",
          "train10435",
          "train7718",
          "train11356",
          "train9333",
          "train7905",
          "train4520",
          "train1745",
          "train7639",
          "train4804",
          "train7719",
          "train9118",
          "train7606",
          "train7669"
        ],
        [
          "train12217",
          "train3802",
          "train1458",
          "train5221",
          "train11798",
          "train1715",
          "train7868",
          "train12252",
          "train9034",
          "train6213",
          "train809",
          "train3797",
          "train8969",
          "train4079",
          "train1413",
          "train5629"
        ],
        [
          "train9013",
          "train8429",
          "train4326",
          "train455",
          "train4096",
          "train142",
          "train5022",
          "train2755",
          "train10248",
          "train11558",
          "train1399",
          "train10975",
          "train2883",
          "train7513",
          "train2195",
          "train5110"
        ],
        [
          "train12400",
          "train5496",
          "train9416",
          "train11778",
          "train186",
          "train6364",
          "train12046",
          "train1098",
          "train3108",
          "train7705",
          "train5372",
          "train10161",
          "train12078",
          "train6388",
          "train9635",
          "train613"
        ],
        [
          "train10749",
          "train11092",
          "train7605",
          "train10951",
          "train1670",
          "train11281",
          "train2829",
          "train8158",
          "train2514",
          "train5780",
          "train10615",
          "train2807",
          "train1851",
          "train8037",
          "train5583",
          "train6184"
        ],
        [
          "train10075",
          "train6934",
          "train4604",
          "train8112",
          "train9470",
          "train4727",
          "train7116",
          "train9997",
          "train10938",
          "train6756",
          "train1592",
          "train9559",
          "train7721",
          "train5614",
          "train11377",
          "train1264"
        ],
        [
          "train2318",
          "train1160",
          "train11079",
          "train9625",
          "train1545",
          "train895",
          "train705",
          "train12181",
          "train2065",
          "train4220",
          "train9493",
          "train7977",
          "train2316",
          "train7528",
          "train11620",
          "train8008"
        ],
        [
          "train10901",
          "train3862",
          "train9106",
          "train5080",
          "train8199",
          "train3905",
          "train1596",
          "train200",
          "train7885",
          "train9203",
          "train6816",
          "train9452",
          "train10401",
          "train3258",
          "train3317",
          "train7549"
        ],
        [
          "train6352",
          "train2520",
          "train8748",
          "train9370",
          "train1836",
          "train6009",
          "train8678",
          "train4305",
          "train9829",
          "train1985",
          "train6166",
          "train8244",
          "train1894",
          "train35",
          "train375",
          "train4943"
        ],
        [
          "train7012",
          "train8018",
          "train5006",
          "train3169",
          "train5149",
          "train4476",
          "train6686",
          "train12113",
          "train9422",
          "train6719",
          "train9476",
          "train10208",
          "train4354",
          "train7754",
          "train9849",
          "train4940"
        ],
        [
          "train3635",
          "train7592",
          "train11107",
          "train2189",
          "train7255",
          "train3029",
          "train5160",
          "train6647",
          "train3530",
          "train4834",
          "train11612",
          "train4986",
          "train7403",
          "train7274",
          "train1623",
          "train9695"
        ],
        [
          "train9308",
          "train4991",
          "train9532",
          "train4418",
          "train10154",
          "train6397",
          "train1770",
          "train10781",
          "train12015",
          "train2856",
          "train4716",
          "train1127",
          "train2556",
          "train3839",
          "train236",
          "train468"
        ],
        [
          "train3856",
          "train8177",
          "train11087",
          "train2951",
          "train10603",
          "train6209",
          "train4350",
          "train3350",
          "train10748",
          "train3516",
          "train8728",
          "train2797",
          "train10158",
          "train2930",
          "train6322",
          "train7448"
        ],
        [
          "train1859",
          "train11928",
          "train1815",
          "train4993",
          "train6419",
          "train4204",
          "train8196",
          "train1310",
          "train11376",
          "train88",
          "train1487",
          "train2454",
          "train3145",
          "train1040",
          "train5744",
          "train7238"
        ],
        [
          "train2692",
          "train6734",
          "train2678",
          "train749",
          "train2209",
          "train1703",
          "train3113",
          "train1402",
          "train2149",
          "train6807",
          "train3548",
          "train10619",
          "train11718",
          "train5555",
          "train9080",
          "train4559"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.7590953707695007
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 2.584446668624878
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.08515522256493568,
          "negative_fraction": 0.1875
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.3840087801218033
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.684577226638794
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.006572761572897434,
          "negative_fraction": 0.25
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 2.911793351173401
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 9.623836517333984
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.08804232627153397,
          "negative_fraction": 0.1875
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.288727045059204
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.565065622329712
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2965196967124939
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.060430884361267
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.4000482559204102
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.9082580804824829
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6099326610565186
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.3838255405426025
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.41228336095809937
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.13837991654872894
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4194374084472656
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3566816747188568
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.0869250297546387
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.28515318036079407
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.37809184193611145
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.2957392930984497
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.1574699878692627
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.479396343231201
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.422020673751831
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1049485206604004
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.2427563667297363
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.981405019760132
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.681246280670166
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.115125894546509
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.5447163581848145
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.313795804977417
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.4230406284332275
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.0002434253692627
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.608651876449585
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.9094624519348145
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.5043516159057617
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.560241460800171
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.28879421949386597
          },
          {
            "full_block_cosine": 0.24945205450057983
          },
          {
            "full_block_cosine": 0.06752022355794907
          },
          {
            "full_block_cosine": 0.02957063354551792
          },
          {
            "full_block_cosine": 0.14443716406822205
          },
          {
            "full_block_cosine": 0.030908018350601196
          },
          {
            "full_block_cosine": 0.07495510578155518
          },
          {
            "full_block_cosine": 0.09535533934831619
          },
          {
            "full_block_cosine": -0.07547661662101746
          },
          {
            "full_block_cosine": -0.033220551908016205
          },
          {
            "full_block_cosine": 0.1147543415427208
          },
          {
            "full_block_cosine": -0.04734155163168907
          },
          {
            "full_block_cosine": 0.10929035395383835
          },
          {
            "full_block_cosine": 0.07329016923904419
          },
          {
            "full_block_cosine": 0.21156898140907288
          },
          {
            "full_block_cosine": 0.24671821296215057
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8568699359893799
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8709449172019958
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.17358721792697906
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.42837950587272644
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5826824903488159
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4710994362831116
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3396380543708801
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7542422413825989
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.25911399722099304
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10048623383045197
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2484443336725235
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2391122281551361
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.46351921558380127
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.14296658337116241
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.25418347120285034
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5285130739212036
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.594433784484863
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.412944793701172
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.364992141723633
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.7491912841796875
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.0055887699127197
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.892970561981201
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.516087055206299
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.818124294281006
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.12534236907959
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.394176006317139
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.0747225284576416
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.921615123748779
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.703566551208496
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.665587902069092
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.3916015625
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.366525173187256
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": 0.011691426858305931
          },
          {
            "full_block_cosine": 0.029300566762685776
          },
          {
            "full_block_cosine": -0.005345105659216642
          },
          {
            "full_block_cosine": 0.007689908146858215
          },
          {
            "full_block_cosine": 0.009536221623420715
          },
          {
            "full_block_cosine": 0.016106005758047104
          },
          {
            "full_block_cosine": 0.01847577467560768
          },
          {
            "full_block_cosine": -0.0036338858772069216
          },
          {
            "full_block_cosine": -0.03323058411478996
          },
          {
            "full_block_cosine": 0.003698294283822179
          },
          {
            "full_block_cosine": 0.0013290022034198046
          },
          {
            "full_block_cosine": 0.004865193739533424
          },
          {
            "full_block_cosine": 0.02538747526705265
          },
          {
            "full_block_cosine": 0.005455614998936653
          },
          {
            "full_block_cosine": 0.014698108658194542
          },
          {
            "full_block_cosine": -0.005328537430614233
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.258288383483887
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.497790336608887
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8737812638282776
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.985778570175171
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.996557235717773
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.9027507305145264
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.2694485187530518
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.380878448486328
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.3295824527740479
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.36117953062057495
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.6876306533813477
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.1221076250076294
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.8961708545684814
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.0144084692001343
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.1937212944030762
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.55413818359375
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.056513786315918
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.247102737426758
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.364596366882324
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 16.54076385498047
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.74790096282959
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.772104263305664
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.509812355041504
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.209534645080566
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.038138389587402
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.738377571105957
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.519110679626465
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.72397518157959
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.985482215881348
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.52056360244751
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.33846664428711
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.171278953552246
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": 0.19659051299095154
          },
          {
            "full_block_cosine": 0.2085634469985962
          },
          {
            "full_block_cosine": 0.07752367854118347
          },
          {
            "full_block_cosine": 0.09856097400188446
          },
          {
            "full_block_cosine": 0.049839943647384644
          },
          {
            "full_block_cosine": 0.07182947546243668
          },
          {
            "full_block_cosine": 0.20370686054229736
          },
          {
            "full_block_cosine": 0.29171764850616455
          },
          {
            "full_block_cosine": -0.2190534472465515
          },
          {
            "full_block_cosine": -0.08202530443668365
          },
          {
            "full_block_cosine": 0.1375119388103485
          },
          {
            "full_block_cosine": -0.10878043621778488
          },
          {
            "full_block_cosine": 0.09871713072061539
          },
          {
            "full_block_cosine": 0.015373725444078445
          },
          {
            "full_block_cosine": 0.07369096577167511
          },
          {
            "full_block_cosine": 0.2520318329334259
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    },
    "latest": {
      "checkpoint_epoch_zero_based": 76,
      "checkpoint_sha256": "52b5d61a01030b2acd2f14a48137caa9b39f0f652e1be00653c502519c64abf7",
      "model_tensor_sha256": "a6d68e00809dca75403fbacf7cab230521f9aba3bd5be334f7d8f2802c8f2637",
      "original_diagnostic_sha256": "e0699178ff9eb6e211738e69ce65657f50e339fd96617d0965e85de7cc0f2b9e",
      "qids": [
        [
          "train12379",
          "train714",
          "train5246",
          "train6874",
          "train10461",
          "train10087",
          "train1159",
          "train852",
          "train2384",
          "train1373",
          "train596",
          "train9855",
          "train724",
          "train7556",
          "train6878",
          "train10480"
        ],
        [
          "train9665",
          "train10386",
          "train6567",
          "train10435",
          "train7718",
          "train11356",
          "train9333",
          "train7905",
          "train4520",
          "train1745",
          "train7639",
          "train4804",
          "train7719",
          "train9118",
          "train7606",
          "train7669"
        ],
        [
          "train12217",
          "train3802",
          "train1458",
          "train5221",
          "train11798",
          "train1715",
          "train7868",
          "train12252",
          "train9034",
          "train6213",
          "train809",
          "train3797",
          "train8969",
          "train4079",
          "train1413",
          "train5629"
        ],
        [
          "train9013",
          "train8429",
          "train4326",
          "train455",
          "train4096",
          "train142",
          "train5022",
          "train2755",
          "train10248",
          "train11558",
          "train1399",
          "train10975",
          "train2883",
          "train7513",
          "train2195",
          "train5110"
        ],
        [
          "train12400",
          "train5496",
          "train9416",
          "train11778",
          "train186",
          "train6364",
          "train12046",
          "train1098",
          "train3108",
          "train7705",
          "train5372",
          "train10161",
          "train12078",
          "train6388",
          "train9635",
          "train613"
        ],
        [
          "train10749",
          "train11092",
          "train7605",
          "train10951",
          "train1670",
          "train11281",
          "train2829",
          "train8158",
          "train2514",
          "train5780",
          "train10615",
          "train2807",
          "train1851",
          "train8037",
          "train5583",
          "train6184"
        ],
        [
          "train10075",
          "train6934",
          "train4604",
          "train8112",
          "train9470",
          "train4727",
          "train7116",
          "train9997",
          "train10938",
          "train6756",
          "train1592",
          "train9559",
          "train7721",
          "train5614",
          "train11377",
          "train1264"
        ],
        [
          "train2318",
          "train1160",
          "train11079",
          "train9625",
          "train1545",
          "train895",
          "train705",
          "train12181",
          "train2065",
          "train4220",
          "train9493",
          "train7977",
          "train2316",
          "train7528",
          "train11620",
          "train8008"
        ],
        [
          "train10901",
          "train3862",
          "train9106",
          "train5080",
          "train8199",
          "train3905",
          "train1596",
          "train200",
          "train7885",
          "train9203",
          "train6816",
          "train9452",
          "train10401",
          "train3258",
          "train3317",
          "train7549"
        ],
        [
          "train6352",
          "train2520",
          "train8748",
          "train9370",
          "train1836",
          "train6009",
          "train8678",
          "train4305",
          "train9829",
          "train1985",
          "train6166",
          "train8244",
          "train1894",
          "train35",
          "train375",
          "train4943"
        ],
        [
          "train7012",
          "train8018",
          "train5006",
          "train3169",
          "train5149",
          "train4476",
          "train6686",
          "train12113",
          "train9422",
          "train6719",
          "train9476",
          "train10208",
          "train4354",
          "train7754",
          "train9849",
          "train4940"
        ],
        [
          "train3635",
          "train7592",
          "train11107",
          "train2189",
          "train7255",
          "train3029",
          "train5160",
          "train6647",
          "train3530",
          "train4834",
          "train11612",
          "train4986",
          "train7403",
          "train7274",
          "train1623",
          "train9695"
        ],
        [
          "train9308",
          "train4991",
          "train9532",
          "train4418",
          "train10154",
          "train6397",
          "train1770",
          "train10781",
          "train12015",
          "train2856",
          "train4716",
          "train1127",
          "train2556",
          "train3839",
          "train236",
          "train468"
        ],
        [
          "train3856",
          "train8177",
          "train11087",
          "train2951",
          "train10603",
          "train6209",
          "train4350",
          "train3350",
          "train10748",
          "train3516",
          "train8728",
          "train2797",
          "train10158",
          "train2930",
          "train6322",
          "train7448"
        ],
        [
          "train1859",
          "train11928",
          "train1815",
          "train4993",
          "train6419",
          "train4204",
          "train8196",
          "train1310",
          "train11376",
          "train88",
          "train1487",
          "train2454",
          "train3145",
          "train1040",
          "train5744",
          "train7238"
        ],
        [
          "train2692",
          "train6734",
          "train2678",
          "train749",
          "train2209",
          "train1703",
          "train3113",
          "train1402",
          "train2149",
          "train6807",
          "train3548",
          "train10619",
          "train11718",
          "train5555",
          "train9080",
          "train4559"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.5669078379869461
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 3.4461100101470947
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.04287859424948692,
          "negative_fraction": 0.3125
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.07934609241783619
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.514900207519531
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.001339675160124898,
          "negative_fraction": 0.4375
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 1.4378502368927002
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 9.432656288146973
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.0309860585257411,
          "negative_fraction": 0.3125
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.086979627609253
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.8711532354354858
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.013867349363863468
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8533948063850403
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.6037094593048096
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.9168224334716797
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.28042086958885193
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 11.021540641784668
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.3856475353240967
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.19300585985183716
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.11960578709840775
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.17720547318458557
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.16253916919231415
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.007537306752055883
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.2894994020462036
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.049097418785095215
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.475513219833374
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.491057872772217
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.4167068004608154
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8054051399230957
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.18386697769165
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.069124698638916
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8794522285461426
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.768988132476807
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.660736560821533
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.067772626876831
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.549583435058594
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1382787227630615
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.0941765308380127
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1662371158599854
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8771162033081055
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.6624958515167236
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.07551561295986176
          },
          {
            "full_block_cosine": -0.027771513909101486
          },
          {
            "full_block_cosine": 0.0747845396399498
          },
          {
            "full_block_cosine": 0.03190222755074501
          },
          {
            "full_block_cosine": 0.050883643329143524
          },
          {
            "full_block_cosine": -0.0477815717458725
          },
          {
            "full_block_cosine": 0.11881308257579803
          },
          {
            "full_block_cosine": 0.6857807040214539
          },
          {
            "full_block_cosine": -0.00847142655402422
          },
          {
            "full_block_cosine": 0.03326677158474922
          },
          {
            "full_block_cosine": 0.07236727327108383
          },
          {
            "full_block_cosine": -0.049814388155937195
          },
          {
            "full_block_cosine": 0.03487354516983032
          },
          {
            "full_block_cosine": 0.10272792726755142
          },
          {
            "full_block_cosine": 0.11445020139217377
          },
          {
            "full_block_cosine": -0.08392313122749329
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5365959405899048
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.20840419828891754
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0045825713314116
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10198740661144257
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.41159600019454956
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3337293267250061
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.045530810952186584
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.4281952381134033
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.30687597393989563
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.05670477822422981
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.012314814142882824
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.024790482595562935
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03460066765546799
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0021062856540083885
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.23740197718143463
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01176088210195303
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.217905521392822
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.170368194580078
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.6148529052734375
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.2786478996276855
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.414947509765625
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.316622257232666
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.003901958465576
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.965046405792236
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.25689697265625
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.714592218399048
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.348595142364502
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.743288040161133
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.871615409851074
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.13509464263916
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.822509765625
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.4822540283203125
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": 0.001187575631774962
          },
          {
            "full_block_cosine": 0.007435675710439682
          },
          {
            "full_block_cosine": 0.006211588624864817
          },
          {
            "full_block_cosine": 0.006560719106346369
          },
          {
            "full_block_cosine": 0.0017092524794861674
          },
          {
            "full_block_cosine": -0.00031656085047870874
          },
          {
            "full_block_cosine": -0.0018919655121862888
          },
          {
            "full_block_cosine": 0.07604560256004333
          },
          {
            "full_block_cosine": 0.001491774688474834
          },
          {
            "full_block_cosine": 0.019711913540959358
          },
          {
            "full_block_cosine": -0.001822858233936131
          },
          {
            "full_block_cosine": -0.0010516569018363953
          },
          {
            "full_block_cosine": -0.011375918984413147
          },
          {
            "full_block_cosine": -0.011135912500321865
          },
          {
            "full_block_cosine": 0.002160297706723213
          },
          {
            "full_block_cosine": -0.034497711807489395
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.528668403625488
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.796030044555664
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.043780624866485596
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.0351035594940186
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.604864597320557
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3476061820983887
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8405969142913818
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 48.80076599121094
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.412131309509277
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3112432360649109
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.354513019323349
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6739163398742676
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3209242522716522
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.016248080879449844
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.930971145629883
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.11711922287940979
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.405348777770996
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.628341674804688
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.88648796081543
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.321081638336182
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.581161499023438
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.77099609375
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.941205978393555
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 21.05955696105957
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.286916732788086
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.214616775512695
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 12.089686393737793
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.514244556427002
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.166043281555176
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.309821128845215
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.6668901443481445
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.45996379852295
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": 0.07500217854976654
          },
          {
            "full_block_cosine": -0.006523762829601765
          },
          {
            "full_block_cosine": 0.09281165152788162
          },
          {
            "full_block_cosine": 0.025091340765357018
          },
          {
            "full_block_cosine": 0.02449178509414196
          },
          {
            "full_block_cosine": -0.00536368228495121
          },
          {
            "full_block_cosine": 0.10737095028162003
          },
          {
            "full_block_cosine": 0.9048970341682434
          },
          {
            "full_block_cosine": 0.04427729547023773
          },
          {
            "full_block_cosine": 0.11438256502151489
          },
          {
            "full_block_cosine": 0.12476857751607895
          },
          {
            "full_block_cosine": -0.0631791278719902
          },
          {
            "full_block_cosine": 0.028006048873066902
          },
          {
            "full_block_cosine": -0.0005311943241395056
          },
          {
            "full_block_cosine": 0.0339660681784153
          },
          {
            "full_block_cosine": -0.11308107525110245
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    }
  },
  "interpretation": "S+ only, eval mode local geometry; unused tensors treated as zero in full-block cosine. Original norms used only the jointly differentiable tensor intersection; detail fixes interpretation without overwriting original output. Inactive saliency is unavailable, not agreement. No S- localization gradient is inferred."
}
```

## diagnostics/sit/baseline/GRADIENT_RELATIONS_best.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/best.ckpt",
  "checkpoint_sha256": "67dadc67ff6018741578ed0a405d59c608b07d7161b9bbb7cbe76cc35557a6f3",
  "checkpoint_epoch_zero_based": 11,
  "executed_source_sha256": "0cefac0e2209e91c37897790ccc595c159083f570579c9996f2663d10a5af524",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train12379",
      "train714",
      "train5246",
      "train6874",
      "train10461",
      "train10087",
      "train1159",
      "train852",
      "train2384",
      "train1373",
      "train596",
      "train9855",
      "train724",
      "train7556",
      "train6878",
      "train10480"
    ],
    [
      "train9665",
      "train10386",
      "train6567",
      "train10435",
      "train7718",
      "train11356",
      "train9333",
      "train7905",
      "train4520",
      "train1745",
      "train7639",
      "train4804",
      "train7719",
      "train9118",
      "train7606",
      "train7669"
    ],
    [
      "train12217",
      "train3802",
      "train1458",
      "train5221",
      "train11798",
      "train1715",
      "train7868",
      "train12252",
      "train9034",
      "train6213",
      "train809",
      "train3797",
      "train8969",
      "train4079",
      "train1413",
      "train5629"
    ],
    [
      "train9013",
      "train8429",
      "train4326",
      "train455",
      "train4096",
      "train142",
      "train5022",
      "train2755",
      "train10248",
      "train11558",
      "train1399",
      "train10975",
      "train2883",
      "train7513",
      "train2195",
      "train5110"
    ],
    [
      "train12400",
      "train5496",
      "train9416",
      "train11778",
      "train186",
      "train6364",
      "train12046",
      "train1098",
      "train3108",
      "train7705",
      "train5372",
      "train10161",
      "train12078",
      "train6388",
      "train9635",
      "train613"
    ],
    [
      "train10749",
      "train11092",
      "train7605",
      "train10951",
      "train1670",
      "train11281",
      "train2829",
      "train8158",
      "train2514",
      "train5780",
      "train10615",
      "train2807",
      "train1851",
      "train8037",
      "train5583",
      "train6184"
    ],
    [
      "train10075",
      "train6934",
      "train4604",
      "train8112",
      "train9470",
      "train4727",
      "train7116",
      "train9997",
      "train10938",
      "train6756",
      "train1592",
      "train9559",
      "train7721",
      "train5614",
      "train11377",
      "train1264"
    ],
    [
      "train2318",
      "train1160",
      "train11079",
      "train9625",
      "train1545",
      "train895",
      "train705",
      "train12181",
      "train2065",
      "train4220",
      "train9493",
      "train7977",
      "train2316",
      "train7528",
      "train11620",
      "train8008"
    ],
    [
      "train10901",
      "train3862",
      "train9106",
      "train5080",
      "train8199",
      "train3905",
      "train1596",
      "train200",
      "train7885",
      "train9203",
      "train6816",
      "train9452",
      "train10401",
      "train3258",
      "train3317",
      "train7549"
    ],
    [
      "train6352",
      "train2520",
      "train8748",
      "train9370",
      "train1836",
      "train6009",
      "train8678",
      "train4305",
      "train9829",
      "train1985",
      "train6166",
      "train8244",
      "train1894",
      "train35",
      "train375",
      "train4943"
    ],
    [
      "train7012",
      "train8018",
      "train5006",
      "train3169",
      "train5149",
      "train4476",
      "train6686",
      "train12113",
      "train9422",
      "train6719",
      "train9476",
      "train10208",
      "train4354",
      "train7754",
      "train9849",
      "train4940"
    ],
    [
      "train3635",
      "train7592",
      "train11107",
      "train2189",
      "train7255",
      "train3029",
      "train5160",
      "train6647",
      "train3530",
      "train4834",
      "train11612",
      "train4986",
      "train7403",
      "train7274",
      "train1623",
      "train9695"
    ],
    [
      "train9308",
      "train4991",
      "train9532",
      "train4418",
      "train10154",
      "train6397",
      "train1770",
      "train10781",
      "train12015",
      "train2856",
      "train4716",
      "train1127",
      "train2556",
      "train3839",
      "train236",
      "train468"
    ],
    [
      "train3856",
      "train8177",
      "train11087",
      "train2951",
      "train10603",
      "train6209",
      "train4350",
      "train3350",
      "train10748",
      "train3516",
      "train8728",
      "train2797",
      "train10158",
      "train2930",
      "train6322",
      "train7448"
    ],
    [
      "train1859",
      "train11928",
      "train1815",
      "train4993",
      "train6419",
      "train4204",
      "train8196",
      "train1310",
      "train11376",
      "train88",
      "train1487",
      "train2454",
      "train3145",
      "train1040",
      "train5744",
      "train7238"
    ],
    [
      "train2692",
      "train6734",
      "train2678",
      "train749",
      "train2209",
      "train1703",
      "train3113",
      "train1402",
      "train2149",
      "train6807",
      "train3548",
      "train10619",
      "train11718",
      "train5555",
      "train9080",
      "train4559"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.08515522629022598,
      "negative_fraction": 0.1875,
      "cosines": [
        0.28879424929618835,
        0.24945203959941864,
        0.06752023100852966,
        0.029570631682872772,
        0.14443714916706085,
        0.030908018350601196,
        0.07495509833097458,
        0.09535535424947739,
        -0.07547663152217865,
        -0.033220548182725906,
        0.11475436389446259,
        -0.04734154790639877,
        0.10929034650325775,
        0.07329016178846359,
        0.21156901121139526,
        0.24671822786331177
      ],
      "gradient_norms": [
        {
          "exist_norm": 2.288727045059204,
          "other_norm": 2.1574697494506836
        },
        {
          "exist_norm": 2.565065622329712,
          "other_norm": 2.479396343231201
        },
        {
          "exist_norm": 0.2965196669101715,
          "other_norm": 3.42202091217041
        },
        {
          "exist_norm": 1.0604310035705566,
          "other_norm": 3.1049482822418213
        },
        {
          "exist_norm": 1.4000482559204102,
          "other_norm": 2.2427563667297363
        },
        {
          "exist_norm": 0.9082579612731934,
          "other_norm": 3.981405258178711
        },
        {
          "exist_norm": 0.6099326610565186,
          "other_norm": 2.681246519088745
        },
        {
          "exist_norm": 2.3838255405426025,
          "other_norm": 2.115125894546509
        },
        {
          "exist_norm": 0.41228336095809937,
          "other_norm": 3.5447163581848145
        },
        {
          "exist_norm": 0.13837991654872894,
          "other_norm": 2.313795804977417
        },
        {
          "exist_norm": 0.4194374084472656,
          "other_norm": 3.4230408668518066
        },
        {
          "exist_norm": 0.3566816747188568,
          "other_norm": 2.0002434253692627
        },
        {
          "exist_norm": 1.0869252681732178,
          "other_norm": 2.608651876449585
        },
        {
          "exist_norm": 0.28515318036079407,
          "other_norm": 2.9094622135162354
        },
        {
          "exist_norm": 0.37809184193611145,
          "other_norm": 2.5043513774871826
        },
        {
          "exist_norm": 1.2957392930984497,
          "other_norm": 2.560241460800171
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.01929923053830862,
      "negative_fraction": 0.25,
      "cosines": [
        0.039089400321245193,
        0.09083165228366852,
        -0.015177182853221893,
        0.026144899427890778,
        0.022150753065943718,
        0.04467397928237915,
        0.04905008524656296,
        -0.010783323086798191,
        -0.07267995178699493,
        0.009603098966181278,
        0.0026775591541081667,
        0.016447708010673523,
        0.07348424941301346,
        0.014295682311058044,
        0.058952998369932175,
        -0.01445042621344328
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.8568698763847351,
          "other_norm": 1.3741700649261475
        },
        {
          "exist_norm": 0.8709448575973511,
          "other_norm": 1.423532247543335
        },
        {
          "exist_norm": 0.17358721792697906,
          "other_norm": 1.8894450664520264
        },
        {
          "exist_norm": 0.42837950587272644,
          "other_norm": 1.3968634605407715
        },
        {
          "exist_norm": 0.5826824307441711,
          "other_norm": 1.2939497232437134
        },
        {
          "exist_norm": 0.4710994362831116,
          "other_norm": 2.1245529651641846
        },
        {
          "exist_norm": 0.3396380543708801,
          "other_norm": 1.7010818719863892
        },
        {
          "exist_norm": 0.7542423605918884,
          "other_norm": 1.6236655712127686
        },
        {
          "exist_norm": 0.25911396741867065,
          "other_norm": 1.8861809968948364
        },
        {
          "exist_norm": 0.10048623383045197,
          "other_norm": 1.692261815071106
        },
        {
          "exist_norm": 0.2484443336725235,
          "other_norm": 1.5261337757110596
        },
        {
          "exist_norm": 0.2391122430562973,
          "other_norm": 1.7516005039215088
        },
        {
          "exist_norm": 0.46351924538612366,
          "other_norm": 1.6249972581863403
        },
        {
          "exist_norm": 0.14296658337116241,
          "other_norm": 1.7805129289627075
        },
        {
          "exist_norm": 0.25418347120285034,
          "other_norm": 1.3442294597625732
        },
        {
          "exist_norm": 0.5285130739212036,
          "other_norm": 1.9788860082626343
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.08804232627153397,
      "negative_fraction": 0.1875,
      "cosines": [
        0.19659049808979034,
        0.2085634171962738,
        0.07752367854118347,
        0.09856097400188446,
        0.04983993247151375,
        0.07182947546243668,
        0.20370684564113617,
        0.2917175889015198,
        -0.2190534621477127,
        -0.08202530443668365,
        0.1375119388103485,
        -0.10878044366836548,
        0.09871713072061539,
        0.01537372451275587,
        0.07369096577167511,
        0.2520318031311035
      ],
      "gradient_norms": [
        {
          "exist_norm": 8.258289337158203,
          "other_norm": 9.056513786315918
        },
        {
          "exist_norm": 9.497791290283203,
          "other_norm": 12.247102737426758
        },
        {
          "exist_norm": 0.8737813234329224,
          "other_norm": 8.36459732055664
        },
        {
          "exist_norm": 3.985778331756592,
          "other_norm": 16.5407657623291
        },
        {
          "exist_norm": 4.996557235717773,
          "other_norm": 8.74790096282959
        },
        {
          "exist_norm": 3.9027507305145264,
          "other_norm": 10.772104263305664
        },
        {
          "exist_norm": 2.269448757171631,
          "other_norm": 10.509812355041504
        },
        {
          "exist_norm": 10.380878448486328,
          "other_norm": 9.209535598754883
        },
        {
          "exist_norm": 1.3295824527740479,
          "other_norm": 10.038138389587402
        },
        {
          "exist_norm": 0.36117950081825256,
          "other_norm": 6.738377094268799
        },
        {
          "exist_norm": 1.687630534172058,
          "other_norm": 12.519110679626465
        },
        {
          "exist_norm": 1.1221075057983398,
          "other_norm": 12.72397518157959
        },
        {
          "exist_norm": 3.8961708545684814,
          "other_norm": 12.985483169555664
        },
        {
          "exist_norm": 1.0144084692001343,
          "other_norm": 7.520564079284668
        },
        {
          "exist_norm": 1.1937212944030762,
          "other_norm": 8.33846664428711
        },
        {
          "exist_norm": 3.554137945175171,
          "other_norm": 9.171278953552246
        }
      ]
    }
  },
  "state": "completed",
  "interpretation": "cross-checkpoint and cross-family evidence required; duplicated best/latest epoch is not independent evidence"
}
```

## diagnostics/sit/baseline/GRADIENT_RELATIONS_latest.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/diagnostics/sit/baseline/evaluation_bundle/latest.ckpt",
  "checkpoint_sha256": "52b5d61a01030b2acd2f14a48137caa9b39f0f652e1be00653c502519c64abf7",
  "checkpoint_epoch_zero_based": 76,
  "executed_source_sha256": "0cefac0e2209e91c37897790ccc595c159083f570579c9996f2663d10a5af524",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train12379",
      "train714",
      "train5246",
      "train6874",
      "train10461",
      "train10087",
      "train1159",
      "train852",
      "train2384",
      "train1373",
      "train596",
      "train9855",
      "train724",
      "train7556",
      "train6878",
      "train10480"
    ],
    [
      "train9665",
      "train10386",
      "train6567",
      "train10435",
      "train7718",
      "train11356",
      "train9333",
      "train7905",
      "train4520",
      "train1745",
      "train7639",
      "train4804",
      "train7719",
      "train9118",
      "train7606",
      "train7669"
    ],
    [
      "train12217",
      "train3802",
      "train1458",
      "train5221",
      "train11798",
      "train1715",
      "train7868",
      "train12252",
      "train9034",
      "train6213",
      "train809",
      "train3797",
      "train8969",
      "train4079",
      "train1413",
      "train5629"
    ],
    [
      "train9013",
      "train8429",
      "train4326",
      "train455",
      "train4096",
      "train142",
      "train5022",
      "train2755",
      "train10248",
      "train11558",
      "train1399",
      "train10975",
      "train2883",
      "train7513",
      "train2195",
      "train5110"
    ],
    [
      "train12400",
      "train5496",
      "train9416",
      "train11778",
      "train186",
      "train6364",
      "train12046",
      "train1098",
      "train3108",
      "train7705",
      "train5372",
      "train10161",
      "train12078",
      "train6388",
      "train9635",
      "train613"
    ],
    [
      "train10749",
      "train11092",
      "train7605",
      "train10951",
      "train1670",
      "train11281",
      "train2829",
      "train8158",
      "train2514",
      "train5780",
      "train10615",
      "train2807",
      "train1851",
      "train8037",
      "train5583",
      "train6184"
    ],
    [
      "train10075",
      "train6934",
      "train4604",
      "train8112",
      "train9470",
      "train4727",
      "train7116",
      "train9997",
      "train10938",
      "train6756",
      "train1592",
      "train9559",
      "train7721",
      "train5614",
      "train11377",
      "train1264"
    ],
    [
      "train2318",
      "train1160",
      "train11079",
      "train9625",
      "train1545",
      "train895",
      "train705",
      "train12181",
      "train2065",
      "train4220",
      "train9493",
      "train7977",
      "train2316",
      "train7528",
      "train11620",
      "train8008"
    ],
    [
      "train10901",
      "train3862",
      "train9106",
      "train5080",
      "train8199",
      "train3905",
      "train1596",
      "train200",
      "train7885",
      "train9203",
      "train6816",
      "train9452",
      "train10401",
      "train3258",
      "train3317",
      "train7549"
    ],
    [
      "train6352",
      "train2520",
      "train8748",
      "train9370",
      "train1836",
      "train6009",
      "train8678",
      "train4305",
      "train9829",
      "train1985",
      "train6166",
      "train8244",
      "train1894",
      "train35",
      "train375",
      "train4943"
    ],
    [
      "train7012",
      "train8018",
      "train5006",
      "train3169",
      "train5149",
      "train4476",
      "train6686",
      "train12113",
      "train9422",
      "train6719",
      "train9476",
      "train10208",
      "train4354",
      "train7754",
      "train9849",
      "train4940"
    ],
    [
      "train3635",
      "train7592",
      "train11107",
      "train2189",
      "train7255",
      "train3029",
      "train5160",
      "train6647",
      "train3530",
      "train4834",
      "train11612",
      "train4986",
      "train7403",
      "train7274",
      "train1623",
      "train9695"
    ],
    [
      "train9308",
      "train4991",
      "train9532",
      "train4418",
      "train10154",
      "train6397",
      "train1770",
      "train10781",
      "train12015",
      "train2856",
      "train4716",
      "train1127",
      "train2556",
      "train3839",
      "train236",
      "train468"
    ],
    [
      "train3856",
      "train8177",
      "train11087",
      "train2951",
      "train10603",
      "train6209",
      "train4350",
      "train3350",
      "train10748",
      "train3516",
      "train8728",
      "train2797",
      "train10158",
      "train2930",
      "train6322",
      "train7448"
    ],
    [
      "train1859",
      "train11928",
      "train1815",
      "train4993",
      "train6419",
      "train4204",
      "train8196",
      "train1310",
      "train11376",
      "train88",
      "train1487",
      "train2454",
      "train3145",
      "train1040",
      "train5744",
      "train7238"
    ],
    [
      "train2692",
      "train6734",
      "train2678",
      "train749",
      "train2209",
      "train1703",
      "train3113",
      "train1402",
      "train2149",
      "train6807",
      "train3548",
      "train10619",
      "train11718",
      "train5555",
      "train9080",
      "train4559"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.042878592386841774,
      "negative_fraction": 0.3125,
      "cosines": [
        0.07551560550928116,
        -0.027771515771746635,
        0.07478455454111099,
        0.03190222755074501,
        0.05088363215327263,
        -0.04778158664703369,
        0.11881308257579803,
        0.6857807040214539,
        -0.008471429347991943,
        0.03326676785945892,
        0.07236727327108383,
        -0.04981440305709839,
        0.03487355262041092,
        0.10272793471813202,
        0.11445020139217377,
        -0.08392314612865448
      ],
      "gradient_norms": [
        {
          "exist_norm": 3.086979627609253,
          "other_norm": 3.475512981414795
        },
        {
          "exist_norm": 1.8711532354354858,
          "other_norm": 3.4910576343536377
        },
        {
          "exist_norm": 0.013867348432540894,
          "other_norm": 3.4167070388793945
        },
        {
          "exist_norm": 0.8533949255943298,
          "other_norm": 2.8054049015045166
        },
        {
          "exist_norm": 2.6037099361419678,
          "other_norm": 4.183867454528809
        },
        {
          "exist_norm": 1.9168224334716797,
          "other_norm": 4.069124698638916
        },
        {
          "exist_norm": 0.28042086958885193,
          "other_norm": 2.8794522285461426
        },
        {
          "exist_norm": 11.021539688110352,
          "other_norm": 4.768988609313965
        },
        {
          "exist_norm": 2.3856475353240967,
          "other_norm": 3.6607367992401123
        },
        {
          "exist_norm": 0.19300585985183716,
          "other_norm": 3.067772626876831
        },
        {
          "exist_norm": 0.11960577219724655,
          "other_norm": 5.549583911895752
        },
        {
          "exist_norm": 0.17720545828342438,
          "other_norm": 3.1382787227630615
        },
        {
          "exist_norm": 0.16253915429115295,
          "other_norm": 2.0941762924194336
        },
        {
          "exist_norm": 0.007537307217717171,
          "other_norm": 3.1662373542785645
        },
        {
          "exist_norm": 1.289499282836914,
          "other_norm": 2.8771159648895264
        },
        {
          "exist_norm": 0.049097415059804916,
          "other_norm": 3.6624958515167236
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.0037718364037573338,
      "negative_fraction": 0.4375,
      "cosines": [
        0.0038194942753762007,
        0.03198068216443062,
        0.015894344076514244,
        0.022121572867035866,
        0.003724178532138467,
        -0.0010367321083322167,
        -0.004953188356012106,
        0.22936862707138062,
        0.004533517174422741,
        0.05143188685178757,
        -0.006236911751329899,
        -0.003951170947402716,
        -0.0423598550260067,
        -0.03730243071913719,
        0.00724991038441658,
        -0.11367974430322647
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.5365959405899048,
          "other_norm": 1.3114513158798218
        },
        {
          "exist_norm": 0.20840418338775635,
          "other_norm": 1.4346429109573364
        },
        {
          "exist_norm": 0.004582570865750313,
          "other_norm": 1.8035082817077637
        },
        {
          "exist_norm": 0.10198739171028137,
          "other_norm": 1.268942952156067
        },
        {
          "exist_norm": 0.41159602999687195,
          "other_norm": 2.0262887477874756
        },
        {
          "exist_norm": 0.3337293267250061,
          "other_norm": 1.6234064102172852
        },
        {
          "exist_norm": 0.04553081467747688,
          "other_norm": 1.147398591041565
        },
        {
          "exist_norm": 1.4281952381134033,
          "other_norm": 1.6461271047592163
        },
        {
          "exist_norm": 0.30687591433525085,
          "other_norm": 1.729803204536438
        },
        {
          "exist_norm": 0.05670477822422981,
          "other_norm": 1.4236642122268677
        },
        {
          "exist_norm": 0.012314814142882824,
          "other_norm": 1.5632308721542358
        },
        {
          "exist_norm": 0.024790482595562935,
          "other_norm": 1.2624894380569458
        },
        {
          "exist_norm": 0.03460066765546799,
          "other_norm": 1.0397387742996216
        },
        {
          "exist_norm": 0.0021062856540083885,
          "other_norm": 1.2344515323638916
        },
        {
          "exist_norm": 0.23740194737911224,
          "other_norm": 1.139016032218933
        },
        {
          "exist_norm": 0.01176088210195303,
          "other_norm": 1.6636673212051392
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.0309860622510314,
      "negative_fraction": 0.3125,
      "cosines": [
        0.07500218600034714,
        -0.006523760035634041,
        0.09281165897846222,
        0.025091346353292465,
        0.024491790682077408,
        -0.005363680887967348,
        0.10737094283103943,
        0.904897153377533,
        0.04427729919552803,
        0.11438252776861191,
        0.12476857751607895,
        -0.0631791278719902,
        0.0280060563236475,
        -0.0005311923450790346,
        0.0339660681784153,
        -0.11308109015226364
      ],
      "gradient_norms": [
        {
          "exist_norm": 6.528668403625488,
          "other_norm": 9.405349731445312
        },
        {
          "exist_norm": 6.796030044555664,
          "other_norm": 10.628342628479004
        },
        {
          "exist_norm": 0.043780624866485596,
          "other_norm": 9.886487007141113
        },
        {
          "exist_norm": 2.0351035594940186,
          "other_norm": 7.32108211517334
        },
        {
          "exist_norm": 7.604864597320557,
          "other_norm": 9.581161499023438
        },
        {
          "exist_norm": 3.3476061820983887,
          "other_norm": 9.770997047424316
        },
        {
          "exist_norm": 0.8405969142913818,
          "other_norm": 7.941206455230713
        },
        {
          "exist_norm": 48.80076599121094,
          "other_norm": 21.059555053710938
        },
        {
          "exist_norm": 9.412132263183594,
          "other_norm": 10.286916732788086
        },
        {
          "exist_norm": 0.3112432360649109,
          "other_norm": 8.214617729187012
        },
        {
          "exist_norm": 0.3545130491256714,
          "other_norm": 12.089686393737793
        },
        {
          "exist_norm": 0.6739163994789124,
          "other_norm": 7.514244556427002
        },
        {
          "exist_norm": 0.32092422246932983,
          "other_norm": 6.166043281555176
        },
        {
          "exist_norm": 0.016248079016804695,
          "other_norm": 9.309821128845215
        },
        {
          "exist_norm": 2.930971145629883,
          "other_norm": 7.6668901443481445
        },
        {
          "exist_norm": 0.11711922287940979,
          "other_norm": 9.45996379852295
        }
      ]
    }
  },
  "state": "completed",
  "interpretation": "cross-checkpoint and cross-family evidence required; duplicated best/latest epoch is not independent evidence"
}
```

## diagnostics/sit/baseline/INPUT_SENSITIVITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "rows": 976,
  "videos": 452,
  "manifest_sha256": "d0790af2d7d4d595d65f38aa7e1933ce114d6f8eb10433649146d887fa226107",
  "identity_max_abs_error": 0.0,
  "summaries": {
    "identity": {
      "exist_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      }
    },
    "zero_visual": {
      "exist_abs_delta": {
        "row_mean": 0.015844794692563228,
        "video_mean": 0.013559612985017478,
        "video_bootstrap_ci95": [
          0.011536178862243528,
          0.015605512692240208
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.10348360655737705,
        "video_mean": 0.09184049726085124,
        "video_bootstrap_ci95": [
          0.06867322482090182,
          0.116042193426043
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.11326554910753106,
        "video_mean": 0.10620356016536076,
        "video_bootstrap_ci95": [
          0.09297239304005274,
          0.12082254778040494
        ]
      }
    },
    "shuffle_time": {
      "exist_abs_delta": {
        "row_mean": 0.0036353297287323436,
        "video_mean": 0.002823410222280945,
        "video_bootstrap_ci95": [
          0.002206635889218507,
          0.0035086949845148808
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.017418032786885244,
        "video_mean": 0.013053097345132745,
        "video_bootstrap_ci95": [
          0.006120022123893805,
          0.021165191740412977
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.018766387705462146,
        "video_mean": 0.015693561146600945,
        "video_bootstrap_ci95": [
          0.011516324367358579,
          0.020584653088229068
        ]
      }
    },
    "zero_clip": {
      "exist_abs_delta": {
        "row_mean": 0.009976962016376316,
        "video_mean": 0.008404745113966439,
        "video_bootstrap_ci95": [
          0.007173572247820443,
          0.00970397690758486
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.08094262295081968,
        "video_mean": 0.06702486304256215,
        "video_bootstrap_ci95": [
          0.047555704804045515,
          0.08673975453013064
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.07508602797542317,
        "video_mean": 0.06617970334348695,
        "video_bootstrap_ci95": [
          0.05297404279307919,
          0.07886240343253213
        ]
      }
    },
    "zero_slowfast": {
      "exist_abs_delta": {
        "row_mean": 0.015253914001046634,
        "video_mean": 0.01287504108367567,
        "video_bootstrap_ci95": [
          0.010504347905493079,
          0.015219265870974441
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.29713114754098363,
        "video_mean": 0.27114412136536037,
        "video_bootstrap_ci95": [
          0.23587823957016438,
          0.30826972713864315
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.23067825537587164,
        "video_mean": 0.21306157895248873,
        "video_bootstrap_ci95": [
          0.19062980232638496,
          0.23726621365309514
        ]
      }
    }
  },
  "limitations": "Sensitivity of frozen model, not necessity/causal proof. Zeroing is out of distribution; shuffle preserves positions. No perturbed-label AUROC, R1, FRR or RR computed. Raw top span before official temporal postprocessing; original official gate is a scalar per row and does not change exact-precision slot ranking."
}
```

## diagnostics/sit/baseline/INPUT_SENSITIVITY_MANIFEST.json

```json
{
  "state": "frozen_before_inference",
  "seed": 3407,
  "training_updates": 0,
  "checkpoint_sha256": "67dadc67ff6018741578ed0a405d59c608b07d7161b9bbb7cbe76cc35557a6f3",
  "checkpoint_epoch_zero_based": 11,
  "source_sha256": "d980356f74f3bed35178abf6120b6ea99e8ac23aaef7748dd2e8a4f42f38dec8",
  "view_sha256": "f1ee87f31d4e0257a2e3eb0d794b1ab55aa8024c51aa2967508d15d35d95b43c",
  "qids": [
    "train12",
    "train31",
    "train55",
    "train62",
    "train81",
    "train82",
    "train83",
    "train113",
    "train115",
    "train128",
    "train153",
    "train164",
    "train165",
    "train229",
    "train231",
    "train233",
    "train274",
    "train275",
    "train308",
    "train382",
    "train383",
    "train384",
    "train385",
    "train403",
    "train418",
    "train471",
    "train472",
    "train488",
    "train581",
    "train598",
    "train630",
    "train661",
    "train662",
    "train842",
    "train857",
    "train858",
    "train878",
    "train880",
    "train912",
    "train940",
    "train942",
    "train944",
    "train956",
    "train979",
    "train1031",
    "train1032",
    "train1048",
    "train1049",
    "train1070",
    "train1145",
    "train1146",
    "train1211",
    "train1232",
    "train1240",
    "train1241",
    "train1243",
    "train1307",
    "train1355",
    "train1433",
    "train1441",
    "train1443",
    "train1495",
    "train1568",
    "train1583",
    "train1584",
    "train1585",
    "train1650",
    "train1651",
    "train1656",
    "train1666",
    "train1692",
    "train1716",
    "train1732",
    "train1733",
    "train1870",
    "train1874",
    "train1922",
    "train1923",
    "train1924",
    "train2004",
    "train2021",
    "train2022",
    "train2025",
    "train2099",
    "train2110",
    "train2112",
    "train2114",
    "train2123",
    "train2125",
    "train2134",
    "train2139",
    "train2159",
    "train2226",
    "train2227",
    "train2235",
    "train2260",
    "train2272",
    "train2273",
    "train2339",
    "train2340",
    "train2363",
    "train2364",
    "train2369",
    "train2370",
    "train2374",
    "train2378",
    "train2379",
    "train2387",
    "train2406",
    "train2409",
    "train2458",
    "train2494",
    "train2496",
    "train2550",
    "train2567",
    "train2568",
    "train2578",
    "train2579",
    "train2588",
    "train2597",
    "train2599",
    "train2610",
    "train2643",
    "train2702",
    "train2716",
    "train2717",
    "train2765",
    "train2776",
    "train2851",
    "train2879",
    "train2892",
    "train2900",
    "train2904",
    "train2941",
    "train2954",
    "train2955",
    "train2985",
    "train2996",
    "train3035",
    "train3067",
    "train3068",
    "train3074",
    "train3138",
    "train3141",
    "train3151",
    "train3157",
    "train3181",
    "train3288",
    "train3311",
    "train3323",
    "train3344",
    "train3379",
    "train3391",
    "train3392",
    "train3399",
    "train3400",
    "train3433",
    "train3462",
    "train3464",
    "train3468",
    "train3611",
    "train3673",
    "train3706",
    "train3708",
    "train3714",
    "train3715",
    "train3717",
    "train3719",
    "train3733",
    "train3737",
    "train3778",
    "train3779",
    "train3786",
    "train3788",
    "train3790",
    "train3816",
    "train3832",
    "train3840",
    "train3847",
    "train3976",
    "train3977",
    "train4013",
    "train4037",
    "train4067",
    "train4087",
    "train4118",
    "train4121",
    "train4137",
    "train4174",
    "train4175",
    "train4183",
    "train4296",
    "train4333",
    "train4334",
    "train4375",
    "train4376",
    "train4402",
    "train4403",
    "train4407",
    "train4433",
    "train4443",
    "train4444",
    "train4461",
    "train4486",
    "train4487",
    "train4544",
    "train4545",
    "train4549",
    "train4626",
    "train4629",
    "train4665",
    "train4712",
    "train4740",
    "train4756",
    "train4759",
    "train4781",
    "train4782",
    "train4805",
    "train4824",
    "train4826",
    "train4827",
    "train4835",
    "train4836",
    "train4888",
    "train4896",
    "train4903",
    "train4920",
    "train4926",
    "train4931",
    "train4932",
    "train4961",
    "train4962",
    "train4969",
    "train4973",
    "train5010",
    "train5012",
    "train5024",
    "train5025",
    "train5029",
    "train5041",
    "train5046",
    "train5058",
    "train5059",
    "train5099",
    "train5127",
    "train5164",
    "train5171",
    "train5212",
    "train5222",
    "train5232",
    "train5233",
    "train5236",
    "train5250",
    "train5251",
    "train5297",
    "train5298",
    "train5301",
    "train5330",
    "train5355",
    "train5392",
    "train5394",
    "train5454",
    "train5456",
    "train5461",
    "train5462",
    "train5502",
    "train5511",
    "train5514",
    "train5548",
    "train5573",
    "train5576",
    "train5585",
    "train5586",
    "train5593",
    "train5596",
    "train5608",
    "train5728",
    "train5736",
    "train5749",
    "train5828",
    "train5842",
    "train5844",
    "train5852",
    "train5853",
    "train5862",
    "train5863",
    "train5945",
    "train5959",
    "train5996",
    "train5997",
    "train6015",
    "train6034",
    "train6036",
    "train6111",
    "train6127",
    "train6138",
    "train6203",
    "train6266",
    "train6267",
    "train6282",
    "train6283",
    "train6301",
    "train6303",
    "train6305",
    "train6319",
    "train6333",
    "train6351",
    "train6368",
    "train6466",
    "train6467",
    "train6520",
    "train6522",
    "train6532",
    "train6542",
    "train6585",
    "train6604",
    "train6648",
    "train6668",
    "train6681",
    "train6689",
    "train6699",
    "train6713",
    "train6767",
    "train6768",
    "train6799",
    "train6800",
    "train6833",
    "train6846",
    "train6849",
    "train6857",
    "train6900",
    "train6902",
    "train6903",
    "train6904",
    "train6906",
    "train6960",
    "train6961",
    "train6969",
    "train7017",
    "train7042",
    "train7043",
    "train7057",
    "train7059",
    "train7087",
    "train7126",
    "train7127",
    "train7131",
    "train7192",
    "train7214",
    "train7217",
    "train7244",
    "train7245",
    "train7307",
    "train7308",
    "train7320",
    "train7328",
    "train7329",
    "train7330",
    "train7339",
    "train7340",
    "train7386",
    "train7436",
    "train7439",
    "train7440",
    "train7442",
    "train7479",
    "train7509",
    "train7541",
    "train7545",
    "train7547",
    "train7571",
    "train7573",
    "train7581",
    "train7595",
    "train7683",
    "train7684",
    "train7702",
    "train7764",
    "train7809",
    "train7832",
    "train7838",
    "train7858",
    "train7860",
    "train7870",
    "train7916",
    "train7918",
    "train7929",
    "train7937",
    "train7962",
    "train7993",
    "train8055",
    "train8057",
    "train8065",
    "train8066",
    "train8118",
    "train8119",
    "train8120",
    "train8132",
    "train8135",
    "train8162",
    "train8181",
    "train8209",
    "train8249",
    "train8267",
    "train8271",
    "train8276",
    "train8286",
    "train8339",
    "train8367",
    "train8378",
    "train8380",
    "train8381",
    "train8382",
    "train8393",
    "train8394",
    "train8416",
    "train8487",
    "train8489",
    "train8530",
    "train8600",
    "train8601",
    "train8637",
    "train8639",
    "train8642",
    "train8658",
    "train8674",
    "train8703",
    "train8718",
    "train8719",
    "train8733",
    "train8752",
    "train8777",
    "train8797",
    "train8822",
    "train8852",
    "train8853",
    "train8911",
    "train8934",
    "train8935",
    "train8940",
    "train8943",
    "train8978",
    "train8992",
    "train9039",
    "train9083",
    "train9090",
    "train9096",
    "train9097",
    "train9107",
    "train9108",
    "train9148",
    "train9149",
    "train9150",
    "train9161",
    "train9163",
    "train9169",
    "train9170",
    "train9202",
    "train9230",
    "train9236",
    "train9373",
    "train9408",
    "train9466",
    "train9480",
    "train9568",
    "train9594",
    "train9654",
    "train9655",
    "train9683",
    "train9744",
    "train9758",
    "train9759",
    "train9761",
    "train9771",
    "train9786",
    "train9787",
    "train9788",
    "train9808",
    "train9812",
    "train9840",
    "train9888",
    "train9902",
    "train9903",
    "train9950",
    "train9992",
    "train9994",
    "train9998",
    "train10013",
    "train10028",
    "train10038",
    "train10039",
    "train10040",
    "train10095",
    "train10098",
    "train10117",
    "train10163",
    "train10167",
    "train10188",
    "train10192",
    "train10204",
    "train10305",
    "train10306",
    "train10325",
    "train10352",
    "train10353",
    "train10447",
    "train10451",
    "train10456",
    "train10458",
    "train10488",
    "train10498",
    "train10501",
    "train10502",
    "train10531",
    "train10547",
    "train10566",
    "train10592",
    "train10605",
    "train10648",
    "train10651",
    "train10702",
    "train10729",
    "train10735",
    "train10737",
    "train10764",
    "train10765",
    "train10795",
    "train10813",
    "train10815",
    "train10886",
    "train10887",
    "train10888",
    "train10896",
    "train10898",
    "train10911",
    "train10912",
    "train10925",
    "train10940",
    "train10946",
    "train10961",
    "train10969",
    "train10971",
    "train10983",
    "train10988",
    "train10989",
    "train10999",
    "train11005",
    "train11013",
    "train11049",
    "train11053",
    "train11064",
    "train11083",
    "train11104",
    "train11105",
    "train11112",
    "train11135",
    "train11146",
    "train11149",
    "train11156",
    "train11157",
    "train11159",
    "train11163",
    "train11164",
    "train11170",
    "train11172",
    "train11176",
    "train11197",
    "train11199",
    "train11204",
    "train11215",
    "train11219",
    "train11230",
    "train11240",
    "train11242",
    "train11243",
    "train11250",
    "train11328",
    "train11340",
    "train11341",
    "train11382",
    "train11383",
    "train11385",
    "train11475",
    "train11476",
    "train11482",
    "train11550",
    "train11579",
    "train11627",
    "train11705",
    "train11726",
    "train11753",
    "train11756",
    "train11757",
    "train11853",
    "train11854",
    "train11858",
    "train11880",
    "train11899",
    "train11900",
    "train11901",
    "train11922",
    "train11923",
    "train11953",
    "train11954",
    "train11978",
    "train11990",
    "train12055",
    "train12056",
    "train12067",
    "train12070",
    "train12084",
    "train12098",
    "train12135",
    "train12150",
    "train12153",
    "train12158",
    "train12219",
    "train12229",
    "train12244",
    "train12259",
    "train12271",
    "train12272",
    "train12326",
    "train12332",
    "train12354",
    "neg_0123f49ff5c49869",
    "neg_018516587239cb1c",
    "neg_0325808f25a901d5",
    "neg_042b1fb3f5c12b16",
    "neg_04b5513d5e674dd3",
    "neg_055e0bfb095287f8",
    "neg_059b173d4683cf1a",
    "neg_08bf8191490ff14b",
    "neg_093f49e32e660dda",
    "neg_095b2c36fd8ef3bd",
    "neg_09a13014fbfde423",
    "neg_09ece2125c06d232",
    "neg_0a1d7592a95d522e",
    "neg_0af91e16979072f6",
    "neg_0be7cd21f34a0d80",
    "neg_0c30b2804e1f2b35",
    "neg_0c69bdf9e9ef754d",
    "neg_0cee474d8129f426",
    "neg_0d8489b3f8ec5488",
    "neg_0e4e21344880ce62",
    "neg_0e67fa57abe21018",
    "neg_0e92758798a7de8d",
    "neg_0eb9a33ee3b7772c",
    "neg_0fa831b4608f790d",
    "neg_0ff8669398e64ed3",
    "neg_1088e2978c20a764",
    "neg_1099289c1fafd4b8",
    "neg_12767870545aa7a1",
    "neg_12c96add4a685924",
    "neg_1345491be20be8ad",
    "neg_13ce94adb890128c",
    "neg_14212ca99ab4e3e4",
    "neg_15cbf04e3ededaa6",
    "neg_17344cac102c418d",
    "neg_180baa1d541555b0",
    "neg_1966eecfd919fc00",
    "neg_19a717c46ef9e9e4",
    "neg_1a688b72c73b3f56",
    "neg_1ae0f1592adb24fa",
    "neg_1cb4cdca3e39ed32",
    "neg_1cf41a36d31ba8b9",
    "neg_1e4a296ffc6cdd98",
    "neg_1e91825a40167e95",
    "neg_1e958b4a775cc15d",
    "neg_20c8388f8c12a201",
    "neg_20ee5c66894dc837",
    "neg_2118d317cb9b0dda",
    "neg_2276d697d61e771d",
    "neg_22a9e134101e4704",
    "neg_2380f5fa486c229c",
    "neg_23e811c843cfa55e",
    "neg_2480371bdb5d33f2",
    "neg_24b14e867c1e088e",
    "neg_24d7c3a067974e11",
    "neg_278cdb1cdb1bdae9",
    "neg_291b8ef6279fecb6",
    "neg_2bca24e77d96aec5",
    "neg_2cd7ede2d9806040",
    "neg_2e37350e54b34ae8",
    "neg_2eaebbbae69f3384",
    "neg_2f3b3375e680e687",
    "neg_2fe9081a8fd5eddc",
    "neg_3195dc10f37869af",
    "neg_3234f8617aeb3af7",
    "neg_32dc1bdaad800d37",
    "neg_336121a106a54bc8",
    "neg_33bdc488301443cf",
    "neg_3441c9d1534a657e",
    "neg_34a6d2b4a4ea7496",
    "neg_35847bb4978c494f",
    "neg_39044064b21c5133",
    "neg_399ffea57f53b8c7",
    "neg_3a790fae795fd3d8",
    "neg_3bc8d04f18e97758",
    "neg_3bcc986551a5aeb2",
    "neg_3c6493a95421bd82",
    "neg_3ce8a356fcb8c3d5",
    "neg_3db0c3230411e701",
    "neg_3e3426987ea6634f",
    "neg_3f60944df7d9e8b6",
    "neg_3f7fb945ca0d9e18",
    "neg_3f98fa4d030550ce",
    "neg_3fca1604924ccba3",
    "neg_3fdc1aeb881dbd14",
    "neg_40c3020c90f824fe",
    "neg_4179e378a32ae404",
    "neg_417c2c7f12c86da9",
    "neg_43d7559561ac4b93",
    "neg_449fa41324cb3dfd",
    "neg_45040723b8827c2f",
    "neg_464426a26b9dbd7e",
    "neg_4649ad6bd22070ea",
    "neg_47455204fd5827bb",
    "neg_4756121ac0fba7e6",
    "neg_476ef34ffe19e538",
    "neg_499b0804ab4b8d87",
    "neg_49d6f7909cc833bd",
    "neg_49ee102fa1f95fda",
    "neg_4a2fbbac60e10033",
    "neg_4a5140ee6c020c4f",
    "neg_4c1796791843e75e",
    "neg_4c362705edd66431",
    "neg_4cac71e8eaf4e9ba",
    "neg_4ce0a40cc56c338c",
    "neg_4d2884d1079e5f50",
    "neg_4ea85ca1f10c9a48",
    "neg_4ee3b32b7eca68bb",
    "neg_506c831be5358f9e",
    "neg_51acc7bd980cd390",
    "neg_520ad737e2925755",
    "neg_5246b16e4fa28b88",
    "neg_534516fc851403af",
    "neg_546bb3286bf3ee47",
    "neg_54c7e8908e3335b6",
    "neg_54dd079ee4f6b033",
    "neg_555c8e270c960f93",
    "neg_558513b8eba9bcdb",
    "neg_57344eb0b8ed9199",
    "neg_57dc9e824219b3a9",
    "neg_583b7c8a151d9324",
    "neg_5900614ea23f191e",
    "neg_5993a4427e40e3b5",
    "neg_59cd2bfb8c76a69e",
    "neg_5ab6cca777a64320",
    "neg_5abd1fca17f7f0fc",
    "neg_5af5ec31f4a6ea31",
    "neg_5d433d71efc5ca71",
    "neg_5d516740e70d0520",
    "neg_5e16a87a80d8235b",
    "neg_5eb169daad4141b3",
    "neg_5ec71a92b6770eb9",
    "neg_5f43b6e9f0b8df7f",
    "neg_5fb1d10f005c9bc2",
    "neg_606c528057e08418",
    "neg_612b2fdc1179bace",
    "neg_6141729953832709",
    "neg_6244b39ff5931712",
    "neg_6277d4aa84d44ae6",
    "neg_641567864f25cd0f",
    "neg_65f0e84f49848ad7",
    "neg_6924c9410857ea67",
    "neg_69d537ade03b66e4",
    "neg_6a9ad31483a102b1",
    "neg_6aecbf261acc31f8",
    "neg_6b162d655b802e4d",
    "neg_6b5afed2f9eb55b6",
    "neg_6b7c4468117cbb0f",
    "neg_6bad1acff4e7314d",
    "neg_6be90c5ef9b29a6c",
    "neg_6c76729669e48779",
    "neg_6d5ad488966e43f2",
    "neg_71e563070c87e197",
    "neg_72151b678c786edc",
    "neg_72d60dc4b334b483",
    "neg_73c3d94050ce6715",
    "neg_742de04093d76f5f",
    "neg_746bb2a08aa47ff8",
    "neg_75f89bb6a2ea0989",
    "neg_76299e312092ee7b",
    "neg_77a1d69fa6133332",
    "neg_77c9ad8a453b18b8",
    "neg_787e61a3538ae5d6",
    "neg_79e38c4ce30ca986",
    "neg_7a0811103be8710a",
    "neg_7bb14d956bde0af0",
    "neg_7c1dce3afbcb6732",
    "neg_7c9281186821dda2",
    "neg_7ed05dbbd40de425",
    "neg_7f99369fef37f124",
    "neg_7f9ea4c914fbdac6",
    "neg_813b9655ad81ee9c",
    "neg_818fe1d5975645d4",
    "neg_82f0660f355de998",
    "neg_8387a3a3f17fd394",
    "neg_84cbbe6de2351d5c",
    "neg_85533e3a322e9744",
    "neg_85762752e3a68e79",
    "neg_857e3d8aa689f0eb",
    "neg_858bd2ba4ac9a4cd",
    "neg_85cc12404acf39dc",
    "neg_86c33ffac2a67983",
    "neg_8729e648a7e46ef9",
    "neg_8751f02f1b3103f0",
    "neg_87d7fe857ed5c177",
    "neg_87fce2824ed7bfcf",
    "neg_8b2e2116142f6e81",
    "neg_8b3cf612d2649a0a",
    "neg_8c2571a7bd1b90ad",
    "neg_8c5ec667c4448a7d",
    "neg_8d823b39d64f2181",
    "neg_8d9edcdfcd54ec96",
    "neg_8ddf19655e0f88f2",
    "neg_8e84759d43a0dc67",
    "neg_8f6a7ca3c6786f2d",
    "neg_9011ae82d3984518",
    "neg_902a7683c23bfd22",
    "neg_9126b619bf00e3c2",
    "neg_917d4b36c41f00b1",
    "neg_917dce516e2e5457",
    "neg_9206b731875e4790",
    "neg_92ece90fa8eb96f7",
    "neg_933b2475b417e910",
    "neg_952dcdf870aa332c",
    "neg_957106579ecfeb3e",
    "neg_96877b9835c4d75f",
    "neg_98467aad6a8e47b1",
    "neg_989a8484e8f98f6c",
    "neg_9959d402110713d7",
    "neg_9997d1ad26b746e3",
    "neg_99bf54bca31aec99",
    "neg_9a5541e8fde83b53",
    "neg_9b7328b0e8ce3d50",
    "neg_9d44556062371d03",
    "neg_9d8d690adecbf4db",
    "neg_9ea504aea4e7ab27",
    "neg_a131fe6b08cf8be3",
    "neg_a2ba1a6f587964ed",
    "neg_a67229aef624ffe8",
    "neg_a6ac35aec5227aa4",
    "neg_a783cef90faecb38",
    "neg_a8ad80a25cd9e444",
    "neg_a91733bcb18f76c6",
    "neg_a9d5429c3c82e780",
    "neg_aa339c9394106d34",
    "neg_abc2741e15ef241b",
    "neg_ac3b0848bb9dac97",
    "neg_ac937ead01194a5e",
    "neg_ae11c4c7f5c95f40",
    "neg_af1d1181dc959fa4",
    "neg_af2e6fbc9d6ac834",
    "neg_af83057031310f79",
    "neg_afa2f514d25456a6",
    "neg_afff05fa388c2e9e",
    "neg_b152a99f6bbcccb9",
    "neg_b157e49a592a0b91",
    "neg_b194605fe846e213",
    "neg_b2f3b4fc99e427ad",
    "neg_b51a5b1ac061bf87",
    "neg_b59eeeffca7e46f0",
    "neg_b6926223119b8223",
    "neg_b7f5ef02c4f8b212",
    "neg_b83cfd352c1fc139",
    "neg_b9d65774b1cdd12e",
    "neg_bb034251584ddde2",
    "neg_bc59317999f3b149",
    "neg_bc911ea6b90d921d",
    "neg_bce40d9f07c8f661",
    "neg_bd7bebb1015a19ab",
    "neg_bdd32251b0d6f26d",
    "neg_beefaac0dda982d0",
    "neg_bf21cafff3585137",
    "neg_bf34a66fb14c51a6",
    "neg_bf396c7eb2dc714c",
    "neg_bf8ff9b28639450d",
    "neg_bfa59f22bd1cff62",
    "neg_bfdfd4e1ba0dfabd",
    "neg_c06f03fb0bde8873",
    "neg_c1305af0cf380d2b",
    "neg_c22040e9b7578b5f",
    "neg_c26cd92f9cf9b6ee",
    "neg_c2754502fefd5f64",
    "neg_c2abbb0fd3b4ae0a",
    "neg_c308d0a2b0ea6008",
    "neg_c528b2cf92b73bc5",
    "neg_c5d9d2d16d63d2a7",
    "neg_c68027405dbb50c8",
    "neg_c6db43669bbf0039",
    "neg_c748bb92b2b0f255",
    "neg_c87a5d749223b6e8",
    "neg_c8e8ef8ecbba26b3",
    "neg_ca8200724aea638d",
    "neg_cb149f15f0923753",
    "neg_ccee752fe5e5e52e",
    "neg_cdeab69ead038a95",
    "neg_cf35375d6938f9b4",
    "neg_cfed810b0fb2f889",
    "neg_d0a8a228c3c67aef",
    "neg_d266a047cfb8a590",
    "neg_d2cf7c528db35f01",
    "neg_d2e0aba0cb6c0b65",
    "neg_d2eb5bcb51c195f1",
    "neg_d42baad9cf87ef14",
    "neg_d5fc89d9a315b242",
    "neg_d628ecfe25f97317",
    "neg_d6a4b22b38ab8fcd",
    "neg_d744d9ad67edeb7c",
    "neg_d7d722fae2ac12bd",
    "neg_d84f002b46e5eea5",
    "neg_d96aafddcd1fa9b9",
    "neg_d9fa6089b0b917d9",
    "neg_dad8e5a42948a27d",
    "neg_daf2bbf610d1f6c2",
    "neg_db017904c3deead3",
    "neg_dbd771fd941a5e06",
    "neg_dc7c0d5569456d77",
    "neg_dca5e4f16aaa1a49",
    "neg_dd7517b74bfdf1fb",
    "neg_de3ab9eb48382205",
    "neg_df44b76a89a0c8a5",
    "neg_dfddf90fd27901f6",
    "neg_e050ec29ecdd06b8",
    "neg_e0a0697318ff2f0f",
    "neg_e1325da3cb99749d",
    "neg_e1892c825d5801b6",
    "neg_e18b5b7a763ce088",
    "neg_e1d954c02b7507c9",
    "neg_e1e11d423175e052",
    "neg_e23564274091e9e2",
    "neg_e2fca92fa4b0c5f9",
    "neg_e38f85a96c51d573",
    "neg_e3ce12c50a2e0bed",
    "neg_e46778f55fb3c179",
    "neg_e5888cd0d5436c5c",
    "neg_e6304a6ec4019e42",
    "neg_e63632e0e5e95536",
    "neg_e7d6f12d1562a8ab",
    "neg_e9e33492f1e76a57",
    "neg_ea72b30a247de2b1",
    "neg_eaa8938eb413b225",
    "neg_eb01bfd54e3b7892",
    "neg_eb70a2e9928cbcd0",
    "neg_eb72f544234700ce",
    "neg_ec61e31243cfda81",
    "neg_eca40f0463e9bdcd",
    "neg_ed1abcc2e6ef31a2",
    "neg_ee12ad0d570c1de3",
    "neg_ee39e384806ebe3c",
    "neg_ee4d8dc51299925e",
    "neg_ee980ddd7b356f9c",
    "neg_f01163afb31ece5c",
    "neg_f1b280b0e240efa3",
    "neg_f2f90e9752c02fb6",
    "neg_f38da16e6f4b38c0",
    "neg_f3bf785b5cb4a0e4",
    "neg_f3e68ba9e31beb42",
    "neg_f4eeba73cba7f915",
    "neg_f5365a3cd14b9fb2",
    "neg_f53aa47db86acdfa",
    "neg_f63a4373f57e84cf",
    "neg_f6c8fcfdbb1b6ff9",
    "neg_f6ebb438089efc10",
    "neg_f75c9622ffead4fc",
    "neg_f7a0e8407062df90",
    "neg_fa626ab951c3c485",
    "neg_fde11f4bfb85f80c",
    "neg_fe12f3e1e27bc8a8",
    "neg_fe5a4b2a4194c63f",
    "neg_fe8c9053af85f3e4",
    "neg_fe8dc45cd49d0748",
    "neg_feb7c8a1c456fb65",
    "neg_ff3b880997df03c1"
  ],
  "branches": [
    [
      "vid_clip",
      0,
      512
    ],
    [
      "vid_slowfast",
      512,
      2816
    ]
  ],
  "modes": [
    "identity",
    "zero_visual",
    "shuffle_time",
    "zero_clip",
    "zero_slowfast"
  ],
  "perturbation": "zero normalized visual channels; shuffle valid visual rows only; masks, padded rows, text and TEF preserved",
  "permutation": "same permutation for each video and all queries; CPU generator seeded by SHA256(seed|vid|length)",
  "selection": "all existing pseudo rows, original order; no outcome-based selection",
  "accuracy_under_perturbation": "not computed"
}
```

## diagnostics/sit/baseline/LATEST_FAILURE_DECOMPOSITION.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "checkpoint_epoch_zero_based": 76,
  "checkpoint_sha256": "52b5d61a01030b2acd2f14a48137caa9b39f0f652e1be00653c502519c64abf7",
  "source_sha256": "a4a8dc5c9317945a71a184eab08e9a7962137004e736c19e12dcc34ba62741d0",
  "same_model_tensors_as_best": false,
  "predictions_reused_from_best": false,
  "results": {
    "pseudo": {
      "AUROC": 0.6208752136752137,
      "raw_R1_05": 0.3264,
      "gated_R1_05": 0.3216,
      "FRR": 0.1216,
      "RR": 0.2535612535612536,
      "counts": {
        "positive": 625,
        "raw_incorrect": 421,
        "positive_rejected": 76,
        "official_gated_correct": 201,
        "raw_correct_gated_wrong": 5,
        "raw_wrong_gated_correct": 2,
        "official_empty": 0,
        "raw_correct": 204,
        "raw_correct_accepted": 183,
        "raw_correct_rejected": 21,
        "negative": 351,
        "negative_accepted": 262
      },
      "raw_correct_rejected_over_raw_correct": 0.10294117647058823,
      "raw_errors_over_hard_failures": 0.9524886877828054,
      "threshold": 0.7025,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "36eb827d6887486f49098d8b994a05759bcdf47673c53b189c3e10ac392d5870"
    },
    "seen": {
      "AUROC": 0.7857159154865305,
      "raw_R1_05": 0.3328402366863905,
      "gated_R1_05": 0.32840236686390534,
      "FRR": 0.17455621301775148,
      "RR": 0.6478149100257069,
      "counts": {
        "positive": 676,
        "raw_correct": 225,
        "raw_correct_accepted": 190,
        "positive_rejected": 118,
        "official_gated_correct": 222,
        "raw_correct_gated_wrong": 4,
        "raw_wrong_gated_correct": 1,
        "official_empty": 0,
        "raw_incorrect": 451,
        "raw_correct_rejected": 35,
        "negative": 389,
        "negative_accepted": 137
      },
      "raw_correct_rejected_over_raw_correct": 0.15555555555555556,
      "raw_errors_over_hard_failures": 0.9279835390946503,
      "threshold": 0.7025,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "49848dd5bc021ce91946ceb9f1f8a9640e7a6840add5dc3f4a8172edf9a2abe5"
    }
  },
  "limitations": "Latest comparison is descriptive, not an alternative pseudo-based checkpoint selection or full training trajectory; unchanged official gate, diagnostic threshold fitted on latest seen only."
}
```

## diagnostics/sit/baseline/SCORE_COMPARABILITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "splits": {
    "pseudo": {
      "same_video_pairacc": 0.6943493150684932,
      "same_video_pairs": 584,
      "cross_video_pairacc": 0.6539140092599787,
      "exact_query_cross_video_pairacc": 0.564066852367688,
      "exact_query_cross_video_pairs": 359,
      "exact_query_groups": 45,
      "exact_query_feature_consistent_groups": 0,
      "mixed_label_videos": 229
    },
    "seen": {
      "same_video_pairacc": 0.753968253968254,
      "same_video_pairs": 882,
      "cross_video_pairacc": 0.8435146251936418,
      "exact_query_cross_video_pairacc": 0.6573816155988857,
      "exact_query_cross_video_pairs": 359,
      "exact_query_groups": 45,
      "exact_query_feature_consistent_groups": 0,
      "mixed_label_videos": 185
    }
  },
  "limitations": "Within/cross-video rank decomposition uses original queries and labels; differing compositions do not prove video bias. Identical string ranks before feature control are not a text tie control."
}
```

## diagnostics/sit/baseline/VISUAL_INCREMENT.json

```json
{
  "pseudo": {
    "same_video_pairacc": 0.6943493150684932,
    "same_video_pairs": 584,
    "cross_video_pairacc": 0.6539140092599787,
    "exact_query_cross_video_pairacc": 0.564066852367688,
    "exact_query_cross_video_pairs": 359,
    "exact_query_groups": 45,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 229
  },
  "seen": {
    "same_video_pairacc": 0.753968253968254,
    "same_video_pairs": 882,
    "cross_video_pairacc": 0.8435146251936418,
    "exact_query_cross_video_pairacc": 0.6573816155988857,
    "exact_query_cross_video_pairs": 359,
    "exact_query_groups": 45,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 185
  }
}
```

## diagnostics/throw/adapter/CONTROLLED_QUERY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "query_groups": 10,
  "rows": 36,
  "pairs": 37,
  "pairacc": 0.5135135135135135,
  "video_endpoint_bootstrap_ci95": [
    0.17130952380952383,
    0.8501785714285712
  ],
  "text_input": "same normalized cached feature and mask per identical query, canonical lexicographically smallest qid; original video and labels unchanged",
  "pure_text_pairacc_control": 0.5,
  "checkpoint_sha256": "7343847dc15992410f7ffb8f43502e2c3ea5e26d527b9b78d5be1124ce3135a7",
  "scores": {
    "train2036": 0.9971358776092529,
    "train2914": 0.9282615780830383,
    "train4094": 0.9442466497421265,
    "train4551": 0.9978158473968506,
    "train4988": 0.9851367473602295,
    "train5151": 0.9689505696296692,
    "train5386": 0.9976478219032288,
    "train5713": 0.998018741607666,
    "train6081": 0.6620653867721558,
    "train6586": 0.9985368251800537,
    "train6717": 0.9317652583122253,
    "train7222": 0.9947899580001831,
    "train9531": 0.9971961975097656,
    "train9586": 0.998234748840332,
    "train12079": 0.9989994168281555,
    "neg_2903529dc003a31f": 0.9952318072319031,
    "neg_2c1e2bafcc1c2ba3": 0.8217297196388245,
    "neg_2e0d0161d366342d": 0.9246770143508911,
    "neg_3226064207f4f425": 0.9964082837104797,
    "neg_4111a15dd5106a66": 0.9934171438217163,
    "neg_469d70306c4e8cb6": 0.9987426400184631,
    "neg_48f05f2ac84c8997": 0.9977720379829407,
    "neg_68b517b1666eb195": 0.9979636669158936,
    "neg_6edb4b00ee70e4cb": 0.9955891370773315,
    "neg_70950f8705e9536e": 0.999622106552124,
    "neg_7353b57ab1f9c95a": 0.9996895790100098,
    "neg_90273c67420ee208": 0.9953289031982422,
    "neg_a9c02641b1594466": 0.9946371912956238,
    "neg_af88201bd348e15c": 0.9300334453582764,
    "neg_b517bddadc52e173": 0.9944140911102295,
    "neg_b545b4e592aeba0c": 0.9920846223831177,
    "neg_c0cf96cf6ce024b2": 0.9922307133674622,
    "neg_d0b2246178816f8e": 0.9597054719924927,
    "neg_d5c6a9c0b6fcfb45": 0.9345945715904236,
    "neg_feae6426d2be85b7": 0.884044885635376,
    "neg_ffbdd422c37c6880": 0.9984210729598999
  },
  "limitations": "original labels only; sparse correlated pairs, endpoint video bootstrap; not a causal proof or full-sample metric"
}
```

## diagnostics/throw/adapter/FAILURE_DECOMPOSITION.json

```json
{
  "pseudo": {
    "AUROC": 0.600032530904359,
    "raw_R1_05": 0.2349137931034483,
    "gated_R1_05": 0.23275862068965517,
    "FRR": 0.1206896551724138,
    "RR": 0.160377358490566,
    "counts": {
      "positive": 464,
      "raw_incorrect": 355,
      "positive_rejected": 56,
      "official_gated_correct": 108,
      "raw_correct_gated_wrong": 4,
      "raw_wrong_gated_correct": 3,
      "official_empty": 0,
      "raw_correct": 109,
      "raw_correct_accepted": 94,
      "raw_correct_rejected": 15,
      "negative": 106,
      "negative_accepted": 89
    },
    "raw_correct_rejected_over_positives": 0.032327586206896554,
    "raw_correct_rejected_over_raw_correct": 0.13761467889908258,
    "raw_errors_over_hard_failures": 0.9594594594594594,
    "threshold": 0.8262,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.9846153846153847,
    "same_video_pairs": 65,
    "cross_video_pairacc": 0.5995236059366029,
    "exact_query_cross_video_pairacc": 0.5,
    "exact_query_cross_video_pairs": 37,
    "exact_query_groups": 10,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 32,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/pseudo.jsonl": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
      "pseudo_predictions.jsonl": "b4964ae712a0d0909ac28eb6d9eae91612ccd94aa2cb4612b96e8b9b6f79f03f"
    }
  },
  "seen": {
    "AUROC": 0.8445837432293086,
    "raw_R1_05": 0.3441466854724965,
    "gated_R1_05": 0.3441466854724965,
    "FRR": 0.3540197461212976,
    "RR": 0.8991596638655462,
    "counts": {
      "positive": 709,
      "raw_correct": 244,
      "raw_correct_accepted": 166,
      "positive_rejected": 251,
      "official_gated_correct": 244,
      "raw_correct_gated_wrong": 4,
      "raw_wrong_gated_correct": 4,
      "official_empty": 0,
      "raw_incorrect": 465,
      "raw_correct_rejected": 78,
      "negative": 476,
      "negative_accepted": 48
    },
    "raw_correct_rejected_over_positives": 0.11001410437235543,
    "raw_correct_rejected_over_raw_correct": 0.319672131147541,
    "raw_errors_over_hard_failures": 0.856353591160221,
    "threshold": 0.8262,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.7450361010830325,
    "same_video_pairs": 1108,
    "cross_video_pairacc": 0.8449116464908317,
    "exact_query_cross_video_pairacc": 0.6929347826086957,
    "exact_query_cross_video_pairs": 368,
    "exact_query_groups": 52,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 199,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/val_seen.jsonl": "29166e4d694480fd41184bd4ff5802d1251103f4a042cdcbd9ac25ab7ddb6685",
      "best_seen_predictions.jsonl": "d2aa74f9f14537ba10e60e54a334bcb0eebce54edae722e9602d9173c27e158f"
    }
  }
}
```

## diagnostics/throw/adapter/GATE_POSTPROCESS_AUDIT.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "results": {
    "pseudo": {
      "rows": 570,
      "positive": 464,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train640",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train3916",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train5713",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train6642",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train6670",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train7712",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train12236",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.23275862068965517,
      "official_gated_R1_05": 0.23275862068965517,
      "prediction_sha256": "b4964ae712a0d0909ac28eb6d9eae91612ccd94aa2cb4612b96e8b9b6f79f03f"
    },
    "seen": {
      "rows": 1185,
      "positive": 709,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train3061",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train4947",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train5086",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train6920",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train7602",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train10626",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train11094",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train11672",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.3441466854724965,
      "official_gated_R1_05": 0.3441466854724965,
      "prediction_sha256": "d2aa74f9f14537ba10e60e54a334bcb0eebce54edae722e9602d9173c27e158f"
    }
  },
  "source_sha256": "e8f3da3638ebe09271ab1e32db99dd2ce36e12e5d52584165ea6d7310791f5f4",
  "official_evaluator_sha256": "b71f952fa6cfbfbaae1ca0b6bd1f476159c17c2448b87d55f82300fa97a50537",
  "official_postprocessor_sha256": "50e6501c642e77502f7a4d781e01e12bbd97521d3b0a8f47d793b3044be30046",
  "gate_sha256": "0e1235c8425f9c61883e88a57a8a1feec2c9ceb15046aeecd83563deb3cefc67",
  "interpretation": "Official soft gate is a per-row nonnegative scalar. Exact positive scalar scaling preserves within-row ranking. Saved gated coordinates alone receive clip_ts/round_multiple; frozen raw endpoint remains untouched. When aligned coordinates match, hit changes are explained by temporal postprocessing rather than gate veto or reranking. Aligned raw is auxiliary only, not a replacement co-primary endpoint."
}
```

## diagnostics/throw/adapter/GRADIENT_DETAIL.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "source_sha256": "aa62ab661c26930186b53405490d723cc70e4c952e94a60596cd0584f7619473",
  "checkpoints": {
    "best": {
      "checkpoint_epoch_zero_based": 13,
      "checkpoint_sha256": "7343847dc15992410f7ffb8f43502e2c3ea5e26d527b9b78d5be1124ce3135a7",
      "model_tensor_sha256": "ca17dadf24aaefb3f8d366493a54b965a75f106f8bea26482b0f0c1c4137ea8f",
      "original_diagnostic_sha256": "ccc38ef2b8a60508f21faa97719d01c886f51e7c5c923bd165590546e0b6566b",
      "qids": [
        [
          "train10943",
          "train1927",
          "train6733",
          "train1214",
          "train10272",
          "train8188",
          "train3902",
          "train8169",
          "train7847",
          "train4389",
          "train9821",
          "train10930",
          "train8193",
          "train11900",
          "train7692",
          "train3375"
        ],
        [
          "train11235",
          "train2648",
          "train6552",
          "train9774",
          "train7587",
          "train9744",
          "train3797",
          "train6960",
          "train9018",
          "train2139",
          "train2990",
          "train1412",
          "train598",
          "train4481",
          "train4406",
          "train11839"
        ],
        [
          "train2195",
          "train2067",
          "train5592",
          "train6447",
          "train11550",
          "train4668",
          "train8694",
          "train6039",
          "train1825",
          "train2402",
          "train2620",
          "train12049",
          "train4621",
          "train4110",
          "train7121",
          "train1999"
        ],
        [
          "train768",
          "train5303",
          "train251",
          "train9380",
          "train6951",
          "train1791",
          "train2333",
          "train10227",
          "train12170",
          "train6371",
          "train6993",
          "train11858",
          "train4755",
          "train8046",
          "train2562",
          "train2772"
        ],
        [
          "train7780",
          "train8849",
          "train7819",
          "train5536",
          "train12139",
          "train3821",
          "train913",
          "train9358",
          "train4882",
          "train1639",
          "train1199",
          "train8496",
          "train5695",
          "train7362",
          "train4452",
          "train9836"
        ],
        [
          "train1823",
          "train128",
          "train11066",
          "train2426",
          "train4513",
          "train10535",
          "train7550",
          "train8329",
          "train5659",
          "train6368",
          "train4317",
          "train9626",
          "train8955",
          "train10944",
          "train3846",
          "train8613"
        ],
        [
          "train9779",
          "train9204",
          "train11510",
          "train1390",
          "train256",
          "train490",
          "train1209",
          "train10294",
          "train7952",
          "train2763",
          "train7063",
          "train3461",
          "train7946",
          "train8748",
          "train11756",
          "train3175"
        ],
        [
          "train11665",
          "train3053",
          "train3447",
          "train8611",
          "train2240",
          "train10971",
          "train4486",
          "train4831",
          "train10947",
          "train7497",
          "train9854",
          "train10039",
          "train1222",
          "train8954",
          "train3345",
          "train12251"
        ],
        [
          "train1187",
          "train10581",
          "train7598",
          "train4900",
          "train6300",
          "train7023",
          "train8743",
          "train4760",
          "train6762",
          "train1735",
          "train1499",
          "train12101",
          "train526",
          "train6557",
          "train2279",
          "train6852"
        ],
        [
          "train6124",
          "train11078",
          "train5797",
          "train3363",
          "train6579",
          "train11079",
          "train2838",
          "train5468",
          "train7708",
          "train2879",
          "train5254",
          "train8621",
          "train9102",
          "train12033",
          "train12292",
          "train2593"
        ],
        [
          "train11565",
          "train6365",
          "train12400",
          "train8572",
          "train8511",
          "train7116",
          "train11921",
          "train2816",
          "train11106",
          "train11159",
          "train6360",
          "train11182",
          "train10346",
          "train11647",
          "train1585",
          "train3522"
        ],
        [
          "train5584",
          "train9281",
          "train5623",
          "train10490",
          "train8941",
          "train2833",
          "train7240",
          "train11111",
          "train3591",
          "train1196",
          "train1084",
          "train378",
          "train1684",
          "train307",
          "train2404",
          "train7906"
        ],
        [
          "train2078",
          "train5708",
          "train6213",
          "train10772",
          "train1332",
          "train12332",
          "train11301",
          "train1149",
          "train6648",
          "train9917",
          "train7467",
          "train1651",
          "train7739",
          "train2932",
          "train9440",
          "train10096"
        ],
        [
          "train2904",
          "train8002",
          "train902",
          "train9408",
          "train1429",
          "train10597",
          "train9886",
          "train4622",
          "train12224",
          "train4718",
          "train11288",
          "train10832",
          "train4359",
          "train11704",
          "train2312",
          "train3573"
        ],
        [
          "train6463",
          "train6015",
          "train10250",
          "train6203",
          "train5413",
          "train5380",
          "train7591",
          "train10604",
          "train8644",
          "train1695",
          "train2922",
          "train8334",
          "train9407",
          "train7683",
          "train5641",
          "train6187"
        ],
        [
          "train3502",
          "train9050",
          "train10050",
          "train519",
          "train7232",
          "train5890",
          "train5811",
          "train4545",
          "train3021",
          "train8201",
          "train10343",
          "train9812",
          "train9940",
          "train10172",
          "train2558",
          "train11753"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.52254918217659
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 1.9936259984970093
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.00017901381943374872,
          "negative_fraction": 0.5
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.2931784689426422
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 5.07639217376709
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.001292578934226185,
          "negative_fraction": 0.625
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 1.7845335602760315
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 8.97212553024292
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.09030797332525253,
          "negative_fraction": 0.125
        },
        "adapter|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.09721560031175613
        },
        "adapter|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.35033538937568665
        },
        "adapter|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "adapter|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.08352332562208176,
          "negative_fraction": 0.1875
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.35791003704071045
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.985609233379364
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4655146300792694
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.103795051574707
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6457313895225525
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8408929109573364
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7366912364959717
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5360970497131348
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.36455926299095154
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.23479747772216797
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3709243834018707
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3217952847480774
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5616074800491333
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6553815603256226
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5090013146400452
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3302641212940216
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.6608315706253052
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.3531033992767334
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.5977476835250854
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.590853214263916
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.6826313734054565
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.9982168674468994
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.334505081176758
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.1101760864257812
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.2515385150909424
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.9890351295471191
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.7378056049346924
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.1314587593078613
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.9270954132080078
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.8535792827606201
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.7779618501663208
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.810550332069397
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": -0.08275984972715378
          },
          {
            "full_block_cosine": 0.07362598180770874
          },
          {
            "full_block_cosine": -0.006098628044128418
          },
          {
            "full_block_cosine": 0.5874762535095215
          },
          {
            "full_block_cosine": -0.09491709619760513
          },
          {
            "full_block_cosine": 0.2606116235256195
          },
          {
            "full_block_cosine": 0.2279098778963089
          },
          {
            "full_block_cosine": -0.09403526782989502
          },
          {
            "full_block_cosine": 0.06487300246953964
          },
          {
            "full_block_cosine": -0.17842812836170197
          },
          {
            "full_block_cosine": 0.013848177157342434
          },
          {
            "full_block_cosine": -0.002574528567492962
          },
          {
            "full_block_cosine": -0.11196756362915039
          },
          {
            "full_block_cosine": 0.1639123409986496
          },
          {
            "full_block_cosine": 0.0029325562063604593
          },
          {
            "full_block_cosine": -0.03314046189188957
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.19869333505630493
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4461342990398407
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.29799920320510864
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6338270902633667
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2886643707752228
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4449578523635864
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3444271385669708
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.29769256711006165
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.20874223113059998
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.12913326919078827
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1790854036808014
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.20271363854408264
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.31799277663230896
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.33110976219177246
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.26745495200157166
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1487119495868683
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.0248517990112305
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.043367385864258
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.152158260345459
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.3798604011535645
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.01629638671875
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1028199195861816
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.681854486465454
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.251193523406982
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.52418327331543
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.090699195861816
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.47593879699707
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.7697317600250244
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.13648796081543
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.109375953674316
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.1742780208587646
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.594027519226074
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": -0.005932664033025503
          },
          {
            "full_block_cosine": -0.04539709910750389
          },
          {
            "full_block_cosine": -0.001439779414795339
          },
          {
            "full_block_cosine": 0.1540278196334839
          },
          {
            "full_block_cosine": -0.0032521430402994156
          },
          {
            "full_block_cosine": 0.026278583332896233
          },
          {
            "full_block_cosine": 0.008447946980595589
          },
          {
            "full_block_cosine": -0.009103359654545784
          },
          {
            "full_block_cosine": 0.0014283856144174933
          },
          {
            "full_block_cosine": -0.001954856561496854
          },
          {
            "full_block_cosine": -0.0003760950348805636
          },
          {
            "full_block_cosine": 0.001449817093089223
          },
          {
            "full_block_cosine": -0.006048304494470358
          },
          {
            "full_block_cosine": 0.006680659018456936
          },
          {
            "full_block_cosine": -0.0014790138229727745
          },
          {
            "full_block_cosine": -0.001145378453657031
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.0315502882003784
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.289137840270996
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.619736671447754
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.650036811828613
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.3774325847625732
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.3686788082122803
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.1261978149414062
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.9292510747909546
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.031750202178955
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8746607899665833
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8507192730903625
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8841649889945984
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.6398160457611084
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.2992160320281982
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.9674460887908936
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.258201241493225
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.369010925292969
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.680673599243164
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.607765197753906
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 21.172880172729492
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.120148658752441
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.581658840179443
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.801702499389648
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 13.921594619750977
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 15.785737991333008
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 14.094854354858398
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.055879592895508
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 14.929107666015625
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.455926418304443
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.908771991729736
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.263577461242676
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.12963581085205
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": 0.04531824588775635
          },
          {
            "full_block_cosine": 0.15508438646793365
          },
          {
            "full_block_cosine": 0.3553107678890228
          },
          {
            "full_block_cosine": 0.6334419250488281
          },
          {
            "full_block_cosine": 0.09435676038265228
          },
          {
            "full_block_cosine": 0.26969826221466064
          },
          {
            "full_block_cosine": 0.1489662230014801
          },
          {
            "full_block_cosine": 0.11994995176792145
          },
          {
            "full_block_cosine": 0.08625918626785278
          },
          {
            "full_block_cosine": -0.1651925891637802
          },
          {
            "full_block_cosine": 0.035393401980400085
          },
          {
            "full_block_cosine": 0.029181864112615585
          },
          {
            "full_block_cosine": 0.060410045087337494
          },
          {
            "full_block_cosine": 0.112851083278656
          },
          {
            "full_block_cosine": 0.027693741023540497
          },
          {
            "full_block_cosine": -0.08009247481822968
          }
        ],
        "adapter|exist": [
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06661814451217651
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.21831545233726501
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.07158274203538895
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.2550240457057953
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.14766427874565125
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.18159334361553192
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10807231813669205
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10856038331985474
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.05276735499501228
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03862650692462921
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.05746157839894295
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03680048882961273
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.11170610785484314
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10489208251237869
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.08953911811113358
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0631457194685936
          }
        ],
        "adapter|loc": [
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3549923300743103
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.41520529985427856
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.22337952256202698
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.937698483467102
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.29463836550712585
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.32425588369369507
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.345678448677063
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4695202112197876
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4654250144958496
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4521813988685608
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3195115923881531
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4665099084377289
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.21777784824371338
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.23472370207309723
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3306759297847748
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.3607780933380127
          }
        ],
        "adapter|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "adapter|exist_vs_loc": [
          {
            "full_block_cosine": -0.06130053848028183
          },
          {
            "full_block_cosine": 0.19192227721214294
          },
          {
            "full_block_cosine": 0.30979177355766296
          },
          {
            "full_block_cosine": 0.7941279411315918
          },
          {
            "full_block_cosine": 0.07936028391122818
          },
          {
            "full_block_cosine": 0.28664466738700867
          },
          {
            "full_block_cosine": 0.28365299105644226
          },
          {
            "full_block_cosine": 0.031942497938871384
          },
          {
            "full_block_cosine": 0.03306526318192482
          },
          {
            "full_block_cosine": -0.16629712283611298
          },
          {
            "full_block_cosine": 0.08768636733293533
          },
          {
            "full_block_cosine": 0.05739447474479675
          },
          {
            "full_block_cosine": 0.09897028654813766
          },
          {
            "full_block_cosine": 0.24292267858982086
          },
          {
            "full_block_cosine": 0.022845949977636337
          },
          {
            "full_block_cosine": -0.10910963267087936
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    },
    "latest": {
      "checkpoint_epoch_zero_based": 99,
      "checkpoint_sha256": "52d5fb1db8de2848a1c694798c7ee99e15f305ff4794d5e94eebef3311e31432",
      "model_tensor_sha256": "73736ac0c711ee3c4ae8d4f9a6634aff4566c4b85cb767613c13a5c74e79d1b1",
      "original_diagnostic_sha256": "1d735e134f0c00326dafd5f192b1affeb200dfc4848501d94e2a46e42678ad49",
      "qids": [
        [
          "train10943",
          "train1927",
          "train6733",
          "train1214",
          "train10272",
          "train8188",
          "train3902",
          "train8169",
          "train7847",
          "train4389",
          "train9821",
          "train10930",
          "train8193",
          "train11900",
          "train7692",
          "train3375"
        ],
        [
          "train11235",
          "train2648",
          "train6552",
          "train9774",
          "train7587",
          "train9744",
          "train3797",
          "train6960",
          "train9018",
          "train2139",
          "train2990",
          "train1412",
          "train598",
          "train4481",
          "train4406",
          "train11839"
        ],
        [
          "train2195",
          "train2067",
          "train5592",
          "train6447",
          "train11550",
          "train4668",
          "train8694",
          "train6039",
          "train1825",
          "train2402",
          "train2620",
          "train12049",
          "train4621",
          "train4110",
          "train7121",
          "train1999"
        ],
        [
          "train768",
          "train5303",
          "train251",
          "train9380",
          "train6951",
          "train1791",
          "train2333",
          "train10227",
          "train12170",
          "train6371",
          "train6993",
          "train11858",
          "train4755",
          "train8046",
          "train2562",
          "train2772"
        ],
        [
          "train7780",
          "train8849",
          "train7819",
          "train5536",
          "train12139",
          "train3821",
          "train913",
          "train9358",
          "train4882",
          "train1639",
          "train1199",
          "train8496",
          "train5695",
          "train7362",
          "train4452",
          "train9836"
        ],
        [
          "train1823",
          "train128",
          "train11066",
          "train2426",
          "train4513",
          "train10535",
          "train7550",
          "train8329",
          "train5659",
          "train6368",
          "train4317",
          "train9626",
          "train8955",
          "train10944",
          "train3846",
          "train8613"
        ],
        [
          "train9779",
          "train9204",
          "train11510",
          "train1390",
          "train256",
          "train490",
          "train1209",
          "train10294",
          "train7952",
          "train2763",
          "train7063",
          "train3461",
          "train7946",
          "train8748",
          "train11756",
          "train3175"
        ],
        [
          "train11665",
          "train3053",
          "train3447",
          "train8611",
          "train2240",
          "train10971",
          "train4486",
          "train4831",
          "train10947",
          "train7497",
          "train9854",
          "train10039",
          "train1222",
          "train8954",
          "train3345",
          "train12251"
        ],
        [
          "train1187",
          "train10581",
          "train7598",
          "train4900",
          "train6300",
          "train7023",
          "train8743",
          "train4760",
          "train6762",
          "train1735",
          "train1499",
          "train12101",
          "train526",
          "train6557",
          "train2279",
          "train6852"
        ],
        [
          "train6124",
          "train11078",
          "train5797",
          "train3363",
          "train6579",
          "train11079",
          "train2838",
          "train5468",
          "train7708",
          "train2879",
          "train5254",
          "train8621",
          "train9102",
          "train12033",
          "train12292",
          "train2593"
        ],
        [
          "train11565",
          "train6365",
          "train12400",
          "train8572",
          "train8511",
          "train7116",
          "train11921",
          "train2816",
          "train11106",
          "train11159",
          "train6360",
          "train11182",
          "train10346",
          "train11647",
          "train1585",
          "train3522"
        ],
        [
          "train5584",
          "train9281",
          "train5623",
          "train10490",
          "train8941",
          "train2833",
          "train7240",
          "train11111",
          "train3591",
          "train1196",
          "train1084",
          "train378",
          "train1684",
          "train307",
          "train2404",
          "train7906"
        ],
        [
          "train2078",
          "train5708",
          "train6213",
          "train10772",
          "train1332",
          "train12332",
          "train11301",
          "train1149",
          "train6648",
          "train9917",
          "train7467",
          "train1651",
          "train7739",
          "train2932",
          "train9440",
          "train10096"
        ],
        [
          "train2904",
          "train8002",
          "train902",
          "train9408",
          "train1429",
          "train10597",
          "train9886",
          "train4622",
          "train12224",
          "train4718",
          "train11288",
          "train10832",
          "train4359",
          "train11704",
          "train2312",
          "train3573"
        ],
        [
          "train6463",
          "train6015",
          "train10250",
          "train6203",
          "train5413",
          "train5380",
          "train7591",
          "train10604",
          "train8644",
          "train1695",
          "train2922",
          "train8334",
          "train9407",
          "train7683",
          "train5641",
          "train6187"
        ],
        [
          "train3502",
          "train9050",
          "train10050",
          "train519",
          "train7232",
          "train5890",
          "train5811",
          "train4545",
          "train3021",
          "train8201",
          "train10343",
          "train9812",
          "train9940",
          "train10172",
          "train2558",
          "train11753"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.0043239109218120575
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.196811199188232
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.08276436105370522,
          "negative_fraction": 0.1875
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.0015441610594280064
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.520284414291382
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.07217064499855042,
          "negative_fraction": 0.0625
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.006610144628211856
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 8.204204082489014
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.031288729049265385,
          "negative_fraction": 0.6875
        },
        "adapter|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.00098560523474589
        },
        "adapter|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.894145667552948
        },
        "adapter|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "adapter|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.0032256702543236315,
          "negative_fraction": 0.5
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.013098646886646748
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002355144126340747
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.04893317073583603
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0071320561692118645
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.4904012680053711
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002716575749218464
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0027555134147405624
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0014395829057320952
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004919110331684351
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0013111458392813802
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003728711511939764
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.11749780923128128
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0021381524857133627
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.017028560861945152
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0027438169345259666
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.006562212016433477
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.707395076751709
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.029581069946289
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.616057872772217
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.5401830673217773
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.202977657318115
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.59327507019043
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.824608564376831
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.090882778167725
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.692183971405029
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.15265941619873
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.000452518463135
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.170196056365967
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.075945854187012
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.530601501464844
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.2075212001800537
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.19064474105835
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.002719195792451501
          },
          {
            "full_block_cosine": 0.0713140219449997
          },
          {
            "full_block_cosine": 0.12180066853761673
          },
          {
            "full_block_cosine": -0.14979968965053558
          },
          {
            "full_block_cosine": 0.10261335223913193
          },
          {
            "full_block_cosine": 0.042413946241140366
          },
          {
            "full_block_cosine": -0.11770103126764297
          },
          {
            "full_block_cosine": 0.031710751354694366
          },
          {
            "full_block_cosine": 0.19937029480934143
          },
          {
            "full_block_cosine": 0.13860392570495605
          },
          {
            "full_block_cosine": -0.033833157271146774
          },
          {
            "full_block_cosine": 0.09421470016241074
          },
          {
            "full_block_cosine": 0.20738856494426727
          },
          {
            "full_block_cosine": 0.06971689313650131
          },
          {
            "full_block_cosine": 0.1355862021446228
          },
          {
            "full_block_cosine": 0.15014590322971344
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003349869279190898
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0007405331125482917
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0066092838533222675
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0016791292000561953
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.052037231624126434
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0009507279610261321
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0008264115895144641
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0006726612919010222
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0016036645974963903
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0004433915892150253
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0014846575213596225
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.02680353820323944
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0007131182355806231
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0028688486199826
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0010855341097339988
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002405804581940174
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.1140668392181396
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.535236835479736
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.2480058670043945
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.497375965118408
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.912170886993408
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.098502159118652
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.864378452301025
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.6790387630462646
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.531912326812744
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.028733253479004
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.505331993103027
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.031760215759277
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.7743964195251465
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.6843793392181396
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.263340950012207
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.13688850402832
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": 0.10891424864530563
          },
          {
            "full_block_cosine": 0.017581582069396973
          },
          {
            "full_block_cosine": 0.11917977780103683
          },
          {
            "full_block_cosine": 0.02483585849404335
          },
          {
            "full_block_cosine": 0.03910987451672554
          },
          {
            "full_block_cosine": 0.06651599705219269
          },
          {
            "full_block_cosine": -0.028032423928380013
          },
          {
            "full_block_cosine": 0.11207019537687302
          },
          {
            "full_block_cosine": 0.08611803501844406
          },
          {
            "full_block_cosine": 0.1536962240934372
          },
          {
            "full_block_cosine": 0.02285907231271267
          },
          {
            "full_block_cosine": 0.001267220126464963
          },
          {
            "full_block_cosine": 0.09190129488706589
          },
          {
            "full_block_cosine": 0.0753360316157341
          },
          {
            "full_block_cosine": 0.06900525838136673
          },
          {
            "full_block_cosine": 0.07746618986129761
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.014201071113348007
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002997518051415682
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.12444324791431427
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0128228310495615
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5416843891143799
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0027823925483971834
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.008019555360078812
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0012627922696992755
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0052007338963449
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0022769987117499113
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0032216033432632685
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1125640943646431
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.002645379165187478
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.025465326383709908
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003842657431960106
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00864050816744566
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 16.169626235961914
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.275461673736572
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.6872124671936035
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.55740213394165
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.89715576171875
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.228191375732422
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.013887405395508
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.154057502746582
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.958178520202637
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 17.16387367248535
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.7714715003967285
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.180216789245605
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.2121477127075195
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.353592872619629
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.66439962387085
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.790621757507324
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": -0.011029052548110485
          },
          {
            "full_block_cosine": -0.07030685991048813
          },
          {
            "full_block_cosine": -0.06172022223472595
          },
          {
            "full_block_cosine": -0.15976379811763763
          },
          {
            "full_block_cosine": 0.013884305953979492
          },
          {
            "full_block_cosine": -0.08622851967811584
          },
          {
            "full_block_cosine": -0.09110517054796219
          },
          {
            "full_block_cosine": -0.02925374172627926
          },
          {
            "full_block_cosine": 0.34485557675361633
          },
          {
            "full_block_cosine": -0.038044944405555725
          },
          {
            "full_block_cosine": 0.05168336257338524
          },
          {
            "full_block_cosine": -0.03332371637225151
          },
          {
            "full_block_cosine": 0.12073725461959839
          },
          {
            "full_block_cosine": 0.04472321644425392
          },
          {
            "full_block_cosine": -0.054270267486572266
          },
          {
            "full_block_cosine": -0.018328635022044182
          }
        ],
        "adapter|exist": [
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003247175831347704
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0004041512729600072
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.011997336521744728
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001257849857211113
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.10051990300416946
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005686787189915776
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0007133606122806668
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0002412735193502158
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0013153216568753123
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00027255903114564717
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0006412803777493536
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.023761523887515068
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0003888621286023408
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004167228005826473
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0004912751028314233
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0012958244187757373
          }
        ],
        "adapter|loc": [
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.7360773086547852
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.785236120223999
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.0067254304885864
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6814782619476318
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.941673219203949
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7625278234481812
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.846618115901947
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.2558016777038574
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.078446388244629
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.227560043334961
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.6588656902313232
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7404140830039978
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.7083574533462524
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.983761191368103
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.648127555847168
          },
          {
            "available": true,
            "tensor_count": 8,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.9972522854804993
          }
        ],
        "adapter|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "adapter|exist_vs_loc": [
          {
            "full_block_cosine": -0.0011180498404428363
          },
          {
            "full_block_cosine": -0.04364331066608429
          },
          {
            "full_block_cosine": -0.03967941924929619
          },
          {
            "full_block_cosine": -0.1458691954612732
          },
          {
            "full_block_cosine": 0.012224530801177025
          },
          {
            "full_block_cosine": -0.09128211438655853
          },
          {
            "full_block_cosine": -0.2071070671081543
          },
          {
            "full_block_cosine": 0.023088211193680763
          },
          {
            "full_block_cosine": 0.034718599170446396
          },
          {
            "full_block_cosine": 0.027776025235652924
          },
          {
            "full_block_cosine": 0.06940590590238571
          },
          {
            "full_block_cosine": 0.007569390349090099
          },
          {
            "full_block_cosine": -0.010776431299746037
          },
          {
            "full_block_cosine": 0.026774639263749123
          },
          {
            "full_block_cosine": -0.02678443305194378
          },
          {
            "full_block_cosine": 0.053796205669641495
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    }
  },
  "interpretation": "S+ only, eval mode local geometry; unused tensors treated as zero in full-block cosine. Original norms used only the jointly differentiable tensor intersection; detail fixes interpretation without overwriting original output. Inactive saliency is unavailable, not agreement. No S- localization gradient is inferred."
}
```

## diagnostics/throw/adapter/GRADIENT_RELATIONS_best.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_adapter_s3407_attempt1/best.ckpt",
  "checkpoint_sha256": "7343847dc15992410f7ffb8f43502e2c3ea5e26d527b9b78d5be1124ce3135a7",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train10943",
      "train1927",
      "train6733",
      "train1214",
      "train10272",
      "train8188",
      "train3902",
      "train8169",
      "train7847",
      "train4389",
      "train9821",
      "train10930",
      "train8193",
      "train11900",
      "train7692",
      "train3375"
    ],
    [
      "train11235",
      "train2648",
      "train6552",
      "train9774",
      "train7587",
      "train9744",
      "train3797",
      "train6960",
      "train9018",
      "train2139",
      "train2990",
      "train1412",
      "train598",
      "train4481",
      "train4406",
      "train11839"
    ],
    [
      "train2195",
      "train2067",
      "train5592",
      "train6447",
      "train11550",
      "train4668",
      "train8694",
      "train6039",
      "train1825",
      "train2402",
      "train2620",
      "train12049",
      "train4621",
      "train4110",
      "train7121",
      "train1999"
    ],
    [
      "train768",
      "train5303",
      "train251",
      "train9380",
      "train6951",
      "train1791",
      "train2333",
      "train10227",
      "train12170",
      "train6371",
      "train6993",
      "train11858",
      "train4755",
      "train8046",
      "train2562",
      "train2772"
    ],
    [
      "train7780",
      "train8849",
      "train7819",
      "train5536",
      "train12139",
      "train3821",
      "train913",
      "train9358",
      "train4882",
      "train1639",
      "train1199",
      "train8496",
      "train5695",
      "train7362",
      "train4452",
      "train9836"
    ],
    [
      "train1823",
      "train128",
      "train11066",
      "train2426",
      "train4513",
      "train10535",
      "train7550",
      "train8329",
      "train5659",
      "train6368",
      "train4317",
      "train9626",
      "train8955",
      "train10944",
      "train3846",
      "train8613"
    ],
    [
      "train9779",
      "train9204",
      "train11510",
      "train1390",
      "train256",
      "train490",
      "train1209",
      "train10294",
      "train7952",
      "train2763",
      "train7063",
      "train3461",
      "train7946",
      "train8748",
      "train11756",
      "train3175"
    ],
    [
      "train11665",
      "train3053",
      "train3447",
      "train8611",
      "train2240",
      "train10971",
      "train4486",
      "train4831",
      "train10947",
      "train7497",
      "train9854",
      "train10039",
      "train1222",
      "train8954",
      "train3345",
      "train12251"
    ],
    [
      "train1187",
      "train10581",
      "train7598",
      "train4900",
      "train6300",
      "train7023",
      "train8743",
      "train4760",
      "train6762",
      "train1735",
      "train1499",
      "train12101",
      "train526",
      "train6557",
      "train2279",
      "train6852"
    ],
    [
      "train6124",
      "train11078",
      "train5797",
      "train3363",
      "train6579",
      "train11079",
      "train2838",
      "train5468",
      "train7708",
      "train2879",
      "train5254",
      "train8621",
      "train9102",
      "train12033",
      "train12292",
      "train2593"
    ],
    [
      "train11565",
      "train6365",
      "train12400",
      "train8572",
      "train8511",
      "train7116",
      "train11921",
      "train2816",
      "train11106",
      "train11159",
      "train6360",
      "train11182",
      "train10346",
      "train11647",
      "train1585",
      "train3522"
    ],
    [
      "train5584",
      "train9281",
      "train5623",
      "train10490",
      "train8941",
      "train2833",
      "train7240",
      "train11111",
      "train3591",
      "train1196",
      "train1084",
      "train378",
      "train1684",
      "train307",
      "train2404",
      "train7906"
    ],
    [
      "train2078",
      "train5708",
      "train6213",
      "train10772",
      "train1332",
      "train12332",
      "train11301",
      "train1149",
      "train6648",
      "train9917",
      "train7467",
      "train1651",
      "train7739",
      "train2932",
      "train9440",
      "train10096"
    ],
    [
      "train2904",
      "train8002",
      "train902",
      "train9408",
      "train1429",
      "train10597",
      "train9886",
      "train4622",
      "train12224",
      "train4718",
      "train11288",
      "train10832",
      "train4359",
      "train11704",
      "train2312",
      "train3573"
    ],
    [
      "train6463",
      "train6015",
      "train10250",
      "train6203",
      "train5413",
      "train5380",
      "train7591",
      "train10604",
      "train8644",
      "train1695",
      "train2922",
      "train8334",
      "train9407",
      "train7683",
      "train5641",
      "train6187"
    ],
    [
      "train3502",
      "train9050",
      "train10050",
      "train519",
      "train7232",
      "train5890",
      "train5811",
      "train4545",
      "train3021",
      "train8201",
      "train10343",
      "train9812",
      "train9940",
      "train10172",
      "train2558",
      "train11753"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.00017901614774018526,
      "negative_fraction": 0.5,
      "cosines": [
        -0.08275985717773438,
        0.07362599670886993,
        -0.0060986122116446495,
        0.587476372718811,
        -0.09491710364818573,
        0.2606116235256195,
        0.2279098927974701,
        -0.09403526037931442,
        0.06487301737070084,
        -0.17842812836170197,
        0.013848181813955307,
        -0.0025745269376784563,
        -0.11196757107973099,
        0.1639123260974884,
        0.002932559233158827,
        -0.033140454441308975
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.35791000723838806,
          "other_norm": 1.6608315706253052
        },
        {
          "exist_norm": 0.9856092929840088,
          "other_norm": 2.3531033992767334
        },
        {
          "exist_norm": 0.465514600276947,
          "other_norm": 1.5977479219436646
        },
        {
          "exist_norm": 1.103795051574707,
          "other_norm": 4.590853214263916
        },
        {
          "exist_norm": 0.6457313895225525,
          "other_norm": 1.6826313734054565
        },
        {
          "exist_norm": 0.8408929109573364,
          "other_norm": 1.9982168674468994
        },
        {
          "exist_norm": 0.7366912364959717,
          "other_norm": 2.334505081176758
        },
        {
          "exist_norm": 0.5360970497131348,
          "other_norm": 2.1101760864257812
        },
        {
          "exist_norm": 0.36455923318862915,
          "other_norm": 2.2515382766723633
        },
        {
          "exist_norm": 0.23479747772216797,
          "other_norm": 1.9890352487564087
        },
        {
          "exist_norm": 0.3709244132041931,
          "other_norm": 2.7378053665161133
        },
        {
          "exist_norm": 0.3217952847480774,
          "other_norm": 2.1314589977264404
        },
        {
          "exist_norm": 0.5616074800491333,
          "other_norm": 1.9270952939987183
        },
        {
          "exist_norm": 0.6553815603256226,
          "other_norm": 1.8535792827606201
        },
        {
          "exist_norm": 0.5090013146400452,
          "other_norm": 1.7779622077941895
        },
        {
          "exist_norm": 0.330264151096344,
          "other_norm": 1.810550332069397
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.004373856354504824,
      "negative_fraction": 0.625,
      "cosines": [
        -0.01367178838700056,
        -0.09417467564344406,
        -0.0057874699123203754,
        0.355621337890625,
        -0.012285266071557999,
        0.05250829458236694,
        0.026021063327789307,
        -0.026702437549829483,
        0.005577306263148785,
        -0.005907583516091108,
        -0.0012263000244274735,
        0.003947621677070856,
        -0.019309720024466515,
        0.03068632446229458,
        -0.0034966417588293552,
        -0.005251070950180292
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.19869330525398254,
          "other_norm": 1.7465239763259888
        },
        {
          "exist_norm": 0.4461342990398407,
          "other_norm": 1.9491134881973267
        },
        {
          "exist_norm": 0.29799923300743103,
          "other_norm": 1.2817295789718628
        },
        {
          "exist_norm": 0.6338271498680115,
          "other_norm": 2.7632641792297363
        },
        {
          "exist_norm": 0.2886643409729004,
          "other_norm": 1.3279087543487549
        },
        {
          "exist_norm": 0.4449578523635864,
          "other_norm": 1.552854061126709
        },
        {
          "exist_norm": 0.3444271385669708,
          "other_norm": 1.1953438520431519
        },
        {
          "exist_norm": 0.29769256711006165,
          "other_norm": 1.7902297973632812
        },
        {
          "exist_norm": 0.2087422013282776,
          "other_norm": 1.6708875894546509
        },
        {
          "exist_norm": 0.12913326919078827,
          "other_norm": 1.3536378145217896
        },
        {
          "exist_norm": 0.1790854036808014,
          "other_norm": 1.6794211864471436
        },
        {
          "exist_norm": 0.20271362364292145,
          "other_norm": 1.3844846487045288
        },
        {
          "exist_norm": 0.31799277663230896,
          "other_norm": 1.6088811159133911
        },
        {
          "exist_norm": 0.33110976219177246,
          "other_norm": 1.765476107597351
        },
        {
          "exist_norm": 0.26745495200157166,
          "other_norm": 0.9196785688400269
        },
        {
          "exist_norm": 0.1487119495868683,
          "other_norm": 1.6564297676086426
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.09030795842409134,
      "negative_fraction": 0.125,
      "cosines": [
        0.045318253338336945,
        0.15508438646793365,
        0.35531073808670044,
        0.6334419846534729,
        0.09435675293207169,
        0.2696983218193054,
        0.1489662081003189,
        0.11994996666908264,
        0.08625916391611099,
        -0.1651925891637802,
        0.03539340943098068,
        0.029181867837905884,
        0.060410041362047195,
        0.11285107582807541,
        0.027693741023540497,
        -0.08009246736764908
      ],
      "gradient_norms": [
        {
          "exist_norm": 1.0315502882003784,
          "other_norm": 10.369010925292969
        },
        {
          "exist_norm": 3.289138078689575,
          "other_norm": 8.680673599243164
        },
        {
          "exist_norm": 1.619736909866333,
          "other_norm": 8.60776424407959
        },
        {
          "exist_norm": 4.650036811828613,
          "other_norm": 21.172880172729492
        },
        {
          "exist_norm": 2.3774328231811523,
          "other_norm": 8.120149612426758
        },
        {
          "exist_norm": 2.368678569793701,
          "other_norm": 7.581658363342285
        },
        {
          "exist_norm": 2.126197576522827,
          "other_norm": 10.801703453063965
        },
        {
          "exist_norm": 1.9292510747909546,
          "other_norm": 13.921594619750977
        },
        {
          "exist_norm": 1.031750202178955,
          "other_norm": 15.785737991333008
        },
        {
          "exist_norm": 0.8746607899665833,
          "other_norm": 14.094854354858398
        },
        {
          "exist_norm": 0.8507192134857178,
          "other_norm": 7.055879592895508
        },
        {
          "exist_norm": 0.8841649889945984,
          "other_norm": 14.929107666015625
        },
        {
          "exist_norm": 1.6398160457611084,
          "other_norm": 5.455925941467285
        },
        {
          "exist_norm": 2.2992160320281982,
          "other_norm": 7.908771991729736
        },
        {
          "exist_norm": 1.967446208000183,
          "other_norm": 9.263577461242676
        },
        {
          "exist_norm": 1.258201241493225,
          "other_norm": 8.12963581085205
        }
      ]
    },
    "adapter|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.08352332189679146,
      "negative_fraction": 0.1875,
      "cosines": [
        -0.061300527304410934,
        0.19192223250865936,
        0.30979177355766296,
        0.7941280007362366,
        0.07936028391122818,
        0.2866446375846863,
        0.28365302085876465,
        0.03194249048829079,
        0.03306526318192482,
        -0.16629712283611298,
        0.08768635988235474,
        0.05739448219537735,
        0.09897027909755707,
        0.24292264878749847,
        0.022845953702926636,
        -0.10910962522029877
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.06661814451217651,
          "other_norm": 0.3549923598766327
        },
        {
          "exist_norm": 0.2183154672384262,
          "other_norm": 0.41520529985427856
        },
        {
          "exist_norm": 0.07158274203538895,
          "other_norm": 0.22337952256202698
        },
        {
          "exist_norm": 0.2550240457057953,
          "other_norm": 0.9376984238624573
        },
        {
          "exist_norm": 0.14766427874565125,
          "other_norm": 0.29463836550712585
        },
        {
          "exist_norm": 0.18159334361553192,
          "other_norm": 0.32425588369369507
        },
        {
          "exist_norm": 0.10807231068611145,
          "other_norm": 0.345678448677063
        },
        {
          "exist_norm": 0.10856038331985474,
          "other_norm": 0.4695201814174652
        },
        {
          "exist_norm": 0.05276735499501228,
          "other_norm": 0.4654250144958496
        },
        {
          "exist_norm": 0.03862650692462921,
          "other_norm": 0.4521813988685608
        },
        {
          "exist_norm": 0.05746157839894295,
          "other_norm": 0.31951162219047546
        },
        {
          "exist_norm": 0.036800485104322433,
          "other_norm": 0.4665099084377289
        },
        {
          "exist_norm": 0.11170610785484314,
          "other_norm": 0.21777784824371338
        },
        {
          "exist_norm": 0.10489208996295929,
          "other_norm": 0.23472370207309723
        },
        {
          "exist_norm": 0.08953911811113358,
          "other_norm": 0.3306758999824524
        },
        {
          "exist_norm": 0.0631457194685936,
          "other_norm": 0.3607780933380127
        }
      ]
    }
  },
  "state": "completed",
  "checkpoint_comparison_note": "adapter best selected at epoch14; latest at epoch100"
}
```

## diagnostics/throw/adapter/GRADIENT_RELATIONS_latest.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_adapter_s3407_attempt1/latest.ckpt",
  "checkpoint_sha256": "52d5fb1db8de2848a1c694798c7ee99e15f305ff4794d5e94eebef3311e31432",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train10943",
      "train1927",
      "train6733",
      "train1214",
      "train10272",
      "train8188",
      "train3902",
      "train8169",
      "train7847",
      "train4389",
      "train9821",
      "train10930",
      "train8193",
      "train11900",
      "train7692",
      "train3375"
    ],
    [
      "train11235",
      "train2648",
      "train6552",
      "train9774",
      "train7587",
      "train9744",
      "train3797",
      "train6960",
      "train9018",
      "train2139",
      "train2990",
      "train1412",
      "train598",
      "train4481",
      "train4406",
      "train11839"
    ],
    [
      "train2195",
      "train2067",
      "train5592",
      "train6447",
      "train11550",
      "train4668",
      "train8694",
      "train6039",
      "train1825",
      "train2402",
      "train2620",
      "train12049",
      "train4621",
      "train4110",
      "train7121",
      "train1999"
    ],
    [
      "train768",
      "train5303",
      "train251",
      "train9380",
      "train6951",
      "train1791",
      "train2333",
      "train10227",
      "train12170",
      "train6371",
      "train6993",
      "train11858",
      "train4755",
      "train8046",
      "train2562",
      "train2772"
    ],
    [
      "train7780",
      "train8849",
      "train7819",
      "train5536",
      "train12139",
      "train3821",
      "train913",
      "train9358",
      "train4882",
      "train1639",
      "train1199",
      "train8496",
      "train5695",
      "train7362",
      "train4452",
      "train9836"
    ],
    [
      "train1823",
      "train128",
      "train11066",
      "train2426",
      "train4513",
      "train10535",
      "train7550",
      "train8329",
      "train5659",
      "train6368",
      "train4317",
      "train9626",
      "train8955",
      "train10944",
      "train3846",
      "train8613"
    ],
    [
      "train9779",
      "train9204",
      "train11510",
      "train1390",
      "train256",
      "train490",
      "train1209",
      "train10294",
      "train7952",
      "train2763",
      "train7063",
      "train3461",
      "train7946",
      "train8748",
      "train11756",
      "train3175"
    ],
    [
      "train11665",
      "train3053",
      "train3447",
      "train8611",
      "train2240",
      "train10971",
      "train4486",
      "train4831",
      "train10947",
      "train7497",
      "train9854",
      "train10039",
      "train1222",
      "train8954",
      "train3345",
      "train12251"
    ],
    [
      "train1187",
      "train10581",
      "train7598",
      "train4900",
      "train6300",
      "train7023",
      "train8743",
      "train4760",
      "train6762",
      "train1735",
      "train1499",
      "train12101",
      "train526",
      "train6557",
      "train2279",
      "train6852"
    ],
    [
      "train6124",
      "train11078",
      "train5797",
      "train3363",
      "train6579",
      "train11079",
      "train2838",
      "train5468",
      "train7708",
      "train2879",
      "train5254",
      "train8621",
      "train9102",
      "train12033",
      "train12292",
      "train2593"
    ],
    [
      "train11565",
      "train6365",
      "train12400",
      "train8572",
      "train8511",
      "train7116",
      "train11921",
      "train2816",
      "train11106",
      "train11159",
      "train6360",
      "train11182",
      "train10346",
      "train11647",
      "train1585",
      "train3522"
    ],
    [
      "train5584",
      "train9281",
      "train5623",
      "train10490",
      "train8941",
      "train2833",
      "train7240",
      "train11111",
      "train3591",
      "train1196",
      "train1084",
      "train378",
      "train1684",
      "train307",
      "train2404",
      "train7906"
    ],
    [
      "train2078",
      "train5708",
      "train6213",
      "train10772",
      "train1332",
      "train12332",
      "train11301",
      "train1149",
      "train6648",
      "train9917",
      "train7467",
      "train1651",
      "train7739",
      "train2932",
      "train9440",
      "train10096"
    ],
    [
      "train2904",
      "train8002",
      "train902",
      "train9408",
      "train1429",
      "train10597",
      "train9886",
      "train4622",
      "train12224",
      "train4718",
      "train11288",
      "train10832",
      "train4359",
      "train11704",
      "train2312",
      "train3573"
    ],
    [
      "train6463",
      "train6015",
      "train10250",
      "train6203",
      "train5413",
      "train5380",
      "train7591",
      "train10604",
      "train8644",
      "train1695",
      "train2922",
      "train8334",
      "train9407",
      "train7683",
      "train5641",
      "train6187"
    ],
    [
      "train3502",
      "train9050",
      "train10050",
      "train519",
      "train7232",
      "train5890",
      "train5811",
      "train4545",
      "train3021",
      "train8201",
      "train10343",
      "train9812",
      "train9940",
      "train10172",
      "train2558",
      "train11753"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.08276436850428581,
      "negative_fraction": 0.1875,
      "cosines": [
        0.0027192120905965567,
        0.07131402939558029,
        0.12180065363645554,
        -0.14979971945285797,
        0.10261338204145432,
        0.04241395741701126,
        -0.11770101636648178,
        0.031710755079984665,
        0.1993703544139862,
        0.13860391080379486,
        -0.033833183348178864,
        0.09421470761299133,
        0.20738855004310608,
        0.06971690058708191,
        0.13558626174926758,
        0.15014594793319702
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.013098646886646748,
          "other_norm": 7.707395076751709
        },
        {
          "exist_norm": 0.002355144126340747,
          "other_norm": 4.029581069946289
        },
        {
          "exist_norm": 0.04893317073583603,
          "other_norm": 5.616058349609375
        },
        {
          "exist_norm": 0.00713205523788929,
          "other_norm": 3.5401830673217773
        },
        {
          "exist_norm": 0.4904012084007263,
          "other_norm": 4.202977657318115
        },
        {
          "exist_norm": 0.0027165759820491076,
          "other_norm": 4.593275547027588
        },
        {
          "exist_norm": 0.0027555134147405624,
          "other_norm": 3.824608564376831
        },
        {
          "exist_norm": 0.001439583022147417,
          "other_norm": 5.090882778167725
        },
        {
          "exist_norm": 0.004919110331684351,
          "other_norm": 4.692183971405029
        },
        {
          "exist_norm": 0.0013111457228660583,
          "other_norm": 8.15265941619873
        },
        {
          "exist_norm": 0.0037287112791091204,
          "other_norm": 4.000452518463135
        },
        {
          "exist_norm": 0.11749779433012009,
          "other_norm": 4.170196056365967
        },
        {
          "exist_norm": 0.0021381524857133627,
          "other_norm": 4.075945854187012
        },
        {
          "exist_norm": 0.017028558999300003,
          "other_norm": 4.530601501464844
        },
        {
          "exist_norm": 0.0027438171673566103,
          "other_norm": 3.2075209617614746
        },
        {
          "exist_norm": 0.00656221155077219,
          "other_norm": 4.190644264221191
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.16369756311178207,
      "negative_fraction": 0.0625,
      "cosines": [
        0.2226044088602066,
        0.06230248883366585,
        0.21414683759212494,
        0.09536715596914291,
        0.13493220508098602,
        0.1567889004945755,
        -0.13016927242279053,
        0.20636193454265594,
        0.25126245617866516,
        0.2485838085412979,
        0.0733560174703598,
        0.004209431353956461,
        0.22495350241661072,
        0.167347714304924,
        0.16004741191864014,
        0.17928197979927063
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.003349869279190898,
          "other_norm": 1.5236276388168335
        },
        {
          "exist_norm": 0.0007405331125482917,
          "other_norm": 1.2798305749893188
        },
        {
          "exist_norm": 0.006609284318983555,
          "other_norm": 2.920687675476074
        },
        {
          "exist_norm": 0.0016791292000561953,
          "other_norm": 1.1712226867675781
        },
        {
          "exist_norm": 0.052037231624126434,
          "other_norm": 1.423784852027893
        },
        {
          "exist_norm": 0.000950728019233793,
          "other_norm": 1.7387452125549316
        },
        {
          "exist_norm": 0.000826411705929786,
          "other_norm": 1.6936225891113281
        },
        {
          "exist_norm": 0.0006726612336933613,
          "other_norm": 1.9979974031448364
        },
        {
          "exist_norm": 0.0016036647139117122,
          "other_norm": 1.8960150480270386
        },
        {
          "exist_norm": 0.00044339161831885576,
          "other_norm": 3.1092021465301514
        },
        {
          "exist_norm": 0.0014846574049443007,
          "other_norm": 1.403943657875061
        },
        {
          "exist_norm": 0.02680354006588459,
          "other_norm": 1.5147756338119507
        },
        {
          "exist_norm": 0.0007131182355806231,
          "other_norm": 1.950506329536438
        },
        {
          "exist_norm": 0.0028688483871519566,
          "other_norm": 1.6586215496063232
        },
        {
          "exist_norm": 0.001085533993318677,
          "other_norm": 1.407006025314331
        },
        {
          "exist_norm": 0.002405804581940174,
          "other_norm": 1.7875138521194458
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.031288725323975086,
      "negative_fraction": 0.6875,
      "cosines": [
        -0.011029050685465336,
        -0.07030687481164932,
        -0.06172022223472595,
        -0.15976382791996002,
        0.013884306885302067,
        -0.08622851967811584,
        -0.09110517799854279,
        -0.02925374172627926,
        0.34485557675361633,
        -0.038044948130846024,
        0.05168336257338524,
        -0.033323708921670914,
        0.12073725461959839,
        0.04472322016954422,
        -0.05427026376128197,
        -0.018328635022044182
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.014201070182025433,
          "other_norm": 16.169626235961914
        },
        {
          "exist_norm": 0.002997517818585038,
          "other_norm": 7.275461673736572
        },
        {
          "exist_norm": 0.12444324791431427,
          "other_norm": 7.6872124671936035
        },
        {
          "exist_norm": 0.0128228310495615,
          "other_norm": 7.55740213394165
        },
        {
          "exist_norm": 0.5416843891143799,
          "other_norm": 8.89715576171875
        },
        {
          "exist_norm": 0.0027823925483971834,
          "other_norm": 8.228191375732422
        },
        {
          "exist_norm": 0.008019555360078812,
          "other_norm": 8.013886451721191
        },
        {
          "exist_norm": 0.0012627922696992755,
          "other_norm": 10.154058456420898
        },
        {
          "exist_norm": 0.005200733430683613,
          "other_norm": 8.958179473876953
        },
        {
          "exist_norm": 0.0022769987117499113,
          "other_norm": 17.16387176513672
        },
        {
          "exist_norm": 0.003221603576093912,
          "other_norm": 6.77147102355957
        },
        {
          "exist_norm": 0.1125641018152237,
          "other_norm": 8.180216789245605
        },
        {
          "exist_norm": 0.002645379165187478,
          "other_norm": 6.2121477127075195
        },
        {
          "exist_norm": 0.025465326383709908,
          "other_norm": 9.353592872619629
        },
        {
          "exist_norm": 0.0038426576647907495,
          "other_norm": 6.66439962387085
        },
        {
          "exist_norm": 0.008640507236123085,
          "other_norm": 8.790621757507324
        }
      ]
    },
    "adapter|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.0032256707781925797,
      "negative_fraction": 0.5,
      "cosines": [
        -0.0011180483270436525,
        -0.04364331439137459,
        -0.03967942297458649,
        -0.1458692103624344,
        0.012224533595144749,
        -0.09128212183713913,
        -0.2071070522069931,
        0.023088207468390465,
        0.034718599170446396,
        0.027776028960943222,
        0.06940590590238571,
        0.007569389883428812,
        -0.010776430368423462,
        0.026774639263749123,
        -0.026784434914588928,
        0.05379621312022209
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.003247175831347704,
          "other_norm": 1.7360773086547852
        },
        {
          "exist_norm": 0.0004041512729600072,
          "other_norm": 0.785236120223999
        },
        {
          "exist_norm": 0.011997336521744728,
          "other_norm": 1.0067254304885864
        },
        {
          "exist_norm": 0.0012578497407957911,
          "other_norm": 0.6814782619476318
        },
        {
          "exist_norm": 0.10051990300416946,
          "other_norm": 0.9416732788085938
        },
        {
          "exist_norm": 0.0005686787189915776,
          "other_norm": 0.7625278234481812
        },
        {
          "exist_norm": 0.0007133606122806668,
          "other_norm": 0.8466181755065918
        },
        {
          "exist_norm": 0.0002412735193502158,
          "other_norm": 1.2558016777038574
        },
        {
          "exist_norm": 0.0013153216568753123,
          "other_norm": 1.078446388244629
        },
        {
          "exist_norm": 0.00027255903114564717,
          "other_norm": 2.227560043334961
        },
        {
          "exist_norm": 0.0006412803777493536,
          "other_norm": 0.6588656902313232
        },
        {
          "exist_norm": 0.023761525750160217,
          "other_norm": 0.7404140830039978
        },
        {
          "exist_norm": 0.0003888621286023408,
          "other_norm": 0.7083574533462524
        },
        {
          "exist_norm": 0.004167228005826473,
          "other_norm": 0.983761191368103
        },
        {
          "exist_norm": 0.0004912751028314233,
          "other_norm": 0.648127555847168
        },
        {
          "exist_norm": 0.0012958244187757373,
          "other_norm": 0.9972522854804993
        }
      ]
    }
  },
  "state": "completed",
  "checkpoint_comparison_note": "adapter best selected at epoch14; latest at epoch100"
}
```

## diagnostics/throw/adapter/INPUT_SENSITIVITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "rows": 570,
  "videos": 389,
  "manifest_sha256": "668a2ad56821e1114127c00185a1db2000902aab41e6442feb0811145305b966",
  "identity_max_abs_error": 0.0,
  "summaries": {
    "identity": {
      "exist_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      }
    },
    "zero_visual": {
      "exist_abs_delta": {
        "row_mean": 0.14367835941610108,
        "video_mean": 0.14206183792252314,
        "video_bootstrap_ci95": [
          0.11717088411054583,
          0.16927955170731027
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.21403508771929824,
        "video_mean": 0.20629820051413883,
        "video_bootstrap_ci95": [
          0.1675074978577549,
          0.24464974293059122
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.15097215907615527,
        "video_mean": 0.14817493452811048,
        "video_bootstrap_ci95": [
          0.12812801500444795,
          0.16657569894300586
        ]
      }
    },
    "shuffle_time": {
      "exist_abs_delta": {
        "row_mean": 0.0064503990244447135,
        "video_mean": 0.006582053290439039,
        "video_bootstrap_ci95": [
          0.004407971243804197,
          0.009033813597610492
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.03859649122807018,
        "video_mean": 0.04048843187660668,
        "video_bootstrap_ci95": [
          0.023350471293916025,
          0.0599882176520994
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.028939597236744146,
        "video_mean": 0.030409618776416104,
        "video_bootstrap_ci95": [
          0.020103884589297325,
          0.042619377944415754
        ]
      }
    },
    "zero_clip": {
      "exist_abs_delta": {
        "row_mean": 0.027248827753621235,
        "video_mean": 0.028595733088413264,
        "video_bootstrap_ci95": [
          0.021381128748564404,
          0.03649584346920916
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.11052631578947368,
        "video_mean": 0.10711225364181662,
        "video_bootstrap_ci95": [
          0.0792523564695801,
          0.1366805912596401
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.09064221714149441,
        "video_mean": 0.08851110220000136,
        "video_bootstrap_ci95": [
          0.07122865212325488,
          0.10648555491525033
        ]
      }
    },
    "zero_slowfast": {
      "exist_abs_delta": {
        "row_mean": 0.020577901471079442,
        "video_mean": 0.020143193650061796,
        "video_bootstrap_ci95": [
          0.014823527080617401,
          0.02572980384600142
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.17719298245614035,
        "video_mean": 0.16473864610111397,
        "video_bootstrap_ci95": [
          0.13152313624678666,
          0.20032133676092542
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.1356136528807774,
        "video_mean": 0.1288279654831652,
        "video_bootstrap_ci95": [
          0.10913634161395439,
          0.14961799216255603
        ]
      }
    }
  },
  "limitations": "Sensitivity of frozen model, not necessity/causal proof. Zeroing is out of distribution; shuffle preserves positions. No perturbed-label AUROC, R1, FRR or RR computed. Raw top span before official temporal postprocessing; original official gate is a scalar per row and does not change exact-precision slot ranking."
}
```

## diagnostics/throw/adapter/INPUT_SENSITIVITY_MANIFEST.json

```json
{
  "state": "frozen_before_inference",
  "seed": 3407,
  "training_updates": 0,
  "checkpoint_sha256": "7343847dc15992410f7ffb8f43502e2c3ea5e26d527b9b78d5be1124ce3135a7",
  "checkpoint_epoch_zero_based": 13,
  "source_sha256": "d980356f74f3bed35178abf6120b6ea99e8ac23aaef7748dd2e8a4f42f38dec8",
  "view_sha256": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
  "qids": [
    "train88",
    "train89",
    "train90",
    "train124",
    "train131",
    "train211",
    "train212",
    "train218",
    "train271",
    "train278",
    "train279",
    "train282",
    "train324",
    "train325",
    "train357",
    "train361",
    "train374",
    "train451",
    "train452",
    "train456",
    "train461",
    "train502",
    "train640",
    "train649",
    "train651",
    "train652",
    "train677",
    "train678",
    "train749",
    "train750",
    "train825",
    "train848",
    "train849",
    "train881",
    "train883",
    "train950",
    "train951",
    "train1006",
    "train1007",
    "train1081",
    "train1107",
    "train1108",
    "train1111",
    "train1184",
    "train1270",
    "train1323",
    "train1329",
    "train1354",
    "train1362",
    "train1465",
    "train1536",
    "train1537",
    "train1571",
    "train1659",
    "train1674",
    "train1690",
    "train1723",
    "train1772",
    "train1773",
    "train1840",
    "train2009",
    "train2033",
    "train2035",
    "train2036",
    "train2069",
    "train2070",
    "train2087",
    "train2088",
    "train2209",
    "train2222",
    "train2223",
    "train2313",
    "train2316",
    "train2317",
    "train2383",
    "train2384",
    "train2488",
    "train2507",
    "train2508",
    "train2513",
    "train2574",
    "train2575",
    "train2576",
    "train2587",
    "train2589",
    "train2590",
    "train2608",
    "train2615",
    "train2616",
    "train2626",
    "train2644",
    "train2683",
    "train2684",
    "train2707",
    "train2708",
    "train2808",
    "train2810",
    "train2914",
    "train3028",
    "train3079",
    "train3103",
    "train3104",
    "train3105",
    "train3153",
    "train3161",
    "train3191",
    "train3206",
    "train3236",
    "train3237",
    "train3283",
    "train3287",
    "train3319",
    "train3336",
    "train3410",
    "train3411",
    "train3441",
    "train3472",
    "train3498",
    "train3500",
    "train3512",
    "train3513",
    "train3517",
    "train3518",
    "train3624",
    "train3625",
    "train3650",
    "train3681",
    "train3682",
    "train3701",
    "train3802",
    "train3803",
    "train3862",
    "train3891",
    "train3892",
    "train3916",
    "train3955",
    "train3956",
    "train4032",
    "train4093",
    "train4094",
    "train4163",
    "train4179",
    "train4224",
    "train4310",
    "train4326",
    "train4327",
    "train4337",
    "train4338",
    "train4339",
    "train4367",
    "train4368",
    "train4508",
    "train4551",
    "train4628",
    "train4636",
    "train4677",
    "train4728",
    "train4744",
    "train4745",
    "train4761",
    "train4804",
    "train4840",
    "train4841",
    "train4878",
    "train4879",
    "train4913",
    "train4914",
    "train4981",
    "train4987",
    "train4988",
    "train4991",
    "train5011",
    "train5018",
    "train5145",
    "train5151",
    "train5161",
    "train5201",
    "train5202",
    "train5225",
    "train5226",
    "train5227",
    "train5314",
    "train5386",
    "train5412",
    "train5435",
    "train5471",
    "train5503",
    "train5507",
    "train5609",
    "train5610",
    "train5630",
    "train5631",
    "train5673",
    "train5713",
    "train5716",
    "train5747",
    "train5748",
    "train5794",
    "train5801",
    "train5805",
    "train5823",
    "train5846",
    "train5848",
    "train5994",
    "train6021",
    "train6076",
    "train6077",
    "train6081",
    "train6134",
    "train6135",
    "train6177",
    "train6178",
    "train6195",
    "train6208",
    "train6242",
    "train6245",
    "train6274",
    "train6275",
    "train6321",
    "train6386",
    "train6387",
    "train6388",
    "train6401",
    "train6402",
    "train6480",
    "train6502",
    "train6504",
    "train6517",
    "train6518",
    "train6586",
    "train6595",
    "train6596",
    "train6598",
    "train6630",
    "train6631",
    "train6632",
    "train6633",
    "train6642",
    "train6661",
    "train6662",
    "train6670",
    "train6676",
    "train6688",
    "train6690",
    "train6716",
    "train6717",
    "train6730",
    "train6738",
    "train6790",
    "train6811",
    "train6864",
    "train6911",
    "train6928",
    "train6980",
    "train6981",
    "train7032",
    "train7033",
    "train7035",
    "train7106",
    "train7111",
    "train7112",
    "train7138",
    "train7146",
    "train7218",
    "train7219",
    "train7222",
    "train7282",
    "train7345",
    "train7373",
    "train7385",
    "train7419",
    "train7420",
    "train7428",
    "train7429",
    "train7430",
    "train7448",
    "train7455",
    "train7483",
    "train7484",
    "train7485",
    "train7555",
    "train7556",
    "train7574",
    "train7580",
    "train7582",
    "train7583",
    "train7605",
    "train7606",
    "train7646",
    "train7662",
    "train7663",
    "train7664",
    "train7710",
    "train7712",
    "train7777",
    "train7794",
    "train7799",
    "train7814",
    "train7875",
    "train7894",
    "train7902",
    "train7910",
    "train8000",
    "train8010",
    "train8011",
    "train8014",
    "train8015",
    "train8144",
    "train8158",
    "train8185",
    "train8187",
    "train8196",
    "train8213",
    "train8264",
    "train8268",
    "train8269",
    "train8353",
    "train8354",
    "train8355",
    "train8411",
    "train8464",
    "train8514",
    "train8577",
    "train8578",
    "train8603",
    "train8604",
    "train8648",
    "train8724",
    "train8725",
    "train8758",
    "train8814",
    "train8840",
    "train8842",
    "train8860",
    "train8865",
    "train8939",
    "train8969",
    "train8970",
    "train9013",
    "train9014",
    "train9016",
    "train9197",
    "train9247",
    "train9272",
    "train9315",
    "train9316",
    "train9347",
    "train9348",
    "train9361",
    "train9387",
    "train9415",
    "train9420",
    "train9422",
    "train9476",
    "train9478",
    "train9479",
    "train9482",
    "train9505",
    "train9507",
    "train9508",
    "train9531",
    "train9534",
    "train9547",
    "train9548",
    "train9551",
    "train9576",
    "train9585",
    "train9586",
    "train9588",
    "train9593",
    "train9620",
    "train9669",
    "train9762",
    "train9763",
    "train9789",
    "train9791",
    "train9809",
    "train9882",
    "train9883",
    "train9958",
    "train9959",
    "train10007",
    "train10027",
    "train10052",
    "train10054",
    "train10055",
    "train10056",
    "train10133",
    "train10194",
    "train10206",
    "train10207",
    "train10246",
    "train10260",
    "train10268",
    "train10357",
    "train10358",
    "train10368",
    "train10413",
    "train10455",
    "train10457",
    "train10460",
    "train10461",
    "train10593",
    "train10613",
    "train10660",
    "train10661",
    "train10780",
    "train10830",
    "train10844",
    "train10863",
    "train10881",
    "train10935",
    "train10953",
    "train10954",
    "train11015",
    "train11020",
    "train11141",
    "train11142",
    "train11195",
    "train11342",
    "train11432",
    "train11438",
    "train11454",
    "train11458",
    "train11464",
    "train11465",
    "train11473",
    "train11493",
    "train11504",
    "train11505",
    "train11513",
    "train11514",
    "train11515",
    "train11522",
    "train11523",
    "train11531",
    "train11532",
    "train11559",
    "train11561",
    "train11585",
    "train11621",
    "train11622",
    "train11644",
    "train11645",
    "train11653",
    "train11684",
    "train11735",
    "train11742",
    "train11759",
    "train11762",
    "train11770",
    "train12014",
    "train12076",
    "train12079",
    "train12194",
    "train12196",
    "train12236",
    "train12262",
    "train12322",
    "train12355",
    "train12356",
    "train12367",
    "train12405",
    "train12406",
    "neg_0356f3aa545fecc9",
    "neg_05e3781e6a69476e",
    "neg_0aa097b2b049bb42",
    "neg_0ac079a7c120857d",
    "neg_0ce4d23bf3a3e434",
    "neg_0de51182aa554280",
    "neg_0e340ee7d685e84b",
    "neg_0fff5c470a66e632",
    "neg_1372aab42e4b6266",
    "neg_179ec5fdae1f9378",
    "neg_1ccab5e73f4807f4",
    "neg_1d70ded749aff498",
    "neg_1d769cf7c1b70366",
    "neg_1eeb6def7111cf70",
    "neg_27df813d3f94b7c3",
    "neg_2903529dc003a31f",
    "neg_2c1e2bafcc1c2ba3",
    "neg_2e0d0161d366342d",
    "neg_3226064207f4f425",
    "neg_37695fff75d90f51",
    "neg_3f7b950c37d9a581",
    "neg_4031558675d4d139",
    "neg_4111a15dd5106a66",
    "neg_411d970212c60a96",
    "neg_42536139424de1b2",
    "neg_42c682ee833e83f1",
    "neg_435816eda25f1fd8",
    "neg_437acf83063023f1",
    "neg_448b93dac696bfce",
    "neg_469d70306c4e8cb6",
    "neg_46eb057bf3a55e97",
    "neg_48f05f2ac84c8997",
    "neg_4ae29350b63a613f",
    "neg_512c88b24866769e",
    "neg_5226bb80dc5674c9",
    "neg_5536ca1f334e1d71",
    "neg_55d46a75a2d09114",
    "neg_58f0b27bcfe789b6",
    "neg_5994fb6b06b62c51",
    "neg_5bbc13251a588cde",
    "neg_5c97e4119d6809db",
    "neg_6287083a25151280",
    "neg_632bbab755d6ff84",
    "neg_643c8e6ea67d15ad",
    "neg_664463d35b05230a",
    "neg_66da85a7c759e30d",
    "neg_68b517b1666eb195",
    "neg_69230b4c00eacca8",
    "neg_6b90a483930e5f31",
    "neg_6c6ce774a4aada77",
    "neg_6dfad46dafbb00c1",
    "neg_6edb4b00ee70e4cb",
    "neg_70950f8705e9536e",
    "neg_7353b57ab1f9c95a",
    "neg_7431b6b3327c4780",
    "neg_7ace005038981993",
    "neg_7bc9e9171d299a6d",
    "neg_7c2b47d9a11e5792",
    "neg_7fa99e6f253121de",
    "neg_80c6e675d7e0a8b9",
    "neg_82c7b2807162032d",
    "neg_875a21f921d70187",
    "neg_90273c67420ee208",
    "neg_90b47dd04770f19d",
    "neg_91f8407c5b699dfa",
    "neg_965f68151037127f",
    "neg_9751265dd820b49d",
    "neg_a0ca537abbe4bde6",
    "neg_a35291186747e3f1",
    "neg_a4bf9fd31e4aa2ba",
    "neg_a9c02641b1594466",
    "neg_aa528afe06333e9f",
    "neg_af2ff4fe426214d7",
    "neg_af88201bd348e15c",
    "neg_b185a39f6d977e10",
    "neg_b2921dad672deac2",
    "neg_b517bddadc52e173",
    "neg_b545b4e592aeba0c",
    "neg_b848bcb0623eae3a",
    "neg_bbeb1e2061be898a",
    "neg_bce609411f7d8dfd",
    "neg_bd4aa8f36e05348f",
    "neg_bec95039b2572b8f",
    "neg_c0cf96cf6ce024b2",
    "neg_c6756135cc6ee5cc",
    "neg_ce857dc57a6200c7",
    "neg_d0b2246178816f8e",
    "neg_d3cfcea3d420682f",
    "neg_d5c6a9c0b6fcfb45",
    "neg_d69f031f8290f17e",
    "neg_d817cd7c0d438450",
    "neg_d846d2630a4e4e58",
    "neg_df0cf681fd091297",
    "neg_e20f9f830c32fde6",
    "neg_e56f3c6f7c809732",
    "neg_e632e1abead00f11",
    "neg_ee6c8350b1dac3dc",
    "neg_eeb5d6b75fc092bd",
    "neg_f0889a6f394a2f0c",
    "neg_f1caffb03205a176",
    "neg_f3d89fd21be00c36",
    "neg_f70d8013dda0361c",
    "neg_f8fa52252d4cea83",
    "neg_fc195ed1d23b1b9f",
    "neg_feae6426d2be85b7",
    "neg_ffbdd422c37c6880"
  ],
  "branches": [
    [
      "vid_clip",
      0,
      512
    ],
    [
      "vid_slowfast",
      512,
      2816
    ]
  ],
  "modes": [
    "identity",
    "zero_visual",
    "shuffle_time",
    "zero_clip",
    "zero_slowfast"
  ],
  "perturbation": "zero normalized visual channels; shuffle valid visual rows only; masks, padded rows, text and TEF preserved",
  "permutation": "same permutation for each video and all queries; CPU generator seeded by SHA256(seed|vid|length)",
  "selection": "all existing pseudo rows, original order; no outcome-based selection",
  "accuracy_under_perturbation": "not computed"
}
```

## diagnostics/throw/adapter/LATEST_FAILURE_DECOMPOSITION.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "checkpoint_epoch_zero_based": 99,
  "checkpoint_sha256": "52d5fb1db8de2848a1c694798c7ee99e15f305ff4794d5e94eebef3311e31432",
  "source_sha256": "a4a8dc5c9317945a71a184eab08e9a7962137004e736c19e12dcc34ba62741d0",
  "same_model_tensors_as_best": false,
  "predictions_reused_from_best": false,
  "results": {
    "pseudo": {
      "AUROC": 0.612668754066363,
      "raw_R1_05": 0.23060344827586207,
      "gated_R1_05": 0.23922413793103448,
      "FRR": 0.16810344827586207,
      "RR": 0.3867924528301887,
      "counts": {
        "positive": 464,
        "raw_incorrect": 357,
        "positive_rejected": 78,
        "official_gated_correct": 111,
        "raw_correct_gated_wrong": 2,
        "raw_wrong_gated_correct": 6,
        "official_empty": 0,
        "raw_correct": 107,
        "raw_correct_rejected": 25,
        "raw_correct_accepted": 82,
        "negative": 106,
        "negative_accepted": 65
      },
      "raw_correct_rejected_over_raw_correct": 0.2336448598130841,
      "raw_errors_over_hard_failures": 0.9345549738219895,
      "threshold": 0.9997,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "24fc1d11c7cf00816bfb4cc22d88b4c9373c7ad327bce86788f6946348505735"
    },
    "seen": {
      "AUROC": 0.7834667717580684,
      "raw_R1_05": 0.3695345557122708,
      "gated_R1_05": 0.36530324400564174,
      "FRR": 0.29055007052186177,
      "RR": 0.7563025210084033,
      "counts": {
        "positive": 709,
        "raw_incorrect": 447,
        "positive_rejected": 206,
        "official_gated_correct": 259,
        "raw_correct_gated_wrong": 8,
        "raw_wrong_gated_correct": 5,
        "official_empty": 0,
        "raw_correct": 262,
        "raw_correct_accepted": 200,
        "raw_correct_rejected": 62,
        "negative": 476,
        "negative_accepted": 116
      },
      "raw_correct_rejected_over_raw_correct": 0.2366412213740458,
      "raw_errors_over_hard_failures": 0.8781925343811395,
      "threshold": 0.9997,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "299e42544987f130d21240f45277f6a5019e83479bb3fd0e42238c657833531b"
    }
  },
  "limitations": "Latest comparison is descriptive, not an alternative pseudo-based checkpoint selection or full training trajectory; unchanged official gate, diagnostic threshold fitted on latest seen only."
}
```

## diagnostics/throw/adapter/VISUAL_INCREMENT.json

```json
{
  "pseudo": {
    "same_video_pairacc": 0.9846153846153847,
    "same_video_pairs": 65,
    "cross_video_pairacc": 0.5995236059366029,
    "exact_query_cross_video_pairacc": 0.5,
    "exact_query_cross_video_pairs": 37,
    "exact_query_groups": 10,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 32
  },
  "seen": {
    "same_video_pairacc": 0.7450361010830325,
    "same_video_pairs": 1108,
    "cross_video_pairacc": 0.8449116464908317,
    "exact_query_cross_video_pairacc": 0.6929347826086957,
    "exact_query_cross_video_pairs": 368,
    "exact_query_groups": 52,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 199
  }
}
```

## diagnostics/throw/baseline/CONTROLLED_QUERY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "query_groups": 10,
  "rows": 36,
  "pairs": 37,
  "pairacc": 0.25675675675675674,
  "video_endpoint_bootstrap_ci95": [
    0.02939762443438914,
    0.5232696566998893
  ],
  "text_input": "same normalized cached feature and mask per identical query, canonical lexicographically smallest qid; original video and labels unchanged",
  "pure_text_pairacc_control": 0.5,
  "checkpoint_sha256": "bf7e1ac3fc68e9718797e9dcae12960b56f04e48d2f138cac381f13145b46d26",
  "scores": {
    "train2036": 0.9999849796295166,
    "train2914": 0.9993324875831604,
    "train4094": 0.9995380640029907,
    "train4551": 0.9999723434448242,
    "train4988": 0.9999963045120239,
    "train5151": 0.9715062975883484,
    "train5386": 0.9999034404754639,
    "train5713": 0.9999978542327881,
    "train6081": 2.1942103558103554e-05,
    "train6586": 0.9999973773956299,
    "train6717": 0.9960154891014099,
    "train7222": 0.9983997941017151,
    "train9531": 0.9999904632568359,
    "train9586": 0.9999535083770752,
    "train12079": 0.9999938011169434,
    "neg_2903529dc003a31f": 0.9995892643928528,
    "neg_2c1e2bafcc1c2ba3": 0.998917818069458,
    "neg_2e0d0161d366342d": 0.9999597072601318,
    "neg_3226064207f4f425": 0.9999959468841553,
    "neg_4111a15dd5106a66": 0.9999972581863403,
    "neg_469d70306c4e8cb6": 0.9999958276748657,
    "neg_48f05f2ac84c8997": 0.9999849796295166,
    "neg_68b517b1666eb195": 0.9999949932098389,
    "neg_6edb4b00ee70e4cb": 0.9999895095825195,
    "neg_70950f8705e9536e": 0.9999994039535522,
    "neg_7353b57ab1f9c95a": 0.9999994039535522,
    "neg_90273c67420ee208": 0.9999877214431763,
    "neg_a9c02641b1594466": 0.9999977350234985,
    "neg_af88201bd348e15c": 0.9999479055404663,
    "neg_b517bddadc52e173": 0.9999887943267822,
    "neg_b545b4e592aeba0c": 0.9999891519546509,
    "neg_c0cf96cf6ce024b2": 0.9996196031570435,
    "neg_d0b2246178816f8e": 0.9997307658195496,
    "neg_d5c6a9c0b6fcfb45": 0.9999542236328125,
    "neg_feae6426d2be85b7": 0.9998407363891602,
    "neg_ffbdd422c37c6880": 0.9999967813491821
  },
  "limitations": "original labels only; sparse correlated pairs, endpoint video bootstrap; not a causal proof or full-sample metric"
}
```

## diagnostics/throw/baseline/FAILURE_DECOMPOSITION.json

```json
{
  "pseudo": {
    "AUROC": 0.5731030416395576,
    "raw_R1_05": 0.2672413793103448,
    "gated_R1_05": 0.26939655172413796,
    "FRR": 0.08836206896551724,
    "RR": 0.13207547169811318,
    "counts": {
      "positive": 464,
      "raw_incorrect": 340,
      "positive_rejected": 41,
      "official_gated_correct": 125,
      "raw_correct_gated_wrong": 6,
      "raw_wrong_gated_correct": 7,
      "official_empty": 0,
      "raw_correct": 124,
      "raw_correct_accepted": 109,
      "raw_correct_rejected": 15,
      "negative": 106,
      "negative_accepted": 92
    },
    "raw_correct_rejected_over_positives": 0.032327586206896554,
    "raw_correct_rejected_over_raw_correct": 0.12096774193548387,
    "raw_errors_over_hard_failures": 0.9577464788732394,
    "threshold": 0.9973,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.8153846153846154,
    "same_video_pairs": 65,
    "cross_video_pairacc": 0.572782426352328,
    "exact_query_cross_video_pairacc": 0.3783783783783784,
    "exact_query_cross_video_pairs": 37,
    "exact_query_groups": 10,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 32,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/pseudo.jsonl": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
      "pseudo_predictions.jsonl": "a5c4d5c0d3a5ee7bb4cb517a0af0c829868ddef9dd249964b7feb8230685501f"
    }
  },
  "seen": {
    "AUROC": 0.7996112408291949,
    "raw_R1_05": 0.4400564174894217,
    "gated_R1_05": 0.4414668547249647,
    "FRR": 0.2073342736248237,
    "RR": 0.703781512605042,
    "counts": {
      "positive": 709,
      "raw_correct": 312,
      "raw_correct_accepted": 255,
      "positive_rejected": 147,
      "official_gated_correct": 313,
      "raw_correct_gated_wrong": 8,
      "raw_wrong_gated_correct": 9,
      "official_empty": 0,
      "raw_incorrect": 397,
      "raw_correct_rejected": 57,
      "negative": 476,
      "negative_accepted": 141
    },
    "raw_correct_rejected_over_positives": 0.08039492242595205,
    "raw_correct_rejected_over_raw_correct": 0.18269230769230768,
    "raw_errors_over_hard_failures": 0.8744493392070485,
    "threshold": 0.9973,
    "threshold_source": "seen validation only",
    "unit": "original rows; pair combinations correlated",
    "training_updates": 0,
    "same_video_pairacc": 0.7333032490974729,
    "same_video_pairs": 1108,
    "cross_video_pairacc": 0.7998296549099817,
    "exact_query_cross_video_pairacc": 0.6290760869565217,
    "exact_query_cross_video_pairs": 368,
    "exact_query_groups": 52,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 199,
    "input_feature_audit": "normalized last_hidden_state first 32 tokens; determinism and feature equality required for text tie control",
    "source_hashes": {
      "views/val_seen.jsonl": "29166e4d694480fd41184bd4ff5802d1251103f4a042cdcbd9ac25ab7ddb6685",
      "best_seen_predictions.jsonl": "606dd34aa6a38cacb278b767183719efa483a0fba24aa782806cb34798461d1f"
    }
  }
}
```

## diagnostics/throw/baseline/GATE_POSTPROCESS_AUDIT.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "results": {
    "pseudo": {
      "rows": 570,
      "positive": 464,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train131",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train1465",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2009",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2087",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2587",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train2589",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train3283",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train4327",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train5202",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train6135",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train6195",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train9883",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train10260",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.26939655172413796,
      "official_gated_R1_05": 0.26939655172413796,
      "prediction_sha256": "a5c4d5c0d3a5ee7bb4cb517a0af0c829868ddef9dd249964b7feb8230685501f"
    },
    "seen": {
      "rows": 1185,
      "positive": 709,
      "all_ranked_coordinate_mismatches": 0,
      "mismatch_qids": [],
      "raw_to_gated_hit_changes": [
        {
          "qid": "train290",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train622",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train1540",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train1541",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train1941",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train3542",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train3982",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train5907",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train7757",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train8826",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train9640",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train10827",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train10828",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train11094",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train11414",
          "raw_hit": true,
          "gated_hit": false,
          "aligned_raw_hit": false
        },
        {
          "qid": "train12155",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        },
        {
          "qid": "train12156",
          "raw_hit": false,
          "gated_hit": true,
          "aligned_raw_hit": true
        }
      ],
      "aligned_raw_R1_05_auxiliary": 0.4414668547249647,
      "official_gated_R1_05": 0.4414668547249647,
      "prediction_sha256": "606dd34aa6a38cacb278b767183719efa483a0fba24aa782806cb34798461d1f"
    }
  },
  "source_sha256": "e8f3da3638ebe09271ab1e32db99dd2ce36e12e5d52584165ea6d7310791f5f4",
  "official_evaluator_sha256": "b71f952fa6cfbfbaae1ca0b6bd1f476159c17c2448b87d55f82300fa97a50537",
  "official_postprocessor_sha256": "50e6501c642e77502f7a4d781e01e12bbd97521d3b0a8f47d793b3044be30046",
  "gate_sha256": "0e1235c8425f9c61883e88a57a8a1feec2c9ceb15046aeecd83563deb3cefc67",
  "interpretation": "Official soft gate is a per-row nonnegative scalar. Exact positive scalar scaling preserves within-row ranking. Saved gated coordinates alone receive clip_ts/round_multiple; frozen raw endpoint remains untouched. When aligned coordinates match, hit changes are explained by temporal postprocessing rather than gate veto or reranking. Aligned raw is auxiliary only, not a replacement co-primary endpoint."
}
```

## diagnostics/throw/baseline/GRADIENT_DETAIL.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "source_sha256": "aa62ab661c26930186b53405490d723cc70e4c952e94a60596cd0584f7619473",
  "checkpoints": {
    "best": {
      "checkpoint_epoch_zero_based": 99,
      "checkpoint_sha256": "bf7e1ac3fc68e9718797e9dcae12960b56f04e48d2f138cac381f13145b46d26",
      "model_tensor_sha256": "7f6d9a2ea09d96eb00ed01f44221b539919a377ffe853e1a22d016b10a8012bb",
      "original_diagnostic_sha256": "8ec130996863dccf2bced2900b942a8266ec894271de6ec913a61d930afda671",
      "qids": [
        [
          "train10943",
          "train1927",
          "train6733",
          "train1214",
          "train10272",
          "train8188",
          "train3902",
          "train8169",
          "train7847",
          "train4389",
          "train9821",
          "train10930",
          "train8193",
          "train11900",
          "train7692",
          "train3375"
        ],
        [
          "train11235",
          "train2648",
          "train6552",
          "train9774",
          "train7587",
          "train9744",
          "train3797",
          "train6960",
          "train9018",
          "train2139",
          "train2990",
          "train1412",
          "train598",
          "train4481",
          "train4406",
          "train11839"
        ],
        [
          "train2195",
          "train2067",
          "train5592",
          "train6447",
          "train11550",
          "train4668",
          "train8694",
          "train6039",
          "train1825",
          "train2402",
          "train2620",
          "train12049",
          "train4621",
          "train4110",
          "train7121",
          "train1999"
        ],
        [
          "train768",
          "train5303",
          "train251",
          "train9380",
          "train6951",
          "train1791",
          "train2333",
          "train10227",
          "train12170",
          "train6371",
          "train6993",
          "train11858",
          "train4755",
          "train8046",
          "train2562",
          "train2772"
        ],
        [
          "train7780",
          "train8849",
          "train7819",
          "train5536",
          "train12139",
          "train3821",
          "train913",
          "train9358",
          "train4882",
          "train1639",
          "train1199",
          "train8496",
          "train5695",
          "train7362",
          "train4452",
          "train9836"
        ],
        [
          "train1823",
          "train128",
          "train11066",
          "train2426",
          "train4513",
          "train10535",
          "train7550",
          "train8329",
          "train5659",
          "train6368",
          "train4317",
          "train9626",
          "train8955",
          "train10944",
          "train3846",
          "train8613"
        ],
        [
          "train9779",
          "train9204",
          "train11510",
          "train1390",
          "train256",
          "train490",
          "train1209",
          "train10294",
          "train7952",
          "train2763",
          "train7063",
          "train3461",
          "train7946",
          "train8748",
          "train11756",
          "train3175"
        ],
        [
          "train11665",
          "train3053",
          "train3447",
          "train8611",
          "train2240",
          "train10971",
          "train4486",
          "train4831",
          "train10947",
          "train7497",
          "train9854",
          "train10039",
          "train1222",
          "train8954",
          "train3345",
          "train12251"
        ],
        [
          "train1187",
          "train10581",
          "train7598",
          "train4900",
          "train6300",
          "train7023",
          "train8743",
          "train4760",
          "train6762",
          "train1735",
          "train1499",
          "train12101",
          "train526",
          "train6557",
          "train2279",
          "train6852"
        ],
        [
          "train6124",
          "train11078",
          "train5797",
          "train3363",
          "train6579",
          "train11079",
          "train2838",
          "train5468",
          "train7708",
          "train2879",
          "train5254",
          "train8621",
          "train9102",
          "train12033",
          "train12292",
          "train2593"
        ],
        [
          "train11565",
          "train6365",
          "train12400",
          "train8572",
          "train8511",
          "train7116",
          "train11921",
          "train2816",
          "train11106",
          "train11159",
          "train6360",
          "train11182",
          "train10346",
          "train11647",
          "train1585",
          "train3522"
        ],
        [
          "train5584",
          "train9281",
          "train5623",
          "train10490",
          "train8941",
          "train2833",
          "train7240",
          "train11111",
          "train3591",
          "train1196",
          "train1084",
          "train378",
          "train1684",
          "train307",
          "train2404",
          "train7906"
        ],
        [
          "train2078",
          "train5708",
          "train6213",
          "train10772",
          "train1332",
          "train12332",
          "train11301",
          "train1149",
          "train6648",
          "train9917",
          "train7467",
          "train1651",
          "train7739",
          "train2932",
          "train9440",
          "train10096"
        ],
        [
          "train2904",
          "train8002",
          "train902",
          "train9408",
          "train1429",
          "train10597",
          "train9886",
          "train4622",
          "train12224",
          "train4718",
          "train11288",
          "train10832",
          "train4359",
          "train11704",
          "train2312",
          "train3573"
        ],
        [
          "train6463",
          "train6015",
          "train10250",
          "train6203",
          "train5413",
          "train5380",
          "train7591",
          "train10604",
          "train8644",
          "train1695",
          "train2922",
          "train8334",
          "train9407",
          "train7683",
          "train5641",
          "train6187"
        ],
        [
          "train3502",
          "train9050",
          "train10050",
          "train519",
          "train7232",
          "train5890",
          "train5811",
          "train4545",
          "train3021",
          "train8201",
          "train10343",
          "train9812",
          "train9940",
          "train10172",
          "train2558",
          "train11753"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.003692119149491191
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.392452955245972
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.08697203174233437,
          "negative_fraction": 0.0
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.0012982243788428605
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.362616539001465
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.0069575002416968346,
          "negative_fraction": 0.6875
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.006329986033961177
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 7.00980544090271
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.0011668792139971629,
          "negative_fraction": 0.5
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0009948520455509424
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0342913419008255
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1935899704694748
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003782973624765873
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0011250530369579792
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03355933725833893
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01514214277267456
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003601264674216509
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5163825154304504
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0004919166094623506
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0380488857626915
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.0863442420959473
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0012626778334379196
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0009560472099110484
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001022028038278222
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0008991325157694519
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.206856727600098
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.846637487411499
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.546026229858398
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.394691467285156
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.390214443206787
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.1479902267456055
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.6621286869049072
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.945169448852539
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.094541072845459
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.733137130737305
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.03436803817749
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.451921463012695
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.818717002868652
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3944389820098877
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3022263050079346
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.967593669891357
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.09228387475013733
          },
          {
            "full_block_cosine": 0.10818704962730408
          },
          {
            "full_block_cosine": 0.0816601887345314
          },
          {
            "full_block_cosine": 0.04777093231678009
          },
          {
            "full_block_cosine": 0.023311354219913483
          },
          {
            "full_block_cosine": 0.15440650284290314
          },
          {
            "full_block_cosine": 0.07755106687545776
          },
          {
            "full_block_cosine": 0.20775724947452545
          },
          {
            "full_block_cosine": 0.09993183612823486
          },
          {
            "full_block_cosine": 0.0036477793473750353
          },
          {
            "full_block_cosine": 0.024829596281051636
          },
          {
            "full_block_cosine": 0.03285786882042885
          },
          {
            "full_block_cosine": 0.17799192667007446
          },
          {
            "full_block_cosine": 0.05528495833277702
          },
          {
            "full_block_cosine": 0.13963532447814941
          },
          {
            "full_block_cosine": 0.16427959501743317
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.000489872763864696
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004748494829982519
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03138153627514839
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0014670572709292173
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005465236026793718
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004826808348298073
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0025055143050849438
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0011293914867565036
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06316497176885605
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0002717931056395173
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0068612233735620975
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1096108928322792
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005361547810025513
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00044501369120553136
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005490267649292946
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005096192471683025
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.1838908195495605
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.5229427814483643
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.9634528160095215
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8429839611053467
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.461026668548584
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.458636283874512
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.0175323486328125
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.467162609100342
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.357828140258789
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.4163665771484375
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.258070468902588
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.295029640197754
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.714860439300537
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.5276341438293457
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3577709197998047
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.075929164886475
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": -0.00898493081331253
          },
          {
            "full_block_cosine": -0.002294393489137292
          },
          {
            "full_block_cosine": 0.0035333794075995684
          },
          {
            "full_block_cosine": -0.02094789408147335
          },
          {
            "full_block_cosine": -0.007928329519927502
          },
          {
            "full_block_cosine": -0.049186330288648605
          },
          {
            "full_block_cosine": -0.016137607395648956
          },
          {
            "full_block_cosine": -0.0059866709634661674
          },
          {
            "full_block_cosine": -0.026068657636642456
          },
          {
            "full_block_cosine": -0.001441206899471581
          },
          {
            "full_block_cosine": 0.014208192005753517
          },
          {
            "full_block_cosine": 0.0007813255651853979
          },
          {
            "full_block_cosine": 0.002282137284055352
          },
          {
            "full_block_cosine": 0.002922484651207924
          },
          {
            "full_block_cosine": -0.011229196563363075
          },
          {
            "full_block_cosine": -0.010502327233552933
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001603215467184782
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.07401183247566223
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.318111777305603
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00657753786072135
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0016019388567656279
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06615268439054489
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03907999396324158
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.006082434207201004
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8231972455978394
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0006774942157790065
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.07132408767938614
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.459388017654419
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001795572112314403
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0015103997429832816
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0016332798404619098
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0011115365196019411
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.026609420776367
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.204413414001465
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.438023090362549
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.241738319396973
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.113771438598633
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.27379035949707
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.1023969650268555
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.3317389488220215
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.9172139167785645
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.581883430480957
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.653757095336914
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.234419822692871
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.670456409454346
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.30422306060791
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.574842929840088
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.998705863952637
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": -0.027902767062187195
          },
          {
            "full_block_cosine": 0.0038227932527661324
          },
          {
            "full_block_cosine": -0.013997281901538372
          },
          {
            "full_block_cosine": -0.015546778216958046
          },
          {
            "full_block_cosine": -0.09725131839513779
          },
          {
            "full_block_cosine": -0.0026977655943483114
          },
          {
            "full_block_cosine": 0.025910183787345886
          },
          {
            "full_block_cosine": -0.030558258295059204
          },
          {
            "full_block_cosine": 0.00036400716635398567
          },
          {
            "full_block_cosine": 0.030522147193551064
          },
          {
            "full_block_cosine": 0.07253633439540863
          },
          {
            "full_block_cosine": -0.03483681008219719
          },
          {
            "full_block_cosine": 0.09826712310314178
          },
          {
            "full_block_cosine": -0.09185706079006195
          },
          {
            "full_block_cosine": 0.06511545926332474
          },
          {
            "full_block_cosine": 0.004338898696005344
          }
        ]
      },
      "reused_identical_model_from": null,
      "independent_checkpoint_evidence": true
    },
    "latest": {
      "checkpoint_epoch_zero_based": 99,
      "checkpoint_sha256": "bf7e1ac3fc68e9718797e9dcae12960b56f04e48d2f138cac381f13145b46d26",
      "model_tensor_sha256": "7f6d9a2ea09d96eb00ed01f44221b539919a377ffe853e1a22d016b10a8012bb",
      "original_diagnostic_sha256": "8ec130996863dccf2bced2900b942a8266ec894271de6ec913a61d930afda671",
      "qids": [
        [
          "train10943",
          "train1927",
          "train6733",
          "train1214",
          "train10272",
          "train8188",
          "train3902",
          "train8169",
          "train7847",
          "train4389",
          "train9821",
          "train10930",
          "train8193",
          "train11900",
          "train7692",
          "train3375"
        ],
        [
          "train11235",
          "train2648",
          "train6552",
          "train9774",
          "train7587",
          "train9744",
          "train3797",
          "train6960",
          "train9018",
          "train2139",
          "train2990",
          "train1412",
          "train598",
          "train4481",
          "train4406",
          "train11839"
        ],
        [
          "train2195",
          "train2067",
          "train5592",
          "train6447",
          "train11550",
          "train4668",
          "train8694",
          "train6039",
          "train1825",
          "train2402",
          "train2620",
          "train12049",
          "train4621",
          "train4110",
          "train7121",
          "train1999"
        ],
        [
          "train768",
          "train5303",
          "train251",
          "train9380",
          "train6951",
          "train1791",
          "train2333",
          "train10227",
          "train12170",
          "train6371",
          "train6993",
          "train11858",
          "train4755",
          "train8046",
          "train2562",
          "train2772"
        ],
        [
          "train7780",
          "train8849",
          "train7819",
          "train5536",
          "train12139",
          "train3821",
          "train913",
          "train9358",
          "train4882",
          "train1639",
          "train1199",
          "train8496",
          "train5695",
          "train7362",
          "train4452",
          "train9836"
        ],
        [
          "train1823",
          "train128",
          "train11066",
          "train2426",
          "train4513",
          "train10535",
          "train7550",
          "train8329",
          "train5659",
          "train6368",
          "train4317",
          "train9626",
          "train8955",
          "train10944",
          "train3846",
          "train8613"
        ],
        [
          "train9779",
          "train9204",
          "train11510",
          "train1390",
          "train256",
          "train490",
          "train1209",
          "train10294",
          "train7952",
          "train2763",
          "train7063",
          "train3461",
          "train7946",
          "train8748",
          "train11756",
          "train3175"
        ],
        [
          "train11665",
          "train3053",
          "train3447",
          "train8611",
          "train2240",
          "train10971",
          "train4486",
          "train4831",
          "train10947",
          "train7497",
          "train9854",
          "train10039",
          "train1222",
          "train8954",
          "train3345",
          "train12251"
        ],
        [
          "train1187",
          "train10581",
          "train7598",
          "train4900",
          "train6300",
          "train7023",
          "train8743",
          "train4760",
          "train6762",
          "train1735",
          "train1499",
          "train12101",
          "train526",
          "train6557",
          "train2279",
          "train6852"
        ],
        [
          "train6124",
          "train11078",
          "train5797",
          "train3363",
          "train6579",
          "train11079",
          "train2838",
          "train5468",
          "train7708",
          "train2879",
          "train5254",
          "train8621",
          "train9102",
          "train12033",
          "train12292",
          "train2593"
        ],
        [
          "train11565",
          "train6365",
          "train12400",
          "train8572",
          "train8511",
          "train7116",
          "train11921",
          "train2816",
          "train11106",
          "train11159",
          "train6360",
          "train11182",
          "train10346",
          "train11647",
          "train1585",
          "train3522"
        ],
        [
          "train5584",
          "train9281",
          "train5623",
          "train10490",
          "train8941",
          "train2833",
          "train7240",
          "train11111",
          "train3591",
          "train1196",
          "train1084",
          "train378",
          "train1684",
          "train307",
          "train2404",
          "train7906"
        ],
        [
          "train2078",
          "train5708",
          "train6213",
          "train10772",
          "train1332",
          "train12332",
          "train11301",
          "train1149",
          "train6648",
          "train9917",
          "train7467",
          "train1651",
          "train7739",
          "train2932",
          "train9440",
          "train10096"
        ],
        [
          "train2904",
          "train8002",
          "train902",
          "train9408",
          "train1429",
          "train10597",
          "train9886",
          "train4622",
          "train12224",
          "train4718",
          "train11288",
          "train10832",
          "train4359",
          "train11704",
          "train2312",
          "train3573"
        ],
        [
          "train6463",
          "train6015",
          "train10250",
          "train6203",
          "train5413",
          "train5380",
          "train7591",
          "train10604",
          "train8644",
          "train1695",
          "train2922",
          "train8334",
          "train9407",
          "train7683",
          "train5641",
          "train6187"
        ],
        [
          "train3502",
          "train9050",
          "train10050",
          "train519",
          "train7232",
          "train5890",
          "train5811",
          "train4545",
          "train3021",
          "train8201",
          "train10343",
          "train9812",
          "train9940",
          "train10172",
          "train2558",
          "train11753"
        ]
      ],
      "batches": 16,
      "observed_weighted_loss_keys": [
        "loss_exist",
        "loss_giou",
        "loss_giou_0",
        "loss_label",
        "loss_label_0",
        "loss_span",
        "loss_span_0"
      ],
      "loss_weights": {
        "loss_span": 10,
        "loss_giou": 1,
        "loss_label": 4,
        "loss_saliency": 0,
        "loss_span_0": 10,
        "loss_giou_0": 1,
        "loss_label_0": 4,
        "loss_exist": 1.0
      },
      "summary": {
        "interaction|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.003692119149491191
        },
        "interaction|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.392452955245972
        },
        "interaction|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "interaction|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": 0.08697203174233437,
          "negative_fraction": 0.0
        },
        "decoder|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.06521739130434782,
          "median_full_block_norm": 0.0012982243788428605
        },
        "decoder|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 4.362616539001465
        },
        "decoder|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "decoder|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.0069575002416968346,
          "negative_fraction": 0.6875
        },
        "input_projection|exist": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 0.006329986033961177
        },
        "input_projection|loc": {
          "available_batches": 16,
          "unavailable_batches": 0,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": 0.0,
          "median_full_block_norm": 7.00980544090271
        },
        "input_projection|saliency": {
          "available_batches": 0,
          "unavailable_batches": 16,
          "nonfinite_tensors": 0,
          "mean_unused_tensor_fraction": null,
          "median_full_block_norm": null
        },
        "input_projection|exist_vs_loc": {
          "valid_batches": 16,
          "invalid_batches": 0,
          "median_cosine": -0.0011668792139971629,
          "negative_fraction": 0.5
        }
      },
      "batch_records": {
        "interaction|exist": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0009948520455509424
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0342913419008255
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1935899704694748
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003782973624765873
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0011250530369579792
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03355933725833893
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.01514214277267456
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.003601264674216509
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.5163825154304504
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0004919166094623506
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0380488857626915
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 1.0863442420959473
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0012626778334379196
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0009560472099110484
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001022028038278222
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0008991325157694519
          }
        ],
        "interaction|loc": [
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.206856727600098
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.846637487411499
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.546026229858398
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.394691467285156
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.390214443206787
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.1479902267456055
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.6621286869049072
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.945169448852539
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.094541072845459
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.733137130737305
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.03436803817749
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.451921463012695
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.818717002868652
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3944389820098877
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3022263050079346
          },
          {
            "available": true,
            "tensor_count": 52,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.967593669891357
          }
        ],
        "interaction|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "interaction|exist_vs_loc": [
          {
            "full_block_cosine": 0.09228387475013733
          },
          {
            "full_block_cosine": 0.10818704962730408
          },
          {
            "full_block_cosine": 0.0816601887345314
          },
          {
            "full_block_cosine": 0.04777093231678009
          },
          {
            "full_block_cosine": 0.023311354219913483
          },
          {
            "full_block_cosine": 0.15440650284290314
          },
          {
            "full_block_cosine": 0.07755106687545776
          },
          {
            "full_block_cosine": 0.20775724947452545
          },
          {
            "full_block_cosine": 0.09993183612823486
          },
          {
            "full_block_cosine": 0.0036477793473750353
          },
          {
            "full_block_cosine": 0.024829596281051636
          },
          {
            "full_block_cosine": 0.03285786882042885
          },
          {
            "full_block_cosine": 0.17799192667007446
          },
          {
            "full_block_cosine": 0.05528495833277702
          },
          {
            "full_block_cosine": 0.13963532447814941
          },
          {
            "full_block_cosine": 0.16427959501743317
          }
        ],
        "decoder|exist": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.000489872763864696
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004748494829982519
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03138153627514839
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0014670572709292173
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005465236026793718
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.004826808348298073
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0025055143050849438
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0011293914867565036
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06316497176885605
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0002717931056395173
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0068612233735620975
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.1096108928322792
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005361547810025513
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00044501369120553136
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005490267649292946
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.06521739130434782,
            "zero_among_used_tensor_fraction": 0.03488372093023256,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0005096192471683025
          }
        ],
        "decoder|loc": [
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.1838908195495605
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.5229427814483643
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.9634528160095215
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 2.8429839611053467
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.461026668548584
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.458636283874512
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.0175323486328125
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.467162609100342
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.357828140258789
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.4163665771484375
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.258070468902588
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.295029640197754
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.714860439300537
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.5276341438293457
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.3577709197998047
          },
          {
            "available": true,
            "tensor_count": 92,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.03260869565217391,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 4.075929164886475
          }
        ],
        "decoder|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "decoder|exist_vs_loc": [
          {
            "full_block_cosine": -0.00898493081331253
          },
          {
            "full_block_cosine": -0.002294393489137292
          },
          {
            "full_block_cosine": 0.0035333794075995684
          },
          {
            "full_block_cosine": -0.02094789408147335
          },
          {
            "full_block_cosine": -0.007928329519927502
          },
          {
            "full_block_cosine": -0.049186330288648605
          },
          {
            "full_block_cosine": -0.016137607395648956
          },
          {
            "full_block_cosine": -0.0059866709634661674
          },
          {
            "full_block_cosine": -0.026068657636642456
          },
          {
            "full_block_cosine": -0.001441206899471581
          },
          {
            "full_block_cosine": 0.014208192005753517
          },
          {
            "full_block_cosine": 0.0007813255651853979
          },
          {
            "full_block_cosine": 0.002282137284055352
          },
          {
            "full_block_cosine": 0.002922484651207924
          },
          {
            "full_block_cosine": -0.011229196563363075
          },
          {
            "full_block_cosine": -0.010502327233552933
          }
        ],
        "input_projection|exist": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001603215467184782
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.07401183247566223
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.318111777305603
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.00657753786072135
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0016019388567656279
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.06615268439054489
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.03907999396324158
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.006082434207201004
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.8231972455978394
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0006774942157790065
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.07132408767938614
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 3.459388017654419
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.001795572112314403
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0015103997429832816
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0016332798404619098
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 0.0011115365196019411
          }
        ],
        "input_projection|loc": [
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.026609420776367
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.204413414001465
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.438023090362549
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 10.241738319396973
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.113771438598633
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.27379035949707
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 7.1023969650268555
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.3317389488220215
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.9172139167785645
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.581883430480957
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.653757095336914
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 9.234419822692871
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.670456409454346
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 5.30422306060791
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 6.574842929840088
          },
          {
            "available": true,
            "tensor_count": 16,
            "unused_tensor_fraction": 0.0,
            "zero_among_used_tensor_fraction": 0.0,
            "nonfinite_used_tensors": 0,
            "full_block_norm": 8.998705863952637
          }
        ],
        "input_projection|saliency": [
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          },
          {
            "available": false,
            "reason": "loss absent or no differentiable loss"
          }
        ],
        "input_projection|exist_vs_loc": [
          {
            "full_block_cosine": -0.027902767062187195
          },
          {
            "full_block_cosine": 0.0038227932527661324
          },
          {
            "full_block_cosine": -0.013997281901538372
          },
          {
            "full_block_cosine": -0.015546778216958046
          },
          {
            "full_block_cosine": -0.09725131839513779
          },
          {
            "full_block_cosine": -0.0026977655943483114
          },
          {
            "full_block_cosine": 0.025910183787345886
          },
          {
            "full_block_cosine": -0.030558258295059204
          },
          {
            "full_block_cosine": 0.00036400716635398567
          },
          {
            "full_block_cosine": 0.030522147193551064
          },
          {
            "full_block_cosine": 0.07253633439540863
          },
          {
            "full_block_cosine": -0.03483681008219719
          },
          {
            "full_block_cosine": 0.09826712310314178
          },
          {
            "full_block_cosine": -0.09185706079006195
          },
          {
            "full_block_cosine": 0.06511545926332474
          },
          {
            "full_block_cosine": 0.004338898696005344
          }
        ]
      },
      "reused_identical_model_from": "best",
      "independent_checkpoint_evidence": false
    }
  },
  "interpretation": "S+ only, eval mode local geometry; unused tensors treated as zero in full-block cosine. Original norms used only the jointly differentiable tensor intersection; detail fixes interpretation without overwriting original output. Inactive saliency is unavailable, not agreement. No S- localization gradient is inferred."
}
```

## diagnostics/throw/baseline/GRADIENT_RELATIONS_best.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/best.ckpt",
  "checkpoint_sha256": "bf7e1ac3fc68e9718797e9dcae12960b56f04e48d2f138cac381f13145b46d26",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train10943",
      "train1927",
      "train6733",
      "train1214",
      "train10272",
      "train8188",
      "train3902",
      "train8169",
      "train7847",
      "train4389",
      "train9821",
      "train10930",
      "train8193",
      "train11900",
      "train7692",
      "train3375"
    ],
    [
      "train11235",
      "train2648",
      "train6552",
      "train9774",
      "train7587",
      "train9744",
      "train3797",
      "train6960",
      "train9018",
      "train2139",
      "train2990",
      "train1412",
      "train598",
      "train4481",
      "train4406",
      "train11839"
    ],
    [
      "train2195",
      "train2067",
      "train5592",
      "train6447",
      "train11550",
      "train4668",
      "train8694",
      "train6039",
      "train1825",
      "train2402",
      "train2620",
      "train12049",
      "train4621",
      "train4110",
      "train7121",
      "train1999"
    ],
    [
      "train768",
      "train5303",
      "train251",
      "train9380",
      "train6951",
      "train1791",
      "train2333",
      "train10227",
      "train12170",
      "train6371",
      "train6993",
      "train11858",
      "train4755",
      "train8046",
      "train2562",
      "train2772"
    ],
    [
      "train7780",
      "train8849",
      "train7819",
      "train5536",
      "train12139",
      "train3821",
      "train913",
      "train9358",
      "train4882",
      "train1639",
      "train1199",
      "train8496",
      "train5695",
      "train7362",
      "train4452",
      "train9836"
    ],
    [
      "train1823",
      "train128",
      "train11066",
      "train2426",
      "train4513",
      "train10535",
      "train7550",
      "train8329",
      "train5659",
      "train6368",
      "train4317",
      "train9626",
      "train8955",
      "train10944",
      "train3846",
      "train8613"
    ],
    [
      "train9779",
      "train9204",
      "train11510",
      "train1390",
      "train256",
      "train490",
      "train1209",
      "train10294",
      "train7952",
      "train2763",
      "train7063",
      "train3461",
      "train7946",
      "train8748",
      "train11756",
      "train3175"
    ],
    [
      "train11665",
      "train3053",
      "train3447",
      "train8611",
      "train2240",
      "train10971",
      "train4486",
      "train4831",
      "train10947",
      "train7497",
      "train9854",
      "train10039",
      "train1222",
      "train8954",
      "train3345",
      "train12251"
    ],
    [
      "train1187",
      "train10581",
      "train7598",
      "train4900",
      "train6300",
      "train7023",
      "train8743",
      "train4760",
      "train6762",
      "train1735",
      "train1499",
      "train12101",
      "train526",
      "train6557",
      "train2279",
      "train6852"
    ],
    [
      "train6124",
      "train11078",
      "train5797",
      "train3363",
      "train6579",
      "train11079",
      "train2838",
      "train5468",
      "train7708",
      "train2879",
      "train5254",
      "train8621",
      "train9102",
      "train12033",
      "train12292",
      "train2593"
    ],
    [
      "train11565",
      "train6365",
      "train12400",
      "train8572",
      "train8511",
      "train7116",
      "train11921",
      "train2816",
      "train11106",
      "train11159",
      "train6360",
      "train11182",
      "train10346",
      "train11647",
      "train1585",
      "train3522"
    ],
    [
      "train5584",
      "train9281",
      "train5623",
      "train10490",
      "train8941",
      "train2833",
      "train7240",
      "train11111",
      "train3591",
      "train1196",
      "train1084",
      "train378",
      "train1684",
      "train307",
      "train2404",
      "train7906"
    ],
    [
      "train2078",
      "train5708",
      "train6213",
      "train10772",
      "train1332",
      "train12332",
      "train11301",
      "train1149",
      "train6648",
      "train9917",
      "train7467",
      "train1651",
      "train7739",
      "train2932",
      "train9440",
      "train10096"
    ],
    [
      "train2904",
      "train8002",
      "train902",
      "train9408",
      "train1429",
      "train10597",
      "train9886",
      "train4622",
      "train12224",
      "train4718",
      "train11288",
      "train10832",
      "train4359",
      "train11704",
      "train2312",
      "train3573"
    ],
    [
      "train6463",
      "train6015",
      "train10250",
      "train6203",
      "train5413",
      "train5380",
      "train7591",
      "train10604",
      "train8644",
      "train1695",
      "train2922",
      "train8334",
      "train9407",
      "train7683",
      "train5641",
      "train6187"
    ],
    [
      "train3502",
      "train9050",
      "train10050",
      "train519",
      "train7232",
      "train5890",
      "train5811",
      "train4545",
      "train3021",
      "train8201",
      "train10343",
      "train9812",
      "train9940",
      "train10172",
      "train2558",
      "train11753"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.08697201684117317,
      "negative_fraction": 0.0,
      "cosines": [
        0.09228385239839554,
        0.10818701237440109,
        0.0816601812839508,
        0.04777095094323158,
        0.023311354219913483,
        0.15440645813941956,
        0.07755105942487717,
        0.20775726437568665,
        0.09993182122707367,
        0.00364778283983469,
        0.024829592555761337,
        0.03285784646868706,
        0.17799192667007446,
        0.05528495833277702,
        0.13963529467582703,
        0.16427962481975555
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.0009948520455509424,
          "other_norm": 5.206857204437256
        },
        {
          "exist_norm": 0.0342913381755352,
          "other_norm": 2.846637487411499
        },
        {
          "exist_norm": 0.193589985370636,
          "other_norm": 4.54602575302124
        },
        {
          "exist_norm": 0.0037829738575965166,
          "other_norm": 4.394691467285156
        },
        {
          "exist_norm": 0.0011250528041273355,
          "other_norm": 4.3902153968811035
        },
        {
          "exist_norm": 0.03355933725833893,
          "other_norm": 5.1479902267456055
        },
        {
          "exist_norm": 0.015142141841351986,
          "other_norm": 3.662128448486328
        },
        {
          "exist_norm": 0.003601264441385865,
          "other_norm": 3.945169448852539
        },
        {
          "exist_norm": 0.5163824558258057,
          "other_norm": 4.094541549682617
        },
        {
          "exist_norm": 0.0004919166094623506,
          "other_norm": 5.733137607574463
        },
        {
          "exist_norm": 0.038048889487981796,
          "other_norm": 4.03436803817749
        },
        {
          "exist_norm": 1.0863443613052368,
          "other_norm": 5.451921463012695
        },
        {
          "exist_norm": 0.001262677600607276,
          "other_norm": 4.818717002868652
        },
        {
          "exist_norm": 0.0009560472681187093,
          "other_norm": 3.394439458847046
        },
        {
          "exist_norm": 0.001022028154693544,
          "other_norm": 3.3022267818450928
        },
        {
          "exist_norm": 0.0008991324575617909,
          "other_norm": 4.967593669891357
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.022348107770085335,
      "negative_fraction": 0.6875,
      "cosines": [
        -0.0299069806933403,
        -0.008699396625161171,
        0.011375650763511658,
        -0.042377471923828125,
        -0.03377358242869377,
        -0.15393495559692383,
        -0.053712207823991776,
        -0.022698992863297462,
        -0.08316057175397873,
        -0.0032654840033501387,
        0.04163914546370506,
        0.003085305215790868,
        0.008535990491509438,
        0.009107105433940887,
        -0.025306010618805885,
        -0.021997222676873207
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.000489872763864696,
          "other_norm": 1.5573921203613281
        },
        {
          "exist_norm": 0.004748494829982519,
          "other_norm": 0.929146945476532
        },
        {
          "exist_norm": 0.03138153627514839,
          "other_norm": 1.541693925857544
        },
        {
          "exist_norm": 0.0014670573873445392,
          "other_norm": 1.40533447265625
        },
        {
          "exist_norm": 0.0005465236026793718,
          "other_norm": 1.2819727659225464
        },
        {
          "exist_norm": 0.004826808348298073,
          "other_norm": 1.74418044090271
        },
        {
          "exist_norm": 0.0025055143050849438,
          "other_norm": 1.5074963569641113
        },
        {
          "exist_norm": 0.0011293913703411818,
          "other_norm": 1.1781768798828125
        },
        {
          "exist_norm": 0.06316497176885605,
          "other_norm": 1.0525909662246704
        },
        {
          "exist_norm": 0.00027179307653568685,
          "other_norm": 1.5077985525131226
        },
        {
          "exist_norm": 0.00686122290790081,
          "other_norm": 1.4529472589492798
        },
        {
          "exist_norm": 0.1096109077334404,
          "other_norm": 1.5941543579101562
        },
        {
          "exist_norm": 0.0005361547810025513,
          "other_norm": 1.7952500581741333
        },
        {
          "exist_norm": 0.0004450137203093618,
          "other_norm": 1.132023572921753
        },
        {
          "exist_norm": 0.0005490267649292946,
          "other_norm": 1.4899650812149048
        },
        {
          "exist_norm": 0.0005096192471683025,
          "other_norm": 1.946006417274475
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.0011668763909256086,
      "negative_fraction": 0.5,
      "cosines": [
        -0.027902772650122643,
        0.003822793485596776,
        -0.013997280970215797,
        -0.015546785667538643,
        -0.09725131094455719,
        -0.0026977669913321733,
        0.025910189375281334,
        -0.030558248981833458,
        0.0003640142094809562,
        0.030522143468260765,
        0.07253634929656982,
        -0.03483681008219719,
        0.09826711565256119,
        -0.09185706079006195,
        0.06511546671390533,
        0.00433889776468277
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.001603215467184782,
          "other_norm": 9.026609420776367
        },
        {
          "exist_norm": 0.07401183247566223,
          "other_norm": 5.204413890838623
        },
        {
          "exist_norm": 0.318111777305603,
          "other_norm": 6.438023090362549
        },
        {
          "exist_norm": 0.00657753786072135,
          "other_norm": 10.241737365722656
        },
        {
          "exist_norm": 0.0016019388567656279,
          "other_norm": 7.113771915435791
        },
        {
          "exist_norm": 0.06615269184112549,
          "other_norm": 8.27379035949707
        },
        {
          "exist_norm": 0.03907999396324158,
          "other_norm": 7.1023969650268555
        },
        {
          "exist_norm": 0.006082434207201004,
          "other_norm": 6.3317389488220215
        },
        {
          "exist_norm": 0.8231973052024841,
          "other_norm": 6.9172139167785645
        },
        {
          "exist_norm": 0.0006774942157790065,
          "other_norm": 9.581883430480957
        },
        {
          "exist_norm": 0.07132408767938614,
          "other_norm": 6.653757095336914
        },
        {
          "exist_norm": 3.459388017654419,
          "other_norm": 9.234420776367188
        },
        {
          "exist_norm": 0.0017955722287297249,
          "other_norm": 6.670456409454346
        },
        {
          "exist_norm": 0.0015103998593986034,
          "other_norm": 5.30422306060791
        },
        {
          "exist_norm": 0.0016332798404619098,
          "other_norm": 6.57484245300293
        },
        {
          "exist_norm": 0.0011115365196019411,
          "other_norm": 8.998705863952637
        }
      ]
    }
  },
  "state": "completed",
  "checkpoint_comparison_note": "baseline best selected at epoch100, identical to final epoch; do not count best/latest as two stages"
}
```

## diagnostics/throw/baseline/GRADIENT_RELATIONS_latest.json

```json
{
  "checkpoint": "/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization/runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1/latest.ckpt",
  "checkpoint_sha256": "c2f475c2229f17927e869cea48379552973ef5e1510831655302d7adf50396c9",
  "training_updates": 0,
  "mode": "eval; local geometry only, not causal evidence",
  "qids": [
    [
      "train10943",
      "train1927",
      "train6733",
      "train1214",
      "train10272",
      "train8188",
      "train3902",
      "train8169",
      "train7847",
      "train4389",
      "train9821",
      "train10930",
      "train8193",
      "train11900",
      "train7692",
      "train3375"
    ],
    [
      "train11235",
      "train2648",
      "train6552",
      "train9774",
      "train7587",
      "train9744",
      "train3797",
      "train6960",
      "train9018",
      "train2139",
      "train2990",
      "train1412",
      "train598",
      "train4481",
      "train4406",
      "train11839"
    ],
    [
      "train2195",
      "train2067",
      "train5592",
      "train6447",
      "train11550",
      "train4668",
      "train8694",
      "train6039",
      "train1825",
      "train2402",
      "train2620",
      "train12049",
      "train4621",
      "train4110",
      "train7121",
      "train1999"
    ],
    [
      "train768",
      "train5303",
      "train251",
      "train9380",
      "train6951",
      "train1791",
      "train2333",
      "train10227",
      "train12170",
      "train6371",
      "train6993",
      "train11858",
      "train4755",
      "train8046",
      "train2562",
      "train2772"
    ],
    [
      "train7780",
      "train8849",
      "train7819",
      "train5536",
      "train12139",
      "train3821",
      "train913",
      "train9358",
      "train4882",
      "train1639",
      "train1199",
      "train8496",
      "train5695",
      "train7362",
      "train4452",
      "train9836"
    ],
    [
      "train1823",
      "train128",
      "train11066",
      "train2426",
      "train4513",
      "train10535",
      "train7550",
      "train8329",
      "train5659",
      "train6368",
      "train4317",
      "train9626",
      "train8955",
      "train10944",
      "train3846",
      "train8613"
    ],
    [
      "train9779",
      "train9204",
      "train11510",
      "train1390",
      "train256",
      "train490",
      "train1209",
      "train10294",
      "train7952",
      "train2763",
      "train7063",
      "train3461",
      "train7946",
      "train8748",
      "train11756",
      "train3175"
    ],
    [
      "train11665",
      "train3053",
      "train3447",
      "train8611",
      "train2240",
      "train10971",
      "train4486",
      "train4831",
      "train10947",
      "train7497",
      "train9854",
      "train10039",
      "train1222",
      "train8954",
      "train3345",
      "train12251"
    ],
    [
      "train1187",
      "train10581",
      "train7598",
      "train4900",
      "train6300",
      "train7023",
      "train8743",
      "train4760",
      "train6762",
      "train1735",
      "train1499",
      "train12101",
      "train526",
      "train6557",
      "train2279",
      "train6852"
    ],
    [
      "train6124",
      "train11078",
      "train5797",
      "train3363",
      "train6579",
      "train11079",
      "train2838",
      "train5468",
      "train7708",
      "train2879",
      "train5254",
      "train8621",
      "train9102",
      "train12033",
      "train12292",
      "train2593"
    ],
    [
      "train11565",
      "train6365",
      "train12400",
      "train8572",
      "train8511",
      "train7116",
      "train11921",
      "train2816",
      "train11106",
      "train11159",
      "train6360",
      "train11182",
      "train10346",
      "train11647",
      "train1585",
      "train3522"
    ],
    [
      "train5584",
      "train9281",
      "train5623",
      "train10490",
      "train8941",
      "train2833",
      "train7240",
      "train11111",
      "train3591",
      "train1196",
      "train1084",
      "train378",
      "train1684",
      "train307",
      "train2404",
      "train7906"
    ],
    [
      "train2078",
      "train5708",
      "train6213",
      "train10772",
      "train1332",
      "train12332",
      "train11301",
      "train1149",
      "train6648",
      "train9917",
      "train7467",
      "train1651",
      "train7739",
      "train2932",
      "train9440",
      "train10096"
    ],
    [
      "train2904",
      "train8002",
      "train902",
      "train9408",
      "train1429",
      "train10597",
      "train9886",
      "train4622",
      "train12224",
      "train4718",
      "train11288",
      "train10832",
      "train4359",
      "train11704",
      "train2312",
      "train3573"
    ],
    [
      "train6463",
      "train6015",
      "train10250",
      "train6203",
      "train5413",
      "train5380",
      "train7591",
      "train10604",
      "train8644",
      "train1695",
      "train2922",
      "train8334",
      "train9407",
      "train7683",
      "train5641",
      "train6187"
    ],
    [
      "train3502",
      "train9050",
      "train10050",
      "train519",
      "train7232",
      "train5890",
      "train5811",
      "train4545",
      "train3021",
      "train8201",
      "train10343",
      "train9812",
      "train9940",
      "train10172",
      "train2558",
      "train11753"
    ]
  ],
  "loss_weights": {
    "loss_span": 10,
    "loss_giou": 1,
    "loss_label": 4,
    "loss_saliency": 0,
    "loss_span_0": 10,
    "loss_giou_0": 1,
    "loss_label_0": 4,
    "loss_exist": 1.0
  },
  "blocks": {
    "interaction|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": 0.08697201684117317,
      "negative_fraction": 0.0,
      "cosines": [
        0.09228385239839554,
        0.10818701237440109,
        0.0816601812839508,
        0.04777095094323158,
        0.023311354219913483,
        0.15440645813941956,
        0.07755105942487717,
        0.20775726437568665,
        0.09993182122707367,
        0.00364778283983469,
        0.024829592555761337,
        0.03285784646868706,
        0.17799192667007446,
        0.05528495833277702,
        0.13963529467582703,
        0.16427962481975555
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.0009948520455509424,
          "other_norm": 5.206857204437256
        },
        {
          "exist_norm": 0.0342913381755352,
          "other_norm": 2.846637487411499
        },
        {
          "exist_norm": 0.193589985370636,
          "other_norm": 4.54602575302124
        },
        {
          "exist_norm": 0.0037829738575965166,
          "other_norm": 4.394691467285156
        },
        {
          "exist_norm": 0.0011250528041273355,
          "other_norm": 4.3902153968811035
        },
        {
          "exist_norm": 0.03355933725833893,
          "other_norm": 5.1479902267456055
        },
        {
          "exist_norm": 0.015142141841351986,
          "other_norm": 3.662128448486328
        },
        {
          "exist_norm": 0.003601264441385865,
          "other_norm": 3.945169448852539
        },
        {
          "exist_norm": 0.5163824558258057,
          "other_norm": 4.094541549682617
        },
        {
          "exist_norm": 0.0004919166094623506,
          "other_norm": 5.733137607574463
        },
        {
          "exist_norm": 0.038048889487981796,
          "other_norm": 4.03436803817749
        },
        {
          "exist_norm": 1.0863443613052368,
          "other_norm": 5.451921463012695
        },
        {
          "exist_norm": 0.001262677600607276,
          "other_norm": 4.818717002868652
        },
        {
          "exist_norm": 0.0009560472681187093,
          "other_norm": 3.394439458847046
        },
        {
          "exist_norm": 0.001022028154693544,
          "other_norm": 3.3022267818450928
        },
        {
          "exist_norm": 0.0008991324575617909,
          "other_norm": 4.967593669891357
        }
      ]
    },
    "decoder|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.022348107770085335,
      "negative_fraction": 0.6875,
      "cosines": [
        -0.0299069806933403,
        -0.008699396625161171,
        0.011375650763511658,
        -0.042377471923828125,
        -0.03377358242869377,
        -0.15393495559692383,
        -0.053712207823991776,
        -0.022698992863297462,
        -0.08316057175397873,
        -0.0032654840033501387,
        0.04163914546370506,
        0.003085305215790868,
        0.008535990491509438,
        0.009107105433940887,
        -0.025306010618805885,
        -0.021997222676873207
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.000489872763864696,
          "other_norm": 1.5573921203613281
        },
        {
          "exist_norm": 0.004748494829982519,
          "other_norm": 0.929146945476532
        },
        {
          "exist_norm": 0.03138153627514839,
          "other_norm": 1.541693925857544
        },
        {
          "exist_norm": 0.0014670573873445392,
          "other_norm": 1.40533447265625
        },
        {
          "exist_norm": 0.0005465236026793718,
          "other_norm": 1.2819727659225464
        },
        {
          "exist_norm": 0.004826808348298073,
          "other_norm": 1.74418044090271
        },
        {
          "exist_norm": 0.0025055143050849438,
          "other_norm": 1.5074963569641113
        },
        {
          "exist_norm": 0.0011293913703411818,
          "other_norm": 1.1781768798828125
        },
        {
          "exist_norm": 0.06316497176885605,
          "other_norm": 1.0525909662246704
        },
        {
          "exist_norm": 0.00027179307653568685,
          "other_norm": 1.5077985525131226
        },
        {
          "exist_norm": 0.00686122290790081,
          "other_norm": 1.4529472589492798
        },
        {
          "exist_norm": 0.1096109077334404,
          "other_norm": 1.5941543579101562
        },
        {
          "exist_norm": 0.0005361547810025513,
          "other_norm": 1.7952500581741333
        },
        {
          "exist_norm": 0.0004450137203093618,
          "other_norm": 1.132023572921753
        },
        {
          "exist_norm": 0.0005490267649292946,
          "other_norm": 1.4899650812149048
        },
        {
          "exist_norm": 0.0005096192471683025,
          "other_norm": 1.946006417274475
        }
      ]
    },
    "input_projection|loc": {
      "valid_batches": 16,
      "invalid_batches": 0,
      "median_cosine": -0.0011668763909256086,
      "negative_fraction": 0.5,
      "cosines": [
        -0.027902772650122643,
        0.003822793485596776,
        -0.013997280970215797,
        -0.015546785667538643,
        -0.09725131094455719,
        -0.0026977669913321733,
        0.025910189375281334,
        -0.030558248981833458,
        0.0003640142094809562,
        0.030522143468260765,
        0.07253634929656982,
        -0.03483681008219719,
        0.09826711565256119,
        -0.09185706079006195,
        0.06511546671390533,
        0.00433889776468277
      ],
      "gradient_norms": [
        {
          "exist_norm": 0.001603215467184782,
          "other_norm": 9.026609420776367
        },
        {
          "exist_norm": 0.07401183247566223,
          "other_norm": 5.204413890838623
        },
        {
          "exist_norm": 0.318111777305603,
          "other_norm": 6.438023090362549
        },
        {
          "exist_norm": 0.00657753786072135,
          "other_norm": 10.241737365722656
        },
        {
          "exist_norm": 0.0016019388567656279,
          "other_norm": 7.113771915435791
        },
        {
          "exist_norm": 0.06615269184112549,
          "other_norm": 8.27379035949707
        },
        {
          "exist_norm": 0.03907999396324158,
          "other_norm": 7.1023969650268555
        },
        {
          "exist_norm": 0.006082434207201004,
          "other_norm": 6.3317389488220215
        },
        {
          "exist_norm": 0.8231973052024841,
          "other_norm": 6.9172139167785645
        },
        {
          "exist_norm": 0.0006774942157790065,
          "other_norm": 9.581883430480957
        },
        {
          "exist_norm": 0.07132408767938614,
          "other_norm": 6.653757095336914
        },
        {
          "exist_norm": 3.459388017654419,
          "other_norm": 9.234420776367188
        },
        {
          "exist_norm": 0.0017955722287297249,
          "other_norm": 6.670456409454346
        },
        {
          "exist_norm": 0.0015103998593986034,
          "other_norm": 5.30422306060791
        },
        {
          "exist_norm": 0.0016332798404619098,
          "other_norm": 6.57484245300293
        },
        {
          "exist_norm": 0.0011115365196019411,
          "other_norm": 8.998705863952637
        }
      ]
    }
  },
  "state": "completed",
  "checkpoint_comparison_note": "baseline best selected at epoch100, identical to final epoch; do not count best/latest as two stages"
}
```

## diagnostics/throw/baseline/INPUT_SENSITIVITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "rows": 570,
  "videos": 389,
  "manifest_sha256": "d7f9d54e90a136b1b2545edf3254a7fd046ad7e073ac37c1c6c58c6bbb879f52",
  "identity_max_abs_error": 0.0,
  "summaries": {
    "identity": {
      "exist_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.0,
        "video_mean": 0.0,
        "video_bootstrap_ci95": [
          0.0,
          0.0
        ]
      }
    },
    "zero_visual": {
      "exist_abs_delta": {
        "row_mean": 0.05328256927038494,
        "video_mean": 0.046892336626387914,
        "video_bootstrap_ci95": [
          0.03096304170551112,
          0.06384832922180902
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.45964912280701753,
        "video_mean": 0.466152527849186,
        "video_bootstrap_ci95": [
          0.41921593830334186,
          0.5113753213367609
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.21663227574082844,
        "video_mean": 0.22037830164028777,
        "video_bootstrap_ci95": [
          0.2032488574785034,
          0.2363686482234512
        ]
      }
    },
    "shuffle_time": {
      "exist_abs_delta": {
        "row_mean": 0.015773166233070936,
        "video_mean": 0.0158960007334634,
        "video_bootstrap_ci95": [
          0.008206664843043176,
          0.024618307066802406
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.2578947368421053,
        "video_mean": 0.25021422450728364,
        "video_bootstrap_ci95": [
          0.20864931448157675,
          0.2917791345329906
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.10672524452470897,
        "video_mean": 0.1060805540155195,
        "video_bootstrap_ci95": [
          0.09064706933717367,
          0.12186994213445693
        ]
      }
    },
    "zero_clip": {
      "exist_abs_delta": {
        "row_mean": 0.05423709511006771,
        "video_mean": 0.053025779027208494,
        "video_bootstrap_ci95": [
          0.03524751571789696,
          0.07236058114828363
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.23684210526315788,
        "video_mean": 0.23436161096829475,
        "video_bootstrap_ci95": [
          0.1951585261353899,
          0.2731416023993145
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.10881709415923085,
        "video_mean": 0.10556357630688917,
        "video_bootstrap_ci95": [
          0.091927766210967,
          0.12027268333678974
        ]
      }
    },
    "zero_slowfast": {
      "exist_abs_delta": {
        "row_mean": 0.041878262018940404,
        "video_mean": 0.036799843183249546,
        "video_bootstrap_ci95": [
          0.02352648652150789,
          0.054210995020475015
        ]
      },
      "raw_top_slot_changed": {
        "row_mean": 0.4017543859649123,
        "video_mean": 0.4012425021422451,
        "video_bootstrap_ci95": [
          0.3549646529562982,
          0.44970544130248497
        ]
      },
      "raw_top_endpoint_mean_abs_delta": {
        "row_mean": 0.17553268999776298,
        "video_mean": 0.17093230005044047,
        "video_bootstrap_ci95": [
          0.1558521445853765,
          0.18510376537021575
        ]
      }
    }
  },
  "limitations": "Sensitivity of frozen model, not necessity/causal proof. Zeroing is out of distribution; shuffle preserves positions. No perturbed-label AUROC, R1, FRR or RR computed. Raw top span before official temporal postprocessing; original official gate is a scalar per row and does not change exact-precision slot ranking."
}
```

## diagnostics/throw/baseline/INPUT_SENSITIVITY_MANIFEST.json

```json
{
  "state": "frozen_before_inference",
  "seed": 3407,
  "training_updates": 0,
  "checkpoint_sha256": "bf7e1ac3fc68e9718797e9dcae12960b56f04e48d2f138cac381f13145b46d26",
  "checkpoint_epoch_zero_based": 99,
  "source_sha256": "d980356f74f3bed35178abf6120b6ea99e8ac23aaef7748dd2e8a4f42f38dec8",
  "view_sha256": "396ff0195a7577b03404e1d25a2aa9ceedd36582e4e07860a407a670b65be61b",
  "qids": [
    "train88",
    "train89",
    "train90",
    "train124",
    "train131",
    "train211",
    "train212",
    "train218",
    "train271",
    "train278",
    "train279",
    "train282",
    "train324",
    "train325",
    "train357",
    "train361",
    "train374",
    "train451",
    "train452",
    "train456",
    "train461",
    "train502",
    "train640",
    "train649",
    "train651",
    "train652",
    "train677",
    "train678",
    "train749",
    "train750",
    "train825",
    "train848",
    "train849",
    "train881",
    "train883",
    "train950",
    "train951",
    "train1006",
    "train1007",
    "train1081",
    "train1107",
    "train1108",
    "train1111",
    "train1184",
    "train1270",
    "train1323",
    "train1329",
    "train1354",
    "train1362",
    "train1465",
    "train1536",
    "train1537",
    "train1571",
    "train1659",
    "train1674",
    "train1690",
    "train1723",
    "train1772",
    "train1773",
    "train1840",
    "train2009",
    "train2033",
    "train2035",
    "train2036",
    "train2069",
    "train2070",
    "train2087",
    "train2088",
    "train2209",
    "train2222",
    "train2223",
    "train2313",
    "train2316",
    "train2317",
    "train2383",
    "train2384",
    "train2488",
    "train2507",
    "train2508",
    "train2513",
    "train2574",
    "train2575",
    "train2576",
    "train2587",
    "train2589",
    "train2590",
    "train2608",
    "train2615",
    "train2616",
    "train2626",
    "train2644",
    "train2683",
    "train2684",
    "train2707",
    "train2708",
    "train2808",
    "train2810",
    "train2914",
    "train3028",
    "train3079",
    "train3103",
    "train3104",
    "train3105",
    "train3153",
    "train3161",
    "train3191",
    "train3206",
    "train3236",
    "train3237",
    "train3283",
    "train3287",
    "train3319",
    "train3336",
    "train3410",
    "train3411",
    "train3441",
    "train3472",
    "train3498",
    "train3500",
    "train3512",
    "train3513",
    "train3517",
    "train3518",
    "train3624",
    "train3625",
    "train3650",
    "train3681",
    "train3682",
    "train3701",
    "train3802",
    "train3803",
    "train3862",
    "train3891",
    "train3892",
    "train3916",
    "train3955",
    "train3956",
    "train4032",
    "train4093",
    "train4094",
    "train4163",
    "train4179",
    "train4224",
    "train4310",
    "train4326",
    "train4327",
    "train4337",
    "train4338",
    "train4339",
    "train4367",
    "train4368",
    "train4508",
    "train4551",
    "train4628",
    "train4636",
    "train4677",
    "train4728",
    "train4744",
    "train4745",
    "train4761",
    "train4804",
    "train4840",
    "train4841",
    "train4878",
    "train4879",
    "train4913",
    "train4914",
    "train4981",
    "train4987",
    "train4988",
    "train4991",
    "train5011",
    "train5018",
    "train5145",
    "train5151",
    "train5161",
    "train5201",
    "train5202",
    "train5225",
    "train5226",
    "train5227",
    "train5314",
    "train5386",
    "train5412",
    "train5435",
    "train5471",
    "train5503",
    "train5507",
    "train5609",
    "train5610",
    "train5630",
    "train5631",
    "train5673",
    "train5713",
    "train5716",
    "train5747",
    "train5748",
    "train5794",
    "train5801",
    "train5805",
    "train5823",
    "train5846",
    "train5848",
    "train5994",
    "train6021",
    "train6076",
    "train6077",
    "train6081",
    "train6134",
    "train6135",
    "train6177",
    "train6178",
    "train6195",
    "train6208",
    "train6242",
    "train6245",
    "train6274",
    "train6275",
    "train6321",
    "train6386",
    "train6387",
    "train6388",
    "train6401",
    "train6402",
    "train6480",
    "train6502",
    "train6504",
    "train6517",
    "train6518",
    "train6586",
    "train6595",
    "train6596",
    "train6598",
    "train6630",
    "train6631",
    "train6632",
    "train6633",
    "train6642",
    "train6661",
    "train6662",
    "train6670",
    "train6676",
    "train6688",
    "train6690",
    "train6716",
    "train6717",
    "train6730",
    "train6738",
    "train6790",
    "train6811",
    "train6864",
    "train6911",
    "train6928",
    "train6980",
    "train6981",
    "train7032",
    "train7033",
    "train7035",
    "train7106",
    "train7111",
    "train7112",
    "train7138",
    "train7146",
    "train7218",
    "train7219",
    "train7222",
    "train7282",
    "train7345",
    "train7373",
    "train7385",
    "train7419",
    "train7420",
    "train7428",
    "train7429",
    "train7430",
    "train7448",
    "train7455",
    "train7483",
    "train7484",
    "train7485",
    "train7555",
    "train7556",
    "train7574",
    "train7580",
    "train7582",
    "train7583",
    "train7605",
    "train7606",
    "train7646",
    "train7662",
    "train7663",
    "train7664",
    "train7710",
    "train7712",
    "train7777",
    "train7794",
    "train7799",
    "train7814",
    "train7875",
    "train7894",
    "train7902",
    "train7910",
    "train8000",
    "train8010",
    "train8011",
    "train8014",
    "train8015",
    "train8144",
    "train8158",
    "train8185",
    "train8187",
    "train8196",
    "train8213",
    "train8264",
    "train8268",
    "train8269",
    "train8353",
    "train8354",
    "train8355",
    "train8411",
    "train8464",
    "train8514",
    "train8577",
    "train8578",
    "train8603",
    "train8604",
    "train8648",
    "train8724",
    "train8725",
    "train8758",
    "train8814",
    "train8840",
    "train8842",
    "train8860",
    "train8865",
    "train8939",
    "train8969",
    "train8970",
    "train9013",
    "train9014",
    "train9016",
    "train9197",
    "train9247",
    "train9272",
    "train9315",
    "train9316",
    "train9347",
    "train9348",
    "train9361",
    "train9387",
    "train9415",
    "train9420",
    "train9422",
    "train9476",
    "train9478",
    "train9479",
    "train9482",
    "train9505",
    "train9507",
    "train9508",
    "train9531",
    "train9534",
    "train9547",
    "train9548",
    "train9551",
    "train9576",
    "train9585",
    "train9586",
    "train9588",
    "train9593",
    "train9620",
    "train9669",
    "train9762",
    "train9763",
    "train9789",
    "train9791",
    "train9809",
    "train9882",
    "train9883",
    "train9958",
    "train9959",
    "train10007",
    "train10027",
    "train10052",
    "train10054",
    "train10055",
    "train10056",
    "train10133",
    "train10194",
    "train10206",
    "train10207",
    "train10246",
    "train10260",
    "train10268",
    "train10357",
    "train10358",
    "train10368",
    "train10413",
    "train10455",
    "train10457",
    "train10460",
    "train10461",
    "train10593",
    "train10613",
    "train10660",
    "train10661",
    "train10780",
    "train10830",
    "train10844",
    "train10863",
    "train10881",
    "train10935",
    "train10953",
    "train10954",
    "train11015",
    "train11020",
    "train11141",
    "train11142",
    "train11195",
    "train11342",
    "train11432",
    "train11438",
    "train11454",
    "train11458",
    "train11464",
    "train11465",
    "train11473",
    "train11493",
    "train11504",
    "train11505",
    "train11513",
    "train11514",
    "train11515",
    "train11522",
    "train11523",
    "train11531",
    "train11532",
    "train11559",
    "train11561",
    "train11585",
    "train11621",
    "train11622",
    "train11644",
    "train11645",
    "train11653",
    "train11684",
    "train11735",
    "train11742",
    "train11759",
    "train11762",
    "train11770",
    "train12014",
    "train12076",
    "train12079",
    "train12194",
    "train12196",
    "train12236",
    "train12262",
    "train12322",
    "train12355",
    "train12356",
    "train12367",
    "train12405",
    "train12406",
    "neg_0356f3aa545fecc9",
    "neg_05e3781e6a69476e",
    "neg_0aa097b2b049bb42",
    "neg_0ac079a7c120857d",
    "neg_0ce4d23bf3a3e434",
    "neg_0de51182aa554280",
    "neg_0e340ee7d685e84b",
    "neg_0fff5c470a66e632",
    "neg_1372aab42e4b6266",
    "neg_179ec5fdae1f9378",
    "neg_1ccab5e73f4807f4",
    "neg_1d70ded749aff498",
    "neg_1d769cf7c1b70366",
    "neg_1eeb6def7111cf70",
    "neg_27df813d3f94b7c3",
    "neg_2903529dc003a31f",
    "neg_2c1e2bafcc1c2ba3",
    "neg_2e0d0161d366342d",
    "neg_3226064207f4f425",
    "neg_37695fff75d90f51",
    "neg_3f7b950c37d9a581",
    "neg_4031558675d4d139",
    "neg_4111a15dd5106a66",
    "neg_411d970212c60a96",
    "neg_42536139424de1b2",
    "neg_42c682ee833e83f1",
    "neg_435816eda25f1fd8",
    "neg_437acf83063023f1",
    "neg_448b93dac696bfce",
    "neg_469d70306c4e8cb6",
    "neg_46eb057bf3a55e97",
    "neg_48f05f2ac84c8997",
    "neg_4ae29350b63a613f",
    "neg_512c88b24866769e",
    "neg_5226bb80dc5674c9",
    "neg_5536ca1f334e1d71",
    "neg_55d46a75a2d09114",
    "neg_58f0b27bcfe789b6",
    "neg_5994fb6b06b62c51",
    "neg_5bbc13251a588cde",
    "neg_5c97e4119d6809db",
    "neg_6287083a25151280",
    "neg_632bbab755d6ff84",
    "neg_643c8e6ea67d15ad",
    "neg_664463d35b05230a",
    "neg_66da85a7c759e30d",
    "neg_68b517b1666eb195",
    "neg_69230b4c00eacca8",
    "neg_6b90a483930e5f31",
    "neg_6c6ce774a4aada77",
    "neg_6dfad46dafbb00c1",
    "neg_6edb4b00ee70e4cb",
    "neg_70950f8705e9536e",
    "neg_7353b57ab1f9c95a",
    "neg_7431b6b3327c4780",
    "neg_7ace005038981993",
    "neg_7bc9e9171d299a6d",
    "neg_7c2b47d9a11e5792",
    "neg_7fa99e6f253121de",
    "neg_80c6e675d7e0a8b9",
    "neg_82c7b2807162032d",
    "neg_875a21f921d70187",
    "neg_90273c67420ee208",
    "neg_90b47dd04770f19d",
    "neg_91f8407c5b699dfa",
    "neg_965f68151037127f",
    "neg_9751265dd820b49d",
    "neg_a0ca537abbe4bde6",
    "neg_a35291186747e3f1",
    "neg_a4bf9fd31e4aa2ba",
    "neg_a9c02641b1594466",
    "neg_aa528afe06333e9f",
    "neg_af2ff4fe426214d7",
    "neg_af88201bd348e15c",
    "neg_b185a39f6d977e10",
    "neg_b2921dad672deac2",
    "neg_b517bddadc52e173",
    "neg_b545b4e592aeba0c",
    "neg_b848bcb0623eae3a",
    "neg_bbeb1e2061be898a",
    "neg_bce609411f7d8dfd",
    "neg_bd4aa8f36e05348f",
    "neg_bec95039b2572b8f",
    "neg_c0cf96cf6ce024b2",
    "neg_c6756135cc6ee5cc",
    "neg_ce857dc57a6200c7",
    "neg_d0b2246178816f8e",
    "neg_d3cfcea3d420682f",
    "neg_d5c6a9c0b6fcfb45",
    "neg_d69f031f8290f17e",
    "neg_d817cd7c0d438450",
    "neg_d846d2630a4e4e58",
    "neg_df0cf681fd091297",
    "neg_e20f9f830c32fde6",
    "neg_e56f3c6f7c809732",
    "neg_e632e1abead00f11",
    "neg_ee6c8350b1dac3dc",
    "neg_eeb5d6b75fc092bd",
    "neg_f0889a6f394a2f0c",
    "neg_f1caffb03205a176",
    "neg_f3d89fd21be00c36",
    "neg_f70d8013dda0361c",
    "neg_f8fa52252d4cea83",
    "neg_fc195ed1d23b1b9f",
    "neg_feae6426d2be85b7",
    "neg_ffbdd422c37c6880"
  ],
  "branches": [
    [
      "vid_clip",
      0,
      512
    ],
    [
      "vid_slowfast",
      512,
      2816
    ]
  ],
  "modes": [
    "identity",
    "zero_visual",
    "shuffle_time",
    "zero_clip",
    "zero_slowfast"
  ],
  "perturbation": "zero normalized visual channels; shuffle valid visual rows only; masks, padded rows, text and TEF preserved",
  "permutation": "same permutation for each video and all queries; CPU generator seeded by SHA256(seed|vid|length)",
  "selection": "all existing pseudo rows, original order; no outcome-based selection",
  "accuracy_under_perturbation": "not computed"
}
```

## diagnostics/throw/baseline/LATEST_FAILURE_DECOMPOSITION.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "checkpoint_epoch_zero_based": 99,
  "checkpoint_sha256": "c2f475c2229f17927e869cea48379552973ef5e1510831655302d7adf50396c9",
  "source_sha256": "a4a8dc5c9317945a71a184eab08e9a7962137004e736c19e12dcc34ba62741d0",
  "same_model_tensors_as_best": true,
  "predictions_reused_from_best": true,
  "results": {
    "pseudo": {
      "AUROC": 0.5731030416395576,
      "raw_R1_05": 0.2672413793103448,
      "gated_R1_05": 0.26939655172413796,
      "FRR": 0.08836206896551724,
      "RR": 0.13207547169811318,
      "counts": {
        "positive": 464,
        "raw_incorrect": 340,
        "positive_rejected": 41,
        "official_gated_correct": 125,
        "raw_correct_gated_wrong": 6,
        "raw_wrong_gated_correct": 7,
        "official_empty": 0,
        "raw_correct": 124,
        "raw_correct_accepted": 109,
        "raw_correct_rejected": 15,
        "negative": 106,
        "negative_accepted": 92
      },
      "raw_correct_rejected_over_raw_correct": 0.12096774193548387,
      "raw_errors_over_hard_failures": 0.9577464788732394,
      "threshold": 0.9973,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "a5c4d5c0d3a5ee7bb4cb517a0af0c829868ddef9dd249964b7feb8230685501f"
    },
    "seen": {
      "AUROC": 0.7996112408291949,
      "raw_R1_05": 0.4400564174894217,
      "gated_R1_05": 0.4414668547249647,
      "FRR": 0.2073342736248237,
      "RR": 0.703781512605042,
      "counts": {
        "positive": 709,
        "raw_correct": 312,
        "raw_correct_accepted": 255,
        "positive_rejected": 147,
        "official_gated_correct": 313,
        "raw_correct_gated_wrong": 8,
        "raw_wrong_gated_correct": 9,
        "official_empty": 0,
        "raw_incorrect": 397,
        "raw_correct_rejected": 57,
        "negative": 476,
        "negative_accepted": 141
      },
      "raw_correct_rejected_over_raw_correct": 0.18269230769230768,
      "raw_errors_over_hard_failures": 0.8744493392070485,
      "threshold": 0.9973,
      "threshold_source": "latest checkpoint seen validation only; Youden J, diagnostic only",
      "source_prediction_sha256": "606dd34aa6a38cacb278b767183719efa483a0fba24aa782806cb34798461d1f"
    }
  },
  "limitations": "Latest comparison is descriptive, not an alternative pseudo-based checkpoint selection or full training trajectory; unchanged official gate, diagnostic threshold fitted on latest seen only."
}
```

## diagnostics/throw/baseline/SCORE_COMPARABILITY.json

```json
{
  "state": "completed",
  "training_updates": 0,
  "splits": {
    "pseudo": {
      "same_video_pairacc": 0.8153846153846154,
      "same_video_pairs": 65,
      "cross_video_pairacc": 0.572782426352328,
      "exact_query_cross_video_pairacc": 0.3783783783783784,
      "exact_query_cross_video_pairs": 37,
      "exact_query_groups": 10,
      "exact_query_feature_consistent_groups": 0,
      "mixed_label_videos": 32
    },
    "seen": {
      "same_video_pairacc": 0.7333032490974729,
      "same_video_pairs": 1108,
      "cross_video_pairacc": 0.7998296549099817,
      "exact_query_cross_video_pairacc": 0.6290760869565217,
      "exact_query_cross_video_pairs": 368,
      "exact_query_groups": 52,
      "exact_query_feature_consistent_groups": 0,
      "mixed_label_videos": 199
    }
  },
  "limitations": "Within/cross-video rank decomposition uses original queries and labels; differing compositions do not prove video bias. Identical string ranks before feature control are not a text tie control."
}
```

## diagnostics/throw/baseline/VISUAL_INCREMENT.json

```json
{
  "pseudo": {
    "same_video_pairacc": 0.8153846153846154,
    "same_video_pairs": 65,
    "cross_video_pairacc": 0.572782426352328,
    "exact_query_cross_video_pairacc": 0.3783783783783784,
    "exact_query_cross_video_pairs": 37,
    "exact_query_groups": 10,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 32
  },
  "seen": {
    "same_video_pairacc": 0.7333032490974729,
    "same_video_pairs": 1108,
    "cross_video_pairacc": 0.7998296549099817,
    "exact_query_cross_video_pairacc": 0.6290760869565217,
    "exact_query_cross_video_pairs": 368,
    "exact_query_groups": 52,
    "exact_query_feature_consistent_groups": 0,
    "mixed_label_videos": 199
  }
}
```
