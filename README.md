# AI Inference System / ML Serving Platform

## 1. 项目简介（Project Overview）

本项目实现了一个接近生产环境的机器学习推理系统，覆盖从模型训练、版本管理到服务部署、监控、自动扩缩容以及灰度发布与回滚的完整流程。

系统重点展示：
- 模型服务化（Model Serving）
- 模型版本管理（MLflow）
- Kubernetes 部署与运维
- 可观测性（Monitoring）
- 自动扩缩容（HPA）
- CI/CD 流程
- 灰度发布（Canary）与回滚机制

该项目体现了机器学习模型在真实工程环境中的落地方式，而不仅仅是训练模型本身。

---

## 2. 系统架构（Architecture）
```text
                ┌──────────────┐
                │   Client     │
                │  (curl/API)  │
                └──────┬───────┘
                       │
                       ▼
              ┌──────────────────┐
              │   FastAPI API    │
              │ /predict /health │
              │ /version         │
              └──────┬───────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│   Pod (Stable)│         │  Pod (Canary) │
│  ML Model     │         │  ML Model     │
└──────┬────────┘         └──────┬────────┘  
       │                         │
       └────────────┬────────────┘
                    ▼
            ┌───────────────────┐
            │  Kubernetes       │
            │ Deployment/Service│
            └────────┬──────────┘
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ Prometheus │ │  Grafana   │ │    HPA     │
│ (metrics)  │ │ dashboard  │ │ autoscale  │
└────────────┘ └────────────┘ └────────────┘

                     │
                     ▼
            ┌──────────────────┐
            │    MLflow        │
            │ Model Registry   │
            └──────────────────┘

                     │
                     ▼
            ┌──────────────────┐
            │ GitHub Actions   │
            │ CI (build/push)  │
            └──────────────────┘
```

系统整体流程：

Client → FastAPI → Kubernetes → Model → Monitoring → CI/CD

---

## 3. 系统时序 （System Flow）
```text
Client
  │
  ▼
FastAPI (/predict)
  │
  ▼
Inference Service
  │
  ▼
Load Model (MLflow URI)
  │
  ▼
Prediction
  │
  ▼
Return Response (/predict)

  │
  └──► Metrics (latency / request_count)
           │
           ▼
      Prometheus
           │
           ▼
        Grafana
```
        
=== With Canary ===

```text
Client
  │
  ▼
Ingress (traffic split 90/10)
  │
  ├──► Stable Deployment
  │
  └──► Canary Deployment
          │
          ▼
      FastAPI → Model → Response
```

---

## 4. 核心能力（Key Features）
- 基于 FastAPI 的模型推理服务（/predict /health /version）
- 使用 MLflow 进行模型实验记录与版本管理
- Kubernetes 多副本部署（Deployment + Service）
- Readiness / Liveness 探针 + Rolling Update· 
- Prometheus + Grafana 监控系统指标
- HPA 自动扩缩容（基于 CPU）
- GitHub Actions 实现自动构建（CI）
- 支持 Canary 灰度发布与回滚机制

---

## 5. 快速开始（Quick Start）

### 本地运行（Docker）
```bash
docker compose up --build api
```


访问接口：
```
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict ...
```


### Kubernetes 部署
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl port-forward svc/fastapi-ml 8000:8000
```

---

## 6. API 示例（API Usage）
### Health Check
```bash
GET /health
```


### Prediction
```bash
POST /predict
```


### Version Info
```bash
GET /version
```


返回示例：
```JSON
{
  "model_version": "...",
  "app_version": "...",
  "release_track": "stable/canary"
}
```

---


## 7. 模型管理（MLflow）
- 使用 MLflow 记录训练参数、指标和模型
- 支持通过 MODEL_URI 加载指定模型
- 模型版本与服务版本解耦

---


## 8. Kubernetes 部署
- 使用 Deployment 管理多副本
- 使用 Service 提供稳定访问入口
- 支持滚动更新（Rolling Update）
- 支持通过 rollout undo 回滚版本

---


## 9. 监控与扩缩容（Monitoring & Autoscaling）
- 暴露自定义指标（请求数、延迟、错误率）
- Prometheus 抓取指标
- Grafana 展示 QPS / p95 latency
- HPA 根据 CPU 自动扩缩容

👉 查看压测与扩缩容报告：
[压测与扩缩容报告](docs/benchmark.md)

---


## 10. CI/CD 流程
- 使用 GitHub Actions 自动构建 Docker 镜像（build & push）
- 部署阶段在 Kubernetes 上验证 rollout 状态
- 支持部署失败后的回滚机制

（说明：部署为本地 Kubernetes 模拟，但流程设计与生产一致）

---

## 11. 灰度发布与回滚（Canary Release & Rollback）
- 同时部署 stable 与 canary 两个版本
- 使用 Ingress 控制流量比例（10% → 30% → 50%）
- 基于 error rate 和 latency 判断是否继续放量
- 指标异常时回滚至 stable

👉 查看计划与报告：
[灰度计划](docs/canary_plan.md)

[灰度报告](docs/canary_report.md)

---

## 12. 项目结果（Results）

👉 查看详细截图与结果：

[项目结果](docs/results.md)

---

## 13. 项目结构（Project Structure）

```bash
fastapi-ml-example/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │	├── prediction.py
│   │   │	├── version.py
│   │   │	├── metrics.py
│   │   │	├── router.py
│   │   │	├── heartbeat.py
│   │   │	└── index.py 
│   │   └── schemas/
│   │   	├── prediction.py
│   │   	├── version.py
│   │   	├── payloads.py
│   │   	└── healthcheck.py
│   ├── core/
│   │   └── lifecycle.py
│   ├── conf/
│   │   └── config.py
│   ├── observability/
│   │   ├── exception_handlers.py
│   │   └── metrics.py
│   ├── infrastructure/
│   │   └── model/
│   │   	├── runtime.py
│   │   	└── loader.py
│   ├── services/
│   │   └── inference_service.py
│   └── main.py
├── monitoring/
│   ├── servicemonitor.yaml
│   └── grafana-dashboard-week5.json 
├── models/
│   └── lr_model.joblib
├── scripts/
│   ├── promote_model.py
│   └── check_all.sh
├── k8s/
│   ├── prod/
│   │   ├── canary/
│   │   │	├── deployment.yaml
│   │   │	├── service.yaml
│   │   │	└── ingress.yaml 
│   │   └── stable/
│   │   	├── deployment.yaml
│   │   	├── service.yaml
│   │   	└── ingress.yaml
│   └── dev/
│       ├── service.yaml
│       └── deployment.yaml
├── deployment_mlruns/
│   ├── promotion_metadata.json
│   └── server_model/
│       
├── training/
│   ├── training.py
│   ├── model_saver_register.py
│   ├── mlflow_logger.py
│   ├── dataset_process.py
│   ├── parser.py
│   ├── config.py
│   ├── config.yaml
│   └── utils/
│       └── seed.py
├── artifacts/
│   └── metadata/
│   	└── latest_model_metadata.json
├── tests/
│   ├── test_smoke.py
│   └── test_api.py
├── mlruns/
├── docs/
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```


---

## 14. 限制与改进（Limitations & Future Work）
- 当前部署基于本地 Kubernetes（minikube）
- CI/CD 未完全自动化部署（CD 为本地模拟）
- 后续可扩展：
	- 云原生部署（EKS / GKE）
	- 基于业务指标的自动扩缩容
	- 更复杂的模型与推理优化（ONNX / batching）























































































