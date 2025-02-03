# use pyinstaller to build serverlist.pyw
# pyinstaller --onefile --icon=brick.ico --name=brickline_viomod.exe serverlist.pyw

import urllib.request
import requests
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk
from bs4 import BeautifulSoup
import subprocess
import psutil

url = "http://brickline.blackspace.lol:45689/"
icon_url = 'https://files.catbox.moe/ojlawh.ico'

server_list = []
last_server_uri = None

def is_novetus_running():
    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == "RobloxApp_client.exe":
            return True
    return False

def is_novetus_running_uri(): # i hate how i have to seperate these fucking hell
    for process in psutil.process_iter(attrs=['name']):
        if process.info['name'] == "NovetusURI.exe":
            return True
    return False

def fetch_servers():
    global server_list
    server_list.clear()
    tree.delete(*tree.get_children())

    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        servers = soup.find_all('div', class_='server')

        for server in servers:
            title_element = server.find('div', class_='server-title')
            button_element = title_element.find('button', class_='join-button') if title_element else None
            details_element = server.find('div', class_='server-details')

            player_count = "couldn't fetch"
            ip_address = "unknown"
            port = "unknown"

            if details_element:
                for p in details_element.find_all('p'):
                    text = p.get_text()
                    if "Players:" in text:
                        player_count = p.find('span').text.strip() if p.find('span') else "couldn't fetch"
                    elif "IP:" in text:
                        spans = p.find_all('span')
                        if len(spans) >= 2:
                            ip_address = spans[0].text.strip()
                            port = spans[1].text.strip()

            if title_element and button_element:
                server_name = title_element.find('span').text.strip()
                novetus_uri = button_element['onclick'].split("`")[1]
                server_list.append((server_name, novetus_uri, player_count, ip_address, port))
                tree.insert("", tk.END, values=(server_name, player_count))

    except requests.RequestException as e:
        messagebox.showerror("error", f"cant fetch servers, probably down: {e}")

def join_server():
    global last_server_uri
    selection = tree.selection()
    if selection:
        index = tree.index(selection[0])
        last_server_uri = server_list[index][1]

        if not multi_instance.get() and is_novetus_running():
            try:
                subprocess.run(["taskkill", "/im", "RobloxApp_client.exe", "/f"], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("error", f"cant close novetus: {e}")

        if not multi_instance.get() and is_novetus_running_uri():
            try:
                subprocess.run(["taskkill", "/im", "NovetusURI.exe", "/f"], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("error", f"cant close novetus: {e}")

        webbrowser.open(last_server_uri)

def rejoin_last_server():
    if last_server_uri:
        if not multi_instance.get() and is_novetus_running():
            try:
                subprocess.run(["taskkill", "/im", "RobloxApp_client.exe", "/f"], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("error", f"cant close novetus: {e}")

        if not multi_instance.get() and is_novetus_running_uri():
            try:
                subprocess.run(["taskkill", "/im", "NovetusURI.exe", "/f"], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("error", f"cant close novetus: {e}")

        webbrowser.open(last_server_uri)
    else:
        messagebox.showwarning("idiot", "no server to rejoin")

def copy_uri():
    selection = tree.selection()
    if selection:
        index = tree.index(selection[0])
        selected_uri = server_list[index][1]
        root.clipboard_clear()
        root.clipboard_append(selected_uri)
        root.update()
        messagebox.showinfo("copier", "uri copied to clipboard!")

def copy_ip():
    selection = tree.selection()
    if selection:
        index = tree.index(selection[0])
        selected_ip = server_list[index][3]
        root.clipboard_clear()
        root.clipboard_append(selected_ip)
        root.update()
        messagebox.showinfo("copier", "ip copied to clipboard!")

def copy_port():
    selection = tree.selection()
    if selection:
        index = tree.index(selection[0])
        selected_port = server_list[index][4]
        root.clipboard_clear()
        root.clipboard_append(selected_port)
        root.update()
        messagebox.showinfo("copier", "port copied to clipboard!")

def fix_novetus():
    if is_novetus_running():
        try:
            subprocess.run(["taskkill", "/im", "RobloxApp_client.exe", "/f"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("error", f"cant close novetus: {e}")

    if is_novetus_running_uri():
        try:
            subprocess.run(["taskkill", "/im", "NovetusURI.exe", "/f"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("error", f"cant close novetus: {e}")

root = tk.Tk()
root.title("brickline browser")
root.iconbitmap('brick.ico')
root.geometry("950x445")
root.resizable(True, True)

style = ttk.Style()
style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
style.configure("TCheckbutton", font=("Arial", 10))

frame = ttk.Frame(root)
frame.pack(pady=10, fill=tk.BOTH, expand=True)

# Use Treeview for separate columns
tree = ttk.Treeview(frame, columns=("Server Name", "Players"), show="headings", height=15)
tree.heading("Server Name", text="Server Name")
tree.heading("Players", text="Players")
tree.column("Server Name", width=200)
tree.column("Players", width=100, anchor="center")

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

join_button = ttk.Button(button_frame, text="join", command=join_server)
join_button.grid(row=0, column=0, padx=5)

rejoin_button = ttk.Button(button_frame, text="rejoin previous", command=rejoin_last_server)
rejoin_button.grid(row=0, column=1, padx=5)

refresh_button = ttk.Button(button_frame, text="refresh list", command=fetch_servers)
refresh_button.grid(row=0, column=2, padx=5)

copy_button = ttk.Button(button_frame, text="copy uri", command=copy_uri)
copy_button.grid(row=0, column=3, padx=5)

copy_ip_button = ttk.Button(button_frame, text="copy ip", command=copy_ip)
copy_ip_button.grid(row=0, column=4, padx=5)

copy_port_button = ttk.Button(button_frame, text="copy port", command=copy_port)
copy_port_button.grid(row=0, column=5, padx=5)

fix = ttk.Button(button_frame, text="close novetus", command=fix_novetus)
fix.grid(row=0, column=6, padx=5)

multi_instance = tk.BooleanVar(value=False)
multi_instance_checkbox = ttk.Checkbutton(root, text="enable mutli-instance?", variable=multi_instance)
multi_instance_checkbox.pack(pady=5)

fetch_servers()

root.mainloop()