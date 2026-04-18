# Week4 Summary - Kubernetes Deployment

## What I built

- Deployed FastAPI ML service on Kubernetes
- Integrated ML model loading via MODEL_URI
- Exposed service via Kubernetes Service

## Key Features

- Multi-replica deployment
- Rolling update (zero downtime)
- Readiness & liveness probes
- Environment-driven configuration
- Failure handling & rollback

## Key Learnings

- Difference between image version and model version
- Role of Service vs Deployment
- Probe behavior and CrashLoopBackOff
- Debugging using logs and describe
- Rollback using rollout undo

## Demo Highlights

- End-to-end deployment
- Rolling update demonstration
- Failure simulation and recovery

## Architecture
┌──────────────┐
│ User / curl  │
└──────┬───────┘
       │
       v
┌──────────────────────┐
│ Service: fastapi-ml  │
│ ClusterIP            │
└──────┬───────────────┘
       │ load balance
       v
┌─────────────────────────────┐
│ Deployment: fastapi-ml      │
│ replicas = 2                │
│ readiness/liveness probes   │
└──────┬───────────────┬──────┘
       │               │
       v               v
┌──────────────┐   ┌──────────────┐
│ Pod 1        │   │ Pod 2        │
│ FastAPI API  │   │ FastAPI API  │
│ /health      │   │ /health      │
│ /predict     │   │ /predict     │
│ /version     │   │ /version     │
└──────┬───────┘   └──────┬───────┘
       │                  │
       v                  v
┌──────────────────────────────────┐
│ Config from Deployment env       │
│ MODEL_URI / APP_VERSION / TRACK  │
└──────────────┬───────────────────┘
               v
        ┌──────────────┐
        │ ML Model     │
        └──────────────┘


# Week4 Day1 - K8s Setup

## Commands
minikube start --driver=docker
kubectl get nodes
kubectl create deployment demo-nginx --image=nginx
kubectl port-forward deployment/demo-nginx 8080:80

## Result
- Cluster started successfully
- nginx deployed
- Accessible via localhost:8080



# Week4 Day2 - Deploy API Image to Kubernetes

## Commands
docker build -t fastapi-ml:week4b .
minikube image load fastapi-ml:week4b
kubectl apply -f k8s/deployment.yaml
kubectl get pods -w
kubectl get deployment

## Result
- API image was built successfully
- Image was loaded into minikube
- Deployment was created successfully
- 2 replicas were running in Kubernetes

## Notes
- Reusing the same image tag caused confusion during debugging
- Switching to a new tag (`week4b`) ensured minikube used the updated image
- MLflow Registry loading worked after:
  - copying `mlruns` into the image
  - setting `MLFLOW_TRACKING_URI=file:///app/mlruns`
  - setting `MLFLOW_REGISTRY_URI=file:///app/mlruns`
  
  
  
# Week4 Day3 - Service Exposure

## Commands
kubectl apply -f k8s/service.yaml
kubectl get svc
kubectl describe svc fastapi-ml
kubectl port-forward svc/fastapi-ml 8000:8000
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d '...'

## Result
- Service created successfully
- Service selected both running Pods
- API became accessible from host machine through port-forward
- /health and /predict were reachable

## Notes
- Service provides a stable endpoint instead of using Pod IP directly
- ClusterIP + port-forward is enough for local verification
- In production, traffic is typically exposed through Ingress or LoadBalancer

## Why not expose Pod IP directly?

Pod IPs cannot be used as stable endpoints for two main reasons:

1. Pod IPs are ephemeral. Pods can be recreated at any time, and their IP addresses may change.
2. Pod IPs are only reachable within the Kubernetes cluster network and are not accessible externally.

Therefore, a Service is required to provide a stable endpoint and load balancing across multiple Pods.


## Week4 Day4 Summary

Configured environment variables in Kubernetes Deployment and exposed deployment/model metadata via the `/version` API.  

Validated that the service behavior is configuration-driven (MODEL_URI, APP_VERSION, RELEASE_TRACK) rather than hardcoded.  

Resolved a Service selector issue and confirmed successful access through Kubernetes Service.


## Week4 Day5 Summary

Implemented readiness and liveness probes to distinguish between traffic readiness and container health.  

Configured rolling update strategy (`maxUnavailable=1`, `maxSurge=1`) to ensure controlled and low-downtime deployment.  

Verified that Kubernetes only routes traffic to ready Pods and automatically restarts unhealthy containers.  

Demonstrated a full rolling update by updating the image version and observing seamless traffic transition.

1. probe 区别
* readiness: controls whether a Pod can receive traffic
* liveness: controls whether a container should be restarted
2. rolling update 参数
* maxUnavailable=1: at most one Pod can be unavailable during update
* maxSurge=1: at most one extra Pod can be created during update
3. 结果
* rollout 成功
* /health 和 /version 更新后仍可访问
* 服务更新过程中保持可用



# Week4 Day6 - Failure Cases (Structured Analysis)

---

## Case 1: Health Check Failure (/health returns 500)

### 1️⃣ 现象（Symptoms）
Pod entered `CrashLoopBackOff` state  
`RESTARTS` count increased continuously  
Pod stayed at `READY 0/1`

---

### 2️⃣ 定位（Investigation）
```bash
kubectl get pods
kubectl logs <pod>
kubectl describe pod <pod>
```
Key findings:

Liveness probe failed: HTTP 500
Readiness probe failed
Container repeatedly restarted
###3️⃣ 原因（Root Cause）

/health endpoint returned HTTP 500, causing:

Readiness probe failure → Pod not ready
Liveness probe failure → container restart loop
###4️⃣ 恢复（Fix）
Restored /health endpoint to return HTTP 200
or
kubectl rollout undo deployment/fastapi-ml
###5️⃣ 结果（Result）

Pod returned to Running (1/1)
RESTARTS stopped increasing
Service recovered successfully

##Case 2: Missing Configuration (MODEL_URI / MODEL_PATH removed)
###1️⃣ 现象（Symptoms）

Pod failed to become ready (0/1)
Application failed to start properly
Eventually entered restart loop / CrashLoopBackOff

###2️⃣ 定位（Investigation）
```
kubectl get pods
kubectl logs <pod>
kubectl describe pod <pod>
````
Key findings:

Application startup errors in logs
Model loading failure
Probe failures following initialization failure
###3️⃣ 原因（Root Cause）

Required environment variables (MODEL_URI, MODEL_PATH) were missing, leading to:

Model initialization failure
Application not functioning correctly
Health check failure → probe failure
###4️⃣ 恢复（Fix）
Restored environment variables in deployment.yaml
or
kubectl rollout undo deployment/fastapi-ml --to-revision=8
###5️⃣ 结果（Result）

Application initialized successfully
Pod reached Running (1/1)
Service resumed normal operation


