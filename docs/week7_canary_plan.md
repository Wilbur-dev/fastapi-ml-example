# Canary 发布验证计划（Week7 Day3）

## 目标

在 stable 与 canary 双版本并存的基础上，通过小流量验证新版本表现，并基于可量化指标决定是否继续放量或回退，降低上线风险。

---

## 当前发布状态

* stable：主版本（稳定服务）
* canary：新版本（灰度验证）
* 当前流量比例：10%
* 分流方式：Ingress + canary-weight

---

## 核心验证指标

### 1. 错误率（Error Rate）

定义：

* 错误请求数 / 总请求数

标准：

* canary error rate < 1%
* 且不高于 stable 的 error rate

回退条件：

* canary error rate > 2%
* 或明显高于 stable

---

### 2. 延迟（Latency）

定义：

* p95 响应时间

标准：

* canary p95 ≤ stable p95 × 1.2

回退条件：

* canary 延迟持续高于 stable 20%以上

---

### 3. 返回结构兼容性（API Compatibility）

定义：

* `/predict` 返回字段结构是否一致

标准：

* 字段完全一致（prediction / probability / model_version 等）

回退条件：

* 出现字段缺失 / 命名变化 / 格式不兼容

---

### 4. 版本识别准确率（30K升级关键指标）

定义：

* 请求命中 canary 的比例是否符合预期（如 10%）

验证方式：

* `/version` 返回 release_track
* 日志中记录 stable / canary 标识

标准：

* canary 命中比例在合理范围（例如 5%~20%）

回退条件：

* 所有请求都打到 stable（分流失效）
* 或全部打到 canary（严重错误）

---

## 放量策略（逐步推进）

### 阶段 1：10%（当前）

* 目标：验证 canary 能正常处理请求
* 状态：已完成

---

### 阶段 2：30%

条件：

* 错误率正常
* 延迟可接受
* 返回结构无变化

动作：

* 调整 canary-weight 为 30
* 持续观测指标

---

### 阶段 3：50%

条件：

* 30% 阶段稳定

动作：

* 提升流量比例至 50%

---

### 阶段 4：全量或替换 stable

条件：

* 所有指标满足要求

动作：

* 将 canary 晋升为主版本
* 下线旧 stable

---

## 回退策略（必须会讲）

触发任一条件立即回退：

* 错误率异常升高
* 延迟明显劣化
* API 返回结构不兼容
* 流量分配异常（未命中 canary）

回退方式：

* 将 canary-weight 调为 0
* 或删除 canary ingress
* 保持 stable 承接 100% 流量

---

## 关键理解（面试加分）

* 灰度发布的核心不是“上线”，而是“风险控制”
* Canary 是一个“逐步验证过程”，不是一次性操作
* 指标 + 阈值 = 发布决策依据
* 没有指标的灰度发布是不可控的

---
