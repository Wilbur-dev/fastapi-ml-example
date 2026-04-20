实现基于 Prometheus 的应用层可观测性，为推理服务埋点请求量、错误率与延迟指标（Counter/Histogram），并通过全局异常处理统一捕获 4xx 校验错误，确保 error rate 统计完整；指标按 model_version 与 release_track 打标签，为后续灰度发布（canary）与性能对比提供数据支持。

完成 Prometheus 集成，通过 ServiceMonitor 实现对推理服务 /metrics 的自动抓取，并基于 PromQL 构建 QPS、Error Rate 和 P95 Latency 查询；在实践中分析低流量场景下 rate() 与 increase() 的差异，确保指标统计准确，同时明确仅监控 CPU 不足以评估系统健康，必须结合延迟与错误率进行应用层监控。

完成了基于 Prometheus 的 Grafana 监控面板搭建，实现了对请求流量、延迟、错误率和副本数的可视化，为后续性能压测和自动扩缩容提供了基础观测能力。

通过对推理服务在不同并发下的压测，获得了系统的 QPS 与延迟变化规律，并识别出高并发下的性能瓶颈，建立了可量化的性能基线，为后续 HPA 自动扩缩容和性能优化提供了依据。

# Week5 Day1 — 应用层指标（Prometheus）

## 1. 概述

本阶段在推理服务中引入了应用层可观测性（Observability），通过集成 Prometheus 指标，实现对请求量、错误率和延迟的量化监控。

该能力将为后续的性能分析、自动扩缩容（HPA）以及灰度发布（canary）提供数据基础。

---

## 2. 实现内容

### 2.1 指标暴露

* 集成 `prometheus_client`
* 新增 `/metrics` 接口，供 Prometheus 抓取

### 2.2 埋点位置

指标在两个层面进行采集：

* **路由层（`/predict`）**

  * 成功请求（2xx）
  * 推理延迟（latency）

* **全局异常处理（exception handler）**

  * 参数校验错误（4xx）

---

## 3. 指标设计

### 3.1 请求计数

```text
inference_request_total
```

* 类型：Counter
* 标签：

  * `endpoint`
  * `method`
  * `status_bucket`（2xx / 4xx）
  * `model_version`
  * `release_track`

---

### 3.2 错误计数

```text
inference_error_total
```

* 类型：Counter
* 统计所有失败请求（当前包含 4xx）
* 使用与 request 相同的标签体系

---

### 3.3 延迟指标

```text
inference_latency_seconds
```

* 类型：Histogram
* 仅统计成功推理请求
* 标签：

  * `endpoint`
  * `method`
  * `model_version`
  * `release_track`

---

## 4. 验证结果

共发送 3 个请求：

1. 类型错误 → 4xx
2. 正常请求 → 2xx
3. 缺字段 → 4xx

对应指标结果：

* `request_total`

  * 4xx：2
  * 2xx：1

* `error_total`

  * 4xx：2

* `latency`

  * 仅记录成功请求：1

验证结论：

* 参数校验错误已被正确统计
* 成功与失败路径分离清晰
* 延迟仅针对有效推理请求记录

---

## 5. 设计说明

* 将 4xx（参数错误）纳入 error metrics，保证 error rate 计算准确。
* 指标中加入 `model_version` 和 `release_track`，为后续 stable / canary 对比提供支持。
* 请求计数在 route 与 exception handler 中分别处理，确保所有请求均被统计。

---

## 6. 下一步计划

下一阶段将接入 Prometheus 并实现指标查询，包括：

* QPS（每秒请求数）
* Error Rate（错误率）
* P95 Latency（延迟分位数）

后续将在 Grafana 中进行可视化展示。




# Week5 Day2 — Prometheus 集成与指标查询

## 1. 概述

本阶段将应用已暴露的 Prometheus 指标接入 Prometheus 服务器，实现指标的自动抓取与查询分析。
通过 ServiceMonitor 将 FastAPI 服务的 `/metrics` 接口纳入监控，并验证关键指标（QPS、Error Rate、Latency）的可查询性。

---

## 2. 实现内容

### 2.1 Prometheus 部署

使用 Helm 安装监控栈：

```bash
helm install monitoring prometheus-community/kube-prometheus-stack
```

通过 port-forward 访问 Prometheus UI：

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090
```

访问地址：

```text
http://127.0.0.1:9090
```

---

### 2.2 指标抓取配置

创建 ServiceMonitor，使 Prometheus 自动抓取服务指标：

```yaml
spec:
  selector:
    matchLabels:
      app: fastapi-ml
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
```

关键点：

* Service 的 port name 必须为 `http`
* ServiceMonitor 匹配的是 **Service labels（不是 Pod labels）**
* `/metrics` 必须在容器中真实存在（否则返回 404，target 为 DOWN）

---

### 2.3 抓取验证

在 Prometheus UI：

* `Status → Targets`：确认服务状态为 **UP**
* `Graph` 页面执行查询：

```promql
inference_request_total
```

成功返回数据，说明指标已接入。

---

## 3. 核心 PromQL 查询

### 3.1 QPS（每秒请求数）

```promql
sum(rate(inference_request_total[1m]))
```

说明：统计最近 1 分钟内平均每秒请求数。

---

### 3.2 P95 延迟

```promql
histogram_quantile(
  0.95,
  sum by (le) (rate(inference_latency_seconds_bucket[5m]))
)
```

说明：计算延迟分布的 95 分位，反映用户体验。

---

### 3.3 Error Rate（错误率）

推荐在低流量场景使用：

```promql
sum(increase(inference_error_total[5m]))
/
sum(increase(inference_request_total[5m]))
```

说明：

* `increase()` 更适合低流量测试
* `rate()` 在小样本下容易出现不稳定或瞬时偏差

---

## 4. 验证结果

通过手动发送请求：

* 2 次错误请求（4xx）
* 1 次成功请求（2xx）

验证：

* `inference_request_total` 按 status_bucket 正确分桶
* `inference_error_total` 正确统计错误请求
* QPS 曲线呈现突发型（burst）流量特征
* Error Rate 在低流量下受时间窗口影响较大

---

## 5. 关键问题与解决

问题：Prometheus target 显示 `DOWN (404 Not Found)`

原因：服务未正确暴露 `/metrics` 接口

解决：

* 确认应用代码注册 metrics 路由
* 重建镜像并更新 Deployment
* 验证 `/metrics` 返回 Prometheus 格式数据

---

## 7. 下一步

后续将接入 Grafana，对 QPS、Error Rate、P95 Latency 进行可视化展示，并支持多版本（stable / canary）对比分析。



# Week5 Day3 - Grafana Dashboard 搭建

## 🎯 目标
将 Prometheus 已采集的指标进行可视化，构建基础监控面板，用于观察服务流量、延迟、错误率和副本变化。

---

## 🧩 实现内容

### 1. 接入 Grafana
- 使用 `kubectl port-forward` 访问 Grafana
- 添加 Prometheus 作为数据源（使用 K8s service 地址）

---

### 2. 构建核心监控面板

#### QPS
```promql
sum(rate(inference_request_total[1m]))
```
#### P95 延迟
```promql
1000 * histogram_quantile(0.95, sum(rate(inference_latency_seconds_bucket[5m])) by (le))
```
#### 错误率
```promql
100 * sum(rate(inference_error_total[5m])) 
/ clamp_min(sum(rate(inference_request_total[5m])), 1e-6)
```
#### Pod 数量
```promql
count(kube_pod_status_phase{phase="Running", pod=~"mlops-api.*"})
```
#### CPU 使用
```promql
sum(rate(container_cpu_usage_seconds_total{pod=~"mlops-api.*", container!="POD"}[5m]))
```

---

### 3. 验证
使用 curl 或 hey 持续发送请求
观察 QPS、延迟曲线是否随流量变化
检查错误率是否反映异常请求
确认 Pod 数量在扩容时变化

---

### ⚠️ 遇到问题
p95 无数据：使用了错误的 metric 名，已修正
error rate 异常：通过拆分指标定位统计问题
Grafana 操作不熟：切换 Code 模式手写 PromQL




# Week5  Day4 Benchmark

## Test Setup
- Tool: hey (Docker)
- Endpoint: /predict
- Method: POST
- Deployment replicas: 2
- Request payload:
  {"feature1":1.0,"feature2":2.0,"request_id":"test-001"}

---

## Results

| Concurrency | Total Requests | QPS | Avg Latency (ms) | P95 Latency (ms) | Error Rate |
|------------|----------------|-----|------------------|------------------|------------|
| 20         | 2000           | 175.05 | 113.7 | 196.8 | 0% |
| 50         | 5000           | 204.98 | 242.1 | 299.7 | 0% |
| 100        | 10000          | 178.13 | 557.2 | 702.7 | 0% |

---

## Observations

1. **QPS 行为**
   - 从 20 → 50 并发时，QPS 从 ~175 提升到 ~205，说明系统在中等负载下仍有扩展能力。
   - 从 50 → 100 并发时，QPS 反而下降到 ~178，说明系统已接近性能瓶颈。

2. **延迟变化**
   - 平均延迟从 113 ms → 242 ms → 557 ms，随并发明显上升。
   - P95 延迟从 196 ms → 299 ms → 702 ms，尾延迟在高负载下显著恶化。

3. **系统稳定性**
   - 所有请求均返回 200，错误率为 0%，说明服务在当前负载下仍保持稳定。
   - 但高并发下延迟明显上升，说明系统进入“高负载但未崩溃”状态。

4. **性能瓶颈**
   - QPS 在高并发下降 + 延迟急剧上升，典型表现为：
     - CPU 或推理逻辑成为瓶颈
     - 单请求处理时间限制整体吞吐

---

## Conclusion

在当前配置（2 replicas）下：

- 系统在 **50 并发时达到最佳吞吐（~205 QPS）**
- 在 **100 并发时进入瓶颈区间**
- 高负载下 **P95 延迟达到 ~700 ms**

👉 当前系统已经具备基本稳定性，但需要通过扩容或优化来提升高并发性能。

---

## 📌 总结

通过对推理服务在不同并发下的压测，获得了系统的 QPS 与延迟变化规律，并识别出高并发下的性能瓶颈，建立了可量化的性能基线，为后续 HPA 自动扩缩容和性能优化提供了依据。
