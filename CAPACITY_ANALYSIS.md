# 📊 UNITEST.IN Capacity Analysis

## Current Infrastructure

### Deployment Platform: **Vercel (Serverless)**
- **Type**: Serverless Functions (Python/Flask)
- **Database**: PostgreSQL on NeonDB
- **Domain**: unitest.in

---

## 🔢 Concurrent User Capacity

### **Current Capacity: ~100-500 Concurrent Users**

**Breakdown:**

#### 1. **Vercel Serverless Functions**
- **Free Tier**: 
  - 100 GB-hours execution time per month
  - 10 seconds max execution time per function
  - Unlimited function invocations
  - **Concurrent Limit**: ~100-200 simultaneous requests (auto-scales)

- **Pro Tier** ($20/month):
  - 1,000 GB-hours execution time per month
  - 60 seconds max execution time per function
  - **Concurrent Limit**: ~500-1,000 simultaneous requests

- **Enterprise Tier**:
  - Custom limits
  - **Concurrent Limit**: 10,000+ simultaneous requests

**Your Current Plan**: Based on `vercel.json`, you're likely on **Free Tier**

#### 2. **NeonDB PostgreSQL Database**

- **Free Tier**:
  - **Max Connections**: 100 concurrent connections
  - **Storage**: 0.5 GB
  - **Compute**: 0.25 vCPU, 256 MB RAM
  - **Connection Pooling**: Enabled (via `pool_pre_ping` and `pool_recycle`)

- **Launch Tier** ($19/month):
  - **Max Connections**: 200 concurrent connections
  - **Storage**: 10 GB
  - **Compute**: 0.5 vCPU, 512 MB RAM

- **Scale Tier** ($69/month):
  - **Max Connections**: 500 concurrent connections
  - **Storage**: 50 GB
  - **Compute**: 2 vCPU, 2 GB RAM

**Your Current Plan**: Likely **Free Tier** (100 connections)

#### 3. **Session Management**

- **Flask-Login**: Server-side sessions (stored in database)
- **No explicit session limit**: Sessions are stored in database
- **Session timeout**: Default Flask session (31 days or until logout)

---

## 📈 Actual Concurrent User Capacity

### **Current Setup (Free Tier):**

| Metric | Limit | Impact |
|--------|-------|--------|
| **Vercel Functions** | ~100-200 concurrent | ✅ Usually sufficient |
| **NeonDB Connections** | 100 concurrent | ⚠️ **BOTTLENECK** |
| **Logged-in Users** | **~80-100 users** | Limited by DB connections |

### **Why 80-100 Users?**

- Each logged-in user may use 1-2 database connections
- Connection pooling helps, but:
  - Active quiz-taking: ~2 connections per user
  - Dashboard viewing: ~1 connection per user
  - AI question generation: ~2-3 connections per request

**Formula:**
```
Max Concurrent Users = (DB Connections - Reserved) / Avg Connections per User
Max Concurrent Users = (100 - 10) / 1.2 ≈ 75 users
```

**Safe Capacity: ~50-75 concurrent logged-in users**

---

## 🚀 Scaling Options

### **Option 1: Upgrade NeonDB (Recommended First Step)**

**Upgrade to Launch Tier ($19/month):**
- **New Capacity**: ~150-180 concurrent users
- **Benefits**:
  - 200 database connections (2x increase)
  - More storage (10 GB)
  - Better performance

**Upgrade to Scale Tier ($69/month):**
- **New Capacity**: ~400-450 concurrent users
- **Benefits**:
  - 500 database connections (5x increase)
  - 50 GB storage
  - Better CPU/RAM for AI operations

### **Option 2: Upgrade Vercel Plan**

**Upgrade to Pro ($20/month):**
- **New Capacity**: Better handling of concurrent requests
- **Benefits**:
  - Longer function execution (60s vs 10s)
  - More execution time
  - Better performance monitoring

**Combined (NeonDB Launch + Vercel Pro):**
- **Total Cost**: ~$39/month
- **New Capacity**: ~150-200 concurrent users

### **Option 3: Optimize Current Setup (Free)**

**Immediate Improvements:**
1. **Connection Pooling Optimization**:
   ```python
   app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
       'pool_size': 5,           # Reduce pool size
       'max_overflow': 10,        # Limit overflow
       'pool_pre_ping': True,
       'pool_recycle': 300,
   }
   ```

2. **Session Management**:
   - Use Redis for sessions (if available)
   - Reduce session timeout
   - Implement session cleanup

3. **Database Query Optimization**:
   - Add indexes on frequently queried columns
   - Use connection pooling efficiently
   - Cache frequently accessed data

**Expected Improvement**: +20-30% capacity (~60-90 users)

---

## 📊 Capacity by User Activity

### **Light Usage** (Dashboard viewing, browsing):
- **Connections per user**: ~0.5-1
- **Capacity**: ~80-100 users

### **Medium Usage** (Taking quizzes, viewing results):
- **Connections per user**: ~1-2
- **Capacity**: ~50-75 users

### **Heavy Usage** (AI question generation, code execution):
- **Connections per user**: ~2-3
- **Capacity**: ~30-50 users

### **Peak Usage** (All users active simultaneously):
- **Connections per user**: ~2-3
- **Capacity**: ~30-50 users

---

## 🔍 Monitoring Current Usage

### **How to Check Current Load:**

1. **Vercel Dashboard**:
   - Go to your project → Analytics
   - Check "Function Invocations"
   - Monitor "Execution Time"

2. **NeonDB Dashboard**:
   - Go to your project → Metrics
   - Check "Active Connections"
   - Monitor "Query Performance"

3. **Add Monitoring Code**:
   ```python
   # Add to app.py
   @app.route('/admin/metrics')
   def admin_metrics():
       # Check active database connections
       from sqlalchemy import text
       result = db.session.execute(text("""
           SELECT count(*) FROM pg_stat_activity 
           WHERE datname = current_database()
       """))
       active_connections = result.scalar()
       return jsonify({
           'active_db_connections': active_connections,
           'max_connections': 100,  # Update based on your plan
           'usage_percent': (active_connections / 100) * 100
       })
   ```

---

## ⚠️ Warning Signs of Capacity Issues

### **Symptoms:**
1. **Database Connection Errors**:
   - `OperationalError: too many connections`
   - `Connection pool exhausted`

2. **Slow Response Times**:
   - Pages taking >5 seconds to load
   - Timeout errors

3. **Vercel Function Timeouts**:
   - 504 Gateway Timeout errors
   - Function execution timeouts

### **When to Scale:**
- Active connections consistently >80% of limit
- Users reporting slow performance
- Frequent timeout errors
- Database query time >1 second

---

## 🎯 Recommended Scaling Path

### **Phase 1: Current (Free Tier)**
- **Capacity**: ~50-75 concurrent users
- **Cost**: $0/month
- **Action**: Optimize connection pooling

### **Phase 2: Small Scale (Recommended)**
- **NeonDB Launch**: $19/month
- **Vercel Pro**: $20/month
- **Total**: $39/month
- **Capacity**: ~150-200 concurrent users
- **Action**: Upgrade when you have 30+ regular users

### **Phase 3: Medium Scale**
- **NeonDB Scale**: $69/month
- **Vercel Pro**: $20/month
- **Total**: $89/month
- **Capacity**: ~400-450 concurrent users
- **Action**: Upgrade when you have 100+ regular users

### **Phase 4: Large Scale**
- **NeonDB Custom**: Custom pricing
- **Vercel Enterprise**: Custom pricing
- **Capacity**: 1,000+ concurrent users
- **Action**: Consider dedicated infrastructure

---

## 📝 Summary

### **Current Capacity:**
- **Concurrent Logged-in Users**: **~50-75 users** (safe estimate)
- **Peak Capacity**: **~80-100 users** (with connection pooling)
- **Bottleneck**: NeonDB connection limit (100 connections)

### **Quick Answer:**
**You can currently support approximately 50-75 users logged in simultaneously** on the free tier. This assumes normal usage patterns (browsing, taking quizzes, viewing results).

### **To Support More Users:**
1. **Immediate**: Optimize connection pooling (free)
2. **Short-term**: Upgrade NeonDB to Launch tier ($19/month) → **150-180 users**
3. **Medium-term**: Upgrade both NeonDB + Vercel ($39/month) → **150-200 users**
4. **Long-term**: Scale tier ($89/month) → **400-450 users**

---

## 🔧 Next Steps

1. **Monitor Current Usage**:
   - Check NeonDB dashboard for active connections
   - Monitor Vercel analytics for function invocations

2. **Optimize Current Setup**:
   - Implement connection pooling optimizations
   - Add database indexes
   - Cache frequently accessed data

3. **Plan for Growth**:
   - Set up alerts for high connection usage
   - Prepare upgrade path when needed
   - Consider implementing Redis for session management

---

**Last Updated**: Based on current Vercel + NeonDB free tier configuration

