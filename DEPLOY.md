# 🚀 Deployment Guide — SampleMind AI

## Quick Deploy Options

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
```

### Option 2: Manual
```bash
# Backend
cd backend && python main.py

# Frontend  
cd apps/web && pnpm build && pnpm start
```

### Option 3: Cloud (Vercel + Railway)
```bash
# Frontend to Vercel
vercel --prod

# Backend to Railway
railway up
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database connected
- [ ] Secret key changed
- [ ] CORS origins updated
- [ ] SSL certificates installed
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] CDN configured
- [ ] Rate limiting enabled
- [ ] Security headers set

## Environment Variables

### Backend
```bash
SECRET_KEY=<generate-secure-key>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Frontend
```bash
NEXT_PUBLIC_API_URL=https://api.samplemind.ai
```

## Monitoring

- Backend: http://api.samplemind.ai/health
- Frontend: https://samplemind.ai
- Status: status.samplemind.ai

## Scaling

### Horizontal
- Add more FastAPI workers
- Load balancer (nginx/Caddy)
- Redis cluster
- PostgreSQL replicas

### Vertical
- Increase container resources
- Optimize queries
- Enable caching
- CDN for static assets
