"""
Database migration utility
Handles schema updates for existing databases
"""
from sqlalchemy import create_engine, text, inspect
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database(db_path: str = None):
    """
    Migrate database to add new columns
    """
    if db_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, "guis.db")
    
    if not os.path.exists(db_path):
        logger.info("Database doesn't exist yet. Will be created with correct schema.")
        return
    
    try:
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        inspector = inspect(engine)
        
        # Check if programs table exists
        if 'programs' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('programs')]
            
            if 'delivery_mode' not in columns:
                logger.info("Adding delivery_mode column to programs table...")
                with engine.begin() as conn:
                    # SQLite doesn't support DEFAULT in ALTER TABLE easily
                    # So we add column, then update existing rows
                    conn.execute(text("ALTER TABLE programs ADD COLUMN delivery_mode VARCHAR"))
                    conn.execute(text("UPDATE programs SET delivery_mode = 'offline' WHERE delivery_mode IS NULL"))
                    conn.commit()
                logger.info("✅ Migration complete: delivery_mode column added")
            else:
                logger.info("✅ Database already has delivery_mode column")
        else:
            logger.info("Programs table doesn't exist yet. Will be created with correct schema.")
    
    except Exception as e:
        logger.error(f"Migration error: {e}")
        # If migration fails, database will be recreated on next run
        logger.info("Database will be recreated with correct schema on next app start")


if __name__ == "__main__":
    migrate_database()

