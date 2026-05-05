from app import app
from models.models import db
from sqlalchemy import text

def fix_database():
    with app.app_context():
        try:
            print("Checking database for missing columns...")
            # SQL command to add the mobile column if it doesn't exist
            db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mobile VARCHAR(15);"))
            db.session.commit()
            print("Successfully added 'mobile' column to 'users' table!")
        except Exception as e:
            db.session.rollback()
            print("Error updating database:")
            print(str(e))

if __name__ == "__main__":
    fix_database()
