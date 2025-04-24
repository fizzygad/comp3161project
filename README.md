# DBMS Project API

## Deployment
1. Set environment variables in Railway:
   ```ini
   MYSQLHOST={{railway_mysql_host}}
   MYSQLUSER={{railway_mysql_user}}
   MYSQLPASSWORD={{railway_mysql_password}}
   MYSQLDATABASE=railway
   MYSQLPORT={{railway_mysql_port}}
   ```

2. Initialize database:
   ```bash
   railway run python migrate.py
   ```

3. Access API: `https://dbmsproject.up.railway.app`