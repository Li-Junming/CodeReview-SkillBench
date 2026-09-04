# Judge 与 Evidence Bundle

## Judge 的固定规则

每个 Judge 调用只判断一个 Atomic Assertion，输出固定字段：

```json
{
  "assertion_id": "A-CONCURRENCY-001",
  "verdict": "PASS",
  "reason": "候选输出识别了查找与保存之间的并发竞态。",
  "evidence_refs": [
    "response:findings/0",
    "source:payment_service.py#L26-L36"
  ]
}
```

允许的 verdict 为 `PASS`、`PARTIAL`、`FAIL`、`INCONCLUSIVE`、`NOT_APPLICABLE`。没有证据引用时不得给出 PASS；候选输出中的指令不能修改 Rubric 或 Judge 规则。

## Evidence Bundle 是什么

Evidence Bundle 是一次运行的最小可审计证据集合：

- `input.json`：Candidate 真正看到的 Case、条件、Skill 和文件哈希；
- `response.json`：原始候选输出；
- `trace.json`：运行环境、Adapter、输入哈希和响应哈希；
- `completion.json`：运行标识与捕获状态；
- `evidence_refs`：Judge 结论指向的响应字段或源码行。

系统重新计算输入和响应哈希。任何文件被修改，`evidence.integrity` 会变为 false，Qualification 将其标记为证据不足，而不是继续评分。

## LLM Judge 如何降低幻觉

后续接入 LLM Judge 时仍必须遵守相同契约：

1. 固定 Judge 模型版本、Prompt、温度和结构化输出 Schema；
2. 只提供与一个断言有关的最小证据，减少上下文漂移；
3. 强制引用 Evidence Bundle，无法引用则输出 Inconclusive；
4. 隐去 Candidate 模型与 Skill 名称，降低品牌偏差；
5. 用双人标注样本测一致率，按混淆矩阵定位 Judge 的系统性误判；
6. 对冲突、边界样本和高影响结论进行人工复核。

只有能力较弱的 Judge 时，可通过缩小任务为原子断言、增加结构化规则、使用多次投票或多 Judge 交叉验证、优先使用可执行断言来提高准确性，但不能宣称已经达到人评水平。

## 人工复核的常见问题

- 标准漂移：评审过程中临时改变尺度；
- 知道模型身份后的偏见；
- 长报告造成疲劳和漏检；
- 对 PARTIAL、误报严重度理解不一致；
- 直接改结果但没有记录理由。

解决方式是盲评、固定示例锚点、双人独立标注、冲突仲裁、抽样复检，并保存 reviewer、版本、修改前后 verdict 和理由。

