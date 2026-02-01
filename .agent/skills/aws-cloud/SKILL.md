---
name: aws-cloud
description: AWS Cloud architecture patterns. EC2, Lambda, S3, DynamoDB, CloudFormation, IAM best practices.
---

# AWS Cloud Skill

AWS architecture patterns and best practices for building scalable, secure cloud applications.

## When to Use
- Designing AWS infrastructure
- Choosing between EC2, Lambda, ECS, EKS
- Implementing serverless architectures
- Setting up CI/CD with AWS
- Managing IAM policies and security

## Core Principles

### 1. Well-Architected Framework

Apply the 6 pillars:
1. **Operational Excellence** - Automate everything, IaC
2. **Security** - Least privilege, encryption at rest/transit
3. **Reliability** - Multi-AZ, auto-scaling, backups
4. **Performance** - Right-sizing, caching, CDN
5. **Cost Optimization** - Reserved instances, spot, right-sizing
6. **Sustainability** - Efficient resource usage

### 2. Compute Decision Matrix

| Workload | Service | Why |
|----------|---------|-----|
| Stateless, event-driven | Lambda | Pay per invocation |
| Containers, microservices | ECS/Fargate | Managed containers |
| Kubernetes required | EKS | K8s compatibility |
| Full control needed | EC2 | Maximum flexibility |
| Batch processing | Batch | Cost-effective batch |

### 3. Database Selection

| Need | Service |
|------|---------|
| Relational, complex queries | RDS (PostgreSQL/MySQL) |
| Key-value, high throughput | DynamoDB |
| In-memory caching | ElastiCache |
| Document store | DocumentDB |
| Graph relationships | Neptune |
| Time-series | Timestream |

### 4. Serverless Patterns

```
API Gateway → Lambda → DynamoDB
     ↓
   Cognito (Auth)
     ↓
   S3 (Static assets via CloudFront)
```

**Lambda Best Practices:**
- Keep functions focused (single responsibility)
- Minimize cold starts (provisioned concurrency for critical paths)
- Use layers for shared code
- Set appropriate memory (CPU scales with memory)
- Implement proper error handling and retries

### 5. Infrastructure as Code

**CloudFormation/CDK Structure:**
```
infrastructure/
├── lib/
│   ├── vpc-stack.ts
│   ├── database-stack.ts
│   ├── api-stack.ts
│   └── monitoring-stack.ts
├── bin/
│   └── app.ts
└── cdk.json
```

**Terraform Alternative:**
```hcl
# Use modules for reusability
module "vpc" {
  source = "./modules/vpc"
  cidr   = var.vpc_cidr
}
```

### 6. Security Essentials

**IAM Best Practices:**
- Never use root account
- Enable MFA everywhere
- Use roles, not long-lived credentials
- Apply least privilege
- Use AWS Organizations for multi-account

**Network Security:**
- VPC with public/private subnets
- Security groups (stateful) + NACLs (stateless)
- VPC endpoints for AWS services
- WAF for API Gateway/CloudFront

### 7. Cost Optimization

| Strategy | Savings |
|----------|---------|
| Reserved Instances (1yr) | ~40% |
| Reserved Instances (3yr) | ~60% |
| Spot Instances | Up to 90% |
| Savings Plans | ~30-50% |
| Right-sizing | 20-50% |

**Cost Monitoring:**
- Enable Cost Explorer
- Set billing alerts
- Use AWS Budgets
- Tag everything for cost allocation

### 8. Monitoring & Observability

**Essential Setup:**
```
CloudWatch Logs → CloudWatch Metrics → CloudWatch Alarms → SNS → Slack/PagerDuty
                                                              ↓
                                                        Lambda (auto-remediation)
```

**Key Metrics to Monitor:**
- Lambda: Duration, Errors, Throttles, ConcurrentExecutions
- API Gateway: 4xx/5xx errors, Latency, Count
- DynamoDB: ConsumedReadCapacity, ThrottledRequests
- RDS: CPUUtilization, FreeableMemory, ReadLatency

## Common Architectures

### Serverless Web App
```
Route 53 → CloudFront → S3 (React app)
                    ↓
              API Gateway → Lambda → DynamoDB
                    ↓
                 Cognito
```

### Containerized Microservices
```
ALB → ECS Fargate (Service A)
  ↓        ↓
       RDS Aurora
  
ECS Fargate (Service B) → SQS → Lambda → S3
```

### Event-Driven Processing
```
S3 Upload → EventBridge → Step Functions
                              ↓
                    Lambda (Process) → SNS
                              ↓
                    Lambda (Store) → DynamoDB
```
