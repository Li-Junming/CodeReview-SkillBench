# 快速开始

## 环境要求

- Python 3.11 或更高版本；
- Node.js 22（仅 Web 前端需要）；
- Git。

建议将仓库放在只含英文字符的路径下。部分 Windows Python 发行版在可编辑安装时可能错误解码中文路径；普通安装不受影响。

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install ".[dev]"
```

Linux/macOS 将激活路径替换为 `.venv/bin/python`。

## 验证冻结资产

```powershell
.\.venv\Scripts\skillbench verify --root .
```

输出 `Verification passed` 表示配置、测试文件、示例 Skill 与离线响应的哈希均一致。

## 运行离线演示

```powershell
.\.venv\Scripts\skillbench demo --root . --output build\demo
```

此命令会创建 D0、C_auto、C_forced 三次回放，保存证据并生成报告。它不联网，也不读取模型凭证。

## 启动 Web 工作台

终端一：

```powershell
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

终端二：

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

浏览器打开 `http://127.0.0.1:3000`。

## 下一步

- 了解完整命令与上传要求：[用户指南](user-guide.md)
- 理解为何失败不能直接扣分：[责任归因](bad-case-attribution.md)
- 准备在线模型配置：[模型配置](model-configuration.md)

