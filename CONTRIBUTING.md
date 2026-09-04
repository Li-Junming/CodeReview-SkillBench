# Contributing

感谢你帮助改进 CodeReview SkillBench。项目优先接受可复现、来源清晰且不会泄露私有评测资产的贡献。

## 开始之前

1. 先创建 Issue，说明用户问题、预期行为和公开数据来源；
2. 不要提交商业代码、私有 GT、模型凭证、原始提供商记录或无再分发许可的 Skill；
3. 功能与缺陷修复遵循测试先行；
4. 新 TestCase 必须有明确难度、断言、来源和许可证说明。

## 本地检查

```powershell
python -m pytest -q
python scripts/check_release_manifest.py --root .
python scripts/scan_public_tree.py --root .
python scripts/check_markdown_links.py --root .
npm --prefix frontend ci
npm --prefix frontend run lint
npm --prefix frontend run build
```

## 提交公开 TestCase

案例必须是原创、明确授权或来自兼容许可证的素材。避免包含完整第三方仓库；优先提交能最小复现缺陷的合成代码。Rubric 必须拆为原子断言，并解释证据充分条件。

## Pull Request 要求

- 描述问题、方案、测试与结论边界；
- 说明新增文件来源；
- 不根据实验结果反向修改权重或通过标准；
- 生成物只有在确定性、脱敏且受测试覆盖时才可提交。

