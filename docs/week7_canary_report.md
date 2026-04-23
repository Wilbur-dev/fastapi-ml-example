# Week7 - 灰度发布（Canary）与回退报告

## 1. 背景
为降低上线风险，本项目采用灰度发布（canary）而非直接全量替换。  
系统同时运行两个版本：

- **stable**：当前稳定版本  
- **canary**：待验证新版本  

通过逐步分配流量并结合监控指标判断是否继续放量或回退。

---

## 2. 系统设计

### 部署结构
- 两个 Deployment：`fastapi-ml-stable`、`fastapi-ml-canary`
- `/version` 接口返回：
  - app_version
  - model_version
  - release_track

### 流量分配
- 通过 Ingress 控制流量
- canary 接收部分流量（如 50%）

---

## 3. 验证指标

灰度发布决策基于以下指标：

- **p95 延迟**
- **错误率（error rate）**
- **返回结构兼容性**

判定标准：

- error_rate < 1%  
- p95 不明显高于 stable  
- 返回字段保持一致  

---

## 4. Canary 实验

为模拟异常版本，在 canary 中人为加入延迟：

```python
if runtime.release_track == "canary":
    time.sleep(0.3)
```

通过压测触发流量：
```bash
hey -n 20000 -c 50 ...
```

---

## 5. 问题观测

### 实验结果：

canary 延迟明显高于 stable
错误率正常
返回结构一致

### 结论：

❌ canary 不满足性能要求
→ 不可继续放量

---

## 6. 回退策略

### 采用流量级回退，而非 deployment 回滚：
```bash
kubectl delete -f k8s/prod/canary/ingress.yaml
```

### 说明：

不删除 Pod
不重启服务
仅移除 canary 流量入口

---

## 7. 回退后验证
### 日志
canary：仅剩 /health 和 /metrics
### 监控
canary 流量归零
延迟恢复正常

### 结论：
✅ 流量成功切回 stable
✅ 系统快速恢复

---

## 8. 关键经验

### 1️⃣ 优先做流量回退

生产环境中应先切流量快速止血，而不是立即回滚 deployment。

### 2️⃣ 指标驱动决策

发布判断必须依赖延迟和错误率，而非主观判断。

### 3️⃣ 可观测性是前提

没有 metrics 和日志，就无法判断 canary 是否成功。

---

## 9. 总结

本项目实现了一套完整的安全发布流程：

灰度分流（canary）
实时监控（metrics）
快速回退（traffic rollback）

能够在不影响服务的情况下完成新版本验证与风险控制。