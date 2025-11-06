"""
Database Migration Script for New Features
Run this script to add all required columns for:
- 15-minute review unlock
- Coding question support
- One attempt per student
- Teacher allow retake

Usage: python migrate_new_features.py
"""

from app import app, db
from sqlalchemy import text, inspect

def migrate_database():
    with app.app_context():
        # Check database type
        is_postgres = 'postgresql' in str(db.engine.url).lower() or 'postgres' in str(db.engine.url).lower()
        is_sqlite = 'sqlite' in str(db.engine.url).lower()
        
        print(f"Database type: {'PostgreSQL' if is_postgres else 'SQLite' if is_sqlite else 'Unknown'}")
        print(f"Database URL: {str(db.engine.url).split('@')[-1] if '@' in str(db.engine.url) else 'local'}")
        
        conn = db.engine.connect()
        trans = conn.begin()
        
        try:
            print("\nStarting database migration...")
            
            # Add columns to quiz_question
            print("\n📝 Adding columns to quiz_question table...")
            
            def column_exists(table_name, column_name):
                """Check if a column exists in the table"""
                try:
                    if is_postgres:
                        result = conn.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
                        """))
                        return result.fetchone() is not None
                    else:  # SQLite
                        result = conn.execute(text(f"PRAGMA table_info({table_name});"))
                        for row in result:
                            if row[1] == column_name:
                                return True
                        return False
                except Exception:
                    return False
            
            columns_to_add = [
                ('test_cases_json', 'TEXT'),
                ('language_constraints', 'TEXT'),
                ('time_limit_seconds', 'INTEGER'),
                ('memory_limit_mb', 'INTEGER'),
                ('sample_input', 'TEXT'),
                ('sample_output', 'TEXT'),
                ('starter_code', 'TEXT')
            ]
            
            for col_name, col_type in columns_to_add:
                if not column_exists('quiz_question', col_name):
                    try:
                        conn.execute(text(f"ALTER TABLE quiz_question ADD COLUMN {col_name} {col_type};"))
                        print(f"  ✅ Added {col_name}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if "duplicate column" in error_str or "already exists" in error_str or "column" in error_str and "already" in error_str:
                            print(f"  ⚠️  {col_name} already exists")
                        else:
                            print(f"  ❌ Error adding {col_name}: {e}")
                            raise
                else:
                    print(f"  ⚠️  {col_name} already exists")
            
            # Add columns to quiz_answer
            print("\n📝 Adding columns to quiz_answer table...")
            answer_columns = [
                ('code_language', 'VARCHAR(20)'),
                ('test_results_json', 'TEXT'),
                ('passed_test_cases', 'INTEGER DEFAULT 0'),
                ('total_test_cases', 'INTEGER DEFAULT 0')
            ]
            
            for col_name, col_type in answer_columns:
                if not column_exists('quiz_answer', col_name):
                    try:
                        conn.execute(text(f"ALTER TABLE quiz_answer ADD COLUMN {col_name} {col_type};"))
                        print(f"  ✅ Added {col_name}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if "duplicate column" in error_str or "already exists" in error_str or "column" in error_str and "already" in error_str:
                            print(f"  ⚠️  {col_name} already exists")
                        else:
                            print(f"  ❌ Error adding {col_name}: {e}")
                            raise
                else:
                    print(f"  ⚠️  {col_name} already exists")
            
            # Add columns to quiz_submission
            print("\n📝 Adding columns to quiz_submission table...")
            submission_columns = [
                ('review_unlocked_at', 'TIMESTAMP' if is_postgres else 'DATETIME'),
                ('fullscreen_exit_flag', 'BOOLEAN DEFAULT FALSE' if is_postgres else 'BOOLEAN DEFAULT 0'),
                ('answered_count', 'INTEGER DEFAULT 0'),
                ('question_count', 'INTEGER DEFAULT 0'),
                ('is_full_completion', 'BOOLEAN DEFAULT FALSE' if is_postgres else 'BOOLEAN DEFAULT 0'),
                ('started_at', 'TIMESTAMP' if is_postgres else 'DATETIME'),
                ('completed', 'BOOLEAN DEFAULT FALSE' if is_postgres else 'BOOLEAN DEFAULT 0')
            ]
            
            for col_name, col_type in submission_columns:
                if not column_exists('quiz_submission', col_name):
                    try:
                        conn.execute(text(f"ALTER TABLE quiz_submission ADD COLUMN {col_name} {col_type};"))
                        print(f"  ✅ Added {col_name}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if "duplicate column" in error_str or "already exists" in error_str or "column" in error_str and "already" in error_str:
                            print(f"  ⚠️  {col_name} already exists")
                        else:
                            print(f"  ❌ Error adding {col_name}: {e}")
                            raise
                else:
                    print(f"  ⚠️  {col_name} already exists")
            
            trans.commit()
            print("\n✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Try creating a quiz again")
            print("2. All new features should now work")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database()
