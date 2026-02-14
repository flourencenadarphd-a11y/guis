# 🔄 Database Update Required

## ⚠️ Important: Database Schema Update

The database schema has been updated to include `delivery_mode` field. 

### What Changed:
- Added `delivery_mode` column to `programs` table
- Values: "online", "offline", "hybrid", "bilingual"

### Automatic Update:
The database will automatically update when you:
1. Delete the old database file (`guis.db`)
2. Run the app again (it will create new schema)

### Manual Update (if needed):
If you want to keep existing data, run this SQL:
```sql
ALTER TABLE programs ADD COLUMN delivery_mode VARCHAR DEFAULT 'offline';
```

### Or Delete and Recreate:
```bash
# Delete old database
rm guis.db  # Linux/Mac
del guis.db  # Windows

# Run app - it will create new database with updated schema
streamlit run streamlit_app.py
```

---

**The app will work correctly after database is updated!**

