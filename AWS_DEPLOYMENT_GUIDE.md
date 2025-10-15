# 🚀 Complete AWS Deployment Guide for Helpdesk Platform

## 📋 **Prerequisites**

### **Required Tools**
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Docker
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

### **AWS Account Setup**
1. Create AWS Account
2. Set up IAM user with required permissions
3. Configure AWS CLI credentials
4. Enable required AWS services

## 🏗️ **Step 1: Infrastructure Setup with Terraform**

### **1.1 Initialize Terraform**
```bash
cd aws-infrastructure/terraform

# Create terraform.tfvars file
cat > terraform.tfvars << EOF
aws_region = "us-west-2"
environment = "production"
cluster_name = "helpdesk-cluster"
db_password = "your-secure-db-password-here"
redis_auth_token = "your-secure-redis-token-here"
ssl_certificate_arn = "arn:aws:acm:us-west-2:YOUR-ACCOUNT:certificate/YOUR-CERT-ID"
domain_name = "your-domain.com"
EOF

# Initialize Terraform
terraform init

# Plan the infrastructure
terraform plan

# Apply the infrastructure
terraform apply
```

### **1.2 Configure AWS CLI**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (us-west-2)
# Enter your default output format (json)
```

## 🐳 **Step 2: Container Registry Setup**

### **2.1 Create ECR Repositories**
```bash
# Create repositories for each service
aws ecr create-repository --repository-name helpdesk-django --region us-west-2
aws ecr create-repository --repository-name helpdesk-ai --region us-west-2
aws ecr create-repository --repository-name helpdesk-realtime --region us-west-2

# Get login token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com
```

### **2.2 Build and Push Docker Images**
```bash
# Build Django application
cd core
docker build -t helpdesk-django .
docker tag helpdesk-django:latest YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-django:latest
docker push YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-django:latest

# Build AI service
cd ../ai-service
docker build -t helpdesk-ai .
docker tag helpdesk-ai:latest YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-ai:latest
docker push YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-ai:latest

# Build Realtime service
cd ../realtime-service
docker build -t helpdesk-realtime .
docker tag helpdesk-realtime:latest YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-realtime:latest
docker push YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-realtime:latest
```

## ☸️ **Step 3: Kubernetes Cluster Configuration**

### **3.1 Configure kubectl**
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name helpdesk-cluster

# Verify cluster connection
kubectl cluster-info
kubectl get nodes
```

### **3.2 Install AWS Load Balancer Controller**
```bash
# Install using Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=helpdesk-cluster \
  --set serviceAccount.create=false \
  --set region=us-west-2 \
  --set vpcId=$(terraform output -raw vpc_id)
```

### **3.3 Install Cluster Autoscaler**
```bash
# Create IAM policy for cluster autoscaler
cat > cluster-autoscaler-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "autoscaling:DescribeAutoScalingGroups",
                "autoscaling:DescribeAutoScalingInstances",
                "autoscaling:DescribeLaunchConfigurations",
                "autoscaling:DescribeTags",
                "autoscaling:SetDesiredCapacity",
                "autoscaling:TerminateInstanceInAutoScalingGroup",
                "ec2:DescribeLaunchTemplateVersions"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name AmazonEKSClusterAutoscalerPolicy \
    --policy-document file://cluster-autoscaler-policy.json

# Attach policy to node group role
aws iam attach-role-policy \
    --policy-arn arn:aws:iam::YOUR-ACCOUNT-ID:policy/AmazonEKSClusterAutoscalerPolicy \
    --role-name helpdesk-cluster-nodegroup-NodeInstanceRole-XXXXXXXXX
```

## 🔐 **Step 4: Security Configuration**

### **4.1 Create Secrets**
```bash
# Create secrets file
cat > k8s-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: helpdesk-secrets
  namespace: helpdesk
type: Opaque
data:
  SECRET_KEY: $(echo -n 'your-django-secret-key' | base64)
  DB_PASSWORD: $(echo -n 'your-db-password' | base64)
  REDIS_AUTH_TOKEN: $(echo -n 'your-redis-token' | base64)
  EMAIL_HOST_USER: $(echo -n 'your-email-user' | base64)
  EMAIL_HOST_PASSWORD: $(echo -n 'your-email-password' | base64)
  OPENAI_API_KEY: $(echo -n 'your-openai-key' | base64)
  ANTHROPIC_API_KEY: $(echo -n 'your-anthropic-key' | base64)
  AWS_ACCESS_KEY_ID: $(echo -n 'your-aws-access-key' | base64)
  AWS_SECRET_ACCESS_KEY: $(echo -n 'your-aws-secret-key' | base64)
  AWS_STORAGE_BUCKET_NAME: $(echo -n 'your-s3-bucket-name' | base64)
EOF
```

### **4.2 Update Configuration**
```bash
# Update ConfigMap with your actual values
sed -i 's/your-rds-endpoint.amazonaws.com/ACTUAL-RDS-ENDPOINT/g' aws-infrastructure/k8s/configmap.yaml
sed -i 's/your-redis-endpoint.cache.amazonaws.com/ACTUAL-REDIS-ENDPOINT/g' aws-infrastructure/k8s/configmap.yaml
sed -i 's/your-domain.com/ACTUAL-DOMAIN/g' aws-infrastructure/k8s/configmap.yaml
```

## 🚀 **Step 5: Deploy Application**

### **5.1 Deploy Kubernetes Resources**
```bash
# Create namespace
kubectl apply -f aws-infrastructure/k8s/namespace.yaml

# Deploy configuration
kubectl apply -f aws-infrastructure/k8s/configmap.yaml
kubectl apply -f k8s-secrets.yaml

# Deploy services
kubectl apply -f aws-infrastructure/k8s/django-deployment.yaml
kubectl apply -f aws-infrastructure/k8s/ai-service-deployment.yaml
kubectl apply -f aws-infrastructure/k8s/realtime-service-deployment.yaml
kubectl apply -f aws-infrastructure/k8s/celery-deployment.yaml

# Deploy ingress
kubectl apply -f aws-infrastructure/k8s/ingress.yaml
```

### **5.2 Wait for Deployments**
```bash
# Check deployment status
kubectl get pods -n helpdesk
kubectl get services -n helpdesk
kubectl get ingress -n helpdesk

# Wait for all deployments to be ready
kubectl rollout status deployment/django-app -n helpdesk --timeout=300s
kubectl rollout status deployment/ai-service -n helpdesk --timeout=300s
kubectl rollout status deployment/realtime-service -n helpdesk --timeout=300s
kubectl rollout status deployment/celery-worker -n helpdesk --timeout=300s
kubectl rollout status deployment/celery-beat -n helpdesk --timeout=300s
```

### **5.3 Run Database Migrations**
```bash
# Run migrations
kubectl exec -n helpdesk deployment/django-app -- python manage.py migrate

# Create superuser
kubectl exec -n helpdesk deployment/django-app -- python manage.py createsuperuser

# Collect static files
kubectl exec -n helpdesk deployment/django-app -- python manage.py collectstatic --noinput
```

## 📊 **Step 6: Monitoring Setup**

### **6.1 Install Prometheus and Grafana**
```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values aws-infrastructure/monitoring/prometheus-values.yaml

# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword=helpdesk-admin-2024 \
  --set persistence.enabled=true \
  --set persistence.size=10Gi
```

### **6.2 Configure Alerting**
```bash
# Apply AlertManager configuration
kubectl apply -f aws-infrastructure/monitoring/alertmanager-config.yaml

# Create notification channels
kubectl create secret generic grafana-notification-channels \
  --from-literal=slack-webhook-url=YOUR_SLACK_WEBHOOK_URL \
  --from-literal=email-smtp-host=smtp.amazonaws.com \
  --from-literal=email-smtp-user=YOUR_EMAIL_USER \
  --from-literal=email-smtp-password=YOUR_EMAIL_PASSWORD
```

## 🔒 **Step 7: Security Hardening**

### **7.1 Apply Security Policies**
```bash
# Apply network policies
kubectl apply -f aws-infrastructure/security/security-policies.yaml

# Apply AWS security configuration
kubectl apply -f aws-infrastructure/security/aws-security-config.yaml
```

### **7.2 SSL Certificate Setup**
```bash
# Request SSL certificate (if not already done)
aws acm request-certificate \
  --domain-name your-domain.com \
  --subject-alternative-names "*.your-domain.com" \
  --validation-method DNS \
  --region us-west-2

# Update ingress with certificate ARN
kubectl patch ingress helpdesk-ingress -n helpdesk -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/certificate-arn":"arn:aws:acm:us-west-2:YOUR-ACCOUNT:certificate/YOUR-CERT-ID"}}}'
```

## 💰 **Step 8: Cost Optimization**

### **8.1 Implement Auto Scaling**
```bash
# Apply HPA configuration
kubectl apply -f - << EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: django-hpa
  namespace: helpdesk
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: django-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
EOF
```

### **8.2 Set up Cost Monitoring**
```bash
# Create AWS Budget
aws budgets create-budget \
  --account-id YOUR-ACCOUNT-ID \
  --budget '{
    "BudgetName": "Helpdesk-Platform-Budget",
    "BudgetLimit": {
      "Amount": "500",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

## 🧪 **Step 9: Testing and Validation**

### **9.1 Health Checks**
```bash
# Check application health
kubectl get pods -n helpdesk
kubectl logs -n helpdesk deployment/django-app
kubectl logs -n helpdesk deployment/ai-service
kubectl logs -n helpdesk deployment/realtime-service

# Test endpoints
curl -f http://YOUR-ALB-DNS/health/
curl -f http://YOUR-ALB-DNS/api/health/
```

### **9.2 Load Testing**
```bash
# Install hey for load testing
go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 http://YOUR-ALB-DNS/
```

## 📈 **Step 10: Production Optimization**

### **10.1 Performance Tuning**
```bash
# Optimize Django settings
kubectl exec -n helpdesk deployment/django-app -- python manage.py check --deploy

# Enable database connection pooling
kubectl patch deployment django-app -n helpdesk -p '{"spec":{"template":{"spec":{"containers":[{"name":"django","env":[{"name":"DATABASE_CONN_MAX_AGE","value":"600"}]}]}}}}'
```

### **10.2 Backup Configuration**
```bash
# Set up automated backups
kubectl apply -f - << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: helpdesk
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h \$DB_HOST -U \$DB_USER -d \$DB_NAME > /backup/backup_\$(date +%Y%m%d_%H%M%S).sql
              aws s3 cp /backup/ s3://your-backup-bucket/ --recursive
            env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: helpdesk-config
                  key: DB_HOST
            - name: DB_USER
              valueFrom:
                configMapKeyRef:
                  name: helpdesk-config
                  key: DB_USER
            - name: DB_NAME
              valueFrom:
                configMapKeyRef:
                  name: helpdesk-config
                  key: DB_NAME
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: helpdesk-secrets
                  key: DB_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
EOF
```

## 🔧 **Step 11: Maintenance and Updates**

### **11.1 Rolling Updates**
```bash
# Update application
kubectl set image deployment/django-app django=YOUR-ACCOUNT-ID.dkr.ecr.us-west-2.amazonaws.com/helpdesk-django:new-tag -n helpdesk

# Monitor rollout
kubectl rollout status deployment/django-app -n helpdesk
```

### **11.2 Scaling Operations**
```bash
# Scale up/down
kubectl scale deployment django-app --replicas=5 -n helpdesk
kubectl scale deployment celery-worker --replicas=3 -n helpdesk
```

## 📋 **Step 12: Troubleshooting**

### **Common Issues and Solutions**

#### **Issue: Pods not starting**
```bash
# Check pod status
kubectl describe pod POD_NAME -n helpdesk
kubectl logs POD_NAME -n helpdesk

# Check resource limits
kubectl top pods -n helpdesk
```

#### **Issue: Database connection failed**
```bash
# Check database connectivity
kubectl exec -n helpdesk deployment/django-app -- python manage.py dbshell

# Check security groups
aws ec2 describe-security-groups --group-ids sg-XXXXXXXXX
```

#### **Issue: Load balancer not working**
```bash
# Check ingress status
kubectl describe ingress helpdesk-ingress -n helpdesk

# Check AWS Load Balancer Controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

## 📊 **Monitoring and Alerts**

### **Access Monitoring Dashboards**
```bash
# Get Grafana admin password
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward to access Grafana
kubectl port-forward --namespace monitoring svc/grafana 3000:80

# Access Prometheus
kubectl port-forward --namespace monitoring svc/prometheus-server 9090:80
```

## 🎯 **Final Checklist**

- [ ] Infrastructure deployed with Terraform
- [ ] EKS cluster running and accessible
- [ ] All Docker images pushed to ECR
- [ ] Kubernetes deployments running
- [ ] Database migrations completed
- [ ] SSL certificate configured
- [ ] Monitoring and alerting set up
- [ ] Security policies applied
- [ ] Cost optimization implemented
- [ ] Load testing completed
- [ ] Backup strategy configured
- [ ] Documentation updated

## 📞 **Support and Maintenance**

### **Regular Maintenance Tasks**
1. **Weekly**: Check resource utilization and costs
2. **Monthly**: Review security policies and updates
3. **Quarterly**: Performance optimization and capacity planning
4. **Annually**: Disaster recovery testing

### **Emergency Procedures**
1. **Service Down**: Check pod status and logs
2. **Database Issues**: Check RDS status and connections
3. **High Costs**: Review resource usage and scaling
4. **Security Breach**: Follow incident response procedures

## 💡 **Pro Tips**

1. **Use AWS Cost Explorer** to monitor spending
2. **Set up CloudWatch alarms** for critical metrics
3. **Implement blue-green deployments** for zero-downtime updates
4. **Use AWS Systems Manager** for patch management
5. **Enable AWS Config** for compliance monitoring

---

## 🚀 **Quick Start Commands**

```bash
# Complete deployment in one go
cd aws-infrastructure
terraform init && terraform apply
aws eks update-kubeconfig --region us-west-2 --name helpdesk-cluster
kubectl apply -f k8s/
kubectl rollout status deployment/django-app -n helpdesk
```

Your helpdesk platform is now running on AWS with enterprise-grade infrastructure! 🎉
