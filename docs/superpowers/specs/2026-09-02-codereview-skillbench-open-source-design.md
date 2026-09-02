# CodeReview SkillBench 开源产品设计

日期：2026-09-02  
状态：已确认，等待实施计划

## 1. 产品定位

CodeReview SkillBench 是一个面向 Code Review Agent Skill 的自动化评测平台。项目优先服务实际开源用户，其次作为个人工程能力与项目经历的展示载体。

平台重点回答五个问题：

1. Skill 是否被正确触发；
2. Skill 是否按照约定执行；
3. Skill 是否提升代码审查结果质量；
4. Skill 在不同模型上的表现是否稳定；
5. 失败来自运行系统、评测资产、Skill 还是模型。

仓库首先发布为 GitHub 私有仓库，完成脱敏、验证和授权检查后再公开。

## 2. 发布原则

- 重新建立干净 Git 历史，不继承团队仓库的提交历史。
- 从现有工作区复制经过筛选的成果，不直接修改原始团队仓库。
- 面向用户提供可运行的 CLI 核心和可选 Web 界面。
- 保留可复现的公开 Development 资产，不公开 Hidden Holdout、私有 GT 或 evaluator-only 内容。
- 所有结果必须标注证据范围和结论边界，Development 结果不得包装成正式排行榜。
- 未确认授权的第三方 Skill 不进入公开发布包，仅保留来源说明或用户自行导入机制。

## 3. 目标用户

- Code Review Skill 开发者；
- AI Agent 开发者；
- 自动化测试与测试开发工程师；
- 希望比较不同模型和 Skill 组合的研究或工程人员。

## 4. 用户工作流

### 4.1 CLI 工作流

```bash
skillbench verify
skillbench evaluate --skill ./my-skill --profile development
skillbench report --run <run-id>
skillbench serve
```

CLI 是权威执行入口，负责配置校验、运行、证据采集、Judge、Qualification 和报告生成。Web 界面调用相同的后端能力，不维护第二套评测逻辑。

### 4.2 Web 工作流

上传或选择 Skill → 选择模型和评测 Profile → 执行 D0、C_auto、C_forced 对照实验 → 采集 Trace 与 Artifact → Atomic Judge 判定 → Qualification 门禁 → 生成报告与 Bad Case 归因。

## 5. 系统组成

```text
CodeReview-SkillBench/
├─ README.md
├─ pyproject.toml
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ SECURITY.md
├─ THIRD_PARTY_NOTICES.md
├─ skillbench/
│  ├─ cli/
│  ├─ runner/
│  ├─ evidence/
│  ├─ judge/
│  ├─ qualification/
│  ├─ attribution/
│  └─ reporting/
├─ backend/
├─ frontend/
├─ schemas/
├─ testcases/public/
├─ fixtures/
├─ examples/
├─ reports/samples/
├─ tests/
├─ scripts/
└─ docs/
   ├─ getting-started.md
   ├─ user-guide.md
   ├─ architecture.md
   ├─ methodology.md
   ├─ judge-and-evidence.md
   ├─ bad-case-attribution.md
   ├─ model-configuration.md
   ├─ api-reference.md
   ├─ faq.md
   └─ project-background.md
```

### 5.1 核心执行层

`skillbench/` 提供统一的领域逻辑：

- Runner：执行模型、Skill 和评测条件；
- Evidence：记录输入、输出、Trace、Artifact 和运行指纹；
- Judge：按原子断言评价候选结果；
- Qualification：判断运行是否具备正式计分资格；
- Attribution：定位首个真实偏离点并路由 Bad Case；
- Reporting：生成 JSON 与 HTML 报告。

### 5.2 接口与展示层

- FastAPI 后端暴露任务创建、状态查询、结果读取和报告下载接口；
- Web 前端支持 Skill 上传、模型与 Profile 选择、运行进度、模型对比、证据查看和报告展示；
- CLI、API 和 Web 使用同一 Schema 与核心执行层。

### 5.3 评测资产层

- `testcases/public/` 保存可公开的冻结 Development 用例；
- `fixtures/` 保存匿名化代码和 PR 材料；
- `schemas/` 保存 TestCase、Evidence Bundle、Judge 和报告 Schema；
- `reports/samples/` 保存经过脱敏的代表性结果，不保存供应商原始私有记录。

## 6. 数据链路

所有数据通过稳定标识关联：

```text
TestCase(case_id)
  → Run(run_id, model, skill, condition)
  → Evidence(trace, artifact, output)
  → Atomic Judge(assertion_id, verdict, evidence_refs)
  → Qualification(scoring_eligible)
  → Attribution(first_deviation, root_cause)
  → Report / Rerun
```

旧运行不得被修复结果覆盖；复测通过新的 `run_id` 与原运行关联。

## 7. 失败与归因策略

按照因果顺序寻找第一个不满足预期的节点：

1. 运行系统是否正常；
2. TestCase、输入、GT 和 Rubric 是否正确；
3. Skill 是否正确加载、触发和执行；
4. 证据是否能证明模型产生了目标失败。

系统问题、评测资产问题和证据不足不得直接计为 Skill 失败。证据不足时标记为 `INCONCLUSIVE`；修复后执行定向重跑和回归验证。

## 8. 首次发布范围

`v0.1.0-beta` 包含：

- Python CLI；
- FastAPI 后端；
- Web 可视化界面；
- 公开 Development TestCase 与匿名化 Fixture；
- 模型适配配置示例；
- Evidence Bundle、Atomic Judge 和 Qualification；
- Bad Case 归因流程；
- JSON/HTML 示例报告；
- 用户文档、方法文档与贡献指南；
- 单元、集成和最小端到端测试。

## 9. 不公开内容

- API Key、Token、密钥脚本及本地账号信息；
- Hidden Holdout、私有 GT、Judge 私有答案键和 evaluator-only 材料；
- 原始供应商日志和未脱敏模型记录；
- 团队会议记录、其他成员个人信息和内部工作材料；
- 缓存、临时目录、调试目录、重复压缩包和完整第三方仓库；
- 未确认再分发授权的第三方 Skill。

## 10. 测试与发布门禁

发布前必须通过：

- Python 单元测试与集成测试；
- CLI 最小运行测试；
- 后端接口测试；
- 前端构建与最小端到端测试；
- JSON Schema 校验；
- HTML 报告可读性检查；
- 密钥、个人信息和绝对路径扫描；
- 第三方许可证与来源检查；
- README 从干净环境复现；
- 结论边界审计。

任何真实模型调用测试都必须与默认离线测试隔离，缺少凭据时不得导致基础测试失败。

## 11. GitHub 发布方式

- GitHub 所有者：`Li-Junming`；
- 仓库名：`CodeReview-SkillBench`；
- 初始可见性：Private；
- 默认分支：`main`；
- 首次标签：`v0.1.0-beta`；
- 在授权、脱敏和质量门禁全部通过后，再由仓库所有者切换为 Public。

## 12. 成功标准

首次私有发布完成时，应满足：

1. 新用户能依据 README 安装并运行离线示例；
2. CLI、API 和 Web 共享同一评测核心；
3. 示例报告能追溯到 TestCase、Run 和 Evidence；
4. 仓库不包含密钥、私有评测答案或团队敏感材料；
5. 自动化测试与发布检查通过；
6. 项目说明准确区分项目3、Code Review 小组和个人贡献；
7. 面试官能在 README 首屏理解问题、方法、成果、技术栈和个人职责。
