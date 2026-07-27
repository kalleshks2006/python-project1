"""A small Tkinter project that demonstrates common GUI widgets.

Run with: python widgets_project.py
"""

import tkinter as tk
from tkinter import messagebox, ttk


class WidgetProject(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("My Widgets Project")
        self.geometry("680x560")
        self.minsize(620, 500)
        self.configure(padx=20, pady=18, bg="#f4f7fb")

        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar(value="School")
        self.priority_var = tk.StringVar(value="Medium")
        self.reminder_var = tk.BooleanVar(value=True)
        self.progress_var = tk.IntVar(value=0)
        self.status_var = tk.StringVar(value="Add a task to get started.")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self,
            text="Task Manager",
            font=("Arial", 22, "bold"),
            bg="#f4f7fb",
            fg="#173b66",
        ).pack(anchor="w")
        tk.Label(
            self,
            text="A simple project using Python Tkinter widgets",
            bg="#f4f7fb",
            fg="#52657a",
        ).pack(anchor="w", pady=(0, 14))

        form = ttk.LabelFrame(self, text="New task", padding=14)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Task name:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.task_entry = ttk.Entry(form, textvariable=self.name_var)
        self.task_entry.grid(row=0, column=1, columnspan=3, sticky="ew", pady=5)
        self.task_entry.focus()

        ttk.Label(form, text="Category:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=("School", "Work", "Personal", "Other"),
            state="readonly",
            width=15,
        ).grid(row=1, column=1, sticky="w", pady=5)

        ttk.Checkbutton(form, text="Set reminder", variable=self.reminder_var).grid(
            row=1, column=2, columnspan=2, sticky="w", padx=(18, 0), pady=5
        )

        ttk.Label(form, text="Priority:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        for column, level in enumerate(("Low", "Medium", "High"), start=1):
            ttk.Radiobutton(form, text=level, value=level, variable=self.priority_var).grid(
                row=2, column=column, sticky="w", pady=5
            )

        ttk.Button(form, text="Add task", command=self.add_task).grid(
            row=3, column=0, columnspan=4, pady=(12, 0), sticky="ew"
        )

        list_frame = ttk.LabelFrame(self, text="My tasks", padding=12)
        list_frame.pack(fill="both", expand=True, pady=14)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.task_list = tk.Listbox(list_frame, height=9, font=("Arial", 11), selectmode=tk.SINGLE)
        self.task_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_list.config(yscrollcommand=scrollbar.set)

        controls = ttk.Frame(list_frame)
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(controls, text="Complete selected", command=self.complete_task).pack(side="left")
        ttk.Button(controls, text="Delete selected", command=self.delete_task).pack(side="left", padx=8)
        ttk.Button(controls, text="Clear all", command=self.clear_tasks).pack(side="right")

        footer = ttk.Frame(self)
        footer.pack(fill="x")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left")
        self.progress = ttk.Progressbar(footer, maximum=100, variable=self.progress_var, length=170)
        self.progress.pack(side="right")

    def update_progress(self):
        total = self.task_list.size()
        completed = sum(self.task_list.get(index).startswith("✓") for index in range(total))
        percent = 0 if total == 0 else round(completed / total * 100)
        self.progress_var.set(percent)
        self.status_var.set(f"{completed} of {total} task(s) completed ({percent}%).")

    def add_task(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Task name required", "Please type a task name.")
            self.task_entry.focus()
            return

        reminder = " • Reminder" if self.reminder_var.get() else ""
        task = f"○ {name}  [{self.category_var.get()} | {self.priority_var.get()}]{reminder}"
        self.task_list.insert(tk.END, task)
        self.name_var.set("")
        self.task_entry.focus()
        self.update_progress()

    def selected_index(self):
        selection = self.task_list.curselection()
        if not selection:
            messagebox.showinfo("Select a task", "Choose a task from the list first.")
            return None
        return selection[0]

    def complete_task(self):
        index = self.selected_index()
        if index is None:
            return
        task = self.task_list.get(index)
        if not task.startswith("✓"):
            self.task_list.delete(index)
            self.task_list.insert(index, "✓" + task[1:])
            self.task_list.selection_set(index)
        self.update_progress()

    def delete_task(self):
        index = self.selected_index()
        if index is not None:
            self.task_list.delete(index)
            self.update_progress()

    def clear_tasks(self):
        if self.task_list.size() and messagebox.askyesno("Clear tasks", "Delete every task?"):
            self.task_list.delete(0, tk.END)
            self.update_progress()


if __name__ == "__main__":
    WidgetProject().mainloop()
