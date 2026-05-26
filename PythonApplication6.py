import json
import os
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ============================================================
# Random Password Generator — GUI Application
# ============================================================

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Constants
        self.MIN_LENGTH = 4
        self.MAX_LENGTH = 128
        self.HISTORY_FILE = "password_history.json"

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # History data
        self.history = []
        self.load_history()

        # Build UI
        self.create_widgets()
        self.update_password_preview()

    def configure_styles(self):
        """Configure custom styles for widgets"""
        self.style.configure("Title.TLabel",
                            font=("Segoe UI", 20, "bold"),
                            foreground="#cdd6f4",
                            background="#1e1e2e")

        self.style.configure("Section.TLabel",
                            font=("Segoe UI", 12, "bold"),
                            foreground="#89b4fa",
                            background="#1e1e2e")

        self.style.configure("Info.TLabel",
                            font=("Segoe UI", 10),
                            foreground="#a6adc8",
                            background="#1e1e2e")

        self.style.configure("Password.TLabel",
                            font=("Consolas", 16, "bold"),
                            foreground="#a6e3a1",
                            background="#313244",
                            anchor="center")

        self.style.configure("Generate.TButton",
                            font=("Segoe UI", 12, "bold"),
                            foreground="#1e1e2e",
                            background="#89b4fa")

        self.style.configure("Action.TButton",
                            font=("Segoe UI", 10),
                            foreground="#cdd6f4",
                            background="#45475a")

        self.style.configure("Custom.TCheckbutton",
                            font=("Segoe UI", 11),
                            foreground="#cdd6f4",
                            background="#1e1e2e")

        self.style.configure("Custom.Horizontal.TScale",
                            background="#1e1e2e",
                            troughcolor="#313244")

    def create_widgets(self):
        """Create all UI elements"""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg="#1e1e2e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ===== TITLE =====
        title_label = ttk.Label(main_frame, text="Random Password Generator",
                                style="Title.TLabel")
        title_label.pack(pady=(0, 15))

        # ===== PASSWORD DISPLAY =====
        display_frame = tk.Frame(main_frame, bg="#313244", bd=2, relief=tk.RIDGE)
        display_frame.pack(fill=tk.X, pady=(0, 15))

        self.password_var = tk.StringVar(value="Your password will appear here")
        self.password_label = ttk.Label(display_frame, textvariable=self.password_var,
                                       style="Password.TLabel", wraplength=520)
        self.password_label.pack(pady=15, padx=10, fill=tk.X)

        # Password action buttons
        btn_frame = tk.Frame(display_frame, bg="#313244")
        btn_frame.pack(pady=(0, 10))

        self.copy_btn = ttk.Button(btn_frame, text="Copy", command=self.copy_password,
                                   style="Action.TButton", width=12)
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        self.regenerate_btn = ttk.Button(btn_frame, text="Regenerate",
                                         command=self.generate_password,
                                         style="Action.TButton", width=12)
        self.regenerate_btn.pack(side=tk.LEFT, padx=5)

        # ===== SETTINGS SECTION =====
        settings_frame = tk.LabelFrame(main_frame, text=" Password Settings ",
                                       bg="#1e1e2e", fg="#89b4fa",
                                       font=("Segoe UI", 11, "bold"),
                                       padx=15, pady=15)
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # Length slider
        length_label = ttk.Label(settings_frame, text="Password Length:",
                                 style="Section.TLabel")
        length_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.length_var = tk.IntVar(value=16)
        self.length_display = ttk.Label(settings_frame, text="16",
                                       style="Section.TLabel")
        self.length_display.grid(row=0, column=1, sticky=tk.E, pady=(0, 5))

        self.length_slider = ttk.Scale(settings_frame, from_=self.MIN_LENGTH,
                                       to=self.MAX_LENGTH, orient=tk.HORIZONTAL,
                                       variable=self.length_var,
                                       command=self.on_length_change,
                                       style="Custom.Horizontal.TScale")
        self.length_slider.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        # Character type checkboxes
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)

        checkbox_frame = tk.Frame(settings_frame, bg="#1e1e2e")
        checkbox_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        ttk.Checkbutton(checkbox_frame, text="A-Z (Uppercase)",
                        variable=self.use_uppercase,
                        style="Custom.TCheckbutton").pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame, text="a-z (Lowercase)",
                        variable=self.use_lowercase,
                        style="Custom.TCheckbutton").pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame, text="0-9 (Digits)",
                        variable=self.use_digits,
                        style="Custom.TCheckbutton").pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame, text="!@#$%^&* (Special)",
                        variable=self.use_special,
                        style="Custom.TCheckbutton").pack(anchor=tk.W, pady=2)

        settings_frame.columnconfigure(0, weight=1)

        # ===== GENERATE BUTTON =====
        self.generate_btn = ttk.Button(main_frame, text="GENERATE PASSWORD",
                                         command=self.generate_password,
                                         style="Generate.TButton")
        self.generate_btn.pack(fill=tk.X, pady=(0, 15), ipady=8)

        # ===== HISTORY SECTION =====
        history_frame = tk.LabelFrame(main_frame, text=" Generation History ",
                                      bg="#1e1e2e", fg="#89b4fa",
                                      font=("Segoe UI", 11, "bold"),
                                      padx=10, pady=10)
        history_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for history
        columns = ("time", "length", "password")
        self.history_tree = ttk.Treeview(history_frame, columns=columns,
                                          show="headings", height=8)

        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("length", text="Length")
        self.history_tree.heading("password", text="Password")

        self.history_tree.column("time", width=120, anchor=tk.CENTER)
        self.history_tree.column("length", width=60, anchor=tk.CENTER)
        self.history_tree.column("password", width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL,
                                command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # History buttons
        history_btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        history_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(history_btn_frame, text="Clear History",
                   command=self.clear_history,
                   style="Action.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(history_btn_frame, text="Save to JSON",
                   command=self.save_history,
                   style="Action.TButton").pack(side=tk.RIGHT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                               style="Info.TLabel")
        status_bar.pack(anchor=tk.W, pady=(10, 0))

        # Populate history
        self.refresh_history_display()

    def on_length_change(self, value):
        """Update length display when slider moves"""
        self.length_display.config(text=str(int(float(value))))

    def get_character_set(self):
        """Build character set based on selected options"""
        chars = ""
        if self.use_uppercase.get():
            chars += string.ascii_uppercase
        if self.use_lowercase.get():
            chars += string.ascii_lowercase
        if self.use_digits.get():
            chars += string.digits
        if self.use_special.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return chars

    def validate_settings(self):
        """Validate user input before generation"""
        length = self.length_var.get()

        # Check length bounds
        if length < self.MIN_LENGTH:
            messagebox.showerror("Invalid Length",
                f"Minimum password length is {self.MIN_LENGTH} characters.")
            return False
        if length > self.MAX_LENGTH:
            messagebox.showerror("Invalid Length",
                f"Maximum password length is {self.MAX_LENGTH} characters.")
            return False

        # Check at least one character type selected
        if not self.get_character_set():
            messagebox.showerror("No Characters Selected",
                "Please select at least one character type (uppercase, lowercase, digits, or special).")
            return False

        return True

    def generate_password(self):
        """Generate a random password based on settings"""
        if not self.validate_settings():
            return

        length = self.length_var.get()
        chars = self.get_character_set()

        # Ensure at least one character from each selected type
        password = []
        if self.use_uppercase.get():
            password.append(random.choice(string.ascii_uppercase))
        if self.use_lowercase.get():
            password.append(random.choice(string.ascii_lowercase))
        if self.use_digits.get():
            password.append(random.choice(string.digits))
        if self.use_special.get():
            password.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

        # Fill the rest randomly
        remaining = length - len(password)
        password.extend(random.choices(chars, k=remaining))

        # Shuffle to randomize positions
        random.shuffle(password)
        password = ''.join(password)

        # Update display
        self.password_var.set(password)

        # Add to history
        self.add_to_history(password, length)

        self.status_var.set(f"Generated password of length {length}")

    def add_to_history(self, password, length):
        """Add generated password to history"""
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "length": length,
            "password": password
        }
        self.history.insert(0, entry)

        # Keep only last 50 entries
        if len(self.history) > 50:
            self.history = self.history[:50]

        self.refresh_history_display()
        self.save_history()

    def refresh_history_display(self):
        """Refresh the history treeview"""
        # Clear existing
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Add entries
        for entry in self.history:
            # Mask password for display
            masked = entry["password"][:3] + "***" + entry["password"][-3:] if len(entry["password"]) > 6 else "***"
            self.history_tree.insert("", tk.END, values=(
                entry["time"],
                entry["length"],
                masked
            ))

    def copy_password(self):
        """Copy current password to clipboard"""
        password = self.password_var.get()
        if password and password != "Your password will appear here":
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.status_var.set("Password copied to clipboard!")
        else:
            messagebox.showwarning("No Password", "Generate a password first!")

    def clear_history(self):
        """Clear all history entries"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
            self.history = []
            self.refresh_history_display()
            self.save_history()
            self.status_var.set("History cleared")

    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.status_var.set(f"Error saving history: {e}")

    def load_history(self):
        """Load history from JSON file"""
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                self.history = []
                print(f"Error loading history: {e}")

    def update_password_preview(self):
        """Generate initial password on startup"""
        self.generate_password()


# ============================================================
# Main Entry Point
# ============================================================

def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()