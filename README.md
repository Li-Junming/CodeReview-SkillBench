# CodeReview SkillBench

> 面向 Code Review Agent Skill 的可复现评测工具：固定实验变量、保存运行证据、逐项判定结果，并在计分前完成失败责任归因。

**PRIVATE BETA · v0.1.0-beta.1**

当前版本优先提供可复现的离线演示与本地工作台。它不是商业模型排行榜，也不发布课程项目的私有 TestCase、GT、原始模型记录或第三方 Skill。

## 为什么需要它

普通评测容易把“运行失败”直接当成“Skill 失败”，但失败也可能来自 Runner、测试资产、Skill 未加载或证据缺失。SkillBench 把一次评测拆成可审计链路：

```text
冻结配置 → 执行与取证 → Atomic Judge → Qualification → 责任归因 → 报告
```

只有运行、资产、Skill 执行和证据门全部通过，失败结果才有资格进入分数。

## 五分钟离线体验

离线演示使用原创合成案例与回放响应，**不需要 API Key**。

```powershell
git clone https://github.com/Li-Junming/CodeReview-SkillBench.git
cd CodeReview-SkillBench
python -m venv .venv
.\.venv\Scripts\python -m pip install ".[dev]"
.\.venv\Scripts\skillbench verify --root .
.\.venv\Scripts\skillbench demo --root . --output build\demo
```

生成结果：

- `build/demo/report.json`：机器可读、受 JSON Schema 约束；
- `build/demo/report.html`：无需服务器即可打开的单文件报告；
- `build/demo/.runs/`：输入、响应、Trace 与 completion 证据。

仓库内也提供一份已生成的[示例 HTML 报告](reports/sample/report.html)和[示例 JSON 报告](reports/sample/report.json)。

## Web 工作台

后端：

```powershell
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

前端：

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

打开 `http://127.0.0.1:3000`，可运行公开离线演示，或上传包含一个 `SKILL.md` 的 ZIP。上传接口限制大小，并拒绝目录穿越、符号链接、加密压缩包和非 UTF-8 Skill。

## 三种对照条件

- `D0`：不提供 Skill，得到基线表现；
- `C_auto`：Skill 可由运行环境自动发现与触发；
- `C_forced`：执行前明确加载 Skill，用于区分“Skill 无效”和“Skill 未触发”。

## 当前能力

- 冻结实验配置、测试资产与 Skill 哈希；
- 生成唯一运行计划并使用只追加目录保存结果；
- 构建 Evidence Bundle，检测输入或响应被修改；
- Atomic Judge 输出结构化 verdict、理由与证据引用；
- Qualification 先判断结果能否计分；
- 按第一个真实偏离点完成 Bad Case 责任归因；
- 输出 JSON/HTML 报告；
- 提供 CLI、FastAPI 与 Next.js 三种入口；
- 通过发布白名单、敏感信息扫描和 CI 阻止私有资产外泄。

## 目录

```text
src/skillbench/        评测、取证、判定、归因与报告核心
backend/               调用同一核心包的 FastAPI 接口
frontend/              Next.js 本地评测工作台
testcases/public/      可再分发的公开合成案例
examples/public_demo/  原创示例 Skill 与离线响应
protocols/             难度与责任归因协议
schemas/               报告和证据数据契约
reports/sample/        脱敏示例输出
scripts/               冻结、链接检查与发布扫描
tests/public/          可公开的回归测试
```

## 文档

- [快速开始](docs/getting-started.md)
- [用户指南](docs/user-guide.md)
- [系统架构](docs/architecture.md)
- [评测方法](docs/methodology.md)
- [Judge 与 Evidence Bundle](docs/judge-and-evidence.md)
- [Bad Case 责任归因](docs/bad-case-attribution.md)
- [模型配置与边界](docs/model-configuration.md)
- [API 参考](docs/api-reference.md)
- [常见问题](docs/faq.md)
- [项目背景与个人贡献](docs/project-background.md)

## 结论边界

公开离线演示只证明评测链路可以复现，不证明某个商业模型或 Skill 的真实效果。正式模型结论至少需要冻结版本、足够样本、重复运行、Judge 与人工一致性校准，以及独立 Holdout；这些私有资产不会进入公开仓库。

## 安全、贡献与许可

- 发现安全问题请先阅读 [SECURITY.md](SECURITY.md)，不要公开提交密钥或私有评测资产；
- 贡献代码与公开 TestCase 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)；
- 本仓库原创代码采用 [MIT License](LICENSE)，依赖与来源说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；
- 版本变化见 [CHANGELOG.md](CHANGELOG.md)。

## 路线图

- 接入可替换的模型 Adapter，并保持凭证仅从本地环境读取；
- 扩充经许可的公开 Code Review TestCase；
- 增加多 Judge、盲评与人工一致性校准工具；
- 支持批量实验、趋势比较和回归任务管理；
- 完成公开发布前的许可证与数据来源复核。

项目由李俊铭维护，源于深圳技术大学 × 腾讯 Mini Project 3 中 Code Review 子方向的评测实践；仓库仅代表该子方向的公开重构与维护者贡献，不代表整个项目组成果。
