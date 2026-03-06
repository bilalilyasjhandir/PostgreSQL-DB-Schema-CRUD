import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "dbname": "task_db",
    "user": "postgres",
    "password": "1234"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def pause():
    input("\n Press Enter to continue...")

def ask(prompt, required=True, default=None):
    """Ask user for input, optionally with a default."""
    display = f"{prompt}"
    if default is not None:
        display += f"[leave blank = {default}]"
    display += ": "
    while True:
        val = input(display).strip()
        if val:
            return val
        if not required or default is not None:
            return default
        print("This field is required.")

def print_header(title):
    print(f"{title}")

def print_rows(rows):
    if not rows:
        print("\n No records found)")
        return
    for i, row in enumerate(rows, 1):
        print(f"\n Record {i}")
        for k, v in row.items():
            print(f"{k:20s}: {v}")

def company_create(cur):
    print_header("CREATE — Company")
    name = ask("Company name")
    email = ask("Company email")
    website = ask("Website URL", required=False, default=None)
    cur.execute("INSERT INTO company (name, email, website) VALUES (%s, %s, %s) RETURNING id, name, email, website, created_at", (name, email, website))
    row = cur.fetchone()
    print("\n Company created!")
    print_rows([row])

def company_read(cur):
    print_header("READ — Company")
    print("1. View all companies")
    print("2. Search by name or email")
    choice = ask("Choose option")
    if choice == "1":
        cur.execute("SELECT id, name, email, website, is_active, created_at FROM company ORDER BY created_at DESC")
    else:
        term = ask("Enter name or email to search")
        cur.execute("SELECT id, name, email, website, is_active, created_at FROM company WHERE name ILIKE %s OR email ILIKE %s ORDER BY created_at DESC", (f"%{term}%", f"%{term}%"))
    print_rows(cur.fetchall())

def company_update(cur):
    print_header("UPDATE — Company")
    email = ask("Enter the email of the company to update")
    cur.execute("SELECT * FROM company WHERE email = %s", (email,))
    row = cur.fetchone()
    if not row:
        print("No company found with that email.")
        return
    print("\n Current values:")
    print_rows([row])
    print("\n Enter new values (leave blank to keep current):")
    new_name = ask("New name",    required=False, default=row["name"])
    new_website = ask("New website", required=False, default=row["website"])
    new_active = ask("Active? (true/false)", required=False, default=str(row["is_active"]).lower())
    cur.execute("UPDATE company SET name = %s, website = %s, is_active = %s WHERE email = %s RETURNING id, name, email, website, is_active", (new_name, new_website, new_active == "true", email))
    print("\n Company updated!")
    print_rows([cur.fetchone()])

def company_delete(cur):
    print_header("DELETE — Company")
    print("Deleting a company will SET NULL on linked users.")
    email = ask("Enter the email of the company to delete")
    cur.execute("SELECT id, name, email FROM company WHERE email = %s", (email,))
    row = cur.fetchone()
    if not row:
        print("No company found with that email.")
        return
    confirm = ask(f"Are you sure you want to delete '{row['name']}'? (yes/no)")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    cur.execute("DELETE FROM company WHERE email = %s", (email,))
    print("Company deleted.")

def users_create(cur):
    print_header("CREATE — User")
    email = ask("User email")
    password = ask("Password (will be stored as-is — hash it yourself if needed)")
    full_name = ask("Full name")
    company_email = ask("Company email to link (leave blank to skip)", required=False)
    tone = ask("Tone preference (casual/formal)", required=False, default="casual")
    loom_url = ask("Loom video URL", required=False)
    upwork_id = ask("Upwork agency ID", required=False)
    company_id = None
    if company_email:
        cur.execute("SELECT id FROM company WHERE email = %s", (company_email,))
        c = cur.fetchone()
        if not c:
            print("Company not found — user will be created without a company link.")
        else:
            company_id = c["id"]
    cur.execute("INSERT INTO users (company_id, email, password_hash, full_name, loom_video_url, upwork_agency_id, tone_preference) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, email, full_name, tone_preference, is_active, created_at", (company_id, email, password, full_name, loom_url, upwork_id, tone))
    print("\n User created!")
    print_rows([cur.fetchone()])

def users_read(cur):
    print_header("READ — Users")
    print("1. View all users")
    print("2. Search by name or email")
    print("3. View users of a specific company")
    choice = ask("Choose option")
    if choice == "1":
        cur.execute("SELECT u.id, u.full_name, u.email, u.tone_preference, u.is_active, c.name AS company_name FROM users u LEFT JOIN company c ON u.company_id = c.id ORDER BY u.created_at DESC")
    elif choice == "2":
        term = ask("Enter name or email to search")
        cur.execute("SELECT u.id, u.full_name, u.email, u.tone_preference, u.is_active, c.name AS company_name FROM users u LEFT JOIN company c ON u.company_id = c.id WHERE u.full_name ILIKE %s OR u.email ILIKE %s", (f"%{term}%", f"%{term}%"))
    else:
        company_email = ask("Enter company email")
        cur.execute("SELECT u.id, u.full_name, u.email, u.tone_preference, u.is_active FROM users u JOIN company c ON u.company_id = c.id WHERE c.email = %s", (company_email,))
    print_rows(cur.fetchall())

def users_update(cur):
    print_header("UPDATE — User")
    email = ask("Enter the email of the user to update")
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    if not row:
        print("No user found with that email.")
        return
    print("\n Current values:")
    print_rows([row])
    print("\n Enter new values (leave blank to keep current):")
    new_name = ask("New full name", required=False, default=row["full_name"])
    new_tone = ask("New tone preference", required=False, default=row["tone_preference"])
    new_loom = ask("New Loom URL", required=False, default=row["loom_video_url"])
    new_active = ask("Active? (true/false)", required=False, default=str(row["is_active"]).lower())
    cur.execute("UPDATE users SET full_name = %s, tone_preference = %s, loom_video_url = %s, is_active = %s WHERE email = %s RETURNING id, email, full_name, tone_preference, is_active", (new_name, new_tone, new_loom, new_active == "true", email))
    print("\n User updated!")
    print_rows([cur.fetchone()])

def users_delete(cur):
    print_header("DELETE — User")
    print("Deleting a user will also delete their profile (CASCADE).")
    email = ask("Enter the email of the user to delete")
    cur.execute("SELECT id, full_name, email FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    if not row:
        print("No user found with that email.")
        return
    confirm = ask(f"Are you sure you want to delete '{row['full_name']}'? (yes/no)")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    cur.execute("DELETE FROM users WHERE email = %s", (email,))
    print("User deleted.")

def profile_create(cur):
    print_header("CREATE — Profile")
    user_email = ask("Email of the user this profile belongs to")
    cur.execute("SELECT id, company_id FROM users WHERE email = %s", (user_email,))
    user = cur.fetchone()
    if not user:
        print("No user found with that email.")
        return
    headline = ask("Headline (e.g. 'Senior Developer')", required=False)
    bio = ask("Bio / about text", required=False)
    skills_raw = ask("Skills (comma-separated, e.g. Python, SQL)", required=False)
    hourly_rate = ask("Hourly rate (e.g. 45.00)", required=False)
    skills = [s.strip() for s in skills_raw.split(",")] if skills_raw else None
    rate = float(hourly_rate) if hourly_rate else None
    cur.execute("INSERT INTO profile (company_id, user_id, headline, bio, skills, hourly_rate) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, headline, bio, skills, hourly_rate, created_at", (user["company_id"], user["id"], headline, bio, skills, rate))
    print("\n Profile created!")
    print_rows([cur.fetchone()])

def profile_read(cur):
    print_header("READ — Profile")
    print("1. View all profiles")
    print("2. View profile of a specific user (by email)")
    choice = ask("Choose option")
    if choice == "1":
        cur.execute("SELECT p.id, u.full_name, u.email, p.headline, p.bio, p.skills, p.hourly_rate, p.created_at FROM profile p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC")
    else:
        user_email = ask("Enter user email")
        cur.execute("SELECT p.id, u.full_name, u.email, p.headline, p.bio, p.skills, p.hourly_rate, p.created_at FROM profile p JOIN users u ON p.user_id = u.id WHERE u.email = %s", (user_email,))
    print_rows(cur.fetchall())

def profile_update(cur):
    print_header("UPDATE — Profile")
    user_email = ask("Enter the email of the user whose profile you want to update")
    cur.execute("SELECT p.* FROM profile p JOIN users u ON p.user_id = u.id WHERE u.email = %s", (user_email,))
    row = cur.fetchone()
    if not row:
        print("No profile found for that user.")
        return
    print("\n Current values:")
    print_rows([row])
    print("\n Enter new values (leave blank to keep current):")
    new_headline = ask("New headline", required=False, default=row["headline"])
    new_bio = ask("New bio", required=False, default=row["bio"])
    skills_raw = ask("New skills (comma-separated)", required=False, default=",".join(row["skills"]) if row["skills"] else "")
    new_rate = ask("New hourly rate", required=False, default=str(row["hourly_rate"]))
    skills = [s.strip() for s in skills_raw.split(",")] if skills_raw else None
    rate = float(new_rate) if new_rate else None
    cur.execute("UPDATE profile SET headline = %s, bio = %s, skills = %s, hourly_rate = %s WHERE id = %s RETURNING id, headline, bio, skills, hourly_rate", (new_headline, new_bio, skills, rate, row["id"]))
    print("\n Profile updated!")
    print_rows([cur.fetchone()])

def profile_delete(cur):
    print_header("DELETE — Profile")
    user_email = ask("Enter the email of the user whose profile you want to delete")
    cur.execute("SELECT p.id FROM profile p JOIN users u ON p.user_id = u.id WHERE u.email = %s", (user_email,))
    row = cur.fetchone()
    if not row:
        print("No profile found for that user.")
        return
    confirm = ask("Are you sure you want to delete this profile?(yes/no)")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    cur.execute("DELETE FROM profile WHERE id = %s", (row["id"],))
    print("Profile deleted.")

TABLES = {
    "1": "company",
    "2": "users",
    "3": "profile"
}

OPS = {
    "1": "Create",
    "2": "Read",
    "3": "Update",
    "4": "Delete"
}

HANDLERS = {
    "company": {"Create": company_create, "Read": company_read, "Update": company_update, "Delete": company_delete},
    "users": {"Create": users_create, "Read": users_read, "Update": users_update, "Delete": users_delete},
    "profile": {"Create": profile_create, "Read": profile_read, "Update": profile_update, "Delete": profile_delete},
}

def main():
    try:
        conn = get_connection()
        print("Connected to database successfully!")
    except Exception as e:
        print(f"\n Could not connect to database: {e}")
        print("Check your DB_CONFIG settings at the top of this file.")
        return
    while True:
        print("Which table?")
        print("1. company")
        print("2. users")
        print("3. profile")
        print("0. Exit")
        t_choice = ask("Enter number").strip()
        if t_choice == "0":
            print("\n Ended!\n")
            break
        if t_choice not in TABLES:
            print("Invalid choice.")
            continue
        table = TABLES[t_choice]
        print(f"Operation on [{table}]")
        print(f"1. Create")
        print(f"2. Read")
        print(f"3. Update")
        print(f"4. Delete")
        print(f"0. Back")
        op_choice = ask("Enter number").strip()
        if op_choice == "0":
            continue
        if op_choice not in OPS:
            print("Invalid choice.")
            continue
        operation = OPS[op_choice]
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                HANDLERS[table][operation](cur)
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"\n Error: {e}")
        pause()
    conn.close()

if __name__ == "__main__":
    main()