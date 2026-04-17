import json
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# ---------- Load Students ----------
def load_students():
    try:
        with open("students.json", "r") as f:
            return json.load(f)
    except:
        messagebox.showerror("Error", "students.json not found!")
        return []


# ---------- Generate Seating ----------
def generate_seating(students, rows, cols):
    total_seats = rows * cols
    shuffled = students[:]
    random.shuffle(shuffled)

    grids = []
    
    for i in range(0, len(shuffled), total_seats):
        chunk = shuffled[i:i + total_seats]
        seating = []
        index = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if index < len(chunk):
                    row.append(chunk[index])
                    index += 1
                else:
                    row.append("EMPTY")
            seating.append(row)
        grids.append(seating)

    return grids


# ---------- Save Seating ----------
def save_seating(seating, class_name):
    filename = f"seats_{class_name}.json" if class_name else "seats.json"
    data = {
        "class_name": class_name,
        "seating": seating
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# ---------- Convert Row Index to Letter ----------
def row_label(index):
    return chr(65 + index)  # A, B, C...


# ---------- Display Grid ----------
def display_seating(seating, class_name, parent_frame):
    if class_name:
        title = tk.Label(parent_frame, text=f"Class: {class_name}", font=("Helvetica", 14, "bold"))
        cols_count = len(seating[0]) if seating and seating[0] else 1
        title.grid(row=0, column=0, columnspan=cols_count, pady=(10, 10))

    for r, row in enumerate(seating):
        for c, student in enumerate(row):
            seat_name = f"{row_label(r)}{c+1}"
            text = f"{seat_name}\n{student}"

            label = tk.Label(
                parent_frame,
                text=text,
                borderwidth=1,
                relief="solid",
                width=12,
                height=4
            )
            label.grid(row=r+1, column=c, padx=5, pady=5)

# ---------- Button Action ----------
def assign_seats():
    students = load_students()
    if not students:
        return

    base_class_name = class_entry.get().strip()

    try:
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
    except:
        messagebox.showerror("Error", "Enter valid numbers!")
        return

    grids = generate_seating(students, rows, cols)

    if grids:
        for widget in content_frame.winfo_children():
            widget.destroy()

        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill="both", expand=True)

        for i, seating in enumerate(grids):
            if base_class_name:
                if base_class_name.isdigit():
                    num = int(base_class_name) + i
                    class_name = str(num).zfill(len(base_class_name))
                else:
                    class_name = f"{base_class_name}-{i+1}" if i > 0 else base_class_name
            else:
                class_name = f"Part-{i+1}"

            save_seating(seating, class_name)
            
            tab_frame = tk.Frame(notebook)
            notebook.add(tab_frame, text=class_name)
            display_seating(seating, class_name, tab_frame)


# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Exam Seating System")

# Inputs
tk.Label(root, text="Class Name:").grid(row=0, column=0)
class_entry = tk.Entry(root)
class_entry.insert(0, "001")
class_entry.grid(row=0, column=1)

tk.Label(root, text="Rows:").grid(row=0, column=2)
rows_entry = tk.Entry(root)
rows_entry.grid(row=0, column=3)

tk.Label(root, text="Columns:").grid(row=0, column=4)
cols_entry = tk.Entry(root)
cols_entry.grid(row=0, column=5)

# Button
assign_btn = tk.Button(root, text="Assign Seats", command=assign_seats)
assign_btn.grid(row=0, column=6, padx=10)

# Container for Grid display / Notebook
content_frame = tk.Frame(root)
content_frame.grid(row=1, column=0, columnspan=7, pady=20, padx=20)

root.mainloop()