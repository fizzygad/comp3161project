import mysql.connector
import bcrypt
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Connect to the database
def connectDB():
    return mysql.connector.connect(
        host="localhost",
        user="UWI",
        password="Database1",
        database="project"
    )

# Function to hash a single user password
def hash_password(user):
    user_id, plain_password = user
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return (hashed_password, user_id)

def update_passwords_in_batches(batch_size=500, max_workers=8):
    cnx = connectDB()
    cursor = cnx.cursor()
    total_users=1
    
    while total_users!=0:
        # Get all users who don't already have a hashed password (rough check)
        cursor.execute("SELECT user_id, pswrd FROM users WHERE pswrd NOT LIKE '$2b$%'")
        users = cursor.fetchall()
        total_users = len(users)
        print(f"Found {total_users} users to update.")
        tot=users[:10000]
    
        if total_users == 0:
            print("Nothing to update!")
            return

        # Set up the progress bar
        progress_bar = tqdm(total=total_users, desc="Hashing passwords", unit="user")

        # Use ThreadPoolExecutor for parallel hashing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = [executor.submit(hash_password, user) for user in tot]
        
            # Collect results as they complete
            updates = []
            for future in as_completed(futures):
                hashed_password, user_id = future.result()
                updates.append((hashed_password, user_id))
                progress_bar.update(1)
    
        progress_bar.close()

        # Now update database in batches
        print("Updating database...")
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            update_query = "UPDATE users SET pswrd = %s WHERE user_id = %s"
            cursor.executemany(update_query, batch)
            cnx.commit()
            print("Batch committed")

        print("All passwords updated successfully!")
    
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    update_passwords_in_batches(batch_size=1000, max_workers=8)
