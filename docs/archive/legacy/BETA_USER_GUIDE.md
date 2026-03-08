# SampleMind AI Beta v2.1.0 - User Guide

## 🚀 Getting Started (Docker)

The Beta release is designed to be run via Docker Compose for maximum stability.

### 1. Prerequisites
- Docker Desktop or Docker Engine installed
- 8GB+ RAM available (for AI models)

### 2. Installation & Launch

1. **Configure Environment** (Optional)
   The system works out-of-the-box with local mocks.
   To enable real Cloud Sync, edit `.env`:
   ```bash
   STORAGE_PROVIDER=s3
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

2. **Start the System**
   ```bash
   docker compose up -d --build
   ```

3. **Verify Status**
   ```bash
   docker compose ps
   ```
   Ensure `samplemind-api` is "Up (healthy)".

### 3. Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Docs** | [http://localhost:8000/api/docs](http://localhost:8000/api/docs) | N/A |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | `admin` / `samplemind` |
| **Prometheus**| [http://localhost:9090](http://localhost:9090) | N/A |

## 🧪 Beta Features to Test

### 1. Local-First Sync
The system defaults to "Local Storage Provider". Files uploaded via the API will be "synced" to a local folder in `data/storage_mock`.
- **Test**: Upload a file via `POST /api/v1/audio/upload`.
- **Verify**: Check logs to see hashing logic: `docker compose logs -f samplemind-api`.

### 2. Authentication
The Beta uses a lightweight middleware injection.
- **Pass Header**: `X-User-ID: my-beta-user`
- **Effect**: Collections and files will be scoped to this user ID.

### 3. Monitoring
Check Grafana for real-time memory usage and API request latencies.

## 🆘 Troubleshooting

**"ModuleNotFoundError" in logs?**
We added new dependencies. Run:
```bash
docker compose up -d --build
```

**"Connection Refused" on port 8000?**
The API might be restarting. Check logs:
```bash
docker compose logs --tail=50 -f samplemind-api
```
