import customtkinter as ctk
from tkinter import messagebox

from app.client.services import login_user, register_user
from app.client.gui.dashboard import Dashboard


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class LoginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Network File Server")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.resizable(True, True)

        self.client_socket = None
        self.show_password = False

        self.build_ui()

        self.bind("<Return>", lambda event: self.login())

    # ---------------- UI ---------------- #

    def build_ui(self):

        main_frame = ctk.CTkFrame(self, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT PANEL
        left_frame = ctk.CTkFrame(
            main_frame,
            width=260,
            corner_radius=20,
            fg_color="#0f172a"
        )
        left_frame.pack(side="left", fill="y", padx=(0, 15))
        left_frame.pack_propagate(False)

        logo = ctk.CTkLabel(
            left_frame,
            text="🗂",
            font=("Arial", 100)
        )
        logo.pack(pady=(100, 10))

        ctk.CTkLabel(
            left_frame,
            text="Welcome Back",
            font=("Arial", 28, "bold")
        ).pack()

        ctk.CTkLabel(
            left_frame,
            text="Secure File Storage System",
            font=("Arial", 16)
        ).pack(pady=10)

        ctk.CTkLabel(
            left_frame,
            text=(
                "Upload, Download\n"
                "Share & Manage Files\n"
                "Across Network"
            ),
            font=("Arial", 14),
            justify="left"
        ).pack(pady=10)

        ctk.CTkLabel(
            left_frame,
            text="✓ Secure Login\n✓ File Upload\n✓ File Download\n✓ Sharing",
            font=("Arial", 14),
            justify="left"
        ).pack(pady=20)

        # RIGHT PANEL
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        center_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(
            center_frame,
            text="NETWORK FILE SERVER",
            font=("Arial", 34, "bold")
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            center_frame,
            text="Sign in to continue",
            font=("Arial", 16)
        ).pack(pady=(0, 30))

        # Username
        self.username_entry = ctk.CTkEntry(
            center_frame,
            width=380,
            height=50,
            placeholder_text="Username",
            corner_radius=12,
            border_width=2
        )
        self.username_entry.pack(pady=10)

        # Password
        self.password_entry = ctk.CTkEntry(
            center_frame,
            width=380,
            height=50,
            placeholder_text="Password",
            corner_radius=12,
            border_width=2,
            show="*"
        )
        self.password_entry.pack(pady=10)

        # Toggle password button
        self.toggle_btn = ctk.CTkButton(
            center_frame,
            text="Show Password",
            width=140,
            height=30,
            fg_color="transparent",
            border_width=1,
            command=self.toggle_password
        )
        self.toggle_btn.pack(pady=5)

        # Login button
        self.login_btn = ctk.CTkButton(
            center_frame,
            text="Login",
            width=380,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.login
        )
        self.login_btn.pack(pady=(20, 10))

        # Register button
        ctk.CTkButton(
            center_frame,
            text="Create Account",
            width=380,
            height=50,
            font=("Arial", 16),
            fg_color="transparent",
            border_width=2,
            command=self.register
        ).pack(pady=10)

        # Footer
        ctk.CTkLabel(
            right_frame,
            text="Network File Server v1.0 | Python • Socket • CustomTkinter",
            font=("Arial", 12)
        ).pack(side="bottom", pady=20)

        self.username_entry.focus()

        # UX binds
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Tab>", lambda e: self.password_entry.focus())

    # ---------------- UX ---------------- #

    def toggle_password(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.password_entry.configure(show="")
            self.toggle_btn.configure(text="Hide Password")
        else:
            self.password_entry.configure(show="*")
            self.toggle_btn.configure(text="Show Password")

    # ---------------- LOGIN ---------------- #

    def login(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        self.login_btn.configure(state="disabled", text="Logging in...")
        self.update_idletasks()

        success, client_socket = login_user(username, password)

        self.login_btn.configure(state="normal", text="Login")

        if success:

            self.client_socket = client_socket

            messagebox.showinfo("Success", "Login Successful")

            self.destroy()

            dashboard = Dashboard(client_socket, username)
            dashboard.mainloop()

        else:
            messagebox.showerror("Error", "Invalid Credentials")

    # ---------------- REGISTER ---------------- #

    def register(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        response = register_user(username, password)

        if response == "REGISTER_SUCCESS":
            messagebox.showinfo("Success", "Registration Successful")

        elif response == "USER_EXISTS":
            messagebox.showerror("Error", "User already exists")

        else:
            messagebox.showerror("Error", response)


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()