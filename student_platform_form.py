"""Personal-details form with study-platform guidance for students.

Run with: python student_platform_form.py
"""

import tkinter as tk
from tkinter import messagebox, ttk


class StudentPlatformForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Learning Platform Registration")
        self.geometry("650x610")
        self.configure(padx=24, pady=20, bg="#f3f8ff")
        self.resizable(False, False)

        self.name = tk.StringVar()
        self.age = tk.StringVar()
        self.email = tk.StringVar()
        self.role = tk.StringVar(value="Student")
        self.course = tk.StringVar(value="Python Programming")
        self.learning_mode = tk.StringVar(value="Videos")
        self.help_needed = tk.BooleanVar(value=True)

        self.create_form()

    def create_form(self):
        tk.Label(
            self, text="Learning Platform Form", font=("Arial", 21, "bold"),
            bg="#f3f8ff", fg="#173f70"
        ).pack(anchor="w")
        tk.Label(
            self, text="Fill in your details to get started.", bg="#f3f8ff", fg="#536b85"
        ).pack(anchor="w", pady=(0, 14))

        form = ttk.LabelFrame(self, text="Personal details", padding=16)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)

        self.add_entry(form, "Full name:", self.name, 0)
        self.add_entry(form, "Age:", self.age, 1)
        self.add_entry(form, "Email address:", self.email, 2)

        ttk.Label(form, text="You are a:").grid(row=3, column=0, sticky="w", pady=7)
        ttk.Radiobutton(form, text="Student", variable=self.role, value="Student").grid(
            row=3, column=1, sticky="w", pady=7
        )
        ttk.Radiobutton(form, text="Teacher", variable=self.role, value="Teacher").grid(
            row=3, column=2, sticky="w", pady=7
        )

        ttk.Label(form, text="Course interest:").grid(row=4, column=0, sticky="w", pady=7)
        ttk.Combobox(
            form, textvariable=self.course, state="readonly", width=27,
            values=("Python Programming", "Mathematics", "Science", "English", "Computer Basics")
        ).grid(row=4, column=1, columnspan=2, sticky="w", pady=7)

        ttk.Label(form, text="Preferred learning:").grid(row=5, column=0, sticky="w", pady=7)
        ttk.Combobox(
            form, textvariable=self.learning_mode, state="readonly", width=27,
            values=("Videos", "Reading notes", "Practice exercises", "Live classes")
        ).grid(row=5, column=1, columnspan=2, sticky="w", pady=7)

        ttk.Checkbutton(
            form, text="I need help using the study platform", variable=self.help_needed
        ).grid(row=6, column=0, columnspan=3, sticky="w", pady=(7, 2))

        ttk.Button(self, text="Submit form", command=self.submit_form).pack(fill="x", pady=16)

        self.result = tk.Text(self, height=11, wrap="word", font=("Arial", 10), padx=12, pady=10)
        self.result.pack(fill="both", expand=True)
        self.result.insert("1.0", "Your personalised learning information will appear here.")
        self.result.config(state="disabled")

    @staticmethod
    def add_entry(parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=7)
        ttk.Entry(parent, textvariable=variable, width=34).grid(
            row=row, column=1, columnspan=2, sticky="ew", pady=7
        )

    def submit_form(self):
        name = self.name.get().strip()
        age = self.age.get().strip()
        email = self.email.get().strip()

        if not name or not age or not email:
            messagebox.showwarning("Missing details", "Please enter your name, age, and email address.")
            return
        if not age.isdigit() or not 4 <= int(age) <= 120:
            messagebox.showwarning("Invalid age", "Please enter a valid age.")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showwarning("Invalid email", "Please enter a valid email address.")
            return

        message = (
            f"Welcome, {name}!\n\n"
            f"Profile saved for: {self.role.get()}\n"
            f"Selected course: {self.course.get()}\n"
            f"Preferred learning method: {self.learning_mode.get()}\n\n"
        )

        if self.role.get() == "Student":
            message += (
                "How to use the study platform:\n"
                "1. Open the dashboard and choose your course.\n"
                "2. Watch lessons or read the study notes.\n"
                "3. Complete practice exercises after each lesson.\n"
                "4. Check your progress and repeat difficult topics.\n"
                "5. Ask your teacher or platform support when you need help.\n\n"
            )
            if self.help_needed.get():
                message += "Tip: Start with the first lesson and complete one small activity today."
            else:
                message += "You are ready to begin learning!"
        else:
            message += "You can use the platform to create lessons, share notes, and review student progress."

        self.result.config(state="normal")
        self.result.delete("1.0", tk.END)
        self.result.insert("1.0", message)
        self.result.config(state="disabled")
        messagebox.showinfo("Form submitted", "Your details have been submitted successfully.")


if __name__ == "__main__":
    StudentPlatformForm().mainloop()
