import os
import sqlite3
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog
import colorama
from colorama import Fore, Style
import subprocess
import sys
import json

colorama.init(autoreset=True)

BANNER = f"""
{Fore.GREEN}+---------------------------+
{Fore.GREEN}|{Fore.YELLOW}╔═╗╔═╗ ╦  ┬┌┬┐┌─┐╔╦╗┬─┐┬┌┬┐{Fore.GREEN}|
{Fore.GREEN}|{Fore.YELLOW}╚═╗║═╬╗║  │ │ ├┤  ║ ├┬┘││││{Fore.GREEN}|
{Fore.GREEN}|{Fore.YELLOW}╚═╝╚═╝╚╩═╝┴ ┴ └─┘ ╩ ┴└─┴┴ ┴{Fore.GREEN}|
{Fore.GREEN}+---------------------------+
{Fore.CYAN}visit: https://github.com/g3ntrix
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(BANNER)

def select_file(gui, description):
    if gui:
        return filedialog.askopenfilename(title=description, filetypes=[("SQLite Database Files", "*.db"), ("All Files", "*.*")])
    else:
        return input(f"{Fore.YELLOW}{description}: ")

def select_save_location(gui):
    if gui:
        return filedialog.asksaveasfilename(title="Select save location", defaultextension=".db", filetypes=[("SQLite Database Files", "*.db"), ("All Files", "*.*")])
    else:
        return input(f"{Fore.YELLOW}Enter the path to save the modified database: ")

def get_input(prompt, gui):
    if gui:
        return simpledialog.askstring("Input", prompt)
    else:
        return input(f"{Fore.YELLOW}{prompt}: ")

def recreate_with_sequential_ids(db_path, start_id=1):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(inbounds)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        columns_str = ', '.join(columns)
        placeholders = ', '.join('?' * len(columns))

        cursor.execute("SELECT * FROM inbounds ORDER BY id")
        rows = cursor.fetchall()
        cursor.execute("DELETE FROM inbounds")
        conn.commit()

        for new_id, row in enumerate(rows, start=start_id):
            new_row = (new_id,) + row[1:]
            cursor.execute(f"INSERT INTO inbounds ({columns_str}) VALUES ({placeholders})", new_row)

        conn.commit()

    except sqlite3.OperationalError as e:
        print(f"{Fore.RED}OperationalError: {e}")
    finally:
        conn.close()

def merge_clients(clients1, clients2):
    unique_clients = {client['email']: client for client in clients1}
    for client in clients2:
        unique_clients[client['email']] = client
    return list(unique_clients.values())

def merge_inbounds(rows1, rows2):
    inbounds = {}
    for row in rows1 + rows2:
        id, user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings_json, stream_settings, tag, sniffing = row
        settings = json.loads(settings_json)
        clients = settings.get('clients', [])

        if port in inbounds:
            inbounds[port]['clients'].extend(clients)
        else:
            inbounds[port] = {'row': row, 'clients': clients}

    merged_rows = []
    for port, data in inbounds.items():
        row, clients = data['row'], data['clients']
        unique_clients = merge_clients(clients, [])
        settings = json.loads(row[11])
        settings['clients'] = unique_clients
        row = list(row)
        row[11] = json.dumps(settings)
        merged_rows.append(tuple(row))
    return merged_rows

def merge_databases(db1_path, db2_path, output_path):
    shutil.copyfile(db1_path, output_path)
    conn1 = sqlite3.connect(output_path)
    conn2 = sqlite3.connect(db2_path)
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    try:
        cursor1.execute("PRAGMA table_info(inbounds)")
        columns_info = cursor1.fetchall()
        columns = [col[1] for col in columns_info]
        columns_str = ', '.join(columns)
        placeholders = ', '.join('?' * len(columns))

        cursor1.execute("SELECT * FROM inbounds ORDER BY id")
        rows1 = cursor1.fetchall()

        cursor2.execute("SELECT * FROM inbounds ORDER BY id")
        rows2 = cursor2.fetchall()

        merged_rows = merge_inbounds(rows1, rows2)

        cursor1.execute("DELETE FROM inbounds")
        conn1.commit()

        for new_id, row in enumerate(merged_rows, start=1):
            new_row = (new_id,) + row[1:]
            cursor1.execute(f"INSERT INTO inbounds ({columns_str}) VALUES ({placeholders})", new_row)

        conn1.commit()

    except sqlite3.OperationalError as e:
        print(f"{Fore.RED}OperationalError: {e}")
    finally:
        conn1.close()
        conn2.close()

def delete_and_recreate(original_db_path, new_db_path, delete_type, start_id, end_id=None):
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
        print(f"{Fore.RED}OperationalError: {e}")
    finally:
        conn.close()

def main():
    print_banner()
    print(f"{Fore.CYAN}Do you want to use the GUI or terminal interface?")
    print(f"{Fore.CYAN}1. Terminal")
    print(f"{Fore.CYAN}2. GUI")
    choice = input(f"{Fore.YELLOW}Enter your choice (1 or 2): ")

    gui = choice == '2'

    if gui:
        try:
            import tkinter as tk
            from tkinter import filedialog, simpledialog
        except ImportError:
            print(f"{Fore.RED}Tkinter is not installed. Please install it to use the GUI.")
            print(f"{Fore.CYAN}You can install it by running: sudo apt install python3-tk")
            sys.exit(1)
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

    while True:
        print_banner()
        print(f"{Fore.CYAN}\nMenu:")
        print(f"{Fore.CYAN}1. Delete a single row")
        print(f"{Fore.CYAN}2. Delete a range of rows")
        print(f"{Fore.CYAN}3. Merge two databases")
        print(f"{Fore.CYAN}4. Exit")

        try:
            choice = int(input(f"{Fore.YELLOW}Enter your choice (1, 2, 3, or 4): "))
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number (1, 2, 3, or 4).")
            continue

        if choice == 1:
            db_path = select_file(gui, "Enter the path to the database file")
            if not db_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            output_path = select_save_location(gui)
            if not output_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            try:
                start_id = int(get_input("Enter the ID of the row to delete", gui))
                delete_and_recreate(db_path, output_path, 'single', start_id)
                print(f"{Fore.GREEN}Modified database saved as {output_path}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a valid row ID.")
        elif choice == 2:
            db_path = select_file(gui, "Enter the path to the database file")
            if not db_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            output_path = select_save_location(gui)
            if not output_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            try:
                start_id = int(get_input("Enter the start ID of the range to delete", gui))
                end_id = int(get_input("Enter the end ID of the range to delete", gui))
                delete_and_recreate(db_path, output_path, 'range', start_id, end_id)
                print(f"{Fore.GREEN}Modified database saved as {output_path}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter valid row IDs.")
        elif choice == 3:
            db1_path = select_file(gui, "Enter the path to the first database file")
            if not db1_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            db2_path = select_file(gui, "Enter the path to the second database file")
            if not db2_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            output_path = select_save_location(gui)
            if not output_path:
                print(f"{Fore.RED}No file selected. Exiting.")
                continue

            recreate_with_sequential_ids(db1_path)
            recreate_with_sequential_ids(db2_path, start_id=1)
            merge_databases(db1_path, db2_path, output_path)

            print(f"{Fore.GREEN}Merged database saved as {output_path}")
        elif choice == 4:
            print(f"{Fore.CYAN}Exiting the program.")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
