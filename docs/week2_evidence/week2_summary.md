# Week 2 Summary – MLflow Tracking & Model Registry

## 🎯 本周目标

将训练流程从“单次脚本”升级为：

- 可追踪（MLflow Tracking）
- 可对比（多实验）
- 可注册（Model Registry）
- 可被服务按版本加载（Serving Integration）

最终实现：

train → MLflow → Registry → API 按版本加载模型

---

## 🧱 本周完成内容

### 1️⃣ MLflow 实验追踪

在 `training/training.py` 中接入 MLflow：

- 记录参数：random_state, test_size, solver
- 记录指标：accuracy, train_time_ms
- 记录工程指标：
  - model_size_mb
  - single_request_latency_ms

实现训练过程可追踪、可复现。

---

### 2️⃣ 参数化训练脚本

支持通过 CLI 控制训练：

```bash
python training/training.py \
  --run-name lr_baseline_v1 \
  --random-state 0 \
  --test-size 0.3 \
  --solver lbfgs \
  --register-model
```
实现：

同一脚本支持多实验
实验结果可对比
### 3️⃣ MLflow Model Logging

使用：

mlflow.sklearn.log_model(model, "model")

实现：

模型作为 artifact 存储
可通过 runs:/... 或 registry 加载
### 4️⃣ Model Registry 接入（关键）

使用：

mlflow.register_model(model_uri, "fastapi_ml_classifier")

实现：

同一模型名下多版本管理：
Version 2
Version 3
支持模型生命周期管理
### 5️⃣ 服务按模型版本加载（核心能力）

通过 .env 控制模型版本：

MODEL_URI=models:/fastapi_ml_classifier/2
MODEL_STAGE=versioned
APP_VERSION=week2

API 启动时加载：

mlflow.sklearn.load_model(MODEL_URI)

实现：

不改代码即可切换模型
训练与部署解耦
### 6️⃣ /version 接口增强

返回当前服务加载模型信息：

{
  "app_version": "week2",
  "model_uri": "models:/fastapi_ml_classifier/2",
  "model_version": "2",
  "model_stage": "versioned",
  "loaded_at": "2026-04-13T..."
}

作用：

验证当前线上模型
支持后续灰度发布 / 回滚

### 小结

本周重点不在模型本身，而在于：

> 将“训练代码”升级为“可管理、可追踪、可服务化的模型系统”

项目已从简单的 API Demo，进化为具备基础 MLOps 能力的服务雏形。
