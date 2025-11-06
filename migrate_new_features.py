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
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        conn = db.engine.connect()
        trans = conn.begin()
        
        try:
            print("Starting database migration...")
            
            # Add columns to quiz_question
            print("\n📝 Adding columns to quiz_question table...")
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN test_cases_json TEXT;"))
                print("  ✅ Added test_cases_json")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  test_cases_json already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN language_constraints TEXT;"))
                print("  ✅ Added language_constraints")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  language_constraints already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN time_limit_seconds INTEGER;"))
                print("  ✅ Added time_limit_seconds")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  time_limit_seconds already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN memory_limit_mb INTEGER;"))
                print("  ✅ Added memory_limit_mb")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  memory_limit_mb already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN sample_input TEXT;"))
                print("  ✅ Added sample_input")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  sample_input already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN sample_output TEXT;"))
                print("  ✅ Added sample_output")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  sample_output already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_question ADD COLUMN starter_code TEXT;"))
                print("  ✅ Added starter_code")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  starter_code already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            # Add columns to quiz_answer
            print("\n📝 Adding columns to quiz_answer table...")
            try:
                conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN code_language VARCHAR(20);"))
                print("  ✅ Added code_language")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  code_language already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN test_results_json TEXT;"))
                print("  ✅ Added test_results_json")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  test_results_json already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN passed_test_cases INTEGER DEFAULT 0;"))
                print("  ✅ Added passed_test_cases")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  passed_test_cases already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_answer ADD COLUMN total_test_cases INTEGER DEFAULT 0;"))
                print("  ✅ Added total_test_cases")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  total_test_cases already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            # Add columns to quiz_submission
            print("\n📝 Adding columns to quiz_submission table...")
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN review_unlocked_at DATETIME;"))
                print("  ✅ Added review_unlocked_at")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  review_unlocked_at already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN fullscreen_exit_flag BOOLEAN DEFAULT 0;"))
                print("  ✅ Added fullscreen_exit_flag")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  fullscreen_exit_flag already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN answered_count INTEGER DEFAULT 0;"))
                print("  ✅ Added answered_count")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  answered_count already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN question_count INTEGER DEFAULT 0;"))
                print("  ✅ Added question_count")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  question_count already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN is_full_completion BOOLEAN DEFAULT 0;"))
                print("  ✅ Added is_full_completion")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  is_full_completion already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN started_at DATETIME;"))
                print("  ✅ Added started_at")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  started_at already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            try:
                conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN completed BOOLEAN DEFAULT 0;"))
                print("  ✅ Added completed")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("  ⚠️  completed already exists")
                else:
                    print(f"  ❌ Error: {e}")
            
            trans.commit()
            print("\n✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Update your app.py with the new model fields")
            print("2. Add the new routes and functions")
            print("3. Update your templates")
            print("4. Test the features")
            
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

