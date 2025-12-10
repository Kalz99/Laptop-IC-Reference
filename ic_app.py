import tkinter as tk
from tkinter import ttk
import os
import sqlite3
from PIL import Image, ImageTk

root = tk.Tk()
root.title("IC Finder 1.0")
root.geometry("1200x800")
root.configure(bg="#f0f0f0")

DB_FILE="ic_finder_db.db"

conn=sqlite3.connect(DB_FILE)
cursor=conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS parts(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               part_number TEXT NOT NULL,
               ic_type TEXT,
               related_section TEXT
               replacement_part TEXT
               image_path TEXT
               )''')

cursor.execute('CREATE TABLE IF NOT EXISTS ic_types (type_name TEXT UNIQUE)')
cursor.execute('CREATE TABLE IF NOT EXISTS ic_sections (section_name TEXT UNIQUE)')

conn.commit()
conn.close()

title_label = tk.Label(
    root,
    text="Laptop IC Reference",
    font=("Lato", 20, "bold"),
    bg="#f0f0f0",
    fg="#2c3e50"
)
title_label.pack(pady=15)

search_frame=tk.Frame(root,bg="#f0f0f0")
search_frame.pack(pady=10)

search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, width=25, font=("Arial", 12))
search_entry.pack(side="left", padx=5)

def on_search():
    query = search_var.get()                  
    print(f"Searching for: {query}")

#Mange Types
def open_manage_types():
    type_i=tk.Toplevel(root)
    type_i.title("Manage IC Types")   
    type_i.configure(bg="#f0f0f0")
    
    # Make it stay on top
    type_i.transient(root)        # Stays on top of main window
    type_i.grab_set()             # Blocks clicks on main window until this is closed

    tk.Label(type_i, text="IC Types", font=("Lato", 16, "bold"), bg="#f0f0f0").pack(pady=10)
    type_listbox = tk.Listbox(type_i, width=40, height=15, font=("Arial", 12))
    type_listbox.pack(pady=10)

    # [All your refresh_types(), add_type(), edit_type(), delete_type() functions stay the same here]

    btn_frame = tk.Frame(type_i, bg="#f0f0f0")
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Add New Type", command=add_type, bg="#27ae60", fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Edit Selected", command=edit_type, bg="#e67e22", fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Delete Selected", command=delete_type, bg="#c0392b", fg="white").pack(side="left", padx=10)

    refresh_types()
    
search_button = tk.Button(search_frame, text="Search", command=on_search())   
search_button.pack(side="left", padx=5) 

search_entry.bind("<Return>", lambda event: on_search())

buttons_frame = tk.Frame(root,bg="#f0f0f0")
buttons_frame.pack(pady=15)

btn_addPart=tk.Button(buttons_frame,text="Add a Part",width=10,bg="#1c4d6d",fg="white",font=("Lato",11))

btn_addPart.pack(side="left",padx=20)

btn_addType=tk.Button(buttons_frame,text="Add a Type",width=10,bg="#1c4d6d",fg="white",font=("Lato",11))
btn_addType.pack(side="left",padx=15)
btn_addType.config(command=open_manage_types)
btn_addSection=tk.Button(buttons_frame,text="Add a Related Section",width=18,bg="#1c4d6d",fg="white",font=("Lato",11))
btn_addSection.pack(side="left",padx=15)

columns=("part_No","type","section","replacement","image","actions")

tree=ttk.Treeview(root,columns=columns,show="headings",height=10)
tree.pack(fill="both", expand=True, padx=30, pady=20)


tree.heading("part_No", text="Part Number")
tree.heading("type", text="Type")
tree.heading("section", text="Related Section")
tree.heading("replacement", text="Replacement Part")
tree.heading("image", text="Image")
tree.heading("actions", text="Actions")


tree.column("part_No", width=100, anchor="center")
tree.column("type", width=120, anchor="center")
tree.column("section", width=150, anchor="center")
tree.column("replacement", width=150, anchor="center")
tree.column("image", width=150, anchor="center")
tree.column("actions", width=120, anchor="center")

scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
scrollbar_y.pack(side="right", fill="y")    # Vertical scrollbar on the right
scrollbar_x.pack(side="bottom", fill="x")   # Horizontal at the bottom

tree.insert("", "end", values=(
    "BQ24735",           # Part Number
    "Charging IC",       # Type
    "Charging section",  # Section
    "BQ24737",           # Replacement
    "📷",                # Placeholder for image
    "✏️ 🗑️"             # Edit and Delete symbols
))

# This list will hold real images later (important!)
images = []





root.mainloop()
