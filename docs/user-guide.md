# 用户指南

## CLI 工作流

### 验证资产

```text
skillbench verify --root PATH
```

检查实验状态、Skill Bundle、配置标识和所有冻结文件的 SHA-256。

### 查看运行计划

```text
skillbench plan --root PATH --output plan.json
```

计划由 Case × Skill × Condition × Model Profile × Repetition 的笛卡尔积生成，每个 `run_id` 唯一。

### 离线演示

```text
skillbench demo --root PATH --output OUTPUT_DIR
```

这是推荐的第一次体验。D0 与 C_auto 使用“未发现问题”的回放，C_forced 使用能定位并发缺陷的回放，用于展示评测链路差异，不代表模型真实能力。

### 从已有运行生成报告

```text
skillbench report --root PATH --runs RUN_DIR --output OUTPUT_DIR
```

Runner 只负责保存运行；报告阶段再构建 Evidence Bundle、执行 Judge、检查 Qualification 并归因。

### 在线评测

```text
skillbench evaluate --root PATH --skill SKILL_DIR --profile development --output OUTPUT_DIR
```

私有 Beta 尚未启用通用在线 Adapter。没有配置时命令会明确退出，不会回退到未知代理或硬编码服务。

## Web 工作流

1. 选择公开离线演示或开发配置；
2. 可选上传一个 Skill ZIP；
3. 启动评测；
4. 查看各条件 verdict、证据完整性和责任归因；
5. 打开完整 HTML 报告。

## Skill ZIP 规则

- 压缩包大小不超过 2 MB，解压后不超过 4 MB；
- 文件数不超过 100；
- 必须且只能包含一个 UTF-8 `SKILL.md`；
- `SKILL.md` 必须含 YAML frontmatter 与 `name`；
- 不接受绝对路径、父目录跳转、符号链接或加密条目。

上传内容保存在本地 `.skillbench-data/`，该目录被 Git 与公开发布清单排除。

## 如何阅读结果

- `PASS`：证据支持候选输出满足当前原子断言；
- `FAIL`：证据充分，但候选输出未满足断言；
- `INCONCLUSIVE`：证据不足，暂不计分；
- `qualification.scoring_eligible`：该结果能否进入分数；
- `attribution.first_deviation`：链路中第一个真实偏离点；
- `evidence.integrity`：输入和响应是否与 Trace 中的哈希一致。
