# 👥 Account Management Database Guide

Complete guide for managing user accounts in the HSIRB Study Management System.

## 📊 Database Structure

### Main Tables

**`users`** - Main user accounts
- `id` (UUID, primary key)
- `email` (unique, indexed)
- `first_name`, `last_name`
- `role` (admin, irb_member, researcher, instructor, participant)
- `is_active`, `is_staff`, `is_superuser`
- `email_verified_at`
- `created_at`, `updated_at`
- `password` (hashed)

**`profiles`** - Extended user information
- `id` (UUID, primary key)
- `user_id` (foreign key to users)
- `phone`, `date_of_birth`, `student_id`
- `gender`, `languages` (JSON)
- `department`, `lab_name` (for researchers)
- `no_show_count`, `is_banned`, `ban_reason` (for participants)

**`email_verification_tokens`** - Email verification
- `id`, `user_id`, `token`
- `created_at`, `expires_at`, `used_at`

---

## 🔧 Method 1: Django Admin (Easiest)

### Access Admin Panel

1. **URL:** https://bayoupal.nicholls.edu/hsirb/admin/
2. **Login** with superuser credentials
3. **Navigate to:** "Users" or "User Profiles"

### Create User via Admin

1. Click **"Users"** → **"Add User"**
2. Fill in:
   - Email
   - First name, Last name
   - Role
   - Password
3. Click **"Save"**

### Manage Users

- **View all users:** Users list
- **Filter by role:** Use filter dropdown
- **Search:** By email, name
- **Edit:** Click on user
- **Deactivate:** Uncheck "Active" checkbox

---

## 🐍 Method 2: Django Shell (Command Line)

### Access Django Shell

```bash
ssh bayoupal
cd ~/hsirb-system
source venv/bin/activate
python manage.py shell
```

### Common Operations

#### Create User

```python
from apps.accounts.models import User, Profile

# Create researcher
user = User.objects.create_user(
    email='researcher@nicholls.edu',
    password='secure_password',
    first_name='John',
    last_name='Doe',
    role='researcher'
)

# Create participant
participant = User.objects.create_user(
    email='student@my.nicholls.edu',
    password='secure_password',
    first_name='Jane',
    last_name='Smith',
    role='participant'
)
```

#### List Users

```python
# All users
User.objects.all()

# By role
User.objects.filter(role='researcher')
User.objects.filter(role='participant')

# Active users only
User.objects.filter(is_active=True)

# Search by email
User.objects.filter(email__icontains='nicholls')
```

#### Update User

```python
user = User.objects.get(email='researcher@nicholls.edu')
user.first_name = 'Updated Name'
user.save()

# Update profile
user.profile.department = 'Psychology'
user.profile.save()
```

#### Deactivate User

```python
user = User.objects.get(email='user@nicholls.edu')
user.is_active = False
user.save()
```

#### Change Password

```python
user = User.objects.get(email='user@nicholls.edu')
user.set_password('new_password')
user.save()
```

#### Create Superuser

```python
from apps.accounts.models import User
User.objects.create_superuser(
    email='admin@nicholls.edu',
    password='admin_password',
    first_name='Admin',
    last_name='User'
)
```

---

## 🗄️ Method 3: Direct PostgreSQL Queries

### Connect to Database

```bash
ssh bayoupal
psql -U hsirb_user -d hsirb_db -h localhost
# Enter password when prompted (from ~/hsirb-db-password.txt)
```

### Common Queries

#### View All Users

```sql
SELECT 
    email, 
    first_name, 
    last_name, 
    role, 
    is_active, 
    created_at 
FROM users 
ORDER BY created_at DESC;
```

#### Count Users by Role

```sql
SELECT role, COUNT(*) as count 
FROM users 
GROUP BY role;
```

#### Find User by Email

```sql
SELECT * FROM users WHERE email = 'user@nicholls.edu';
```

#### View User with Profile

```sql
SELECT 
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    p.department,
    p.student_id,
    p.no_show_count
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
WHERE u.email = 'user@nicholls.edu';
```

#### List Inactive Users

```sql
SELECT email, first_name, last_name, role, created_at
FROM users
WHERE is_active = false;
```

#### Update User Role

```sql
UPDATE users 
SET role = 'researcher' 
WHERE email = 'user@nicholls.edu';
```

#### Deactivate User

```sql
UPDATE users 
SET is_active = false 
WHERE email = 'user@nicholls.edu';
```

**⚠️ Note:** Direct SQL updates bypass Django's validation. Use Django shell or admin for safer updates.

---

## 📋 User Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| `admin` | System administrator | Full access to all features |
| `irb_member` | IRB committee member | Can review protocols, make decisions |
| `researcher` | Principal investigator | Can create studies, submit protocols |
| `instructor` | Course instructor | Can view student participation |
| `participant` | Research participant | Can browse studies, sign up, earn credits |

---

## 🔍 Quick Reference Commands

### Via SSH (Django Shell)

```bash
ssh bayoupal
cd ~/hsirb-system
source venv/bin/activate

# Create superuser
python manage.py createsuperuser

# List all users
python manage.py shell -c "from apps.accounts.models import User; print([u.email for u in User.objects.all()])"

# Count users by role
python manage.py shell -c "from apps.accounts.models import User; from collections import Counter; print(Counter([u.role for u in User.objects.all()]))"
```

### Via PostgreSQL

```bash
ssh bayoupal
psql -U hsirb_user -d hsirb_db -h localhost

# Quick queries
\dt                    # List all tables
\d users              # Describe users table
\d profiles           # Describe profiles table
SELECT COUNT(*) FROM users;
SELECT role, COUNT(*) FROM users GROUP BY role;
\q                    # Quit
```

---

## 🛠️ Management Scripts

### Create Multiple Users (Example)

```python
# In Django shell
from apps.accounts.models import User

users_data = [
    {'email': 'researcher1@nicholls.edu', 'first_name': 'John', 'last_name': 'Doe', 'role': 'researcher'},
    {'email': 'researcher2@nicholls.edu', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'researcher'},
    {'email': 'student1@my.nicholls.edu', 'first_name': 'Alice', 'last_name': 'Johnson', 'role': 'participant'},
]

for user_data in users_data:
    User.objects.create_user(
        password='temp_password_123',
        **user_data
    )
    print(f"Created: {user_data['email']}")
```

---

## 🔒 Security Notes

- **Passwords:** Stored as hashes (never plain text)
- **Email verification:** Required for participants (optional for others)
- **Role changes:** Should be done carefully (affects permissions)
- **Deactivation:** Prevents login but preserves data
- **Deletion:** Use Django admin (cascades to related data)

---

## 📊 Useful Queries

### Active Participants Count

```sql
SELECT COUNT(*) 
FROM users 
WHERE role = 'participant' AND is_active = true;
```

### Researchers by Department

```sql
SELECT p.department, COUNT(*) as count
FROM users u
JOIN profiles p ON u.id = p.user_id
WHERE u.role = 'researcher'
GROUP BY p.department;
```

### Users Created This Month

```sql
SELECT email, first_name, last_name, role, created_at
FROM users
WHERE created_at >= date_trunc('month', CURRENT_DATE)
ORDER BY created_at DESC;
```

### Unverified Emails

```sql
SELECT email, first_name, last_name, role, created_at
FROM users
WHERE email_verified_at IS NULL
ORDER BY created_at DESC;
```

---

## 🎯 Common Tasks

### Task: Create Researcher Account

**Via Admin:**
1. Go to https://bayoupal.nicholls.edu/hsirb/admin/
2. Users → Add User
3. Fill in details, set role to "Researcher"
4. Save

**Via Shell:**
```python
User.objects.create_user(
    email='newresearcher@nicholls.edu',
    password='secure_password',
    first_name='First',
    last_name='Last',
    role='researcher'
)
```

### Task: Reset User Password

**Via Admin:**
1. Go to Users → Select user
2. Click "Change password"
3. Enter new password
4. Save

**Via Shell:**
```python
user = User.objects.get(email='user@nicholls.edu')
user.set_password('new_password')
user.save()
```

### Task: Deactivate All Inactive Participants

```python
from apps.accounts.models import User
from django.utils import timezone
from datetime import timedelta

# Deactivate participants who haven't logged in for 1 year
cutoff = timezone.now() - timedelta(days=365)
inactive = User.objects.filter(
    role='participant',
    last_login__lt=cutoff,
    is_active=True
)
count = inactive.update(is_active=False)
print(f"Deactivated {count} participants")
```

---

## 📞 Need Help?

- **Django Admin:** https://bayoupal.nicholls.edu/hsirb/admin/
- **Django Shell:** `python manage.py shell`
- **PostgreSQL:** `psql -U hsirb_user -d hsirb_db`
- **Database Password:** `cat ~/hsirb-db-password.txt` (on server)

---

**Your account management database is ready!** 👥
