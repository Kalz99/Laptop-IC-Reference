import tkinter as tk
from tkinter import ttk, messagebox
import os
import sqlite3
from PIL import Image, ImageTk  # noqa: F401
from tkinter import filedialog
import shutil

root = tk.Tk()
root.title("TraceCore+")
root.geometry("1200x800")
root.configure(bg="#f0f0f0")

DB_FILE = "ic_finder_db.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS parts(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               part_number TEXT NOT NULL,
               ic_type TEXT,
               related_section TEXT,
               replacement_part TEXT,
               image_path TEXT
               )"""
)

cursor.execute("CREATE TABLE IF NOT EXISTS ic_types (type_name TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS ic_sections (section_name TEXT UNIQUE)")

conn.commit()
conn.close()
IMAGE_DIR = "pinout_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Load the View icon (do this once, outside any function)
view_icon_path = "view_ico.png"  # put your PNG file name here
if os.path.exists(view_icon_path):
    img = Image.open("view_ico.png").resize((20, 20), Image.LANCZOS)
    view_icon = ImageTk.PhotoImage(img)
else:
    view_photo = None  # fallback if file not found

title_label = tk.Label(
    root,
    text="TraceCore+",
    font=("Lato", 20, "bold"),
    bg="#f0f0f0",
    fg="#2c3e50",
)
title_label.pack(pady=15)

search_frame = tk.Frame(root, bg="#f0f0f0")
search_frame.pack(pady=10)

search_var = tk.StringVar()
search_entry = tk.Entry(
    search_frame, textvariable=search_var, width=25, font=("Arial", 12)
)
search_entry.pack(side="left", padx=5)


def on_search():
    query = search_var.get().strip().lower()
    load_parts(search_query=query)


# Start of the Mange Types
def open_manage_types():
    type_i = tk.Toplevel(root)
    type_i.title("Manage IC Types")
    type_i.configure(bg="#f0f0f0")

    # Make it stay on top
    type_i.transient(root)  # Stays on top of main window
    type_i.grab_set()  # Blocks clicks on main window until this is closed

    tk.Label(type_i, text="IC Types", font=("Lato", 12, "bold"), bg="#f0f0f0").pack(
        pady=10
    )
    addType_frame = tk.Frame(type_i, bg="#f0f0f0")
    addType_frame.pack(pady=10)

    type_var = tk.StringVar()
    type_entry = tk.Entry(
        addType_frame, textvariable=type_var, width=15, font=("Lato", 12)
    )
    type_entry.pack(side="left", padx=5)

    type_listbox = tk.Listbox(type_i, width=40, height=15, font=("Lato", 12))
    type_listbox.pack(pady=10)

    def refresh_types():
        type_listbox.delete(0, "end")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT type_name FROM ic_types ORDER BY type_name")
        types = cursor.fetchall()
        conn.close()
        for t in types:
            type_listbox.insert("end", t[0])

    def add_type():
        new_type = type_var.get().strip()
        if not new_type:
            messagebox.showwarning("Empty", "Please enter a type name!", parent=type_i)
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO ic_types (type_name) VALUES (?)", (new_type,))
            conn.commit()
            messagebox.showinfo("Success", "Successfully added!", parent=type_i)
            type_var.set("")  # Clear entry
            refresh_types()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Duplicate", f"Type '{type_var}' already exists!", parent=type_i
            )
        conn.close()

    def delete_type():
        selected = type_listbox.curselection()  # returns tuple like (2,)
        if not selected:
            messagebox.showwarning(
                "Select", "Please select a type to delete!", parent=type_i
            )
            return
        type_name = type_listbox.get(selected[0])
        if messagebox.askyesno(
            "Confirm", f"Delete '{type_name}'?\nThis cannot be undone!", parent=type_i
        ):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ic_types WHERE type_name = ?", (type_name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"'{type_name}' removed!", parent=type_i)
            refresh_types()

    refresh_types()
    add_btn = tk.Button(
        addType_frame, text="Add", width=7, bg="#1c4d6d", fg="white", command=add_type
    )
    add_btn.pack(side="left", padx=5)
    tk.Button(
        addType_frame,
        text="Delete",
        width=7,
        bg="#db4837",
        fg="white",
        command=delete_type,
    ).pack(side="left", padx=5)

    # For now, just a placeholder button to test
    tk.Button(type_i, text="Close", command=type_i.destroy).pack(pady=10)
    # === Centering the window Start ===
    type_i.update_idletasks()
    type_i.wait_visibility(type_i)
    width = type_i.winfo_reqwidth()
    height = type_i.winfo_reqheight()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    x = root_x + (root_w // 2) - (width // 2)
    y = root_y + (root_h // 2) - (height // 2)
    type_i.geometry(f"+{x}+{y}")
    # === Centering the window End ===


# End of the manage types


# Start of manage sections
def open_related_section():
    section_i = tk.Toplevel(root)
    section_i.title("Manage Related Sections")
    section_i.configure(bg="#f0f0f0")

    # Make it stay on top
    section_i.transient(root)  # Stays on top of main window
    section_i.grab_set()  # Blocks clicks on main window until this is closed

    tk.Label(
        section_i, text="Related Sections", font=("Lato", 12, "bold"), bg="#f0f0f0"
    ).pack(pady=10)
    addSection_frame = tk.Frame(section_i, bg="#f0f0f0")
    addSection_frame.pack(pady=10)

    sec_var = tk.StringVar()
    sec_entry = tk.Entry(
        addSection_frame, textvariable=sec_var, width=15, font=("Lato", 12)
    )
    sec_entry.pack(side="left", padx=5)

    sec_listbox = tk.Listbox(section_i, width=40, height=15, font=("Lato", 12))
    sec_listbox.pack(pady=10)

    def refresh_sections():
        sec_listbox.delete(0, "end")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT section_name FROM ic_sections ORDER BY section_name")
        types = cursor.fetchall()
        conn.close()
        for t in types:
            sec_listbox.insert("end", t[0])

    def add_section():
        new_sec = sec_var.get().strip()
        if not new_sec:
            messagebox.showwarning(
                "Empty", "Please enter a Section name!", parent=section_i
            )
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO ic_sections (section_name) VALUES (?)", (new_sec,)
            )
            conn.commit()
            messagebox.showinfo("Success", "Successfully added!", parent=section_i)
            sec_var.set("")  # Clear entry
            refresh_sections()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Duplicate", f"Type '{sec_var}' already exists!", parent=section_i
            )
        conn.close()

    def delete_section():
        selected = sec_listbox.curselection()
        if not selected:
            messagebox.showwarning(
                "Select", "Please select a section name to delete!", parent=section_i
            )
            return
        sec_name = sec_listbox.get(selected[0])
        if messagebox.askyesno(
            "Confirm", f"Delete '{sec_name}'?\nThis cannot be undone!", parent=section_i
        ):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM ic_sections WHERE section_name = ?", (sec_name,)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"'{sec_name}' removed!", parent=section_i)
            refresh_sections()

    refresh_sections()
    addS_btn = tk.Button(
        addSection_frame,
        text="Add",
        width=7,
        bg="#1c4d6d",
        fg="white",
        command=add_section,
    )
    addS_btn.pack(side="left", padx=5)
    deleteS_btn = tk.Button(
        addSection_frame,
        text="Delete",
        width=7,
        bg="#db4837",
        fg="white",
        command=delete_section,
    )
    deleteS_btn.pack(side="left", padx=5)

    # For now, just a placeholder button to test
    tk.Button(section_i, text="Close", command=section_i.destroy).pack(pady=10)
    # === Centering the window Start ===
    section_i.update_idletasks()
    section_i.wait_visibility(section_i)
    width = section_i.winfo_reqwidth()
    height = section_i.winfo_reqheight()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    x = root_x + (root_w // 2) - (width // 2)
    y = root_y + (root_h // 2) - (height // 2)
    section_i.geometry(f"+{x}+{y}")
    # === Centering the window End ===


# End of manage sections


# Start of Add a IC
def open_add_part():
    addPart_i = tk.Toplevel(root)
    addPart_i.title("Add a new IC")
    addPart_i.config(bg="#f0f0f0")

    addPart_i.transient(root)  # Stays on top of main window
    addPart_i.grab_set()

    # Form fields
    tk.Label(
        addPart_i, text="Add New IC", font=("Lato", 16, "bold"), bg="#f0f0f0"
    ).pack(pady=10)

    form_frame = tk.Frame(addPart_i, bg="#f0f0f0")
    form_frame.pack(pady=10, padx=20)

    tk.Label(form_frame, text="Part Number:*", bg="#f0f0f0").grid(
        row=0, column=0, sticky="w", pady=5
    )
    partNo_var = tk.StringVar()
    tk.Entry(form_frame, textvariable=partNo_var, width=40).grid(
        row=0, column=1, pady=5
    )

    tk.Label(form_frame, text="Type:", bg="#f0f0f0").grid(
        row=1, column=0, sticky="w", pady=5
    )
    type_dropDown = ttk.Combobox(form_frame, state="readonly", width=37)
    type_dropDown.grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="Related Section:", bg="#f0f0f0").grid(
        row=2, column=0, sticky="w", pady=5
    )
    section_dropDown = ttk.Combobox(form_frame, state="readonly", width=37)
    section_dropDown.grid(row=2, column=1, pady=5)

    tk.Label(form_frame, text="Replacement Part:*", bg="#f0f0f0").grid(
        row=3, column=0, sticky="w", pady=5
    )
    rPart_var = tk.StringVar()
    tk.Entry(form_frame, textvariable=rPart_var, width=40).grid(row=3, column=1, pady=5)

    tk.Label(form_frame, text="Pinout Image:", bg="#f0f0f0").grid(
        row=4, column=0, sticky="w", pady=5
    )
    image_path_var = tk.StringVar()
    tk.Entry(form_frame, textvariable=image_path_var, width=40, state="readonly").grid(
        row=4, column=1, pady=5
    )

    def select_image():
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if path:
            image_path_var.set(path)

    tk.Button(form_frame, text="Browse", command=select_image).grid(
        row=4, column=1, sticky="e", pady=5
    )

    def load_dropdowns():
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT type_name FROM ic_types ORDER BY type_name")
        types = [row[0] for row in cursor.fetchall()]
        type_dropDown["values"] = types

        cursor.execute("SELECT section_name FROM ic_sections ORDER BY section_name")
        sections = [row[0] for row in cursor.fetchall()]
        section_dropDown["values"] = sections
        conn.close()

    load_dropdowns()

    def save_part():
        part_num = partNo_var.get().strip()

        if not part_num:
            messagebox.showerror("Error", "Part Number is required!", parent=addPart_i)
            return
        selected_ic_type = type_dropDown.get()
        selected_section = section_dropDown.get()
        replacement = rPart_var.get().strip()
        saved_img_path = None
        img_original_path = image_path_var.get()
        if image_path_var:
            filename = os.path.basename(img_original_path)
            saved_img_path = os.path.join(IMAGE_DIR, f"{part_num}_{filename}")
            shutil.copy(img_original_path, saved_img_path)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO parts (part_number, ic_type, related_section, replacement_part, image_path)
        VALUES (?, ?, ?, ?, ?)
        """,
            (part_num, selected_ic_type, selected_section, replacement, saved_img_path),
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Part '{part_num}' added!", parent=addPart_i)
        load_parts()
        addPart_i.destroy()

    # For now, just a placeholder button to test
    tk.Button(
        addPart_i, text="Add", width=15, bg="#1c4d6d", fg="white", command=save_part
    ).pack(pady=10)

    # === Centering the window Start ===
    addPart_i.update_idletasks()
    addPart_i.wait_visibility(addPart_i)
    width = addPart_i.winfo_reqwidth()
    height = addPart_i.winfo_reqheight()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    x = root_x + (root_w // 2) - (width // 2)
    y = root_y + (root_h // 2) - (height // 2)
    addPart_i.geometry(f"+{x}+{y}")
    # === Centering the window End ===


# End of the Add a IC

# search_button = tk.Button(search_frame, text="Search", command=on_search)
tk.Label(search_frame, text="🔍", font=("Segoe UI Emoji", 12), bg="#f0f0f0").pack(
    side="left", padx=5
)
# search_button.pack(side="left", padx=5)

search_entry.bind("<Return>", lambda event: on_search())

buttons_frame = tk.Frame(root, bg="#f0f0f0")
buttons_frame.pack(pady=15)

btn_addPart = tk.Button(
    buttons_frame,
    text="Add a Part",
    width=10,
    bg="#1c4d6d",
    fg="white",
    font=("Lato", 11),
)

btn_addPart.pack(side="left", padx=20)
btn_addPart.config(command=open_add_part)
btn_addType = tk.Button(
    buttons_frame,
    text="Add a Type",
    width=10,
    bg="#1c4d6d",
    fg="white",
    font=("Lato", 11),
)
btn_addType.pack(side="left", padx=15)
btn_addType.config(command=open_manage_types)
btn_addSection = tk.Button(
    buttons_frame,
    text="Add a Related Section",
    width=18,
    bg="#1c4d6d",
    fg="white",
    font=("Lato", 11),
)
btn_addSection.pack(side="left", padx=15)
btn_addSection.config(command=open_related_section)
columns = ("part_No", "type", "section", "replacement", "image", "edit", "delete")

tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
tree.pack(fill="both", expand=True, padx=30, pady=20)


tree.heading("part_No", text="Part Number")
tree.heading("type", text="Type")
tree.heading("section", text="Related Section")
tree.heading("replacement", text="Replacement Part")
tree.heading("image", text="Image")
tree.heading("edit", text="Edit")
tree.heading("delete", text="Delete")


tree.column("part_No", width=100, anchor="center")
tree.column("type", width=120, anchor="center")
tree.column("section", width=150, anchor="center")
tree.column("replacement", width=150, anchor="center")
tree.column("image", width=35, anchor="center")
tree.column("edit", width=35, anchor="center")
tree.column("delete", width=35, anchor="center")

from tkinter import ttk

style = ttk.Style()

# Use default theme (important)
style.theme_use("default")

# Style the Treeview heading
style.configure(
    "Treeview.Heading",
    background="#1f2933",  # Dark background
    foreground="white",  # Text color
    font=("Lato", 10, "bold"),
    padding=8,
)

# Style the Treeview rows
style.configure(
    "Treeview",
    font=("Lato", 10),
    rowheight=28,
    background="white",
    fieldbackground="white",
    foreground="#111827",
)


scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
scrollbar_y.pack(side="right", fill="y")  # Vertical scrollbar on the right
scrollbar_x.pack(side="bottom", fill="x")  # Horizontal at the bottom


def load_parts(search_query=""):

    for i in tree.get_children():
        tree.delete(i)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if search_query:
        # Search in part_number (case-insensitive)
        cursor.execute(
            """
            SELECT id, part_number, ic_type, related_section, replacement_part, image_path 
            FROM parts 
            WHERE lower(part_number) LIKE ? 
            ORDER BY part_number
        """,
            (f"%{search_query}%",),
        )
    else:
        cursor.execute(
            """
            SELECT id, part_number, ic_type, related_section, replacement_part, image_path 
            FROM parts 
            ORDER BY part_number
        """
        )

    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        part_id, part_num, ic_type, section, replacement, img_path = row

        if img_path and os.path.exists(img_path):
            tree.insert(
                "",
                "end",
                values=(
                    part_num,
                    ic_type or "",
                    section or "",
                    replacement or "",
                    "🖼️",
                    "✏️",
                    "🗑️",
                ),
                tags=("has_image", str(part_id), img_path),
            )
        else:
            tree.insert(
                "",
                "end",
                values=(
                    part_num,
                    ic_type or "",
                    section or "",
                    replacement or "",
                    "",
                    "Edit",
                    "Delete",
                ),
                tags=("no_image", str(part_id), img_path),
            )


def on_table_click(event):
    column = tree.identify_column(event.x)
    item = tree.identify_row(event.y)
    if not item:
        return

    tags = tree.item(item, "tags")
    part_id = int(tags[1])
    img_path = tags[2] if len(tags) > 2 else ""

    if column == "#5":
        if img_path and os.path.exists(img_path):
            os.startfile(img_path)
        else:
            messagebox.showwarning("No Image", "No pinout image found for this part.")

    elif column == "#7":
        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this IC part?\nThis cannot be undone.",
            parent=root,
        ):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM parts WHERE id = ?", (part_id,))
            conn.commit()
            conn.close()

            if img_path and os.path.exists(img_path):
                try:
                    os.remove(img_path)
                except:
                    pass

            messagebox.showinfo("Deleted", "IC part deleted successfully!")
            load_parts()

    elif column == "#6":  # Edit column
        open_edit_part(part_id)


def open_edit_part(part_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT part_number, ic_type, related_section, replacement_part, image_path FROM parts WHERE id = ?",
        (part_id,),
    )
    current = cursor.fetchone()
    conn.close()

    if not current:
        messagebox.showerror("Error", "Part not found!")
        return

    (
        current_part_num,
        current_type,
        current_section,
        current_replacement,
        current_img_path,
    ) = current

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit IC Part")
    edit_win.configure(bg="#f0f0f0")
    edit_win.transient(root)
    edit_win.grab_set()

    tk.Label(
        edit_win, text="Edit IC Part", font=("Lato", 16, "bold"), bg="#f0f0f0"
    ).pack(pady=10)

    form_frame = tk.Frame(edit_win, bg="#f0f0f0")
    form_frame.pack(pady=10, padx=20)

    tk.Label(form_frame, text="Part Number:", bg="#f0f0f0").grid(
        row=0, column=0, sticky="w", pady=5
    )
    part_var = tk.StringVar(value=current_part_num)
    tk.Entry(form_frame, textvariable=part_var, width=40).grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Type:", bg="#f0f0f0").grid(
        row=1, column=0, sticky="w", pady=5
    )
    type_combo = ttk.Combobox(form_frame, state="readonly", width=37)
    type_combo.grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="Related Section:", bg="#f0f0f0").grid(
        row=2, column=0, sticky="w", pady=5
    )
    section_combo = ttk.Combobox(form_frame, state="readonly", width=37)
    section_combo.grid(row=2, column=1, pady=5)

    tk.Label(form_frame, text="Replacement Part:", bg="#f0f0f0").grid(
        row=3, column=0, sticky="w", pady=5
    )
    replacement_var = tk.StringVar(value=current_replacement or "")
    tk.Entry(form_frame, textvariable=replacement_var, width=40).grid(
        row=3, column=1, pady=5
    )

    tk.Label(form_frame, text="Pinout Image:", bg="#f0f0f0").grid(
        row=4, column=0, sticky="w", pady=5
    )
    image_path_var = tk.StringVar(value=current_img_path or "")
    tk.Entry(form_frame, textvariable=image_path_var, width=30, state="readonly").grid(
        row=4, column=1, pady=5, padx=(0, 5)
    )

    def select_new_image():
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if path:
            image_path_var.set(path)

    tk.Button(form_frame, text="Change Image", command=select_new_image).grid(
        row=4, column=1, sticky="e", pady=5
    )

    print(current_type)

    def load_dropdowns():
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT type_name FROM ic_types ORDER BY type_name")
        types = [row[0] for row in cursor.fetchall()]
        type_combo["values"] = types
        if current_type in types:
            type_combo.set(current_type)

        cursor.execute("SELECT section_name FROM ic_sections ORDER BY section_name")
        sections = [row[0] for row in cursor.fetchall()]
        section_combo["values"] = sections
        if current_section in sections:
            section_combo.set(current_section)
        conn.close()

    load_dropdowns()

    def save_edit():
        new_part_num = part_var.get().strip()
        if not new_part_num:
            messagebox.showerror("Error", "Part Number is required!")
            return

        new_type = type_combo.get()
        new_section = section_combo.get()
        new_replacement = replacement_var.get().strip()
        new_img_original = image_path_var.get()

        new_saved_img_path = current_img_path
        if new_img_original and new_img_original != current_img_path:
            filename = os.path.basename(new_img_original)
            new_saved_img_path = os.path.join(IMAGE_DIR, f"{new_part_num}_{filename}")
            shutil.copy(new_img_original, new_saved_img_path)

            if current_img_path and os.path.exists(current_img_path):
                try:
                    os.remove(current_img_path)
                except:
                    pass

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE parts 
            SET part_number = ?, ic_type = ?, related_section = ?, replacement_part = ?, image_path = ?
            WHERE id = ?
        """,
            (
                new_part_num,
                new_type,
                new_section,
                new_replacement,
                new_saved_img_path,
                part_id,
            ),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Updated", f"Part '{new_part_num}' updated successfully!")
        edit_win.destroy()
        load_parts()

    tk.Button(
        edit_win,
        text="Save Changes",
        bg="#27ae60",
        fg="white",
        width=20,
        command=save_edit,
    ).pack(pady=20)

    edit_win.update_idletasks()
    edit_win.wait_visibility(edit_win)
    x = (
        root.winfo_rootx()
        + (root.winfo_width() // 2)
        - (edit_win.winfo_reqwidth() // 2)
    )
    y = (
        root.winfo_rooty()
        + (root.winfo_height() // 2)
        - (edit_win.winfo_reqheight() // 2)
    )
    edit_win.geometry(f"+{x}+{y}")


def live_search(*args):
    text_user_typed = search_var.get().lower()
    load_parts(text_user_typed)


search_var.trace("w", live_search)
tree.bind("<Button-1>", on_table_click)
load_parts()
root.mainloop()
