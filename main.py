import sqlite3
import os
import shutil

print("""
+---------------------------+
|╔═╗╔═╗ ╦  ┬┌┬┐┌─┐╔╦╗┬─┐┬┌┬┐|
|╚═╗║═╬╗║  │ │ ├┤  ║ ├┬┘││││|
|╚═╝╚═╝╚╩═╝┴ ┴ └─┘ ╩ ┴└─┴┴ ┴|
+---------------------------+
""")
print("visit: https://github.com/g3ntrix")

def recreate_with_sequential_ids(original_db_path, new_db_path, delete_type, start_id, end_id=None):
    shutil.copyfile(original_db_path, new_db_path)
    conn = sqlite3.connect(new_db_path)
    cursor = conn.cursor()

    try:
        if delete_type == 'single':
            cursor.execute("DELETE FROM inbounds WHERE id = ?", (start_id,))
        elif delete_type == 'range':
            cursor.execute("DELETE FROM inbounds WHERE id BETWEEN ? AND ?", (start_id, end_id))

        conn.commit()
        cursor.execute("PRAGMA table_info(inbounds)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        columns_str = ', '.join(columns)
        placeholders = ', '.join('?' * len(columns))

        if delete_type == 'single':
            cursor.execute("SELECT * FROM inbounds WHERE id != ?", (start_id,))
        elif delete_type == 'range':
            cursor.execute("SELECT * FROM inbounds WHERE id < ? OR id > ?", (start_id, end_id))

        rows = cursor.fetchall()
        cursor.execute("DELETE FROM inbounds")
        conn.commit()

        for new_id, row in enumerate(rows, start=1):
            new_row = (new_id,) + row[1:]
            cursor.execute(f"INSERT INTO inbounds ({columns_str}) VALUES ({placeholders})", new_row)

        conn.commit()

    except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
    finally:
        conn.close()

def main():
    original_db_path = 'x-ui.db'
    new_db_path = 'x-ui_modified.db'

    while True:
        print("\nMenu:")
        print("1. Delete a single row")
        print("2. Delete a range of rows")
        print("3. Exit")

        try:
            choice = int(input("Enter your choice (1, 2, or 3): "))
        except ValueError:
            print("Invalid input. Please enter a number (1, 2, or 3).")
            continue

        if choice == 1:
            try:
                start_id = int(input("Enter the ID of the row to delete: "))
                recreate_with_sequential_ids(original_db_path, new_db_path, 'single', start_id)
                print(f"Modified database saved as {new_db_path}")
                break
            except ValueError:
                print("Invalid input. Please enter a valid row ID.")
        elif choice == 2:
            try:
                start_id = int(input("Enter the start ID of the range to delete: "))
                end_id = int(input("Enter the end ID of the range to delete: "))
                recreate_with_sequential_ids(original_db_path, new_db_path, 'range', start_id, end_id)
                print(f"Modified database saved as {new_db_path}")
                break
            except ValueError:
                print("Invalid input. Please enter valid row IDs.")
        elif choice == 3:
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
