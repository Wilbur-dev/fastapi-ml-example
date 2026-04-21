# Week6 Day1 – CI 搭建

## 今日工作
- 新增 GitHub Actions 工作流（.github/workflows/ci.yml）
- 接入自动化检查：
  - ruff（代码规范检查）
  - pytest（单元测试）
  - import smoke test（基础导入检查）
  - startup smoke test（服务启动检查，使用 mock 模型）

## 意义
- 每次代码提交都会自动验证
- 防止错误代码进入主分支
- 避免“测试通过但服务无法启动”的问题

## 结果
- CI 流水线可自动触发（push 后执行）
- 所有检查通过（workflow 为绿色）
- 项目具备基础持续集成能力

## 说明
- 本地开发仍使用 Docker（scripts/check_all.sh）
- CI 采用轻量检查（lint + test + smoke），保证速度和稳定性