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
import warnings

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

def display_status(message):
    print(f"{Fore.CYAN}{message}")

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
        display_status(f"OperationalError: {e}")
    finally:
        conn.close()

def fetch_client_traffic(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT email, up, down, total FROM client_traffics")
    traffic_data = cursor.fetchall()
    traffic_dict = {}
    for email, up, down, total in traffic_data:
        if email not in traffic_dict:
            traffic_dict[email] = {'up': up, 'down': down, 'total': total}
        else:
            traffic_dict[email]['up'] += up
            traffic_dict[email]['down'] += down
            traffic_dict[email]['total'] += total
    return traffic_dict

def get_inbound_client_counts(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT inbound_id, COUNT(*) FROM client_traffics GROUP BY inbound_id")
    inbound_client_counts = {row[0]: row[1] for row in cursor.fetchall()}
    return inbound_client_counts

def merge_clients(clients1, clients2, client_traffic1, client_traffic2, parent_usage1, parent_usage2, total1, total2, inbound_id, client_count1, client_count2):
    unique_clients = {}
    for client in clients1:
        email = client['email']
        if email not in unique_clients:
            unique_clients[email] = client
            if client_count1 == 1 and client['totalGB'] == 0:  # Condition for infinite limit
                client['up'] = parent_usage1['up']
                client['down'] = parent_usage1['down']
                client['total'] = total1
            else:
                client['up'] = client_traffic1.get(email, {}).get('up', parent_usage1['up'])
                client['down'] = client_traffic1.get(email, {}).get('down', parent_usage1['down'])
                client['total'] = client_traffic1.get(email, {}).get('total', total1)
            unique_clients[email]['inbound_id'] = inbound_id
            unique_clients[email]['totalGB'] = unique_clients[email]['total']  # Update totalGB
    for client in clients2:
        email = client['email']
        if email not in unique_clients:
            unique_clients[email] = client
            if client_count2 == 1 and client['totalGB'] == 0:  # Condition for infinite limit
                client['up'] = parent_usage2['up']
                client['down'] = parent_usage2['down']
                client['total'] = total2
            else:
                client['up'] = client_traffic2.get(email, {}).get('up', parent_usage2['up'])
                client['down'] = client_traffic2.get(email, {}).get('down', parent_usage2['down'])
                client['total'] = total2  # Set total to the parent inbound's total
            unique_clients[email]['inbound_id'] = inbound_id
            unique_clients[email]['totalGB'] = unique_clients[email]['total']  # Update totalGB
        else:
            # If the client already exists, merge the traffic data
            existing_client = unique_clients[email]
            existing_client['up'] += client_traffic2.get(email, {}).get('up', parent_usage2['up'])
            existing_client['down'] += client_traffic2.get(email, {}).get('down', parent_usage2['down'])
            existing_client['total'] = total2  # Ensure total is set to the parent inbound's total
    return list(unique_clients.values())

def merge_inbounds(rows1, rows2, client_traffic1, client_traffic2, inbound_client_counts1, inbound_client_counts2):
    inbounds = {}
    similar_ports = set()  # To store similar ports

    for row in rows1:
        id, user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings_json, stream_settings, tag, sniffing = row
        settings = json.loads(settings_json)
        clients = settings.get('clients', [])

        parent_usage = {'up': up, 'down': down}
        if port not in inbounds:
            inbounds[port] = {'row': row, 'clients': clients, 'parent_usage': parent_usage, 'total': total, 'client_count': inbound_client_counts1.get(id, 0)}
        else:
            similar_ports.add(port)
            inbounds[port]['clients'] = merge_clients(
                inbounds[port]['clients'], clients, client_traffic1, {}, inbounds[port]['parent_usage'], parent_usage, inbounds[port]['total'], total, id, inbounds[port]['client_count'], inbound_client_counts1.get(id, 0)
            )
            inbounds[port]['parent_usage'] = {
                'up': inbounds[port]['parent_usage']['up'] + up,
                'down': inbounds[port]['parent_usage']['down'] + down
            }
            inbounds[port]['total'] += total

    for row in rows2:
        id, user_id, up, down, total, remark, enable, expiry_time, listen, port, protocol, settings_json, stream_settings, tag, sniffing = row
        settings = json.loads(settings_json)
        clients = settings.get('clients', [])

        parent_usage = {'up': up, 'down': down}
        if port not in inbounds:
            inbounds[port] = {'row': row, 'clients': clients, 'parent_usage': parent_usage, 'total': total, 'client_count': inbound_client_counts2.get(id, 0)}
        else:
            similar_ports.add(port)
            inbounds[port]['clients'] = merge_clients(
                inbounds[port]['clients'], clients, {}, client_traffic2, inbounds[port]['parent_usage'], parent_usage, inbounds[port]['total'], total, id, inbounds[port]['client_count'], inbound_client_counts2.get(id, 0)
            )
            inbounds[port]['parent_usage'] = {
                'up': inbounds[port]['parent_usage']['up'] + up,
                'down': inbounds[port]['parent_usage']['down'] + down
            }
            inbounds[port]['total'] += total

    merged_rows = []
    for port, data in inbounds.items():
        row, clients, parent_usage, total = data['row'], data['clients'], data['parent_usage'], data['total']
        settings = json.loads(row[11])
        settings['clients'] = clients
        row = list(row)
        row[2] = parent_usage['up']
        row[3] = parent_usage['down']
        row[4] = total
        row[11] = json.dumps(settings)
        merged_rows.append(tuple(row))

    return merged_rows, similar_ports

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

        client_traffic1 = fetch_client_traffic(conn1)
        client_traffic2 = fetch_client_traffic(conn2)

        inbound_client_counts1 = get_inbound_client_counts(conn1)
        inbound_client_counts2 = get_inbound_client_counts(conn2)

        display_status("Merging inbounds and client traffic data...")
        merged_rows, similar_ports = merge_inbounds(rows1, rows2, client_traffic1, client_traffic2, inbound_client_counts1, inbound_client_counts2)

        cursor1.execute("DELETE FROM inbounds")
        conn1.commit()

        for new_id, row in enumerate(merged_rows, start=1):
            new_row = (new_id,) + row[1:]
            cursor1.execute(f"INSERT INTO inbounds ({columns_str}) VALUES ({placeholders})", new_row)

        conn1.commit()

        display_status("Updating client traffics table...")
        cursor1.execute("DELETE FROM client_traffics")
        conn1.commit()

        for row in merged_rows:
            clients = json.loads(row[11]).get('clients', [])
            for c in clients:
                c_total = c.get('total', row[4]) if 'total' in c else row[4]
                cursor1.execute(
                    "INSERT INTO client_traffics (email, up, down, total, inbound_id, enable, expiry_time, reset) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (c['email'], c.get('up', 0), c.get('down', 0), c_total, row[0], 1, 0, 0)
                )

        conn1.commit()

        display_status("Database merge completed.")
        return similar_ports

    except sqlite3.OperationalError as e:
        display_status(f"OperationalError: {e}")
    except sqlite3.Warning as w:
        display_status(f"SQLite Warning: {w}")
    except Exception as e:
        display_status(f"An unexpected error occurred: {e}")
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
        display_status(f"OperationalError: {e}")
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
            similar_ports = merge_databases(db1_path, db2_path, output_path)

            print(f"{Fore.GREEN}Merged database saved as {output_path}")
            if similar_ports:
                print(f"{Fore.CYAN}Similar ports found and merged:")
                for port in similar_ports:
                    print(f"{Fore.YELLOW}Port: {port}")
        elif choice == 4:
            print(f"{Fore.CYAN}Exiting the program.")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    if 'TERM' not in os.environ:
        os.environ['TERM'] = 'xterm-256color'
    main()
