本周主要围绕模型服务的可观测性与弹性扩展能力展开。在服务侧，通过引入 Prometheus 与 Grafana，实现了对请求量（QPS）、延迟（P95）以及资源使用情况（CPU、Pod 数量）的实时监控，使系统运行状态具备可视化能力。在此基础上，使用压测工具对 /predict 接口进行多并发测试，建立了系统性能基线，并分析了不同负载下的响应表现。随后，通过配置基于 CPU 利用率的 HPA（Horizontal Pod Autoscaler），成功实现了服务在高负载下自动扩容（Pod 从 2 扩展至 4），并在负载下降后自动缩容，验证了系统具备动态资源调度能力。通过对扩容前后性能的对比分析，发现系统吞吐能力显著提升，P95 延迟降低约 35%–40%，说明水平扩展在应对高并发场景中具有明显效果。同时也总结了 HPA 的局限性，例如依赖 CPU 指标、扩容存在冷启动延迟等。本周工作标志着项目从“可部署服务”进一步升级为“具备监控与自动扩缩容能力的生产级系统雏形”。

1. 实现基于 Prometheus 的应用层可观测性，为推理服务埋点请求量、错误率与延迟指标（Counter/Histogram），并通过全局异常处理统一捕获 4xx 校验错误，确保 error rate 统计完整；指标按 model_version 与 release_track 打标签，为后续灰度发布（canary）与性能对比提供数据支持。
2. 完成 Prometheus 集成，通过 ServiceMonitor 实现对推理服务 /metrics 的自动抓取，并基于 PromQL 构建 QPS、Error Rate 和 P95 Latency 查询；在实践中分析低流量场景下 rate() 与 increase() 的差异，确保指标统计准确，同时明确仅监控 CPU 不足以评估系统健康，必须结合延迟与错误率进行应用层监控。
3. 完成了基于 Prometheus 的 Grafana 监控面板搭建，实现了对请求流量、延迟、错误率和副本数的可视化，为后续性能压测和自动扩缩容提供了基础观测能力。
4. 通过对推理服务在不同并发下的压测，获得了系统的 QPS 与延迟变化规律，并识别出高并发下的性能瓶颈，建立了可量化的性能基线，为后续 HPA 自动扩缩容和性能优化提供了依据。
5. 完成了 FastAPI 服务的 HPA 自动扩缩容接入与验证：通过配置基于 CPU（50% 阈值）的 HPA，并结合压测工具对服务施加负载，成功观察到 Pod 数量从 2 自动扩容至 4，在负载下降后再缩容回 2。同时结合 Grafana 监控分析发现，扩容后系统 P95 延迟由约 16ms 降至约 10ms，说明扩缩容有效提升了系统在高并发场景下的性能与稳定性，验证了服务具备基础的生产级动态调度能力。

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


# Week5 Day5 - HPA 自动扩缩容总结

## 🎯 目标

Day 5 的目标是为 FastAPI 服务接入 **水平自动扩缩容（HPA, Horizontal Pod Autoscaler）**，并验证系统能够在不同负载下根据 CPU 使用率自动调整 Pod 数量。

---

## ⚙️ 实现步骤

### 1. **确认指标可用**
   - 确保 `metrics-server` 正常运行
   - 通过以下命令验证：
     - `kubectl top pods`
     - `kubectl top nodes`

### 2. **配置 HPA**
   ```bash
   kubectl autoscale deployment fastapi-ml \
     --cpu-percent=50 \
     --min=2 \
     --max=6
### 3. **实时观察扩缩容**
kubectl get hpa -w
kubectl get pods -w
### 4. **进行压测**
使用 hey 进行并发请求
同时通过 Grafana 观察指标变化

### 📊 实验结果

| 阶段          | 并发/QPS        | CPU 使用率   | Pod 数量 | P95 延迟    | 现象        |
|--------------|-----------------|------------|----------|------------|-------------|
| 初始空闲      | ~0 req/s        | ~1%         | 2        | ~9 ms     | 系统空闲     |
| 低负载        | ~100 req/s     | ~50%        | 2        | ~15–17 ms  | 接近扩容阈值  |
| 高负载（峰值） | ~190–200 req/s | ~100%        | 2 → 4    | ~11–14 ms | 触发 HPA 扩容 |
| 扩容稳定后    | ~180 req/s      | ~20%（分摊） | 4        | ~9–11 ms   | 负载被分摊    |
| 负载结束      | ~0 req/s        | ~1%         | 4 → 2   | ~9 ms       | 自动缩容     |

### 🔍 关键观察
扩容触发机制
当 CPU 使用率超过 50% 时触发扩容
Pod 数量从 2 增加到 4
负载分摊效果
扩容后 CPU 使用率明显下降
表明请求被成功分散到更多 Pod
延迟改善
P95 延迟从约 16ms 降至约 10ms
系统响应性能明显提升
Pod 生命周期变化
观察到 Pod 状态变化：
Pending → ContainerCreating → Running → Terminating
说明 Kubernetes 正在动态调度资源
自动缩容
压测结束后 Pod 从 4 自动缩回 2
验证 HPA 完整生命周期正常


### ⚠️ 局限性
HPA 仅基于 CPU 指标，不考虑延迟或错误率
扩容存在延迟（Pod 启动时间）
CPU 不完全等价于真实业务负载
短时间突发流量可能不会立即触发扩容
### 🧠 总结

本实验成功验证了系统具备自动扩缩容能力：

高负载时自动扩容，提高吞吐能力
扩容后延迟下降，系统性能提升
负载降低后自动缩容，节省资源

说明该服务已经从静态部署升级为：

👉 具备动态资源调度能力的生产级服务雏形




# Week5 Day6 - 监控与自动扩缩容分析

## 🎯 目标

Day 6 的目标是基于真实监控数据，对 HPA（水平自动扩缩容）对系统性能的影响进行分析，重点对比扩容前后在吞吐、延迟和资源利用率方面的变化。

---

## ⚙️ 实验环境

- 服务：FastAPI 推理服务
- 部署：Kubernetes（minikube）
- 初始副本数：2
- HPA 配置：
  - CPU 阈值：50%
  - 最小副本：2
  - 最大副本：6
- 压测工具：hey
- 监控系统：Prometheus + Grafana

---

## 📊 扩容前 vs 扩容后对比

| 指标 | 扩容前（2 Pods） | 扩容后（4 Pods） | 变化 |
|------|------------------|------------------|------|
| QPS | ~100 | ~180–200 | ↑ 明显提升 |
| CPU 使用率 | ~50% | ~20% | ↓ 明显下降 |
| P95 延迟 | ~15–17 ms | ~9–11 ms | ↓ 显著降低 |
| Pod 数量 | 2 | 4 | ↑ 自动扩容 |

---

## 📈 监控数据分析

### 1️⃣ CPU 使用率

- 随着请求量增加，CPU 使用率逐步上升
- 当 CPU 超过 50% 阈值时，触发 HPA 扩容
- 扩容后 CPU 使用率显著下降（约 20%）

👉 说明：请求被成功分摊到多个 Pod 上

---

### 2️⃣ QPS（吞吐量）

- 扩容前系统稳定在约 100 req/s
- 扩容后提升至约 200 req/s

👉 说明：系统整体处理能力提升

---

### 3️⃣ P95 延迟

- 扩容前：约 15–17 ms  
- 扩容后：约 9–11 ms  

👉 说明：扩容有效降低了请求响应延迟

---

### 4️⃣ Pod 数量变化

- 初始：2 个 Pod  
- 高负载：自动扩展至 4 个 Pod  
- 负载结束：自动缩回 2 个 Pod  

👉 说明：HPA 完整生命周期正常（扩容 + 缩容）

---

## 🔍 原因分析

1. **CPU 驱动扩容**
   - HPA 根据 CPU 使用率判断是否扩容
   - 请求增加 → CPU 上升 → 触发扩容

2. **负载分摊**
   - 新增 Pod 分担请求压力
   - 单个 Pod 负载下降

3. **延迟降低**
   - 请求并行处理能力增强
   - 排队时间减少 → 延迟下降

4. **自动缩容**
   - 负载下降 → CPU 下降 → 自动回收资源

---

## ⚠️ 局限性分析

- HPA 仅基于 CPU 指标，不考虑延迟或错误率
- 扩容存在延迟（Pod 启动需要时间）
- CPU 并不能完全代表业务复杂度
- 短时间突发流量可能无法及时触发扩容

---

## 🧠 关键结论

- 自动扩缩容显著提升系统吞吐能力
- 扩容后 P95 延迟下降约 35%–40%
- CPU 利用率更加均衡，资源使用更高效
- 系统具备动态适应负载变化的能力

---

## 🧾 总结

本次实验验证了系统具备生产级基础能力：

- 能根据负载自动扩展资源
- 能在高并发下保持较低延迟
- 能在低负载时自动释放资源

👉 说明该系统已经从静态部署升级为：

**具备弹性扩展能力的可观测在线服务系统**

---

## 🚀 后续优化方向

- 基于延迟（P95）或错误率的自定义 HPA
- 引入请求队列长度作为扩容依据
- 优化模型推理性能（ONNX / batching）
- 减少冷启动时间（提升扩容响应速度）