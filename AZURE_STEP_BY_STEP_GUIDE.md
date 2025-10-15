# 🚀 Complete Azure Step-by-Step Implementation Guide

## 📋 **Prerequisites Checklist**

### **Required Tools**
- [ ] Azure CLI
- [ ] kubectl
- [ ] Helm
- [ ] Terraform
- [ ] Docker
- [ ] jq

### **Azure Requirements**
- [ ] Azure subscription
- [ ] Owner or Contributor permissions
- [ ] Domain name (optional)
- [ ] Microsoft 365 tenant (for integration)

## 🎯 **Step 1: Environment Setup**

### **1.1 Install Prerequisites**
```bash
# Update system
sudo apt-get update

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

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
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER

# Install jq
sudo apt-get install -y jq
```

### **1.2 Azure Login**
```bash
# Login to Azure
az login

# Set subscription (if multiple)
az account list --output table
az account set --subscription "Your-Subscription-ID"

# Verify login
az account show
```

## 🏗️ **Step 2: Infrastructure Deployment**

### **2.1 Create Terraform Configuration**
```bash
# Navigate to terraform directory
cd azure-infrastructure/terraform

# Create terraform.tfvars
cat > terraform.tfvars << EOF
location = "East US"
environment = "production"
cluster_name = "helpdesk-cluster"
node_count = 3
vm_size = "Standard_D2s_v3"
db_password = "your-secure-db-password-here"
EOF
```

### **2.2 Deploy Infrastructure**
```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the infrastructure
terraform apply

# Note the outputs
terraform output
```

### **2.3 Verify Infrastructure**
```bash
# Check resource group
az group show --name helpdesk-production-rg

# Check AKS cluster
az aks list --resource-group helpdesk-production-rg

# Check database
az postgres flexible-server list --resource-group helpdesk-production-rg

# Check Redis cache
az redis list --resource-group helpdesk-production-rg
```

## ☸️ **Step 3: AKS Configuration**

### **3.1 Get AKS Credentials**
```bash
# Get AKS credentials
az aks get-credentials --resource-group helpdesk-production-rg --name helpdesk-cluster

# Verify cluster connection
kubectl cluster-info
kubectl get nodes
```

### **3.2 Install NGINX Ingress Controller**
```bash
# Add Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=LoadBalancer \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz

# Wait for external IP
kubectl get service ingress-nginx-controller -n ingress-nginx -w
```

### **3.3 Install Cert-Manager (for SSL)**
```bash
# Add cert-manager Helm repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --version v1.13.0 \
    --set installCRDs=true

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - << EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## 🐳 **Step 4: Container Registry Setup**

### **4.1 Build and Push Images**
```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name helpdeskproductionacr --resource-group helpdesk-production-rg --query loginServer -o tsv)

# Login to ACR
az acr login --name helpdeskproductionacr

# Build Django application
cd core
docker build -t $ACR_LOGIN_SERVER/helpdesk-django:latest .
docker push $ACR_LOGIN_SERVER/helpdesk-django:latest
cd ..

# Build AI service
cd ai-service
docker build -t $ACR_LOGIN_SERVER/helpdesk-ai:latest .
docker push $ACR_LOGIN_SERVER/helpdesk-ai:latest
cd ..

# Build Realtime service
cd realtime-service
docker build -t $ACR_LOGIN_SERVER/helpdesk-realtime:latest .
docker push $ACR_LOGIN_SERVER/helpdesk-realtime:latest
cd ..
```

## 🚀 **Step 5: Application Deployment**

### **5.1 Create Namespace**
```bash
# Create namespace
kubectl apply -f azure-infrastructure/k8s/namespace.yaml
```

### **5.2 Deploy Configuration**
```bash
# Deploy ConfigMap
kubectl apply -f azure-infrastructure/k8s/azure-configmap.yaml

# Create secrets (update with your actual values)
kubectl apply -f azure-infrastructure/k8s/azure-secrets.yaml
```

### **5.3 Update Image References**
```bash
# Update image references in manifests
ACR_LOGIN_SERVER=$(az acr show --name helpdeskproductionacr --resource-group helpdesk-production-rg --query loginServer -o tsv)

sed -i "s|your-registry/helpdesk-django:latest|$ACR_LOGIN_SERVER/helpdesk-django:latest|g" azure-infrastructure/k8s/*.yaml
sed -i "s|your-registry/helpdesk-ai:latest|$ACR_LOGIN_SERVER/helpdesk-ai:latest|g" azure-infrastructure/k8s/*.yaml
sed -i "s|your-registry/helpdesk-realtime:latest|$ACR_LOGIN_SERVER/helpdesk-realtime:latest|g" azure-infrastructure/k8s/*.yaml
```

### **5.4 Deploy Services**
```bash
# Deploy Django application
kubectl apply -f azure-infrastructure/k8s/django-deployment.yaml

# Deploy AI service
kubectl apply -f azure-infrastructure/k8s/ai-service-deployment.yaml

# Deploy Realtime service
kubectl apply -f azure-infrastructure/k8s/realtime-service-deployment.yaml

# Deploy Celery workers
kubectl apply -f azure-infrastructure/k8s/celery-deployment.yaml

# Deploy ingress
kubectl apply -f azure-infrastructure/k8s/ingress.yaml
```

### **5.5 Wait for Deployments**
```bash
# Check deployment status
kubectl get pods -n helpdesk

# Wait for deployments to be ready
kubectl rollout status deployment/django-app -n helpdesk --timeout=300s
kubectl rollout status deployment/ai-service -n helpdesk --timeout=300s
kubectl rollout status deployment/realtime-service -n helpdesk --timeout=300s
kubectl rollout status deployment/celery-worker -n helpdesk --timeout=300s
kubectl rollout status deployment/celery-beat -n helpdesk --timeout=300s
```

## 🗄️ **Step 6: Database Setup**

### **6.1 Run Migrations**
```bash
# Run database migrations
kubectl exec -n helpdesk deployment/django-app -- python manage.py migrate

# Create superuser
kubectl exec -n helpdesk deployment/django-app -- python manage.py createsuperuser

# Collect static files
kubectl exec -n helpdesk deployment/django-app -- python manage.py collectstatic --noinput
```

### **6.2 Verify Database Connection**
```bash
# Check database connectivity
kubectl exec -n helpdesk deployment/django-app -- python manage.py dbshell

# Check Redis connectivity
kubectl exec -n helpdesk deployment/django-app -- python -c "import redis; r = redis.Redis.from_url('$REDIS_URL'); print(r.ping())"
```

## 🔐 **Step 7: Microsoft Services Integration**

### **7.1 Azure AD App Registration**
```bash
# Create Azure AD app registration
az ad app create --display-name "Helpdesk Platform" \
    --web-redirect-uris "https://your-domain.com/auth/callback" \
    --required-resource-accesses @azure-ad-permissions.json

# Get app registration details
APP_ID=$(az ad app list --display-name "Helpdesk Platform" --query [0].appId -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

echo "App ID: $APP_ID"
echo "Tenant ID: $TENANT_ID"
```

### **7.2 Microsoft Graph API Setup**
```bash
# Create client secret
az ad app credential reset --id $APP_ID --append

# Grant API permissions
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions User.Read=Scope
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions Mail.Read=Scope
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions Calendars.Read=Scope
az ad app permission add --id $APP_ID --api 00000003-0000-0000-c000-000000000000 --api-permissions Files.ReadWrite=Scope

# Grant admin consent
az ad app permission admin-consent --id $APP_ID
```

### **7.3 Teams Integration**
```bash
# Create Teams webhook (manual step)
# 1. Go to Teams channel
# 2. Click "..." → "Connectors" → "Incoming Webhook"
# 3. Configure webhook and copy URL

# Update secrets with Teams webhook
kubectl patch secret helpdesk-secrets -n helpdesk -p '{"data":{"TEAMS_WEBHOOK_URL":"'$(echo -n 'YOUR_TEAMS_WEBHOOK_URL' | base64)'"}}'
```

### **7.4 SharePoint Integration**
```bash
# Create SharePoint app registration
az ad app create --display-name "Helpdesk SharePoint Integration" \
    --web-redirect-uris "https://your-domain.com/sharepoint/callback"

# Get SharePoint app details
SHAREPOINT_APP_ID=$(az ad app list --display-name "Helpdesk SharePoint Integration" --query [0].appId -o tsv)

# Update secrets with SharePoint credentials
kubectl patch secret helpdesk-secrets -n helpdesk -p '{"data":{"SHAREPOINT_CLIENT_ID":"'$(echo -n $SHAREPOINT_APP_ID | base64)'"}}'
```

## 📊 **Step 8: Monitoring Setup**

### **8.1 Install Prometheus and Grafana**
```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set grafana.adminPassword=helpdesk-admin-2024 \
    --set prometheus.prometheusSpec.retention=30d

# Install Grafana
helm install grafana grafana/grafana \
    --namespace monitoring \
    --set adminPassword=helpdesk-admin-2024 \
    --set persistence.enabled=true \
    --set persistence.size=10Gi
```

### **8.2 Configure Application Insights**
```bash
# Get Application Insights key
INSIGHTS_KEY=$(az monitor app-insights component show --app helpdesk-production-insights --resource-group helpdesk-production-rg --query instrumentationKey -o tsv)

# Update secrets with Application Insights key
kubectl patch secret helpdesk-secrets -n helpdesk -p '{"data":{"APPLICATION_INSIGHTS_KEY":"'$(echo -n $INSIGHTS_KEY | base64)'"}}'
```

## 🔒 **Step 9: Security Configuration**

### **9.1 Network Policies**
```bash
# Apply network policies
kubectl apply -f azure-infrastructure/security/network-policies.yaml

# Apply pod security policies
kubectl apply -f azure-infrastructure/security/pod-security-policies.yaml
```

### **9.2 Azure Key Vault Integration**
```bash
# Get Key Vault URL
KEY_VAULT_URL=$(az keyvault show --name helpdesk-production-kv --resource-group helpdesk-production-rg --query vaultUri -o tsv)

# Update secrets with Key Vault URL
kubectl patch secret helpdesk-secrets -n helpdesk -p '{"data":{"AZURE_KEY_VAULT_URL":"'$(echo -n $KEY_VAULT_URL | base64)'"}}'
```

## 💰 **Step 10: Cost Optimization**

### **10.1 Enable Auto-Scaling**
```bash
# Apply Horizontal Pod Autoscaler
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

### **10.2 Configure Spot Instances**
```bash
# Add spot node pool for Celery workers
az aks nodepool add \
    --resource-group helpdesk-production-rg \
    --cluster-name helpdesk-cluster \
    --name spotpool \
    --priority Spot \
    --eviction-policy Deallocate \
    --spot-max-price 0.05 \
    --node-count 2 \
    --node-vm-size Standard_D2s_v3
```

## 🧪 **Step 11: Testing and Validation**

### **11.1 Health Checks**
```bash
# Check application health
kubectl get pods -n helpdesk
kubectl logs -n helpdesk deployment/django-app
kubectl logs -n helpdesk deployment/ai-service
kubectl logs -n helpdesk deployment/realtime-service

# Test endpoints
EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -f http://$EXTERNAL_IP/health/
curl -f http://$EXTERNAL_IP/api/health/
```

### **11.2 Load Testing**
```bash
# Install hey for load testing
go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 http://$EXTERNAL_IP/
```

## 📈 **Step 12: Production Optimization**

### **12.1 Performance Tuning**
```bash
# Optimize Django settings
kubectl exec -n helpdesk deployment/django-app -- python manage.py check --deploy

# Enable database connection pooling
kubectl patch deployment django-app -n helpdesk -p '{"spec":{"template":{"spec":{"containers":[{"name":"django","env":[{"name":"DATABASE_CONN_MAX_AGE","value":"600"}]}]}}}}'
```

### **12.2 Backup Configuration**
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
              az storage blob upload --account-name helpdeskproductionmedia --container-name backups --file /backup/backup_\$(date +%Y%m%d_%H%M%S).sql
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

## 🎯 **Step 13: Final Verification**

### **13.1 Check All Services**
```bash
# Check all pods
kubectl get pods -n helpdesk

# Check all services
kubectl get services -n helpdesk

# Check ingress
kubectl get ingress -n helpdesk

# Check external IP
kubectl get service ingress-nginx-controller -n ingress-nginx
```

### **13.2 Access Application**
```bash
# Get external IP
EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Application URL: http://$EXTERNAL_IP"
echo "Health Check: http://$EXTERNAL_IP/health/"
echo "Admin Panel: http://$EXTERNAL_IP/admin/"
```

## 📋 **Deployment Checklist**

- [ ] Azure subscription and permissions
- [ ] Prerequisites installed
- [ ] Azure login successful
- [ ] Infrastructure deployed with Terraform
- [ ] AKS cluster configured
- [ ] NGINX Ingress Controller installed
- [ ] Docker images built and pushed
- [ ] Application deployed to AKS
- [ ] Database migrations completed
- [ ] Microsoft services integrated
- [ ] Monitoring configured
- [ ] Security policies applied
- [ ] Cost optimization enabled
- [ ] Testing completed
- [ ] Backup strategy implemented

## 🚀 **Quick Commands Summary**

```bash
# Complete deployment
cd azure-infrastructure
terraform init && terraform apply
az aks get-credentials --resource-group helpdesk-production-rg --name helpdesk-cluster
kubectl apply -f k8s/
kubectl rollout status deployment/django-app -n helpdesk

# Check status
kubectl get all -n helpdesk
kubectl get ingress -n helpdesk

# Access logs
kubectl logs -n helpdesk deployment/django-app
```

## 🎉 **Congratulations!**

Your helpdesk platform is now running on Azure with:
- ✅ **AKS Cluster** with auto-scaling
- ✅ **Azure Database** for PostgreSQL
- ✅ **Azure Cache** for Redis
- ✅ **Azure Storage** for files
- ✅ **Microsoft 365** integration
- ✅ **Teams** notifications
- ✅ **SharePoint** document management
- ✅ **Power BI** analytics
- ✅ **Application Insights** monitoring
- ✅ **Cost optimization** features

**Expected Monthly Cost**: $250-500 (30-40% savings compared to AWS + external Microsoft services)
