import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Function to create a connection
def create_connection():
    return sqlite3.connect('data.db')

# Function to fetch table names from the database
def get_table_names():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

# Function to fetch table data
def fetch_table_data(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1 ASC")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
    except sqlite3.OperationalError as e:
        messagebox.showerror("Error", f"Could not fetch data: {e}")
        columns, data = [], []
    conn.close()
    return columns, data

# Function to populate the treeview with data
def populate_treeview(tree, table_name):
    columns, data = fetch_table_data(table_name)

    # Clear previous columns
    tree["columns"] = ()
    for col in tree["columns"]:
        tree.heading(col, text="")

    tree["columns"] = columns
    tree["show"] = "headings"

    # Set column headers
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    # Clear previous data
    for item in tree.get_children():
        tree.delete(item)

    # Insert new data
    for row in data:
        tree.insert("", "end", values=row)

# Function to handle table selection change
def on_table_select(event, tree, table_var):
    table_name = table_var.get()
    if table_name:
        populate_treeview(tree, table_name)

# Function to search data in the selected table
def search_data(tree, table_name, search_var):
    search_term = search_var.get().lower()
    columns, data = fetch_table_data(table_name)
    
    if not search_term:
        populate_treeview(tree, table_name)
        return

    filtered_data = [row for row in data if search_term in str(row).lower()]

    # Clear the treeview
    for item in tree.get_children():
        tree.delete(item)

    # Insert filtered data
    for row in filtered_data:
        tree.insert("", "end", values=row)

# Function to delete selected row
def delete_selected(tree, table_name):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "No row selected!")
        return

    item = tree.item(selected_item)
    values = item['values']

    # Ensure we have an identifiable column (Assuming first column is primary key)
    if not values:
        messagebox.showerror("Error", "Could not retrieve row data.")
        return

    primary_key = values[0]  # Assuming the first column is the primary key
    primary_column = tree["columns"][0]

    # Confirm before deletion
    if not messagebox.askyesno("Confirm", "Are you sure you want to delete this row?"):
        return

    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE {primary_column} = ?", (primary_key,))
        conn.commit()
        tree.delete(selected_item)
    except sqlite3.OperationalError as e:
        messagebox.showerror("Error", f"Could not delete row: {e}")
    conn.close()

# Main function to set up the GUI
def main():
    root = tk.Tk()
    root.title("SQLite Database Viewer")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    table_var = tk.StringVar()
    search_var = tk.StringVar()

    # Fetch table names dynamically
    table_names = get_table_names()

    if not table_names:
        messagebox.showerror("Error", "No tables found in database!")
        return

    # Table Selection
    table_label = ttk.Label(frame, text="Select Table:")
    table_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    table_menu = ttk.OptionMenu(frame, table_var, table_names[0], *table_names)
    table_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    # Search Box
    search_label = ttk.Label(frame, text="Search:")
    search_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

    search_entry = ttk.Entry(frame, textvariable=search_var)
    search_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

    search_button = ttk.Button(frame, text="Search", command=lambda: search_data(tree, table_var.get(), search_var))
    search_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

    # Delete Button
    delete_button = ttk.Button(frame, text="Delete", command=lambda: delete_selected(tree, table_var.get()))
    delete_button.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)

    # Table Display
    tree = ttk.Treeview(frame)
    tree.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E, tk.N, tk.S))

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)

    vsb.grid(row=1, column=6, sticky=(tk.N, tk.S))
    hsb.grid(row=2, column=0, columnspan=6, sticky=(tk.W, tk.E))

    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(5, weight=1)

    # Load the first table's data by default
    table_var.trace("w", lambda *args: on_table_select(None, tree, table_var))
    populate_treeview(tree, table_var.get())

    root.mainloop()

if __name__ == "__main__":
    main()
