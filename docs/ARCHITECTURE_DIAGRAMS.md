# 📐 SampleMind AI - Architecture Diagrams

**Version:** 1.0  
**Last Updated:** October 6, 2025  
**Status:** Production

---

## 📋 Table of Contents

- [System Architecture Overview](#system-architecture-overview)
- [Deployment Architecture](#deployment-architecture)
- [Data Flow Diagrams](#data-flow-diagrams)
- [Security Architecture](#security-architecture)
- [Monitoring Architecture](#monitoring-architecture)
- [Network Topology](#network-topology)
- [Integration Points](#integration-points)

---

## 🏗️ System Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[Web Application<br/>React + Vite]
        Mobile[Mobile App<br/>React Native]
        CLI[CLI Tool<br/>Python]
        Plugin[DAW Plugin<br/>VST3/AU]
    end

    subgraph "Edge Layer"
        CDN[CDN<br/>CloudFront/Cloudflare]
        WAF[Web Application Firewall]
        LB[Load Balancer<br/>Nginx/ALB]
    end

    subgraph "Application Layer"
        API[Backend API<br/>FastAPI<br/>3-10 instances]
        Frontend[Frontend Server<br/>Nginx<br/>2-5 instances]
    end

    subgraph "Processing Layer"
        CeleryBeat[Celery Beat<br/>Scheduler]
        CeleryWorker[Celery Workers<br/>2-5 instances]
        Queue[Message Queue<br/>Redis]
    end

    subgraph "Data Layer"
        MongoDB[(MongoDB<br/>ReplicaSet<br/>3 nodes)]
        Redis[(Redis<br/>Cache + Queue<br/>Master-Replica)]
        ChromaDB[(ChromaDB<br/>Vector Store)]
        S3[Object Storage<br/>S3/GCS]
    end

    subgraph "AI Services"
        OpenAI[OpenAI API<br/>GPT-4]
        Google[Google AI<br/>Gemini]
        Anthropic[Anthropic<br/>Claude]
    end

    subgraph "Monitoring Stack"
        Prometheus[Prometheus<br/>Metrics]
        Grafana[Grafana<br/>Dashboards]
        AlertManager[AlertManager<br/>Alerts]
    end

    WebApp --> CDN
    Mobile --> CDN
    CLI --> LB
    Plugin --> LB
    CDN --> WAF
    WAF --> LB
    LB --> API
    LB --> Frontend

    API --> Queue
    API --> MongoDB
    API --> Redis
    API --> ChromaDB
    API --> S3
    API --> OpenAI
    API --> Google
    API --> Anthropic

    CeleryBeat --> Queue
    Queue --> CeleryWorker
    CeleryWorker --> MongoDB
    CeleryWorker --> S3
    CeleryWorker --> OpenAI
    CeleryWorker --> Google

    API --> Prometheus
    CeleryWorker --> Prometheus
    Prometheus --> Grafana
    Prometheus --> AlertManager

    classDef client fill:#e1f5ff,stroke:#01579b
    classDef edge fill:#fff3e0,stroke:#e65100
    classDef app fill:#f3e5f5,stroke:#4a148c
    classDef processing fill:#e8f5e9,stroke:#1b5e20
    classDef data fill:#fce4ec,stroke:#880e4f
    classDef external fill:#fff9c4,stroke:#f57f17
    classDef monitoring fill:#e0f2f1,stroke:#004d40

    class WebApp,Mobile,CLI,Plugin client
    class CDN,WAF,LB edge
    class API,Frontend app
    class CeleryBeat,CeleryWorker,Queue processing
    class MongoDB,Redis,ChromaDB,S3 data
    class OpenAI,Google,Anthropic external
    class Prometheus,Grafana,AlertManager monitoring
```

### Component Responsibilities

| Component | Responsibility | Technology |
|-----------|----------------|------------|
| **Web Application** | User interface for audio management | React, TypeScript, Tailwind |
| **Backend API** | RESTful API, business logic | FastAPI, Python 3.12 |
| **Celery Workers** | Async task processing (audio analysis) | Celery, Python |
| **MongoDB** | Primary data store | MongoDB 7.0 ReplicaSet |
| **Redis** | Caching + message broker | Redis 7.2 |
| **ChromaDB** | Vector embeddings for semantic search | ChromaDB |
| **Object Storage** | Audio file storage | AWS S3 / GCS |

---

## 🚀 Deployment Architecture

### Kubernetes Production Deployment

```mermaid
graph TB
    subgraph "External"
        Users[Users]
        DNS[DNS<br/>Route53/CloudDNS]
    end

    subgraph "Kubernetes Cluster"
        subgraph "Ingress Layer"
            Ingress[Ingress Controller<br/>NGINX<br/>cert-manager]
        end

        subgraph "Frontend Namespace"
            FrontendDeploy[Frontend Deployment<br/>2-5 replicas]
            FrontendHPA[Frontend HPA<br/>CPU: 60%, Mem: 70%]
            FrontendService[Frontend Service<br/>ClusterIP]
        end

        subgraph "Backend Namespace"
            BackendDeploy[Backend Deployment<br/>3-10 replicas]
            BackendHPA[Backend HPA<br/>CPU: 70%, Mem: 80%]
            BackendService[Backend Service<br/>ClusterIP]
        end

        subgraph "Processing Namespace"
            CeleryDeploy[Celery Deployment<br/>2-5 replicas]
            CeleryHPA[Celery HPA<br/>CPU: 80%, Mem: 85%]
            BeatDeploy[Beat Deployment<br/>1 replica]
            FlowerDeploy[Flower Deployment<br/>1 replica]
        end

        subgraph "Data Namespace"
            MongoStatefulSet[MongoDB StatefulSet<br/>3 replicas]
            MongoService[MongoDB Service<br/>Headless]
            RedisStatefulSet[Redis StatefulSet<br/>Master + Replica]
            RedisService[Redis Service<br/>ClusterIP]
            ChromaDeployment[ChromaDB Deployment<br/>1 replica]
        end

        subgraph "Monitoring Namespace"
            PrometheusOp[Prometheus Operator]
            Prometheus[Prometheus<br/>2 replicas]
            GrafanaDeploy[Grafana Deployment]
            AlertManagerDeploy[AlertManager Deployment]
        end

        subgraph "Storage"
            PVC1[MongoDB PVC<br/>100Gi SSD]
            PVC2[Redis PVC<br/>20Gi SSD]
            PVC3[ChromaDB PVC<br/>50Gi SSD]
        end
    end

    subgraph "External Services"
        S3[S3/GCS<br/>Object Storage]
        AI[AI APIs<br/>OpenAI, Google]
    end

    Users --> DNS
    DNS --> Ingress
    Ingress --> FrontendService
    Ingress --> BackendService
    FrontendDeploy -.->|scales| FrontendHPA
    BackendDeploy -.->|scales| BackendHPA
    CeleryDeploy -.->|scales| CeleryHPA
    FrontendService --> FrontendDeploy
    BackendService --> BackendDeploy
    BackendDeploy --> RedisService
    BackendDeploy --> MongoService
    BackendDeploy --> ChromaDeployment
    BackendDeploy --> S3
    BackendDeploy --> AI
    BeatDeploy --> RedisService
    CeleryDeploy --> RedisService
    CeleryDeploy --> MongoService
    CeleryDeploy --> S3
    CeleryDeploy --> AI
    MongoStatefulSet --> PVC1
    RedisStatefulSet --> PVC2
    ChromaDeployment --> PVC3
    BackendDeploy -.->|metrics| Prometheus
    CeleryDeploy -.->|metrics| Prometheus
    Prometheus --> GrafanaDeploy
    Prometheus --> AlertManagerDeploy

    classDef external fill:#e1f5ff,stroke:#01579b
    classDef ingress fill:#fff3e0,stroke:#e65100
    classDef app fill:#f3e5f5,stroke:#4a148c
    classDef data fill:#fce4ec,stroke:#880e4f
    classDef monitoring fill:#e0f2f1,stroke:#004d40
    classDef storage fill:#f1f8e9,stroke:#33691e

    class Users,DNS,S3,AI external
    class Ingress ingress
    class FrontendDeploy,BackendDeploy,CeleryDeploy,BeatDeploy,FlowerDeploy app
    class MongoStatefulSet,RedisStatefulSet,ChromaDeployment data
    class PrometheusOp,Prometheus,GrafanaDeploy,AlertManagerDeploy monitoring
    class PVC1,PVC2,PVC3 storage
```

### Auto-Scaling Behavior

```mermaid
graph LR
    subgraph "Metrics Server"
        CPU[CPU Usage]
        Memory[Memory Usage]
        Custom[Custom Metrics<br/>Queue Depth]
    end

    subgraph "HPA Controllers"
        BackendHPA[Backend HPA<br/>Min: 3, Max: 10]
        FrontendHPA[Frontend HPA<br/>Min: 2, Max: 5]
        CeleryHPA[Celery HPA<br/>Min: 2, Max: 5]
    end

    subgraph "Deployments"
        Backend[Backend Pods]
        Frontend[Frontend Pods]
        Celery[Celery Pods]
    end

    CPU --> BackendHPA
    Memory --> BackendHPA
    CPU --> FrontendHPA
    Memory --> FrontendHPA
    CPU --> CeleryHPA
    Memory --> CeleryHPA
    Custom --> CeleryHPA

    BackendHPA -->|scale| Backend
    FrontendHPA -->|scale| Frontend
    CeleryHPA -->|scale| Celery

    classDef metrics fill:#fff3e0,stroke:#e65100
    classDef hpa fill:#f3e5f5,stroke:#4a148c
    classDef pods fill:#e8f5e9,stroke:#1b5e20

    class CPU,Memory,Custom metrics
    class BackendHPA,FrontendHPA,CeleryHPA hpa
    class Backend,Frontend,Celery pods
```

---

## 📊 Data Flow Diagrams

### Audio Upload and Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant S3 as S3 Storage
    participant Q as Redis Queue
    participant W as Celery Worker
    participant DB as MongoDB
    participant AI as AI Service
    participant V as ChromaDB

    U->>F: Upload audio file
    F->>API: POST /api/v1/audio/upload
    API->>API: Validate file (size, format)
    API->>S3: Upload file
    S3-->>API: File URL
    API->>DB: Create audio_file record
    DB-->>API: Document ID
    API->>Q: Queue analysis tasks
    API-->>F: Upload successful
    F-->>U: Show upload status

    Q->>W: Dequeue BPM detection task
    W->>S3: Download audio file
    W->>W: Analyze BPM with Essentia
    W->>DB: Update audio_file with BPM
    W->>Q: Task complete

    Q->>W: Dequeue key detection task
    W->>S3: Download audio file
    W->>W: Analyze key with Essentia
    W->>DB: Update audio_file with key
    W->>Q: Task complete

    Q->>W: Dequeue embedding task
    W->>S3: Download audio file
    W->>AI: Generate embedding
    AI-->>W: Embedding vector
    W->>V: Store embedding
    W->>DB: Update with embedding_id
    W->>Q: Task complete

    U->>F: Check analysis status
    F->>API: GET /api/v1/audio/:id
    API->>DB: Fetch audio_file
    DB-->>API: Audio file data
    API-->>F: Analysis results
    F-->>U: Display results
```

### Semantic Search Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant R as Redis Cache
    participant V as ChromaDB
    participant AI as AI Service
    participant DB as MongoDB

    U->>F: Enter search query
    F->>API: GET /api/v1/search?q=query

    API->>R: Check cache
    alt Cache hit
        R-->>API: Cached results
        API-->>F: Return results
    else Cache miss
        R-->>API: Cache miss
        
        API->>AI: Generate query embedding
        AI-->>API: Query vector
        
        API->>V: Vector similarity search
        V-->>API: Similar embedding IDs
        
        API->>DB: Fetch audio files by IDs
        DB-->>API: Audio file documents
        
        API->>R: Cache results (5 min TTL)
        API-->>F: Return results
    end

    F-->>U: Display search results
```

### Real-time Analysis Pipeline

```mermaid
graph LR
    subgraph "Ingestion"
        Upload[Audio Upload]
        Validate[Validation]
        Store[S3 Storage]
    end

    subgraph "Task Queue"
        Queue[Redis Queue]
        Priority[Priority Router]
    end

    subgraph "Processing Pipeline"
        BPM[BPM Detection<br/>Essentia]
        Key[Key Detection<br/>Essentia]
        Stems[Stem Separation<br/>Demucs]
        Transcribe[Transcription<br/>Whisper]
        Embed[Embedding<br/>AI Model]
    end

    subgraph "Storage & Indexing"
        MongoDB[(MongoDB<br/>Metadata)]
        Vector[(ChromaDB<br/>Vectors)]
        S3Store[(S3<br/>Files)]
    end

    Upload --> Validate
    Validate --> Store
    Store --> Queue
    Queue --> Priority
    Priority --> BPM
    Priority --> Key
    Priority --> Stems
    Priority --> Transcribe
    Priority --> Embed
    BPM --> MongoDB
    Key --> MongoDB
    Stems --> S3Store
    Transcribe --> MongoDB
    Embed --> Vector
    Embed --> MongoDB

    classDef input fill:#e1f5ff,stroke:#01579b
    classDef queue fill:#fff3e0,stroke:#e65100
    classDef process fill:#f3e5f5,stroke:#4a148c
    classDef storage fill:#fce4ec,stroke:#880e4f

    class Upload,Validate,Store input
    class Queue,Priority queue
    class BPM,Key,Stems,Transcribe,Embed process
    class MongoDB,Vector,S3Store storage
```

---

## 🔒 Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "External Threats"
        DDoS[DDoS Attacks]
        Injection[SQL/NoSQL Injection]
        XSS[XSS Attacks]
        Malware[Malware Upload]
    end

    subgraph "Defense Layer 1: Edge"
        WAF[WAF<br/>Rate Limiting<br/>DDoS Protection]
        CDN[CDN<br/>SSL/TLS<br/>Caching]
    end

    subgraph "Defense Layer 2: Network"
        Firewall[Firewall Rules]
        NetworkPolicy[Network Policies<br/>Pod-to-Pod]
        PrivateSubnet[Private Subnets]
    end

    subgraph "Defense Layer 3: Application"
        Auth[Authentication<br/>JWT + API Keys]
        AuthZ[Authorization<br/>RBAC]
        Validation[Input Validation<br/>Sanitization]
        RateLimit[Rate Limiting<br/>Per-User/IP]
    end

    subgraph "Defense Layer 4: Data"
        Encryption[Encryption at Rest<br/>AES-256]
        TLS[TLS in Transit]
        Backup[Encrypted Backups]
        Audit[Audit Logging]
    end

    subgraph "Monitoring & Response"
        IDS[Intrusion Detection]
        SIEM[Security Monitoring]
        Alerts[Security Alerts]
        Incident[Incident Response]
    end

    DDoS --> WAF
    Injection --> WAF
    XSS --> WAF
    Malware --> WAF

    WAF --> CDN
    CDN --> Firewall
    Firewall --> NetworkPolicy
    NetworkPolicy --> PrivateSubnet
    PrivateSubnet --> Auth
    Auth --> AuthZ
    AuthZ --> Validation
    Validation --> RateLimit
    RateLimit --> Encryption
    Encryption --> TLS
    TLS --> Backup

    Firewall -.->|monitor| IDS
    NetworkPolicy -.->|monitor| IDS
    Auth -.->|logs| Audit
    AuthZ -.->|logs| Audit
    Audit --> SIEM
    IDS --> SIEM
    SIEM --> Alerts
    Alerts --> Incident

    classDef threat fill:#ffebee,stroke:#c62828
    classDef defense fill:#e8f5e9,stroke:#2e7d32
    classDef monitor fill:#e0f2f1,stroke:#004d40

    class DDoS,Injection,XSS,Malware threat
    class WAF,CDN,Firewall,NetworkPolicy,PrivateSubnet,Auth,AuthZ,Validation,RateLimit,Encryption,TLS,Backup defense
    class IDS,SIEM,Alerts,Audit,Incident monitor
```

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant Auth as Auth Service
    participant DB as MongoDB
    participant Redis as Redis Cache

    Note over U,Redis: Login Flow
    U->>F: Enter credentials
    F->>API: POST /api/v1/auth/login
    API->>DB: Verify credentials
    DB-->>API: User found
    API->>Auth: Generate JWT tokens
    Auth-->>API: Access + Refresh tokens
    API->>Redis: Cache session
    API-->>F: Return tokens
    F->>F: Store tokens (httpOnly cookie)
    F-->>U: Login successful

    Note over U,Redis: Authenticated Request
    U->>F: Request protected resource
    F->>API: GET /api/v1/audio (with JWT)
    API->>Auth: Verify JWT signature
    Auth-->>API: Token valid
    API->>Redis: Check session
    Redis-->>API: Session active
    API->>Auth: Check permissions (RBAC)
    Auth-->>API: Authorized
    API->>DB: Fetch data
    DB-->>API: User's data
    API-->>F: Return data
    F-->>U: Display data

    Note over U,Redis: Token Refresh
    U->>F: Access token expired
    F->>API: POST /api/v1/auth/refresh (refresh token)
    API->>Auth: Verify refresh token
    Auth-->>API: Token valid
    API->>Auth: Generate new access token
    Auth-->>API: New access token
    API-->>F: Return new token
    F->>F: Update stored token
```

---

## 📈 Monitoring Architecture

### Observability Stack

```mermaid
graph TB
    subgraph "Application Layer"
        API[Backend API]
        Worker[Celery Workers]
        Frontend[Frontend]
    end

    subgraph "Metrics Collection"
        AppMetrics[Application Metrics<br/>Prometheus Client]
        NodeExporter[Node Exporter<br/>System Metrics]
        cAdvisor[cAdvisor<br/>Container Metrics]
        MongoExporter[MongoDB Exporter]
        RedisExporter[Redis Exporter]
    end

    subgraph "Metrics Storage & Processing"
        Prometheus[Prometheus<br/>Time-Series DB]
        Recording[Recording Rules<br/>Pre-aggregation]
    end

    subgraph "Visualization"
        Grafana[Grafana<br/>Dashboards]
        SystemDash[System Overview]
        AudioDash[Audio Processing]
        DBDash[Database Performance]
        MLDash[ML Models]
    end

    subgraph "Alerting"
        AlertRules[Alert Rules<br/>Critical + Warning]
        AlertManager[AlertManager<br/>Routing & Grouping]
        Slack[Slack Notifications]
        PagerDuty[PagerDuty Alerts]
        Email[Email Alerts]
    end

    subgraph "Logging"
        AppLogs[Application Logs<br/>Structured JSON]
        K8sLogs[Kubernetes Logs]
        Loki[Loki<br/>Log Aggregation]
        LogDash[Log Explorer]
    end

    subgraph "Tracing"
        OpenTelemetry[OpenTelemetry<br/>Instrumentation]
        Jaeger[Jaeger<br/>Distributed Tracing]
        TraceDash[Trace Viewer]
    end

    API --> AppMetrics
    Worker --> AppMetrics
    Frontend --> AppMetrics
    AppMetrics --> Prometheus
    NodeExporter --> Prometheus
    cAdvisor --> Prometheus
    MongoExporter --> Prometheus
    RedisExporter --> Prometheus
    
    Prometheus --> Recording
    Recording --> Grafana
    Grafana --> SystemDash
    Grafana --> AudioDash
    Grafana --> DBDash
    Grafana --> MLDash
    
    Prometheus --> AlertRules
    AlertRules --> AlertManager
    AlertManager --> Slack
    AlertManager --> PagerDuty
    AlertManager --> Email
    
    API --> AppLogs
    Worker --> AppLogs
    K8sLogs --> Loki
    AppLogs --> Loki
    Loki --> LogDash
    Grafana --> LogDash
    
    API --> OpenTelemetry
    Worker --> OpenTelemetry
    OpenTelemetry --> Jaeger
    Jaeger --> TraceDash

    classDef app fill:#f3e5f5,stroke:#4a148c
    classDef collect fill:#fff3e0,stroke:#e65100
    classDef storage fill:#fce4ec,stroke:#880e4f
    classDef visual fill:#e1f5ff,stroke:#01579b
    classDef alert fill:#ffebee,stroke:#c62828
    classDef log fill:#e8f5e9,stroke:#2e7d32

    class API,Worker,Frontend app
    class AppMetrics,NodeExporter,cAdvisor,MongoExporter,RedisExporter collect
    class Prometheus,Recording,Loki,Jaeger storage
    class Grafana,SystemDash,AudioDash,DBDash,MLDash,LogDash,TraceDash visual
    class AlertRules,AlertManager,Slack,PagerDuty,Email alert
    class AppLogs,K8sLogs,OpenTelemetry log
```

### Alert Flow

```mermaid
graph LR
    subgraph "Metrics Sources"
        API[API Metrics]
        Worker[Worker Metrics]
        DB[Database Metrics]
        System[System Metrics]
    end

    subgraph "Alert Rules"
        Critical[Critical Alerts<br/>Error rate >1%<br/>Service down<br/>Disk <10%]
        Warning[Warning Alerts<br/>Error rate >0.5%<br/>High CPU >80%<br/>Queue depth >1000]
    end

    subgraph "AlertManager"
        Router[Alert Router]
        Grouping[Grouping & Dedup]
        Inhibit[Inhibition Rules]
    end

    subgraph "Notification Channels"
        PD[PagerDuty<br/>SEV1 only]
        Slack[Slack<br/>All alerts]
        Email[Email<br/>Daily digest]
    end

    subgraph "Response"
        OnCall[On-Call Engineer]
        Runbook[Runbook/Playbook]
        Escalate[Escalation Matrix]
    end

    API --> Critical
    Worker --> Critical
    DB --> Critical
    System --> Critical
    API --> Warning
    Worker --> Warning
    DB --> Warning
    System --> Warning

    Critical --> Router
    Warning --> Router
    Router --> Grouping
    Grouping --> Inhibit
    Inhibit --> PD
    Inhibit --> Slack
    Inhibit --> Email

    PD --> OnCall
    Slack --> OnCall
    OnCall --> Runbook
    Runbook --> Escalate

    classDef metrics fill:#fff3e0,stroke:#e65100
    classDef rules fill:#ffebee,stroke:#c62828
    classDef manager fill:#f3e5f5,stroke:#4a148c
    classDef notif fill:#e1f5ff,stroke:#01579b
    classDef response fill:#e8f5e9,stroke:#2e7d32

    class API,Worker,DB,System metrics
    class Critical,Warning rules
    class Router,Grouping,Inhibit manager
    class PD,Slack,Email notif
    class OnCall,Runbook,Escalate response
```

---

## 🌐 Network Topology

### Kubernetes Network Architecture

```mermaid
graph TB
    subgraph "Internet"
        Users[Users/Clients]
    end

    subgraph "Load Balancer"
        LB[Cloud Load Balancer<br/>AWS ALB / GCP GLB]
    end

    subgraph "Kubernetes Cluster - Public Subnet"
        IngressCtrl[Ingress Controller<br/>NGINX<br/>10.0.1.0/24]
    end

    subgraph "Kubernetes Cluster - Private Subnet 1"
        FrontendPods[Frontend Pods<br/>10.0.10.0/24]
        BackendPods[Backend Pods<br/>10.0.20.0/24]
        CeleryPods[Celery Pods<br/>10.0.30.0/24]
    end

    subgraph "Kubernetes Cluster - Private Subnet 2"
        MongoCluster[MongoDB Cluster<br/>10.0.50.0/24]
        RedisCluster[Redis Cluster<br/>10.0.60.0/24]
        ChromaDB[ChromaDB<br/>10.0.70.0/24]
    end

    subgraph "Kubernetes Cluster - Monitoring Subnet"
        Prometheus[Prometheus<br/>10.0.100.0/24]
        Grafana[Grafana<br/>10.0.101.0/24]
    end

    subgraph "External Services"
        S3[S3/GCS Storage<br/>HTTPS]
        OpenAI[OpenAI API<br/>HTTPS]
        Google[Google AI API<br/>HTTPS]
    end

    Users -->|HTTPS 443| LB
    LB -->|HTTPS| IngressCtrl
    IngressCtrl -->|HTTP| FrontendPods
    IngressCtrl -->|HTTP| BackendPods
    
    BackendPods -->|27017| MongoCluster
    BackendPods -->|6379| RedisCluster
    BackendPods -->|8000| ChromaDB
    BackendPods -->|HTTPS| S3
    BackendPods -->|HTTPS| OpenAI
    BackendPods -->|HTTPS| Google
    
    CeleryPods -->|6379| RedisCluster
    CeleryPods -->|27017| MongoCluster
    CeleryPods -->|HTTPS| S3
    CeleryPods -->|HTTPS| OpenAI
    
    BackendPods -.->|9090| Prometheus
    CeleryPods -.->|9090| Prometheus
    MongoCluster -.->|9216| Prometheus
    RedisCluster -.->|9121| Prometheus
    Prometheus -.->|3000| Grafana

    classDef external fill:#e1f5ff,stroke:#01579b
    classDef public fill:#fff3e0,stroke:#e65100
    classDef private fill:#f3e5f5,stroke:#4a148c
    classDef data fill:#fce4ec,stroke:#880e4f
    classDef monitoring fill:#e0f2f1,stroke:#004d40
    classDef cloud fill:#fff9c4,stroke:#f57f17

    class Users external
    class LB,IngressCtrl public
    class FrontendPods,BackendPods,CeleryPods private
    class MongoCluster,RedisCluster,ChromaDB data
    class Prometheus,Grafana monitoring
    class S3,OpenAI,Google cloud
```

### Network Policies

```mermaid
graph LR
    subgraph "Ingress Rules"
        Internet[Internet] -->|Allow 443| Ingress[Ingress Controller]
        Ingress -->|Allow HTTP| Frontend[Frontend Pods]
        Ingress -->|Allow HTTP| Backend[Backend Pods]
    end

    subgraph "Inter-Pod Rules"
        Backend -->|Allow 27017| MongoDB[MongoDB Pods]
        Backend -->|Allow 6379| Redis[Redis Pods]
        Backend -->|Allow 8000| Chroma[ChromaDB Pods]
        Celery[Celery Pods] -->|Allow 6379| Redis
        Celery -->|Allow 27017| MongoDB
    end

    subgraph "Egress Rules"
        Backend -->|Allow HTTPS| External[External APIs<br/>OpenAI, Google]
        Celery -->|Allow HTTPS| External
        Backend -->|Allow HTTPS| S3[S3/GCS Storage]
        Celery -->|Allow HTTPS| S3
    end

    subgraph "Monitoring Rules"
        Prometheus[Prometheus] -->|Allow 9090| Backend
        Prometheus -->|Allow 9090| Celery
        Prometheus -->|Allow 9216| MongoDB
        Prometheus -->|Allow 9121| Redis
    end

    subgraph "Denied"
        Frontend -.->|Deny| MongoDB
        Frontend -.->|Deny| Redis
        Frontend -.->|Deny| External
        Internet -.->|Deny| MongoDB
        Internet -.->|Deny| Redis
    end

    classDef allow fill:#e8f5e9,stroke:#2e7d32
    classDef deny fill:#ffebee,stroke:#c62828
    classDef external fill:#fff9c4,stroke:#f57f17

    class Internet,Ingress,Frontend,Backend,Celery,MongoDB,Redis,Chroma,Prometheus allow
    class External,S3 external
```

---

## 🔗 Integration Points

### External Service Integrations

```mermaid
graph TB
    subgraph "SampleMind AI Core"
        API[Backend API]
        Worker[Celery Workers]
    end

    subgraph "AI/ML Services"
        OpenAI[OpenAI API<br/>- GPT-4 for chat<br/>- Whisper for transcription<br/>- Embeddings]
        Google[Google AI<br/>- Gemini Pro<br/>- Text embeddings]
        Anthropic[Anthropic<br/>- Claude for analysis]
    end

    subgraph "Storage Services"
        S3[AWS S3 / GCS<br/>- Audio file storage<br/>- Backup storage<br/>- Static assets]
    end

    subgraph "Authentication"
        OAuth[OAuth Providers<br/>- Google<br/>- GitHub<br/>- Microsoft]
    end

    subgraph "Payment Processing"
        Stripe[Stripe<br/>- Subscriptions<br/>- Usage billing]
    end

    subgraph "Communication"
        SendGrid[SendGrid<br/>- Transactional email<br/>- Notifications]
        Twilio[Twilio<br/>- SMS alerts<br/>- Voice notifications]
    end

    subgraph "Monitoring & Analytics"
        Sentry[Sentry<br/>- Error tracking<br/>- Performance monitoring]
        Mixpanel[Mixpanel<br/>- Product analytics<br/>- User tracking]
    end

    API -->|REST API| OpenAI
    API -->|REST API| Google
    API -->|REST API| Anthropic
    API -->|S3 SDK| S3
    API -->|OAuth 2.0| OAuth
    API -->|Stripe SDK| Stripe
    API -->|REST API| SendGrid
    API -->|REST API| Twilio
    API -->|Sentry SDK| Sentry
    API -->|REST API| Mixpanel
    
    Worker -->|REST API| OpenAI
    Worker -->|REST API| Google
    Worker -->|S3 SDK| S3

    classDef core fill:#f3e5f5,stroke:#4a148c
    classDef ai fill:#e1f5ff,stroke:#01579b
    classDef storage fill:#fff3e0,stroke:#e65100
    classDef auth fill:#e8f5e9,stroke:#2e7d32
    classDef payment fill:#fff9c4,stroke:#f57f17
    classDef comm fill:#fce4ec,stroke:#880e4f
    classDef monitor fill:#e0f2f1,stroke:#004d40

    class API,Worker core
    class OpenAI,Google,Anthropic ai
    class S3 storage
    class OAuth auth
    class Stripe payment
    class SendGrid,Twilio comm
    class Sentry,Mixpanel monitor
```

### API Integration Patterns

```mermaid
sequenceDiagram
    participant Client
    participant API as SampleMind API
    participant Cache as Redis Cache
    participant AI as External AI API
    participant CB as Circuit Breaker
    participant Retry as Retry Logic

    Note over Client,Retry: Resilient Integration Pattern

    Client->>API: Request
    API->>Cache: Check cache
    
    alt Cache Hit
        Cache-->>API: Return cached data
        API-->>Client: Response
    else Cache Miss
        Cache-->>API: Not found
        
        API->>CB: Check circuit state
        
        alt Circuit Closed (Healthy)
            CB-->>API: Allow request
            API->>AI: External API call
            
            alt Success
                AI-->>API: Response
                API->>Cache: Cache result
                API-->>Client: Response
                API->>CB: Record success
            else Failure
                AI-->>API: Error
                API->>CB: Record failure
                API->>Retry: Retry with backoff
                
                alt Retry Success
                    Retry->>AI: Retry request
                    AI-->>Retry: Response
                    Retry-->>API: Response
                    API->>Cache: Cache result
                    API-->>Client: Response
                else Retry Failed
                    Retry-->>API: All retries failed
                    API->>CB: Open circuit
                    API-->>Client: Fallback response
                end
            end
        else Circuit Open (Unhealthy)
            CB-->>API: Block request
            API-->>Client: Fallback response
        end
    end
```

---

## 📚 Related Documentation

- [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md:1) - Deployment procedures
- [`OPERATIONS_MANUAL.md`](OPERATIONS_MANUAL.md:1) - Operations guide
- [`INCIDENT_RESPONSE.md`](INCIDENT_RESPONSE.md:1) - Incident response
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md:1) - Detailed architecture

---

## 📝 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial architecture diagrams | Architecture Team |

---

**Document Owner:** Architecture Team  
**Review Schedule:** Quarterly  
**Last Reviewed:** October 6, 2025

**Note:** Diagrams are rendered using Mermaid. View in GitHub or any Mermaid-compatible viewer.