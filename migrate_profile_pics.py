# migrate_profile_pics.py
import os
import sys
import psycopg
from psycopg.rows import dict_row
import cloudinary
import cloudinary.uploader
import logging

# -----------------------------
# Setup logging for errors
# -----------------------------
logging.basicConfig(filename='migration_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------
# Cloudinary Configuration
# -----------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return psycopg.connect(database_url, row_factory=dict_row)

# -----------------------------
# Migration Function
# -----------------------------
def migrate_existing_users():
    """Migrate existing users' profile pics to Cloudinary"""
    print("Starting migration of existing profile pictures...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, profile_pic 
            FROM users 
        """)
        
        users = cur.fetchall()
        print(f"Found {len(users)} users in the database")
        
        migrated_count = 0
        skipped_count = 0
        failed_count = 0
        
        for user in users:
            user_id = user['id']
            old_pic = user['profile_pic']
            
            # Skip if already Cloudinary URL
            if old_pic.startswith("http"):
                print(f"→ User {user_id} already migrated, skipping")
                skipped_count += 1
                continue
            
            filepath = os.path.join('static', 'uploads', old_pic)
            
            if os.path.exists(filepath):
                try:
                    # Upload to Cloudinary (server-side safe)
                    with open(filepath, 'rb') as f:
                        result = cloudinary.uploader.upload(
                            f,
                            folder="profile_pics",
                            public_id=f"user_migrated_{user_id}",
                            overwrite=True,
                            transformation={
                                'width': 500,
                                'height': 500,
                                'crop': 'fill'
                            }
                        )
                    
                    # Update database with Cloudinary URL
                    cur.execute(
                        "UPDATE users SET profile_pic = %s WHERE id = %s",
                        (result["secure_url"], user_id)
                    )
                    
                    # Optional: delete local file
                    # os.remove(filepath)
                    
                    print(f"✓ Migrated user {user_id}: {old_pic} → Cloudinary")
                    migrated_count += 1
                    
                except Exception as e:
                    logging.error(f"User {user_id} migration failed: {e}", exc_info=True)
                    print(f"✗ Failed to migrate user {user_id}, check migration_errors.log")
                    failed_count += 1
            else:
                # File not found → set default
                cur.execute(
                    "UPDATE users SET profile_pic = %s WHERE id = %s",
                    ("https://res.cloudinary.com/demo/image/upload/v1234567890/profile_pics/default-avatar.png", user_id)
                )
                print(f"⚠ File not found for user {user_id}, set to default")
                skipped_count += 1
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*50)
        print("MIGRATION SUMMARY:")
        print(f"Total users processed: {len(users)}")
        print(f"Successfully migrated: {migrated_count}")
        print(f"Skipped (already migrated or file missing): {skipped_count}")
        print(f"Failed: {failed_count}")
        print("="*50)
        
    except Exception as e:
        logging.error(f"Migration error: {e}", exc_info=True)
        print(f"Migration error: {e}")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == '__main__':
    if not os.environ.get('DATABASE_URL'):
        print("Please set DATABASE_URL environment variable")
        sys.exit(1)
    
    migrate_existing_users()