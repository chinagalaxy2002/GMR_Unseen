# MCV 特征生产依赖

本次仅发布 `prepare_features.py`，用于追溯 [DDV](../decomposed_directional_verifier/README.md) 的十维基础缓存来源；没有把 MCV 历史模型的结果作为新方法结论发布。

输入包括 AC 对齐特征、三骨干训练缓存及 Seen 验证/测试预测、CLIP 和 SlowFast 视频特征。输出为 `cache_features/{split}/{train,val,test}.npz`。DDV 随后加入动作/物体短语相似度形成 12 维输入。缓存、原视频、检查点和逐查询预测保留本地。完整恢复顺序见 DDV README。
