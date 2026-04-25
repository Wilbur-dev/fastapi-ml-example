# 🧠 Canary 部署方案

## 1️⃣ 测试目标

本次测试的目标是：

- 通过**Canary（灰度发布）策略**安全上线新模型版本
- 在逐步放量过程中验证系统表现
- 在出现性能问题时执行**回退（rollback）**，验证系统恢复能力

---

## 2️⃣ 部署架构
### 2.1 服务划分

系统包含两个版本：

- stable（稳定版本）
- canary（灰度版本）

对应资源：

- Deployment：
	- fastapi-ml-stable
	- fastapi-ml-canary
- Service：
	- fastapi-ml-stable
	- fastapi-ml-canary

### 2.2 流量控制（Ingress）

通过 NGINX Ingress 实现灰度：
```
nginx.ingress.kubernetes.io/canary: "true"
nginx.ingress.kubernetes.io/canary-weight: X
```

### 2.3 分阶段灰度策略
|阶段Canary 		|	流量占比	|	目的			|
|---------------|-----------|---------------|
|Stage 1		| 	10%		|	基础验证		|
|Stage 2		| 	30%		|	稳定性验证	|
|Stage 3		| 	50%		|	高负载验证	|

### 2.4 监控指标

每个阶段评估：

- 请求量（Request Count）
- QPS
- p95 延迟
- 日志流量分布（stable vs canary）
- 功能正确性

---

## 3️⃣ 回退策略（关键）

### 3.1 回退触发条件

当出现以下情况时执行回退：

- canary延迟明显高于stable
- 系统吞吐下降
- 存在异常行为

### 3.2 回退方法

本次测试采用：

✅ 删除 Canary Ingress
```bash
kubectl delete -f k8s/prod/canary/ingress.yaml
```

### 3.3 回退后的预期结果
- 所有流量回到stable
- canary不再接收请求
- 系统性能恢复