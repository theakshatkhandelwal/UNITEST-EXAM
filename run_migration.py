import os
from app import app, db, init_db

def run_standalone_migration():
    print("🚀 Starting standalone database migration...")
    try:
        with app.app_context():
            init_db()
            print("✅ Migration completed successfully!")
            print("You can now start your Flask app and login as a student.")
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_standalone_migration()
