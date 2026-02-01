---
description: Database migration workflow. Safe schema changes, rollback strategies, zero-downtime migrations.
---

# /migrate - Database Migration Workflow

Safe database schema changes with rollback support.

## Steps

### 1. Plan Migration
Ask the user:
- What schema change is needed?
- Is this additive or breaking?
- What's the data volume?
- Can we have downtime?

### 2. Assess Risk

| Change Type | Risk | Strategy |
|-------------|------|----------|
| Add column (nullable) | Low | Direct migration |
| Add column (non-null) | Medium | Add nullable → backfill → add constraint |
| Rename column | High | Dual-write → migrate → remove old |
| Drop column | Medium | Stop using → deploy → drop |
| Add index | Medium | CREATE INDEX CONCURRENTLY |
| Change type | High | Add new column → migrate → swap |

### 3. Create Migration

**Node.js (Prisma):**
```bash
npx prisma migrate dev --name add_user_status
```

**Python (Alembic):**
```bash
alembic revision --autogenerate -m "add user status"
alembic upgrade head
```

### 4. Zero-Downtime Pattern

For breaking changes:
1. **Expand**: Add new structure alongside old
2. **Migrate**: Move data to new structure
3. **Contract**: Remove old structure

```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN status VARCHAR(20);

-- Step 2: Backfill
UPDATE users SET status = 'active' WHERE status IS NULL;

-- Step 3: Add constraint (after code deployed)
ALTER TABLE users ALTER COLUMN status SET NOT NULL;
```

### 5. Test Migration

```bash
# Test on copy of production data
pg_dump production_db | psql test_db
npm run migrate -- --dry-run

# Verify data integrity
SELECT COUNT(*) FROM users WHERE status IS NULL;
```

### 6. Deploy

1. Run migration in staging
2. Verify application works
3. Run migration in production
4. Monitor for errors

### 7. Rollback Plan

Always have rollback ready:
```sql
-- rollback.sql
ALTER TABLE users DROP COLUMN status;
```

```bash
# Prisma
npx prisma migrate resolve --rolled-back migration_name

# Alembic
alembic downgrade -1
```

## Migration Checklist

- [ ] Migration tested on staging
- [ ] Rollback script prepared
- [ ] Backup taken before migration
- [ ] Team notified of migration window
- [ ] Monitoring in place
- [ ] Migration executed successfully
- [ ] Application verified working
