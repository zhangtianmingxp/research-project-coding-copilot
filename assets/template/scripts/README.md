# Scripts

本目录存放科研推进模板的辅助脚本。

`research_flow.py` 只负责状态读取、结构检查、编号推断和 prompt 草稿生成。

其中 `init-round` 仅是手动调试脚手架，不代表正式 prompt 已通过内稿质量门。正常 skill 工作流先在上下文审查内稿，再一次性写入正式 prompt。

它不会：

- 调用模型 API；
- 执行 prompt；
- 自动生成下一轮 prompt；
