# Week7 Day2 证据记录 —— Ingress 流量分配

## 环境信息

- Kubernetes: Minikube
- Ingress Controller: ingress-nginx
- 域名: fastapi-ml.local
- 访问方式: Ingress + 本地 hosts 映射 + minikube tunnel

## 已完成验证

### 1. Ingress Controller 状态
已确认 `ingress-nginx-controller` 处于 Running 状态。

### 2. 双版本服务状态
已存在两个版本的服务：

- fastapi-ml-stable
- fastapi-ml-canary

### 3. `/version` 验证
连续请求 `/version` 20 次，结果中同时出现：

- `release_track: stable`
- `release_track: canary`

说明 Ingress 的 canary 流量规则已经生效，部分请求已进入 canary 版本。

## 结果说明

本次结果能够证明：

- Ingress 已正确接管入口流量
- canary 不是单独孤立运行，而是真正收到了部分流量
- Week7 已从“版本共存”进入“灰度分流”阶段

## 说明

当前结果适合作为 Day2 完成证据。
若后续需要更严格说明 90/10 分流比例，应增加更大样本量，并结合日志或监控指标进行统计分析。