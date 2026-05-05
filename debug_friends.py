from app import app
from models.models import db, User, friends_association
from sqlalchemy import text

def debug():
    with app.app_context():
        print("\n" + "="*50)
        print("DATABASE DIAGNOSTIC")
        print("="*50)
        
        # 1. Get current user (Kushal)
        user = User.query.filter_by(username='Kushal').first()
        if not user:
            print("User 'Kushal' not found!")
            return
        
        print(f"User: {user.username} (ID: {user.id})")
        
        # 2. Check relationship property
        print(f"\nRelationship current_user.friends:")
        try:
            rel_friends = user.friends.all()
            print(f"Found {len(rel_friends)} friends via relationship")
            for f in rel_friends:
                print(f"   - {f.username} (ID: {f.id})")
        except Exception as e:
            print(f"Relationship error: {e}")

        # 3. Check raw association table
        print(f"\nRaw friends_association table:")
        try:
            rows = db.session.execute(text(f"SELECT * FROM friends_association WHERE user_id = {user.id}")).fetchall()
            print(f"Found {len(rows)} rows in association table")
            for row in rows:
                print(f"   - User {row[0]} is friends with User {row[1]}")
        except Exception as e:
            print(f"SQL error: {e}")

        print("="*50 + "\n")

if __name__ == "__main__":
    debug()
