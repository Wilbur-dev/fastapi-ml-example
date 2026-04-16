# Week 3 总结 —— 可复现的训练到服务闭环

## 1. 总体目标

本周的主要目标是将原有的模型服务原型，升级为一个**可复现（reproducible）且可追踪（traceable）的训练到服务流程**。

核心闭环为：

> **训练 → 生成模型元信息 → 更新服务配置 → API 加载新模型**

相比之前手动替换模型，本周实现了一个**自动化的模型更新流程**。

---

## 2. 本周核心成果

### 2.1 基于配置的训练流程（Config-driven Training）

* 引入 `training/config.yaml` 管理训练参数
* 支持：

  * 固定随机种子（reproducibility）
  * 可配置训练参数（如是否注册模型等）
* 使用 MLflow 统一记录实验（生成 `runs:/...`）

👉 实现了基础的**可复现训练流程**

---

### 2.2 模型元信息管理（metadata.json）

在每次训练后自动生成：

```text
artifacts/metadata/latest_model_metadata.json
```

包含信息：

* `run_id`
* `model_uri`
* `offline_metrics`（如 accuracy）
* `serving_metrics`（如 latency）
* `chosen_reason`

👉 将**模型评估信息与服务解耦**，增强可追踪性

---

### 2.3 模型自动“晋升”（promote）

实现脚本：

```text
scripts/promote_model.py
```

功能：

* 从 metadata.json 读取最新模型
* 自动更新 `.env` 中：

  * `MODEL_URI`
  * `MODEL_STAGE`

👉 避免手动复制 model URI，减少人为错误

---

### 2.4 API 动态加载模型

* 使用：

```python
mlflow.sklearn.load_model(model_uri)
```

* 支持两种 URI：

  * `runs:/...`（当前使用）
  * `models:/...`（为后续扩展预留）

* `/version` 接口返回：

  * 当前模型 URI
  * 模型版本（如有）
  * 加载时间

👉 实现**服务侧与模型解耦**

---

### 2.5 异常路径测试（Failure-aware Testing）

补充测试用例，包括：

* 正常预测
* 非法输入（schema 校验）
* 模型加载失败（启动失败）

👉 提升系统鲁棒性（robustness）

---

### 2.6 本地质量门槛（Day6）

实现脚本：

```text
scripts/check_all.sh
```

流程：

```text
lint → test → train → promote → serve → smoke test
```

功能包括：

* 自动运行测试（pytest）
* 自动训练模型
* 自动更新配置
* 启动 API 并测试：

  * `/health`
  * `/version`
  * `/predict`
* 使用 `trap` 实现自动清理容器

👉 相当于一个**本地 CI 流水线（Local CI Pipeline）**

---

## 3. 完整流程（End-to-End Workflow）

当前系统流程如下：

```text
1. 训练模型
   → 生成 MLflow run + artifacts

2. 写入 metadata
   → latest_model_metadata.json

3. 执行 promote
   → 更新 .env 中 MODEL_URI

4. 重启 API
   → 加载新模型

5. 验证
   → /version 显示当前模型
   → /predict 可正常推理
```

👉 实现了完整的**训练到服务闭环**

---

## 4. 关键设计决策

### 4.1 使用 `runs:/...` 作为模型来源

* 优点：

  * 简单直接
  * 与训练结果一一对应
* 缺点：

  * 不稳定（run_id 会变化）

👉 当前阶段优先实现闭环，后续再引入 registry

---

### 4.2 职责分离（Separation of Concerns）

| 模块       | 职责                 |
| -------- | ------------------ |
| training | 训练模型 + 生成 metadata |
| promote  | 更新配置               |
| API      | 加载模型并提供服务          |

👉 避免训练逻辑进入服务层

---

### 4.3 本地优先质量控制

* 使用 `check_all.sh` 实现本地验证
* 不依赖 CI 平台即可保证基本质量

---

## 5. 当前局限性

* 尚未实现模型自动选择（best model selection）
* 使用 `runs:/...`，不适合生产环境
* 模型更新需要重启 API
* 质量门槛仅在本地（未接入 CI/CD）

---

## 6. 下一步计划（Week 4）

* 引入模型选择策略（选择最佳模型）
* 使用 MLflow Model Registry（`models:/...`）
* 将 `check_all.sh` 迁移到 CI（如 GitHub Actions）
* 优化模型上线流程（版本管理）

---

## 7. 总结

本周完成了从训练到服务的自动化闭环：

> **实现了一个可复现、可追踪的训练 → 部署流程，并建立了基础的质量保障机制。**

该结构为后续向生产级 MLOps 演进打下了基础。
