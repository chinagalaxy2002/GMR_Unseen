# readout_analysis：全部指标与覆盖

## RESULTS.json

完整机器可读结构如下。NA、有效次数、分母和辅助指标保留，不用缺值补.5。

```json
{
  "state": "completed",
  "training_updates": 0,
  "new_training_epochs": 0,
  "seed": 3407,
  "resamples": 1000,
  "intervals": "Exploratory 95% cluster intervals, no multiplicity correction and no confirmatory candidate claim; original video union weights shared across all families/splits",
  "source_sha256": "dce072c54dbfb450f04c7f507f676aabb54427e4b6cb114b514708b80d2c5e0c",
  "families": {
    "throw": {
      "seen": {
        "coverage": {
          "rows": 1185,
          "positive": 709,
          "negative": 476,
          "raw_correct_positive": 312,
          "raw_incorrect_positive": 397,
          "mixed_localization_quality_positive_videos": 85,
          "within_video_quality_pairs": 193
        },
        "metrics": {
          "original_AUROC": {
            "point": 0.7996112408291949,
            "ci95": [
              0.763360866729321,
              0.8331771491001978
            ],
            "valid_resamples": 1000
          },
          "native_logit_AUROC": {
            "point": 0.8047966718422207,
            "ci95": [
              0.7699837088390875,
              0.8362557208155459
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_AUROC": {
            "point": 0.8048085242559647,
            "ci95": [
              0.7699678881259333,
              0.8362435703984078
            ],
            "valid_resamples": 1000
          },
          "recomputed_serialized_AUROC": {
            "point": 0.7996112408291949,
            "ci95": [
              0.763360866729321,
              0.8331771491001978
            ],
            "valid_resamples": 1000
          },
          "logit_minus_original_AUROC": {
            "point": 0.005185431013025821,
            "ci95": [
              -0.003143824526378225,
              0.012632611484434501
            ],
            "valid_resamples": 1000
          },
          "logit_minus_native_sigmoid_AUROC": {
            "point": -1.1852413744017909e-05,
            "ci95": [
              -8.463359424484284e-05,
              4.771013231655851e-05
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_minus_serialized_AUROC": {
            "point": 0.005197283426769839,
            "ci95": [
              -0.003146361996504368,
              0.012652280967734943
            ],
            "valid_resamples": 1000
          },
          "original_pos_neg_tie_rate": {
            "point": 0.10465088715316874,
            "ci95": [
              0.08370344293402017,
              0.127520392788866
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_pos_neg_tie_rate": {
            "point": 0.0003140889642175629,
            "ci95": [
              0.00019155814478704724,
              0.0004883244387801772
            ],
            "valid_resamples": 1000
          },
          "native_logit_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "positive_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "negative_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.4400564174894217,
            "ci95": [
              0.39657936179946496,
              0.4840932402070919
            ],
            "valid_resamples": 1000
          },
          "oracle_any_candidate_R_05": {
            "point": 0.7983074753173484,
            "ci95": [
              0.7651055194805194,
              0.8319791263388824
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_positives": {
            "point": 0.35825105782792666,
            "ci95": [
              0.3183775304580487,
              0.40159724625767934
            ],
            "valid_resamples": 1000
          },
          "candidate_miss_fraction_of_positives": {
            "point": 0.2016925246826516,
            "ci95": [
              0.16802087366111756,
              0.2348944805194805
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_raw_errors": {
            "point": 0.6397984886649875,
            "ci95": [
              0.587920289584655,
              0.6958800886080546
            ],
            "valid_resamples": 1000
          },
          "native_exist_quality_AUC_Splus": {
            "point": 0.5003875217981012,
            "ci95": [
              0.4485561559338077,
              0.5540449607181064
            ],
            "valid_resamples": 1000
          },
          "foreground_quality_AUC_Splus": {
            "point": 0.6510446941807143,
            "ci95": [
              0.6010462860289691,
              0.7039255035420484
            ],
            "valid_resamples": 1000
          },
          "native_logit_mean_correct_minus_incorrect_Splus": {
            "point": 1.0234643815346711,
            "ci95": [
              -0.15003442202162895,
              2.2550462408097878
            ],
            "valid_resamples": 1000
          },
          "native_logit_top_iou_spearman_Splus": {
            "point": 0.00032727024348533346,
            "ci95": [
              -0.08556154236705658,
              0.08756879127775605
            ],
            "valid_resamples": 1000
          },
          "native_logit_foreground_spearman_Splus": {
            "point": 0.34762685604901905,
            "ci95": [
              0.25069611352395443,
              0.44025534746010847
            ],
            "valid_resamples": 1000
          },
          "within_video_exist_quality_PairAcc_Splus": {
            "point": 0.5077720207253886,
            "ci95": [
              0.4057677808494597,
              0.6060942760942761
            ],
            "valid_resamples": 1000
          },
          "original_AUC_correct_positive_vs_negative": {
            "point": 0.8145873734109028,
            "ci95": [
              0.7766863079984584,
              0.848369220614045
            ],
            "valid_resamples": 1000
          },
          "original_AUC_incorrect_positive_vs_negative": {
            "point": 0.7878415849967191,
            "ci95": [
              0.7431967186366933,
              0.824879640341538
            ],
            "valid_resamples": 1000
          },
          "original_AUC_strata_reconstruction": {
            "point": 0.7996112408291949,
            "ci95": [
              0.763360866729321,
              0.8331771491001979
            ],
            "valid_resamples": 1000
          }
        }
      },
      "pseudo": {
        "coverage": {
          "rows": 570,
          "positive": 464,
          "negative": 106,
          "raw_correct_positive": 124,
          "raw_incorrect_positive": 340,
          "mixed_localization_quality_positive_videos": 27,
          "within_video_quality_pairs": 32
        },
        "metrics": {
          "original_AUROC": {
            "point": 0.5731030416395576,
            "ci95": [
              0.5081094947657225,
              0.6324251750142961
            ],
            "valid_resamples": 1000
          },
          "native_logit_AUROC": {
            "point": 0.5662410540013012,
            "ci95": [
              0.4891644036516124,
              0.6353514378724463
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_AUROC": {
            "point": 0.5662003903708523,
            "ci95": [
              0.48907054844599124,
              0.6355518153207228
            ],
            "valid_resamples": 1000
          },
          "recomputed_serialized_AUROC": {
            "point": 0.5731030416395576,
            "ci95": [
              0.5081094947657225,
              0.6324251750142961
            ],
            "valid_resamples": 1000
          },
          "logit_minus_original_AUROC": {
            "point": -0.006861987638256406,
            "ci95": [
              -0.04089974812404425,
              0.03171639195974062
            ],
            "valid_resamples": 1000
          },
          "logit_minus_native_sigmoid_AUROC": {
            "point": 4.0663630448856125e-05,
            "ci95": [
              -0.000329607647095545,
              0.0004263062074603862
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_minus_serialized_AUROC": {
            "point": -0.006902651268705262,
            "ci95": [
              -0.04094788937736865,
              0.03185095703520215
            ],
            "valid_resamples": 1000
          },
          "original_pos_neg_tie_rate": {
            "point": 0.4435792127521145,
            "ci95": [
              0.36373181211543804,
              0.5251110714596706
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_pos_neg_tie_rate": {
            "point": 0.0021551724137931034,
            "ci95": [
              0.001313331622222197,
              0.003176126802495663
            ],
            "valid_resamples": 1000
          },
          "native_logit_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "positive_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "negative_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.2672413793103448,
            "ci95": [
              0.2208175505050505,
              0.3146934460887949
            ],
            "valid_resamples": 1000
          },
          "oracle_any_candidate_R_05": {
            "point": 0.6530172413793104,
            "ci95": [
              0.5967975357489013,
              0.7064963978387031
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_positives": {
            "point": 0.3857758620689655,
            "ci95": [
              0.33189185697057866,
              0.43488574339567715
            ],
            "valid_resamples": 1000
          },
          "candidate_miss_fraction_of_positives": {
            "point": 0.34698275862068967,
            "ci95": [
              0.2935036021612968,
              0.4032024642510987
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_raw_errors": {
            "point": 0.5264705882352941,
            "ci95": [
              0.4589993169398907,
              0.5905589161213759
            ],
            "valid_resamples": 1000
          },
          "native_exist_quality_AUC_Splus": {
            "point": 0.450853889943074,
            "ci95": [
              0.3769360344898823,
              0.5247651257529307
            ],
            "valid_resamples": 1000
          },
          "foreground_quality_AUC_Splus": {
            "point": 0.573873339658444,
            "ci95": [
              0.5057771728302493,
              0.647781637592559
            ],
            "valid_resamples": 1000
          },
          "native_logit_mean_correct_minus_incorrect_Splus": {
            "point": -1.0131649138154977,
            "ci95": [
              -1.9734471955807784,
              -0.06726807673964451
            ],
            "valid_resamples": 1000
          },
          "native_logit_top_iou_spearman_Splus": {
            "point": -0.03966761904506215,
            "ci95": [
              -0.1498232820921042,
              0.0655915617668419
            ],
            "valid_resamples": 1000
          },
          "native_logit_foreground_spearman_Splus": {
            "point": -0.008822492400300266,
            "ci95": [
              -0.12849445614408142,
              0.09911161333335303
            ],
            "valid_resamples": 1000
          },
          "within_video_exist_quality_PairAcc_Splus": {
            "point": 0.65625,
            "ci95": [
              0.48272669220945086,
              0.8260869565217391
            ],
            "valid_resamples": 1000
          },
          "original_AUC_correct_positive_vs_negative": {
            "point": 0.5329047474132684,
            "ci95": [
              0.45111542161433166,
              0.6086747583461126
            ],
            "valid_resamples": 1000
          },
          "original_AUC_incorrect_positive_vs_negative": {
            "point": 0.5877635960044395,
            "ci95": [
              0.5231725116887861,
              0.6510075010931704
            ],
            "valid_resamples": 1000
          },
          "original_AUC_strata_reconstruction": {
            "point": 0.5731030416395576,
            "ci95": [
              0.5081094947657225,
              0.6324251750142962
            ],
            "valid_resamples": 1000
          }
        }
      }
    },
    "open_close": {
      "seen": {
        "coverage": {
          "rows": 722,
          "positive": 516,
          "negative": 206,
          "raw_correct_positive": 170,
          "raw_incorrect_positive": 346,
          "mixed_localization_quality_positive_videos": 49,
          "within_video_quality_pairs": 111
        },
        "metrics": {
          "original_AUROC": {
            "point": 0.8560905396251975,
            "ci95": [
              0.8167288412461594,
              0.8867241452317539
            ],
            "valid_resamples": 1000
          },
          "native_logit_AUROC": {
            "point": 0.8574828780010537,
            "ci95": [
              0.8179257694332778,
              0.888509547048335
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_AUROC": {
            "point": 0.8574687664634605,
            "ci95": [
              0.8178979016810133,
              0.8884949474649549
            ],
            "valid_resamples": 1000
          },
          "recomputed_serialized_AUROC": {
            "point": 0.8560905396251975,
            "ci95": [
              0.8167288412461594,
              0.8867241452317539
            ],
            "valid_resamples": 1000
          },
          "logit_minus_original_AUROC": {
            "point": 0.0013923383758561725,
            "ci95": [
              -0.0021173252033059946,
              0.005148511405579292
            ],
            "valid_resamples": 1000
          },
          "logit_minus_native_sigmoid_AUROC": {
            "point": 1.4111537593231027e-05,
            "ci95": [
              -2.1114843519537407e-05,
              6.184843364305524e-05
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_minus_serialized_AUROC": {
            "point": 0.0013782268382629415,
            "ci95": [
              -0.0021263926077080384,
              0.005128445688742088
            ],
            "valid_resamples": 1000
          },
          "original_pos_neg_tie_rate": {
            "point": 0.03484609016331753,
            "ci95": [
              0.023128398113090663,
              0.05186874111373022
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_pos_neg_tie_rate": {
            "point": 4.703845864378716e-05,
            "ci95": [
              0.0,
              0.00014121232801736876
            ],
            "valid_resamples": 1000
          },
          "native_logit_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "positive_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "negative_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.32945736434108525,
            "ci95": [
              0.2854435452110901,
              0.3767356584093872
            ],
            "valid_resamples": 1000
          },
          "oracle_any_candidate_R_05": {
            "point": 0.7965116279069767,
            "ci95": [
              0.7555546123372948,
              0.8333413001912047
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_positives": {
            "point": 0.46705426356589147,
            "ci95": [
              0.4177611343557873,
              0.5169745209035481
            ],
            "valid_resamples": 1000
          },
          "candidate_miss_fraction_of_positives": {
            "point": 0.20348837209302326,
            "ci95": [
              0.1666586998087954,
              0.24444538766270515
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_raw_errors": {
            "point": 0.6965317919075145,
            "ci95": [
              0.6407185628742516,
              0.7486350933427831
            ],
            "valid_resamples": 1000
          },
          "native_exist_quality_AUC_Splus": {
            "point": 0.4382012920775247,
            "ci95": [
              0.38096074384985046,
              0.49833561555996697
            ],
            "valid_resamples": 1000
          },
          "foreground_quality_AUC_Splus": {
            "point": 0.6295647738864332,
            "ci95": [
              0.5672327064939173,
              0.6870012211683701
            ],
            "valid_resamples": 1000
          },
          "native_logit_mean_correct_minus_incorrect_Splus": {
            "point": -0.43612957223261883,
            "ci95": [
              -1.1424759411787577,
              0.24593588498711363
            ],
            "valid_resamples": 1000
          },
          "native_logit_top_iou_spearman_Splus": {
            "point": -0.15245172041126562,
            "ci95": [
              -0.2442345274333323,
              -0.046748857550300955
            ],
            "valid_resamples": 1000
          },
          "native_logit_foreground_spearman_Splus": {
            "point": 0.01586362666767962,
            "ci95": [
              -0.09606267407041129,
              0.11825496587946123
            ],
            "valid_resamples": 1000
          },
          "within_video_exist_quality_PairAcc_Splus": {
            "point": 0.3963963963963964,
            "ci95": [
              0.26368131868131867,
              0.5300258620689655
            ],
            "valid_resamples": 1000
          },
          "original_AUC_correct_positive_vs_negative": {
            "point": 0.8450742432895488,
            "ci95": [
              0.8001347163923409,
              0.8846369056161848
            ],
            "valid_resamples": 1000
          },
          "original_AUC_incorrect_positive_vs_negative": {
            "point": 0.8615031707727706,
            "ci95": [
              0.8211790751494307,
              0.8924475400103966
            ],
            "valid_resamples": 1000
          },
          "original_AUC_strata_reconstruction": {
            "point": 0.8560905396251977,
            "ci95": [
              0.8167288412461595,
              0.886724145231754
            ],
            "valid_resamples": 1000
          }
        }
      },
      "pseudo": {
        "coverage": {
          "rows": 2827,
          "positive": 1888,
          "negative": 939,
          "raw_correct_positive": 497,
          "raw_incorrect_positive": 1391,
          "mixed_localization_quality_positive_videos": 119,
          "within_video_quality_pairs": 178
        },
        "metrics": {
          "original_AUROC": {
            "point": 0.5346313130629411,
            "ci95": [
              0.5157634206234314,
              0.5547455215439048
            ],
            "valid_resamples": 1000
          },
          "native_logit_AUROC": {
            "point": 0.5370971417483439,
            "ci95": [
              0.5174365128531088,
              0.5565426499619546
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_AUROC": {
            "point": 0.5370805017057454,
            "ci95": [
              0.5174170263249139,
              0.5565076381498982
            ],
            "valid_resamples": 1000
          },
          "recomputed_serialized_AUROC": {
            "point": 0.5346313130629411,
            "ci95": [
              0.5157634206234314,
              0.5547455215439048
            ],
            "valid_resamples": 1000
          },
          "logit_minus_original_AUROC": {
            "point": 0.0024658286854027933,
            "ci95": [
              -0.0018609950640226247,
              0.006980911741443638
            ],
            "valid_resamples": 1000
          },
          "logit_minus_native_sigmoid_AUROC": {
            "point": 1.66400425984925e-05,
            "ci95": [
              -7.3219067943164354e-06,
              4.314618650764212e-05
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_minus_serialized_AUROC": {
            "point": 0.002449188642804301,
            "ci95": [
              -0.0018846663370014089,
              0.006965751456240987
            ],
            "valid_resamples": 1000
          },
          "original_pos_neg_tie_rate": {
            "point": 0.1385619167524052,
            "ci95": [
              0.1252811556197694,
              0.152687580752983
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_pos_neg_tie_rate": {
            "point": 0.00026229219689175286,
            "ci95": [
              0.00021565867041765504,
              0.0003290351433071021
            ],
            "valid_resamples": 1000
          },
          "native_logit_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "positive_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "negative_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.2632415254237288,
            "ci95": [
              0.23965743417154076,
              0.28768997837058397
            ],
            "valid_resamples": 1000
          },
          "oracle_any_candidate_R_05": {
            "point": 0.645656779661017,
            "ci95": [
              0.6199686595243074,
              0.6720361460722413
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_positives": {
            "point": 0.3824152542372881,
            "ci95": [
              0.35691798038728895,
              0.4098847398672669
            ],
            "valid_resamples": 1000
          },
          "candidate_miss_fraction_of_positives": {
            "point": 0.3543432203389831,
            "ci95": [
              0.3279638539277588,
              0.3800313404756926
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_raw_errors": {
            "point": 0.5190510424155284,
            "ci95": [
              0.4890862937151444,
              0.551885711127558
            ],
            "valid_resamples": 1000
          },
          "native_exist_quality_AUC_Splus": {
            "point": 0.45279730142175845,
            "ci95": [
              0.42032320763131237,
              0.4847994888691923
            ],
            "valid_resamples": 1000
          },
          "foreground_quality_AUC_Splus": {
            "point": 0.655423554989173,
            "ci95": [
              0.6207630707733156,
              0.6872088358975854
            ],
            "valid_resamples": 1000
          },
          "native_logit_mean_correct_minus_incorrect_Splus": {
            "point": -0.14573820447894903,
            "ci95": [
              -0.4462275251480837,
              0.14613344831640698
            ],
            "valid_resamples": 1000
          },
          "native_logit_top_iou_spearman_Splus": {
            "point": -0.08445513337603422,
            "ci95": [
              -0.13427121950728782,
              -0.03137679044257739
            ],
            "valid_resamples": 1000
          },
          "native_logit_foreground_spearman_Splus": {
            "point": -0.11252656343778238,
            "ci95": [
              -0.17287392523477935,
              -0.06478735065020826
            ],
            "valid_resamples": 1000
          },
          "within_video_exist_quality_PairAcc_Splus": {
            "point": 0.398876404494382,
            "ci95": [
              0.31817599067599067,
              0.49098011363636357
            ],
            "valid_resamples": 1000
          },
          "original_AUC_correct_positive_vs_negative": {
            "point": 0.5024374146904859,
            "ci95": [
              0.4733658734858564,
              0.5316125775697077
            ],
            "valid_resamples": 1000
          },
          "original_AUC_incorrect_positive_vs_negative": {
            "point": 0.546134093430382,
            "ci95": [
              0.5243345005971132,
              0.5668458539859575
            ],
            "valid_resamples": 1000
          },
          "original_AUC_strata_reconstruction": {
            "point": 0.5346313130629411,
            "ci95": [
              0.5157634206234314,
              0.5547455215439048
            ],
            "valid_resamples": 1000
          }
        }
      }
    },
    "sit": {
      "seen": {
        "coverage": {
          "rows": 1065,
          "positive": 676,
          "negative": 389,
          "raw_correct_positive": 220,
          "raw_incorrect_positive": 456,
          "mixed_localization_quality_positive_videos": 75,
          "within_video_quality_pairs": 167
        },
        "metrics": {
          "original_AUROC": {
            "point": 0.8432142802817115,
            "ci95": [
              0.8197393462614214,
              0.8641098310756854
            ],
            "valid_resamples": 1000
          },
          "native_logit_AUROC": {
            "point": 0.8431762522626671,
            "ci95": [
              0.8196631571152483,
              0.8641551471434953
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_AUROC": {
            "point": 0.8431762522626671,
            "ci95": [
              0.8196631571152483,
              0.8641551471434953
            ],
            "valid_resamples": 1000
          },
          "recomputed_serialized_AUROC": {
            "point": 0.8432142802817115,
            "ci95": [
              0.8197393462614214,
              0.8641098310756854
            ],
            "valid_resamples": 1000
          },
          "logit_minus_original_AUROC": {
            "point": -3.802801904440045e-05,
            "ci95": [
              -0.0002720508084882306,
              0.00018028294272860179
            ],
            "valid_resamples": 1000
          },
          "logit_minus_native_sigmoid_AUROC": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_minus_serialized_AUROC": {
            "point": -3.802801904440045e-05,
            "ci95": [
              -0.0002720508084882306,
              0.00018028294272860179
            ],
            "valid_resamples": 1000
          },
          "original_pos_neg_tie_rate": {
            "point": 0.0010647845332440943,
            "ci95": [
              0.0005799448308064836,
              0.0017542496254059675
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "native_logit_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "positive_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "negative_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.3254437869822485,
            "ci95": [
              0.2850309994768617,
              0.36321806805588
            ],
            "valid_resamples": 1000
          },
          "oracle_any_candidate_R_05": {
            "point": 0.8550295857988166,
            "ci95": [
              0.8205878965752237,
              0.884082020205828
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_positives": {
            "point": 0.5295857988165681,
            "ci95": [
              0.48827861461955174,
              0.5762221240787174
            ],
            "valid_resamples": 1000
          },
          "candidate_miss_fraction_of_positives": {
            "point": 0.14497041420118342,
            "ci95": [
              0.11591797979417197,
              0.17941210342477626
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_raw_errors": {
            "point": 0.7850877192982456,
            "ci95": [
              0.735476011481684,
              0.8260514688632276
            ],
            "valid_resamples": 1000
          },
          "native_exist_quality_AUC_Splus": {
            "point": 0.49500598086124403,
            "ci95": [
              0.43338691734621965,
              0.5471319029005104
            ],
            "valid_resamples": 1000
          },
          "foreground_quality_AUC_Splus": {
            "point": 0.6326505183413078,
            "ci95": [
              0.5719100467571953,
              0.6829705192698634
            ],
            "valid_resamples": 1000
          },
          "native_logit_mean_correct_minus_incorrect_Splus": {
            "point": 0.05401710747775379,
            "ci95": [
              -0.4536890365667483,
              0.5146738084618154
            ],
            "valid_resamples": 1000
          },
          "native_logit_top_iou_spearman_Splus": {
            "point": -0.008345083007985995,
            "ci95": [
              -0.10096360353516357,
              0.07410902644925312
            ],
            "valid_resamples": 1000
          },
          "native_logit_foreground_spearman_Splus": {
            "point": 0.4308571929240886,
            "ci95": [
              0.33582990986103106,
              0.5245566556914226
            ],
            "valid_resamples": 1000
          },
          "within_video_exist_quality_PairAcc_Splus": {
            "point": 0.5508982035928144,
            "ci95": [
              0.4411697860962567,
              0.6687168380036479
            ],
            "valid_resamples": 1000
          },
          "original_AUC_correct_positive_vs_negative": {
            "point": 0.8528686609020799,
            "ci95": [
              0.8202869816133105,
              0.8793154689809725
            ],
            "valid_resamples": 1000
          },
          "original_AUC_incorrect_positive_vs_negative": {
            "point": 0.8385564650701304,
            "ci95": [
              0.8115343167429974,
              0.8628055537743172
            ],
            "valid_resamples": 1000
          },
          "original_AUC_strata_reconstruction": {
            "point": 0.8432142802817115,
            "ci95": [
              0.8197393462614214,
              0.8641098310756854
            ],
            "valid_resamples": 1000
          }
        }
      },
      "pseudo": {
        "coverage": {
          "rows": 976,
          "positive": 625,
          "negative": 351,
          "raw_correct_positive": 219,
          "raw_incorrect_positive": 406,
          "mixed_localization_quality_positive_videos": 21,
          "within_video_quality_pairs": 27
        },
        "metrics": {
          "original_AUROC": {
            "point": 0.6540216524216524,
            "ci95": [
              0.6119778828817803,
              0.6931954428588613
            ],
            "valid_resamples": 1000
          },
          "native_logit_AUROC": {
            "point": 0.6542769230769231,
            "ci95": [
              0.6122407923957268,
              0.6935051099875862
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_AUROC": {
            "point": 0.6542746438746438,
            "ci95": [
              0.6122407923957268,
              0.6935049897975898
            ],
            "valid_resamples": 1000
          },
          "recomputed_serialized_AUROC": {
            "point": 0.6540216524216524,
            "ci95": [
              0.6119778828817803,
              0.6931954428588613
            ],
            "valid_resamples": 1000
          },
          "logit_minus_original_AUROC": {
            "point": 0.0002552706552706452,
            "ci95": [
              -0.0002619176580869187,
              0.0008598586528407587
            ],
            "valid_resamples": 1000
          },
          "logit_minus_native_sigmoid_AUROC": {
            "point": 2.2792022792428313e-06,
            "ci95": [
              0.0,
              1.4719681508076896e-05
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_minus_serialized_AUROC": {
            "point": 0.00025299145299140235,
            "ci95": [
              -0.00026224326292485225,
              0.000857782254402517
            ],
            "valid_resamples": 1000
          },
          "original_pos_neg_tie_rate": {
            "point": 0.0073207977207977205,
            "ci95": [
              0.006232762050863002,
              0.008660378132051222
            ],
            "valid_resamples": 1000
          },
          "native_sigmoid_pos_neg_tie_rate": {
            "point": 4.558404558404558e-06,
            "ci95": [
              0.0,
              2.9439363016237903e-05
            ],
            "valid_resamples": 1000
          },
          "native_logit_pos_neg_tie_rate": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "positive_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "negative_native_sigmoid_exact_one_fraction": {
            "point": 0.0,
            "ci95": [
              0.0,
              0.0
            ],
            "valid_resamples": 1000
          },
          "raw_R1_05": {
            "point": 0.3504,
            "ci95": [
              0.30213059793537006,
              0.39643566908088057
            ],
            "valid_resamples": 1000
          },
          "oracle_any_candidate_R_05": {
            "point": 0.8192,
            "ci95": [
              0.7829528072782631,
              0.853362724541136
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_positives": {
            "point": 0.4688,
            "ci95": [
              0.42433586286260205,
              0.5171836118023463
            ],
            "valid_resamples": 1000
          },
          "candidate_miss_fraction_of_positives": {
            "point": 0.1808,
            "ci95": [
              0.146637275458864,
              0.21704719272173692
            ],
            "valid_resamples": 1000
          },
          "ranking_error_fraction_of_raw_errors": {
            "point": 0.7216748768472906,
            "ci95": [
              0.670120809423135,
              0.7758341658341659
            ],
            "valid_resamples": 1000
          },
          "native_exist_quality_AUC_Splus": {
            "point": 0.44704995838675576,
            "ci95": [
              0.39317097390601247,
              0.4982213570604061
            ],
            "valid_resamples": 1000
          },
          "foreground_quality_AUC_Splus": {
            "point": 0.6639055716760015,
            "ci95": [
              0.6127528871898615,
              0.7141336438178587
            ],
            "valid_resamples": 1000
          },
          "native_logit_mean_correct_minus_incorrect_Splus": {
            "point": -0.21735652866760002,
            "ci95": [
              -0.4703308946051119,
              0.00016697909676571652
            ],
            "valid_resamples": 1000
          },
          "native_logit_top_iou_spearman_Splus": {
            "point": -0.10658205250228292,
            "ci95": [
              -0.19677724643045877,
              -0.01954053106366507
            ],
            "valid_resamples": 1000
          },
          "native_logit_foreground_spearman_Splus": {
            "point": -0.35100848531647627,
            "ci95": [
              -0.4352100325847258,
              -0.26805925227154626
            ],
            "valid_resamples": 1000
          },
          "within_video_exist_quality_PairAcc_Splus": {
            "point": 0.48148148148148145,
            "ci95": [
              0.2758405172413793,
              0.7059436274509804
            ],
            "valid_resamples": 1000
          },
          "original_AUC_correct_positive_vs_negative": {
            "point": 0.6266440307536197,
            "ci95": [
              0.571068526689794,
              0.6761713783005322
            ],
            "valid_resamples": 1000
          },
          "original_AUC_incorrect_positive_vs_negative": {
            "point": 0.6687893843066257,
            "ci95": [
              0.6254400664232038,
              0.7109021304945978
            ],
            "valid_resamples": 1000
          },
          "original_AUC_strata_reconstruction": {
            "point": 0.6540216524216524,
            "ci95": [
              0.6119778828817802,
              0.6931954428588614
            ],
            "valid_resamples": 1000
          }
        }
      }
    }
  },
  "equal_family_mean": {
    "seen": {
      "original_AUROC": {
        "point": 0.8329720202453679,
        "ci95": [
          0.8090248011460162,
          0.8541712108929852
        ],
        "valid_resamples": 1000
      },
      "native_logit_AUROC": {
        "point": 0.8351519340353137,
        "ci95": [
          0.8107082089101606,
          0.8564290653576827
        ],
        "valid_resamples": 1000
      },
      "logit_minus_original_AUROC": {
        "point": 0.0021799137899458643,
        "ci95": [
          -0.0008547939710260974,
          0.005133754256272841
        ],
        "valid_resamples": 1000
      },
      "logit_minus_native_sigmoid_AUROC": {
        "point": 7.530412830710395e-07,
        "ci95": [
          -2.2318206088209336e-05,
          2.1931075789966e-05
        ],
        "valid_resamples": 1000
      },
      "native_sigmoid_minus_serialized_AUROC": {
        "point": 0.002179160748662793,
        "ci95": [
          -0.0008597467274745852,
          0.005157957276168018
        ],
        "valid_resamples": 1000
      },
      "raw_R1_05": {
        "point": 0.3649858562709185,
        "ci95": [
          0.3323891323132843,
          0.39800072645942
        ],
        "valid_resamples": 1000
      },
      "oracle_any_candidate_R_05": {
        "point": 0.8166162296743806,
        "ci95": [
          0.7883063937635728,
          0.8422921001181936
        ],
        "valid_resamples": 1000
      },
      "ranking_error_fraction_of_positives": {
        "point": 0.4516303734034621,
        "ci95": [
          0.4164354359042843,
          0.48772810239619657
        ],
        "valid_resamples": 1000
      },
      "candidate_miss_fraction_of_positives": {
        "point": 0.18338377032561945,
        "ci95": [
          0.15770789988180636,
          0.21169360623642725
        ],
        "valid_resamples": 1000
      },
      "native_exist_quality_AUC_Splus": {
        "point": 0.47786493157895665,
        "ci95": [
          0.43917384873446336,
          0.5134167088439551
        ],
        "valid_resamples": 1000
      }
    },
    "pseudo": {
      "original_AUROC": {
        "point": 0.5872520023747171,
        "ci95": [
          0.560499708831879,
          0.6119285869896038
        ],
        "valid_resamples": 1000
      },
      "native_logit_AUROC": {
        "point": 0.5858717062755227,
        "ci95": [
          0.5565665224853771,
          0.6124834167768968
        ],
        "valid_resamples": 1000
      },
      "logit_minus_original_AUROC": {
        "point": -0.0013802960991943225,
        "ci95": [
          -0.01339142406947034,
          0.011643556679359325
        ],
        "valid_resamples": 1000
      },
      "logit_minus_native_sigmoid_AUROC": {
        "point": 1.9860958442197152e-05,
        "ci95": [
          -0.0001048660996417002,
          0.00014988450446660147
        ],
        "valid_resamples": 1000
      },
      "native_sigmoid_minus_serialized_AUROC": {
        "point": -0.0014001570576365197,
        "ci95": [
          -0.013418845947806799,
          0.011611039496962246
        ],
        "valid_resamples": 1000
      },
      "raw_R1_05": {
        "point": 0.29362763491135785,
        "ci95": [
          0.2702729276560718,
          0.31587730326254454
        ],
        "valid_resamples": 1000
      },
      "oracle_any_candidate_R_05": {
        "point": 0.7059580070134425,
        "ci95": [
          0.6821845895131416,
          0.7284824848869134
        ],
        "valid_resamples": 1000
      },
      "ranking_error_fraction_of_positives": {
        "point": 0.41233037210208456,
        "ci95": [
          0.3878291062909865,
          0.4373460081496161
        ],
        "valid_resamples": 1000
      },
      "candidate_miss_fraction_of_positives": {
        "point": 0.2940419929865576,
        "ci95": [
          0.2715175151130866,
          0.3178154104868584
        ],
        "valid_resamples": 1000
      },
      "native_exist_quality_AUC_Splus": {
        "point": 0.45023371658386274,
        "ci95": [
          0.41657695481153,
          0.48276153254135845
        ],
        "valid_resamples": 1000
      }
    }
  },
  "limitations": [
    "Oracle uses existing S+ ground-truth windows solely for coverage; it is not achievable retrieval performance or visual support proof.",
    "Loc-correct/incorrect strata are outcome-conditioned and queries differ; cluster intervals do not remove semantic/query confounding or establish causation.",
    "Full native logit and sigmoid precision diagnosis changes no original reported endpoint, gate, threshold or checkpoint; no new labels.",
    "Three saved models, sit truncated at 77 logged epochs; no training seed or equal-completed-budget claim."
  ]
}
```
