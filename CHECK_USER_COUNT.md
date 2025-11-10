# 📊 How to Check User Signups in Neon DB

## Method 1: Using Neon DB SQL Editor (Recommended)

### Step 1: Access Neon DB Dashboard
1. Go to [https://console.neon.tech](https://console.neon.tech)
2. Log in to your account
3. Select your project (the one connected to your UNITEST-EXAM app)

### Step 2: Open SQL Editor
1. In your NeonDB project dashboard, click on **"SQL Editor"** in the left sidebar
2. Or click the **"Query"** button at the top

### Step 3: Run SQL Queries

#### Query 1: Count Total Users
```sql
SELECT COUNT(*) AS total_users FROM "user";
```

#### Query 2: Count Users by Role
```sql
SELECT 
    role,
    COUNT(*) AS user_count
FROM "user"
GROUP BY role
ORDER BY user_count DESC;
```

#### Query 3: Count Users by Signup Date
```sql
SELECT 
    DATE(created_at) AS signup_date,
    COUNT(*) AS users_count
FROM "user"
GROUP BY DATE(created_at)
ORDER BY signup_date DESC
LIMIT 30;
```

#### Query 4: Get All Users with Details
```sql
SELECT 
    id,
    username,
    email,
    role,
    created_at
FROM "user"
ORDER BY created_at DESC
LIMIT 100;
```

#### Query 5: Count Users This Month
```sql
SELECT COUNT(*) AS users_this_month
FROM "user"
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

#### Query 6: Count Users This Week
```sql
SELECT COUNT(*) AS users_this_week
FROM "user"
WHERE created_at >= DATE_TRUNC('week', CURRENT_DATE);
```

#### Query 7: Count Users Today
```sql
SELECT COUNT(*) AS users_today
FROM "user"
WHERE DATE(created_at) = CURRENT_DATE;
```

#### Query 8: User Growth Over Time (Last 30 Days)
```sql
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS new_users,
    SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) AS total_users
FROM "user"
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

#### Query 9: Recent Signups (Last 10 Users)
```sql
SELECT 
    id,
    username,
    email,
    role,
    created_at
FROM "user"
ORDER BY created_at DESC
LIMIT 10;
```

#### Query 10: Total Users, Students, and Teachers
```sql
SELECT 
    COUNT(*) AS total_users,
    SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) AS students,
    SUM(CASE WHEN role = 'teacher' THEN 1 ELSE 0 END) AS teachers
FROM "user";
```

---

## Method 2: Using Admin Dashboard Route (In-App)

You can also add an admin route to your app to view user statistics. See the admin route in `app.py` (if added).

### Access Admin Dashboard
1. Make sure you're logged in as a user
2. Visit: `https://your-app-url.vercel.app/admin/users`
3. You'll see:
   - Total users count
   - Users by role
   - Recent signups
   - Signups over time

---

## Method 3: Using Python Script (Local)

Create a Python script to connect to your database and query users:

```python
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Query total users
result = session.execute(text('SELECT COUNT(*) FROM "user"'))
total_users = result.scalar()
print(f"Total Users: {total_users}")

# Query users by role
result = session.execute(text('''
    SELECT role, COUNT(*) 
    FROM "user" 
    GROUP BY role
'''))
for row in result:
    print(f"{row[0]}: {row[1]}")

session.close()
```

---

## Quick Reference

### Common Queries

| What to Check | SQL Query |
|---------------|-----------|
| Total Users | `SELECT COUNT(*) FROM "user";` |
| Users by Role | `SELECT role, COUNT(*) FROM "user" GROUP BY role;` |
| Recent Signups | `SELECT * FROM "user" ORDER BY created_at DESC LIMIT 10;` |
| Users This Month | `SELECT COUNT(*) FROM "user" WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);` |
| Users Today | `SELECT COUNT(*) FROM "user" WHERE DATE(created_at) = CURRENT_DATE;` |

### Notes
- Table name is `"user"` (lowercase, in quotes because "user" is a reserved word in PostgreSQL)
- The `created_at` field stores the signup timestamp
- Users have a `role` field that can be 'student' or 'teacher'

---

## Troubleshooting

### If you get "relation user does not exist" error:
- Check that you're connected to the correct database
- Verify the table name (it should be `"user"` with lowercase and quotes)
- Check that users have actually signed up (table might be empty)

### If you can't see the SQL Editor:
- Make sure you're logged into the correct Neon DB account
- Check that you have admin access to the project
- Try refreshing the page

### If queries return no results:
- The table might be empty (no users have signed up yet)
- Check that you're querying the correct database
- Verify your app is using the same database

---

**Need more help?** Check the Neon DB documentation at [https://neon.tech/docs](https://neon.tech/docs)

