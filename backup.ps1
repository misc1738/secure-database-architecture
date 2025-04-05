# PostgreSQL backup script with encryption
$DATE = Get-Date -Format "yyyy-MM-dd_HH-mm"
$BACKUP_DIR = "C:\backups\postgresql"
$DB_NAME = "app_db"
$ENCRYPTION_KEY = "your-encryption-key"

# Ensure backup directory exists
New-Item -ItemType Directory -Force -Path $BACKUP_DIR

# Perform pg_dump with encryption
$env:PGPASSWORD = "your-db-password"
pg_dump -h localhost -U postgres -d $DB_NAME | 
    openssl enc -aes-256-cbc -salt -k $ENCRYPTION_KEY -out "$BACKUP_DIR\${DB_NAME}_${DATE}.sql.enc"

# Clean up old backups (keep last 7 days)
Get-ChildItem $BACKUP_DIR -Filter "*.sql.enc" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | 
    Remove-Item