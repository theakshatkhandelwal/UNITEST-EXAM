# 🔗 Quick Access Links

## 📊 User Statistics
- **Admin Dashboard**: https://unitest.in/admin/users
- **Neon DB Console**: https://console.neon.tech

## 🏠 Main Application
- **Homepage**: https://unitest.in
- **Dashboard**: https://unitest.in/dashboard
- **Login**: https://unitest.in/login
- **Signup**: https://unitest.in/signup

## 📚 Documentation
- **User Count Guide**: See `CHECK_USER_COUNT.md`
- **Deployment Guide**: See `VERCEL_DEPLOYMENT_GUIDE.md`
- **Neon DB Migration**: See `NEONDB_MIGRATION_GUIDE.md`

## 🔍 Quick SQL Queries (for Neon DB)
```sql
-- Total Users
SELECT COUNT(*) FROM "user";

-- Users by Role
SELECT role, COUNT(*) FROM "user" GROUP BY role;

-- Users This Month
SELECT COUNT(*) FROM "user" 
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);

-- Recent Signups (Last 10)
SELECT * FROM "user" ORDER BY created_at DESC LIMIT 10;
```

