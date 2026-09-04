# API 参考

默认地址为 `http://127.0.0.1:8000`。交互式 OpenAPI 文档位于 `/docs`。

## 健康检查

```http
GET /api/health
```

返回服务状态与 Beta 版本，不需要模型凭证。

## 上传 Skill

```http
POST /api/skills
Content-Type: multipart/form-data
```

表单字段 `file` 为 ZIP。成功返回：

```json
{
  "skill_id": "generated-id",
  "name": "sample-review",
  "sha256": "64-character-sha256",
  "file_count": 1
}
```

## 查询 Skill

```http
GET /api/skills/{skill_id}
```

不存在时返回 404。

## 创建运行

```http
POST /api/runs
Content-Type: application/json

{"profile":"offline-demo","skill_id":null}
```

`offline-demo` 立即完成三条件回放。`development` 在未配置 provider 时返回 422；私有 Beta 即使检测到 provider 也会返回 501，避免误认为在线能力已实现。

## 查询运行

```http
GET /api/runs/{run_id}
```

返回状态与报告相对路径。

## 获取报告

```http
GET /api/runs/{run_id}/report
GET /api/runs/{run_id}/report?format=html
```

默认返回 JSON；`format=html` 返回自包含报告页面。

## 本地跨域

API 只允许默认本地前端来源 `localhost:3000` 与 `127.0.0.1:3000`，以及 GET、POST、OPTIONS 方法。部署时应使用反向代理或显式配置可信来源，不能改成任意来源通配符。

