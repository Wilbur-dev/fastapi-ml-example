# Week7 Day1 总结 —— 双版本部署（Stable + Canary）

## 目标

在 Kubernetes 中实现双版本部署，为后续灰度发布（Canary）做准备，使 stable 与 canary 版本可以同时运行。

---

## 完成内容

* 创建两个独立 Deployment：

  * `fastapi-ml-stable`
  * `fastapi-ml-canary`

* 配置不同的标签与选择器：

  * `track: stable`
  * `track: canary`

* 在同一集群中同时部署两个版本，实现版本共存

* 为两个版本分别创建 Service：

  * `fastapi-ml-stable`
  * `fastapi-ml-canary`

* 通过 Deployment 注入环境变量：

  * `APP_VERSION`
  * `MODEL_URI`
  * `RELEASE_TRACK`

* 通过 `/version` 接口验证：

  * stable 和 canary 返回不同版本信息

---

## 核心结果

* 成功实现 **双版本并存架构**
* 两个版本可以独立访问
* API 能清晰返回当前版本信息

---

## 关键理解

* Deployment 名称不同 ⇒ 彼此独立，不会互相覆盖
* Pod 由 Deployment 管理，不能直接删除 Pod 控制版本
* Deployment 中的环境变量可通过 `os.getenv()` 在代码中读取
* Canary 的第一步是“版本共存”，而不是直接替换

---

## 下一步

* 实现流量分配（如 90% → stable，10% → canary）
* 基于指标（延迟、错误率等）对两个版本进行对比分析

---



# Week7 Day2 总结 —— Ingress 灰度流量分配

## 目标
在 Kubernetes 中基于 Ingress 实现 stable 与 canary 的流量分配，为后续灰度发布验证做准备。

## 完成内容

- 启用了 `ingress-nginx` 插件，并确认 controller 成功运行
- 在 `k8s/prod/` 下新增了两个 Ingress 资源：
  - `ingress-stable.yaml`
  - `ingress-canary.yaml`
- 为 canary Ingress 配置了权重注解，实现按比例分流
- 配置本地域名 `fastapi-ml.local` 指向 `127.0.0.1`
- 通过 `/version` 接口连续请求 20 次，观察到返回结果中同时出现 stable 与 canary
- 验证了流量已开始分配到 canary 版本

## 核心结果

- 成功实现了基于 Ingress 的基础灰度流量分配
- stable 仍作为主流量版本存在
- canary 已能够接收部分线上流量
- Day1 的“双版本共存”进一步升级为 Day2 的“按比例分流”

## 关键理解

- Ingress 是 HTTP 层流量入口，不是写在 Deployment 内部，而是独立的 Kubernetes 资源
- stable Ingress 负责默认路由
- canary Ingress 通过注解叠加少量流量规则
- 灰度发布的重点不是立即替换旧版本，而是让新版本先接收少量流量并验证表现
- 本地环境可以通过 `minikube tunnel` + `/etc/hosts` 完成 Ingress 访问链路

## 当前限制

- 当前通过 20 次请求只证明“分流机制已生效”，不能严格证明实际比例长期稳定等于 90/10
- 当前验证主要基于 `/version` 返回结果，后续还需要结合日志、错误率和延迟指标做更完整判断

## 下一步

- 编写 canary 验证标准文档
- 明确继续放量与停止回退的阈值
- 对 stable 和 canary 的延迟、错误率、返回字段兼容性进行对比



# Week7 Day4 总结 —— Canary 流量观测与验证

## 目标

在 10% 灰度流量下运行 canary 版本，并通过实际请求验证其稳定性与行为表现。

---

## 完成内容

* 保持 canary 流量比例为 10%
* 使用脚本模拟约 200 次请求，构造持续流量
* 通过 Ingress 将请求自动分配到 stable 和 canary
* 通过日志验证 canary 成功接收部分流量
* 抽样检查接口返回结果，确认无字段变化或错误
* 对请求延迟进行基础观察，未发现明显异常

---

## 核心结果

* canary 已成功接收约 10% 流量
* stable 继续承担主要流量
* 两个版本均能稳定处理请求
* API 返回结构保持一致，无兼容性问题
* 初步验证 canary 可在小流量下稳定运行

---

## 验证方式

* 请求命中验证：通过 `/version` 和日志确认 stable / canary 分布
* 稳定性验证：未出现明显错误响应
* 性能观察：未发现明显延迟劣化
* 接口兼容性：返回字段一致

---

## 关键理解

* 灰度发布的核心是“观测”，而不是仅仅分流
* 少量流量可以用于验证新版本行为
* 日志和接口返回是最基础也是最重要的验证手段
* 没有观测的灰度发布是不可控的

---

## 当前限制

* 未引入 Prometheus / Grafana 进行精确指标统计
* 延迟和错误率判断基于简单观察
* 样本量有限，仅用于初步验证

---

## 下一步

* 提升 canary 流量至 30%
* 引入更精确的监控指标（p95、error rate）
* 比较 stable 与 canary 在负载下的表现差异

---



# Week7 Day5 总结 —— Canary 放量验证（30% / 50%）

## 目标
在 10% 灰度验证通过后，将 canary 流量逐步提升到 30% 和 50%，并根据指标判断是否继续放量。

## 完成内容

- 将 canary 权重从 10% 提升到 30%
- 生成约 300 次请求，验证 30% 分流效果
- 通过 Grafana 观察请求量、错误率和 p95 延迟
- 通过日志确认请求实际命中 canary
- 在 30% 阶段稳定后，将 canary 权重继续提升到 50%
- 再次生成约 300 次请求并观察指标变化

## 验证结果

### 30% 阶段
- canary 请求比例明显上升，接近预期
- 错误率依旧为0
- p95 延迟无明显劣化
- 接口返回结构保持一致

### 50% 阶段
- canary 与 stable 流量接近 1:1
- 错误率依旧为0
- 延迟仍在可接受范围内
- 系统整体运行正常

## 核心结论

- canary 在 30% 和 50% 放量阶段均保持稳定
- 当前版本满足继续推进灰度发布的条件
- 放量过程应基于指标，而不是只看是否“能访问”

## 关键理解

- 发布不是一次切换，而是逐步放量过程
- 请求量、错误率和延迟是灰度决策的核心指标
- release_track 维度使 stable / canary 的对比更清晰
