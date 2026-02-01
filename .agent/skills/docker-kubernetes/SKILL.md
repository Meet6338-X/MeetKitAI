---
name: docker-kubernetes
description: Docker and Kubernetes patterns. Container best practices, K8s deployments, Helm charts, service mesh.
---

# Docker & Kubernetes Skill

Container orchestration patterns for production-grade deployments.

## When to Use
- Containerizing applications
- Designing Kubernetes deployments
- Setting up CI/CD pipelines
- Implementing service mesh
- Managing stateful applications

## Docker Best Practices

### 1. Dockerfile Optimization

```dockerfile
# Multi-stage build for smaller images
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS runner
WORKDIR /app
# Don't run as root
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .
USER nodejs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Key Principles:**
- Use specific tags, not `latest`
- Multi-stage builds for smaller images
- Order layers by change frequency
- Use `.dockerignore`
- Never run as root
- One process per container

### 2. Docker Compose for Development

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://postgres:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app
      - /app/node_modules
  
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## Kubernetes Patterns

### 3. Deployment Structure

```
k8s/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── prod/
│       ├── kustomization.yaml
│       └── hpa.yaml
└── helm/
    └── my-app/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
```

### 4. Production-Ready Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: my-app
          image: my-app:1.0.0
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
```

### 5. Service & Ingress

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 3000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - app.example.com
      secretName: app-tls
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

### 6. Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 7. Helm Chart Values

```yaml
# values.yaml
replicaCount: 3

image:
  repository: my-app
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 500m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

### 8. Common Debugging Commands

```bash
# Logs
kubectl logs -f deployment/my-app --all-containers
kubectl logs -f my-pod -c container-name --previous

# Debug
kubectl describe pod my-pod
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl exec -it my-pod -- /bin/sh

# Resource usage
kubectl top pods
kubectl top nodes

# Network debugging
kubectl run debug --image=busybox -it --rm -- wget -qO- http://my-service
```

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max

- name: Deploy to Kubernetes
  run: |
    kubectl set image deployment/my-app my-app=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    kubectl rollout status deployment/my-app
```
