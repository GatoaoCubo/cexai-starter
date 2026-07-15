---
id: p01_kc_container_deployment_llm
kind: knowledge_card
8f: F3_inject
title: "Container Deployment for LLM Apps"
version: 1.0.0
quality: null
tldr: "Defensive knowledge card derived from the kc-container-deployment-llm skill -- typed for unclassified detection, scoped to authorized use, framework-aligned to its NIST CSF controls."
when_to_use: "Consult to understand the unclassified control defensively before you build, configure, or audit it."
long_tails:
  - "what is the kc-container-deployment-llm defensive control"
  - "how does kc-container-deployment-llm detection work"
  - "reference card for the kc-container-deployment-llm skill"
primary_8f: INJECT
slots:
  AUTHORIZED_SCOPE: "<authorized asset/log source under analysis>"
  CONTROL_FOCUS: "<NIST CSF control to prioritize this run>"
  TIME_WINDOW: "<bounded analysis window>"
pillar: P01
language: en
keywords:
  - "from golang:1.20 as builder"
  - "--gpus all"
  - "nvidia/cuda:12.1.0"
  - "resources: { limits: { memory: \"4gi\" } }"
  - "bash curl -i http://localhost:8000/health"
  - "expected response:"
  - "## autoscaling setup"
  - "container deployment"
  - "key concepts"
  - "model serving"
related:
  - p01_kc_kubernetes_ai_requirement
  - p01_kc_docker_ai_containerization
  - p01_kc_ollama_deployment_guide
  - bld_knowledge_card_search_strategy
  - kc_test_ollama_wrapper
  - bld_output_template_search_strategy
  - bld_knowledge_card_usage_quota
---

# Container Deployment for LLM Applications

## Key Concepts
- **Docker**: Package models and dependencies into portable containers
- **Kubernetes**: Orchestrate containerized workloads at scale
- **GPU Scheduling**: Optimize resource allocation for compute-intensive tasks
- **Model Serving**: Deploy inference pipelines with vLLM, TGI, or Ollama
- **Health Checks**: Monitor service availability and auto-restart failed containers
- **Autoscaling**: Dynamically adjust resources based on workload demand

## Docker Best Practices
| Practice | Description | Example | Benefit |
|---------|-------------|---------|---------|
| Multi-stage builds | Reduce image size by separating build and runtime stages | `FROM golang:1.20 AS builder` | Smaller production images |
| GPU device plugin | Enable GPU access in containers | `--gpus all` flag | Utilize GPU resources |
| Base image selection | Use optimized base images | `nvidia/cuda:12.1.0` | Pre-installed CUDA libraries |
| Resource limits | Define memory and CPU limits | `resources: { limits: { memory: "4Gi" } }` | Prevent resource starvation |
| Image scanning | Detect vulnerabilities in container images | Trivy or Clair tools | Improve security posture |

## Kubernetes Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm
  template:
    metadata:
      labels:
        app: llm
    spec:
      containers:
      - name: llm-container
        image: your-llm-image:latest
        resources:
          limits:
            nvidia.com/gpu: 1
```

## Model Serving Options
| Framework | Features | Use Case | Throughput (QPS) | Latency (ms) |
|----------|----------|----------|------------------|--------------|
| vLLM     | High-throughput inference | Production-scale deployments | 100,000+ | 1-5 |
| TGI      | Text generation inference | Chatbots and conversational AI | 50,000 | 5-10 |
| Ollama   | Local model serving | Development and testing | 10,000 | 10-20 |
| TorchServe | Model serving with PyTorch | Research and prototyping | 20,000 | 5-15 |
| HuggingFace Transformers | Easy model deployment | NLP tasks | 30,000 | 8-12 |

## Health Check Implementation
```bash
curl -I http://localhost:8000/health
```
Expected response:
```
HTTP/1.1 200 OK
Content-Type: application/json
{"status": "healthy", "timestamp": "2023-10-05T14:30:00Z"}
```

## Autoscaling Setup
```hcl
resource "kubernetes_horizontal_pod_autoscaler" "llm_scaler" {
  metadata {
    name = "llm-autoscaler"
  }
  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind       = "Deployment"
      name       = "llm-service"
    }
    min_replicas = 1
    max_replicas = 10
    target_cpu_utilization_percentage = 80
  }
}
```

## Monitoring Stack
| Tool | Purpose | Integration | Example Query |
|-----|---------|-------------|---------------|
| Prometheus | Metrics collection | Kubernetes | `container_cpu_usage_seconds_total` |
| Grafana | Visualization | Prometheus | CPU usage dashboard |
| Alertmanager | Incident management | Prometheus | CPU threshold alerts |
| Loki | Log aggregation | Kubernetes | `container_log_line` |
| Tempo | Distributed tracing | OpenTelemetry | Request latency traces |

## Security Considerations
- **GPU-specific security contexts**: Restrict GPU access to authorized containers only
- **Network policies**: Implement Calico or Cilium policies to control container communication
- **Secret management**: Use Kubernetes Secrets or HashiCorp Vault for API key storage
- **Image scanning**: Regularly scan images with Clair or Trivy for vulnerabilities
- **Resource limits**: Set strict limits on CPU, memory, and GPU usage to prevent abuse

## Related Kinds
- **kc_model_serving**: Focuses on deploying models via frameworks like vLLM, TGI, and Ollama
- **kc_kubernetes_ops**: Covers Kubernetes orchestration, including deployments and autoscaling
- **kc_gpu_optimization**: Deals with GPU resource allocation, scheduling, and performance tuning
- **kc_ci_cd_pipeline**: Involves CI/CD processes for containerized applications
- **kc_security_best_practices**: Includes security measures for container environments

## Boundary

Static, versioned distilled knowledge. Not instruction, template, or configuration.


Canonical baseline: the source skill bundle. The 8F verb is **INJECT** (F3): this
card injects defensive domain knowledge into downstream reasoning. Specific framework
controls are taken from the source bundle, not invented here.

### How to use
```text
8F verb: INJECT (F3). Read this card into context before acting on the control.
Use it to fix the vocabulary and the in-scope controls, not as an attack guide.
Verify any framework control you cite appears in the source bundle (anti-fab).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_kubernetes_ai_requirement | sibling | 0.43 |
| p01_kc_docker_ai_containerization | sibling | 0.36 |
| [[p01_kc_ollama_deployment_guide]] | sibling | 0.25 |
| bld_knowledge_card_search_strategy | sibling | 0.23 |
| kc_test_ollama_wrapper | related | 0.20 |
| bld_output_template_search_strategy | downstream | 0.20 |
| bld_knowledge_card_usage_quota | sibling | 0.19 |