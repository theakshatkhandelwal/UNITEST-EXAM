# 🚀 UNITEST.IN Capacity - Quick Answer

## ❓ Question: How many users can be logged in at a single time?

### ✅ **Answer: ~50-75 concurrent logged-in users** (on free tier)

---

## 📊 Current Capacity Breakdown

### **Free Tier Limits:**
- **Vercel**: ~100-200 concurrent requests (auto-scales)
- **NeonDB**: 100 database connections (BOTTLENECK)
- **Safe Capacity**: ~50-75 concurrent users

### **Why This Number?**
- Each logged-in user uses ~1-2 database connections
- Connection pooling helps, but active users need more connections
- Formula: `(100 connections - 10 reserved) / 1.2 per user ≈ 75 users`

---

## 🔍 How to Check Your Current Usage

### **Option 1: Admin Metrics Endpoint** (New!)
Visit: **https://unitest.in/admin/metrics**

This will show:
- Active database connections
- Max connections available
- Usage percentage
- Estimated capacity
- Recently active users

**Note**: You need admin access. See `ADMIN_SETUP_GUIDE.md` to set yourself as admin.

### **Option 2: NeonDB Dashboard**
1. Go to https://console.neon.tech
2. Select your project
3. Check "Metrics" → "Active Connections"

### **Option 3: Vercel Dashboard**
1. Go to https://vercel.com
2. Select your project
3. Check "Analytics" → "Function Invocations"

---

## 📈 Capacity by Activity Level

| Activity | Connections/User | Max Users |
|----------|----------------|-----------|
| **Browsing Dashboard** | 0.5-1 | ~80-100 |
| **Taking Quiz** | 1-2 | ~50-75 |
| **AI Question Generation** | 2-3 | ~30-50 |
| **Peak Usage (All Active)** | 2-3 | ~30-50 |

**Safe Estimate**: **50-75 concurrent users**

---

## 🚀 How to Support More Users

### **Quick Win (Free)**
- Optimize connection pooling
- Add database indexes
- Cache frequently accessed data
- **Result**: +20-30% capacity (~60-90 users)

### **Upgrade Path**

| Tier | Cost | Capacity | When to Upgrade |
|------|------|----------|-----------------|
| **Current (Free)** | $0 | 50-75 users | - |
| **NeonDB Launch** | $19/mo | 150-180 users | 30+ regular users |
| **NeonDB Scale** | $69/mo | 400-450 users | 100+ regular users |
| **NeonDB + Vercel Pro** | $39/mo | 150-200 users | Better performance |

---

## ⚠️ Warning Signs

You're approaching capacity limits when you see:
- ❌ `OperationalError: too many connections`
- ❌ Pages taking >5 seconds to load
- ❌ 504 Gateway Timeout errors
- ❌ Database connections >80% of limit

**Action**: Check `/admin/metrics` and consider upgrading.

---

## 📝 Summary

**Current Capacity**: **~50-75 concurrent logged-in users**

**Bottleneck**: NeonDB connection limit (100 connections)

**To Check Usage**: Visit https://unitest.in/admin/metrics (admin required)

**To Scale**: Upgrade NeonDB Launch tier ($19/month) → **150-180 users**

---

**For detailed analysis, see**: `CAPACITY_ANALYSIS.md`

