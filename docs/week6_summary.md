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



# Week6 Day2 – 镜像构建与模型部署解耦

## 今日工作

- 新增 Docker 镜像构建与推送 workflow（GitHub Actions）
- 实现代码 push 后自动：
  - build Docker image
  - push 到容器仓库（GHCR）
- 完成模型部署方式重构：
  - 不再依赖整个 mlruns 目录
  - 引入 deployment_mlruns 作为部署专用模型产物目录
- 重构 promote_model.py：
  - 从 MLflow URI（models:/ 或 runs:/）加载模型
  - 导出为部署专用 MLflow artifact
  - 生成 promotion metadata
- 修改 Dockerfile：
  - 删除 COPY mlruns
  - 改为 COPY deployment_mlruns
- 更新本地质量门禁脚本（check_all.sh）：
  - 新增 deployment artifact 校验
  - 集成 promote 流程
  - 完整 smoke test（health / version / predict）

---

## 关键改进点

### 1. 模型部署解耦（核心提升）

将系统从：

> 服务直接依赖 MLflow 本地实验目录（mlruns）

升级为：

> 服务只依赖部署专用模型产物（deployment artifact）

实现了：

- 实验环境（mlruns）与部署环境解耦
- Docker 构建不再依赖本地训练产物
- 更符合真实生产系统架构

---

### 2. 模型加载方式统一

- 服务层仍通过 MLflow 加载模型（mlflow.load_model）
- 但统一为部署专用 URI：file:///app/deployment_mlruns/served_model


实现：

- promote 层支持多种模型来源（models:/、runs:/）
- serving 层只保留一种标准加载方式

---

### 3. 自动化镜像构建

实现 CI 自动：

- 构建镜像
- 打 tag（latest + commit sha）
- 推送到容器仓库

优势：

- 不再手动 docker build
- 镜像版本可追踪
- 为后续 CD（自动部署）打基础

---

### 4. 本地全链路质量门禁

通过 `scripts/check_all.sh` 实现：

- lint（ruff）
- 单元测试（pytest）
- 训练流程
- promote（生成 deployment artifact）
- API 启动验证
- 接口 smoke test

确保：

> 本地通过 = 基本可部署

---

## 当前系统架构（简化）
Training / MLflow Tracking
↓
promote_model.py
（选择模型 + 导出 deployment artifact）
↓
deployment_mlruns/served_model
↓
Docker image（仅包含部署模型）
↓
K8s / 服务加载
（统一 MODEL_URI）


---

## 今日结果

- CI workflow 通过 ✔
- Docker build & push 成功 ✔
- 本地 check_all.sh 全链路通过 ✔
- 服务可正常加载部署模型并预测 ✔

---

## 说明

- 本地仍使用 .env 作为开发配置载体
- K8s 环境通过 Deployment env 注入 MODEL_URI
- deployment_mlruns/served_model 不提交到 Git，仅作为构建产物

---

## 下一步（Week6 Day3）

- 将模型上线流程接入 CD（持续部署）
- 自动将 MODEL_URI 注入 K8s Deployment
- 实现：
  - promote → deploy → rollout
- 完成端到端模型上线自动化流程



# Week6 Day3 – Kubernetes CD

## 今日工作
- 新增 CD workflow（.github/workflows/cd.yml）
- 使用 `kubectl set image` 作为 Deployment 更新方式
- 使用 `kubectl rollout status` 检查发布状态
- 记录 rollout duration
- 本地验证 sha tag 镜像可成功部署到 minikube

## 关键结论
- `latest` 不适合作为正式部署标签，容易受到缓存影响
- commit sha tag 更稳定、更可追踪
- 当前项目采用：
  - CI 负责 build & push image
  - CD 负责 set image + rollout status

## 结果
- 新镜像已在本地 minikube 成功部署
- Pod 可正常启动
- 服务健康检查通过

## 说明
- 当前集群为本地 minikube，GitHub-hosted runner 无法直接访问本地 Kubernetes API
- 因此本阶段已完成 CD workflow 编写与本地部署验证
- 真实生产环境中会使用云上 Kubernetes、self-hosted runner 或受控 kubeconfig / OIDC 实现真正自动部署
