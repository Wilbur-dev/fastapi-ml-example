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
