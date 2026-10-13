# Training records snapshot

Captured: 2026-10-13T08:57:24.952982+08:00

Branch: diagnostics/baseline-auroc-20261013

Full original logs and monitoring arrays: https://github.com/chinagalaxy2002/GMR_Unseen/releases/tag/diagnostics-baseline-auroc-records-20261013-085724

Small text records (up to 1 MiB per file) and the numeric Markdown/CSV tables are also available directly in this directory. Complete files, including larger JSONL and all NPZ arrays, are in the release archives. No checkpoints, model caches, features, videos or credentials are included.

Each group is a gzip-compressed tar stream split into parts of at most 1 GiB. Download all parts for a group, then restore its original paths:

```bash
sha256sum -c RECORDS_SHA256SUMS
cat clean_v3_A1_v3_qd_with_sa.tar.gz.part* | tar -xz -C restored
```

Create the restored directory before extraction. Archive member paths are relative to this queue directory. RECORDS_MANIFEST.json records every original path, captured byte count and SHA256. Training remains running; these files represent the captured interval, not live status. Frozen metrics use Seen-validation checkpoint selection and calibration. Rej-F1 and G-mIoU gaps depend on subset class proportions. Five-split macro averages completed: 0.


## Completed-job update 2026-10-13T10:15:33.714689+08:00

Queue counts: {'complete': 11, 'running': 4, 'queued': 40}.

Newly completed jobs: clean_v3_A1_v3_moment_with_sa.

[Download complete job archives](https://github.com/chinagalaxy2002/GMR_Unseen/releases/tag/diagnostics-baseline-auroc-completed-20261013-101533). Each archive includes all 100 epochs, frozen predictions, metrics, calibration, bootstrap arrays and raw monitoring records for the listed job. Extract from the queue directory to restore original paths. These archives supersede the corresponding partial job records in the earlier release. Checkpoints and model caches are excluded.

[Update manifest](updates/20261013-101533/MANIFEST.json).
