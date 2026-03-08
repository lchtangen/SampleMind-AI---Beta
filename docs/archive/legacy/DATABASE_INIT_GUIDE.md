# 🗄️ Database Initialization Guide

**Date:** October 19, 2025  
**Duration:** 15 minutes  
**Database:** PostgreSQL 15+

---

## 🎯 OBJECTIVES

1. ✅ PostgreSQL running
2. ✅ Database created
3. ✅ Tables initialized
4. ✅ Test user created
5. ✅ Migrations applied
6. ✅ Connection verified

---

## 📋 PRE-REQUISITES

### Option 1: Docker (Recommended)
```bash
# Check Docker running
docker --version

# Start PostgreSQL container
docker-compose up -d postgres

# Verify running
docker ps | grep postgres
```

### Option 2: Local PostgreSQL
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# Windows
# Download from postgresql.org and install
```

---

## 🚀 STEP-BY-STEP INITIALIZATION

### Step 1: Verify PostgreSQL Running (2 min)

```bash
# Check if PostgreSQL is accessible
pg_isready

# Expected output:
# /tmp:5432 - accepting connections

# Or check specific host/port
pg_isready -h localhost -p 5432
```

**If not running:**
```bash
# Docker
docker-compose up -d postgres

# Local (macOS)
brew services start postgresql@15

# Local (Linux)
sudo systemctl start postgresql
```

---

### Step 2: Create Database (3 min)

**Option A: Using psql**
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database
CREATE DATABASE samplemind;

# Create user
CREATE USER samplemind WITH PASSWORD 'samplemind123';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE samplemind TO samplemind;

# Exit
\q
```

**Option B: Using script**
```bash
# Create database with script
createdb -U postgres -h localhost samplemind

# Create user
psql -U postgres -h localhost -c "CREATE USER samplemind WITH PASSWORD 'samplemind123';"

# Grant access
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE samplemind TO samplemind;"
```

**Verify:**
```bash
# List databases
psql -U postgres -h localhost -c "\l" | grep samplemind

# Connect to verify
psql -U samplemind -h localhost -d samplemind -c "SELECT version();"
```

---

### Step 3: Configure Environment (2 min)

**Create backend/.env file:**
```bash
cd backend

# Copy template
cp .env.example .env

# Edit .env file
cat > .env << EOF
# Database
DATABASE_URL=postgresql://samplemind:samplemind123@localhost:5432/samplemind

# Security
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars

# Environment
ENVIRONMENT=development
DEBUG=true

# Optional (for full features)
REDIS_URL=redis://localhost:6379
EOF
```

---

### Step 4: Install Python Dependencies (3 min)

```bash
# Ensure you're in backend directory
cd backend

# Install requirements
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "fastapi|sqlalchemy|alembic|psycopg2"

# Expected output:
# fastapi          0.104.1
# sqlalchemy       2.0.23
# alembic          1.13.0
# psycopg2-binary  2.9.9
```

---

### Step 5: Run Database Initialization (3 min)

```bash
# Make sure you're in backend directory
cd backend

# Run init script
python scripts/init_db.py

# Expected output:
# 🗄️  Creating database tables...
# ✅ Tables created successfully!
# 👤 Creating test user...
# ✅ Test user created: test@samplemind.ai
#    Password: test123456
# 
# ✅ Database initialized successfully!
# 
# 📝 Test credentials:
#    Email: test@samplemind.ai
#    Password: test123456
# 
# 🔗 API: http://localhost:8000
# 📚 Docs: http://localhost:8000/api/docs
```

**What this does:**
- Creates all database tables (users, audio_files, audio_analysis)
- Creates test user account
- Sets up relationships and indexes
- Verifies connection

---

### Step 6: Apply Migrations (2 min)

```bash
# Run Alembic migrations
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema

# Verify current migration
alembic current

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# 001 (head)
```

---

## ✅ VERIFICATION

### Test 1: Database Connection
```bash
# Connect to database
psql postgresql://samplemind:samplemind123@localhost:5432/samplemind

# List tables
\dt

# Expected output:
#               List of relations
#  Schema |        Name        | Type  |   Owner    
# --------+--------------------+-------+------------
#  public | alembic_version    | table | samplemind
#  public | audio_analysis     | table | samplemind
#  public | audio_files        | table | samplemind
#  public | users              | table | samplemind

# Check users table
SELECT id, email, full_name, created_at FROM users;

# Expected output (test user):
#  id |         email         | full_name  |        created_at
# ----+-----------------------+------------+---------------------------
#   1 | test@samplemind.ai    | Test User  | 2025-10-19 22:00:00.000

# Exit
\q
```

### Test 2: Python Connection
```bash
# Test from Python
cd backend
python << EOF
from app.core.database import engine, SessionLocal
from app.models import User

# Test connection
with engine.connect() as conn:
    print("✅ Database connection successful!")

# Test query
db = SessionLocal()
user = db.query(User).first()
print(f"✅ Found user: {user.email}")
db.close()
EOF

# Expected output:
# ✅ Database connection successful!
# ✅ Found user: test@samplemind.ai
```

### Test 3: API Connection
```bash
# Start API temporarily
python main.py &
API_PID=$!

# Wait for startup
sleep 5

# Test endpoint that requires DB
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"samplemind-api","checks":{"api":"ok","database":"ok"}}

# Stop API
kill $API_PID
```

---

## 📊 DATABASE SCHEMA

### Tables Created

**1. users**
```sql
- id (PRIMARY KEY)
- email (UNIQUE, INDEXED)
- hashed_password
- full_name
- is_active
- is_superuser
- is_premium
- is_beta_user
- created_at
- updated_at
- last_login_at
```

**2. audio_files**
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY → users.id, INDEXED)
- filename
- original_filename
- file_path
- file_format
- file_size
- duration
- sample_rate
- channels
- bit_depth
- status (INDEXED)
- error_message
- uploaded_at (INDEXED)
- processed_at
```

**3. audio_analysis**
```sql
- id (PRIMARY KEY)
- audio_id (FOREIGN KEY → audio_files.id, UNIQUE, INDEXED)
- tempo
- key
- time_signature
- loudness
- energy, danceability, valence
- acousticness, instrumentalness
- liveness, speechiness
- spectral_centroid, spectral_rolloff
- zero_crossing_rate
- genres (JSON)
- moods (JSON)
- instruments (JSON)
- tags (JSON)
- description
- similarity_score
- analyzed_at
```

---

## 🐛 TROUBLESHOOTING

### Error: "could not connect to server"
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
docker-compose up -d postgres
# OR
brew services start postgresql@15
```

### Error: "password authentication failed"
```bash
# Reset password
psql -U postgres -h localhost -c "ALTER USER samplemind WITH PASSWORD 'samplemind123';"

# Verify DATABASE_URL in .env matches
cat backend/.env | grep DATABASE_URL
```

### Error: "database does not exist"
```bash
# Create database
createdb -U postgres -h localhost samplemind

# Or manually
psql -U postgres -h localhost -c "CREATE DATABASE samplemind;"
```

### Error: "permission denied"
```bash
# Grant privileges
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE samplemind TO samplemind;"

# Grant on schema
psql -U postgres -d samplemind -c "GRANT ALL ON SCHEMA public TO samplemind;"
```

### Error: "module 'psycopg2' not found"
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Verify
python -c "import psycopg2; print('✅ psycopg2 installed')"
```

### Tables Not Created
```bash
# Run init script again
python scripts/init_db.py

# Or use Alembic
alembic upgrade head

# Verify
psql postgresql://samplemind:samplemind123@localhost:5432/samplemind -c "\dt"
```

---

## 🔄 RESET DATABASE (If Needed)

```bash
# WARNING: This will delete all data!

# Drop and recreate database
psql -U postgres -h localhost << EOF
DROP DATABASE IF EXISTS samplemind;
CREATE DATABASE samplemind;
GRANT ALL PRIVILEGES ON DATABASE samplemind TO samplemind;
EOF

# Re-initialize
python scripts/init_db.py

# Apply migrations
alembic upgrade head
```

---

## 📈 NEXT STEPS

After successful initialization:

1. ✅ **Start Backend**
   ```bash
   python main.py
   ```

2. ✅ **Test API**
   ```bash
   curl http://localhost:8000/health
   ```

3. ✅ **Login with Test User**
   - Email: test@samplemind.ai
   - Password: test123456

4. ✅ **Run Full Stack Tests**
   - See FULL_STACK_TEST_GUIDE.md

---

## 📝 CONFIGURATION CHECKLIST

- [ ] PostgreSQL installed and running
- [ ] Database `samplemind` created
- [ ] User `samplemind` created with password
- [ ] Backend .env file configured
- [ ] Python dependencies installed
- [ ] Init script executed successfully
- [ ] Migrations applied
- [ ] Test user created
- [ ] Connection verified
- [ ] Tables visible in database

**Status:** ✅ Ready for development!

---

## 🎯 PRODUCTION NOTES

For production deployment:

1. **Change Credentials**
   - Use strong passwords
   - Don't commit .env to Git
   - Use environment variables

2. **Use Managed PostgreSQL**
   - AWS RDS
   - Google Cloud SQL
   - Supabase
   - Neon

3. **Enable SSL**
   ```python
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

4. **Backups**
   - Automated daily backups
   - Point-in-time recovery
   - Backup retention policy

---

**Database Init Status:** ✅ Ready to Execute  
**Estimated Time:** 15 minutes  
**Difficulty:** Easy  
**Next:** Full Stack Testing
