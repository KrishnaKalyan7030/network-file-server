import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "..", "downloads")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


class Dashboard(ctk.CTk):

    def __init__(self, client_socket, username):
        super().__init__()

        self.client_socket = client_socket
        self.username = username

        self.title("Network File Server")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        self.configure(fg_color="#0b1220")

        self.build_ui()
        self.list_files()

    # ========================= UI ========================= #

    def build_ui(self):

        # ================= HEADER =================
        header = ctk.CTkFrame(self, height=70, fg_color="#0f172a")
        header.pack(fill="x", padx=10, pady=10)

        title = ctk.CTkLabel(
            header,
            text="🗂 Network File Server",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=20)

        user_label = ctk.CTkLabel(
            header,
            text=f"User: {self.username}",
            font=("Arial", 14)
        )
        user_label.pack(side="right", padx=20)

        # ================= MAIN =================
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ================= SIDEBAR =================
        left_frame = ctk.CTkFrame(
            main_frame,
            width=240,
            fg_color="#0f172a"
        )
        left_frame.pack(side="left", fill="y", padx=(10, 10), pady=10)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(
            left_frame,
            text="Operations",
            font=("Arial", 20, "bold")
        ).pack(pady=(20, 25))

        operations = [
            ("⬆ Upload", self.upload_file),
            ("⬇ Download", self.download_file),
            ("📄 List Files", self.list_files),
            ("✏ Rename", self.rename_file),
            ("🗑 Delete", self.delete_file),
            ("🤝 Share", self.share_file),
            ("📜 History", self.view_history),
            ("🚪 Logout", self.logout)
        ]

        for text, command in operations:
            btn = ctk.CTkButton(
                left_frame,
                text=text,
                width=200,
                height=42,
                fg_color="#1f2937",
                hover_color="#2563eb",
                corner_radius=10,
                anchor="w",
                command=command
            )
            btn.pack(pady=6, padx=10)

        # ================= RIGHT PANEL =================
        right_frame = ctk.CTkFrame(main_frame, fg_color="#0f172a")
        right_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        ctk.CTkLabel(
            right_frame,
            text="Files",
            font=("Arial", 22, "bold")
        ).pack(pady=10)

        self.files_box = ctk.CTkTextbox(
            right_frame,
            font=("Consolas", 14),
            fg_color="#0b1220",
            text_color="#e5e7eb",
            corner_radius=10
        )
        self.files_box.pack(fill="both", expand=True, padx=15, pady=10)

        self.files_box.insert(
            "end",
            "Welcome to Network File Server\n\nFiles will appear here..."
        )

        # ================= STATUS BAR =================
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready • Connected",
            font=("Arial", 12),
            text_color="#9ca3af"
        )
        self.status_label.pack(side="bottom", pady=5)

    # ================= STATUS ================= #

    def set_status(self, msg):
        self.status_label.configure(text=msg)
        self.update_idletasks()

    # ================= LIST FILES ================= #

    def list_files(self):
        try:
            self.set_status("Loading files...")

            self.client_socket.send("LIST".encode())
            response = self.client_socket.recv(4096).decode()

            self.files_box.delete("1.0", "end")
            self.files_box.insert("end", "📁 Available Files:\n\n")
            self.files_box.insert("end", response)

            self.set_status("Files loaded")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error loading files")

    # ================= LOGOUT ================= #

    def logout(self):
        try:
            self.client_socket.send("LOGOUT".encode())
            self.client_socket.close()
        except:
            pass

        self.destroy()

    # ================= UPLOAD ================= #

    def upload_file(self):

        filepath = filedialog.askopenfilename()
        if not filepath:
            return

        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        try:
            self.set_status("Uploading file...")

            command = f"UPLOAD {filename} {filesize}"
            self.client_socket.send(command.encode())

            response = self.client_socket.recv(1024).decode()

            if response != "READY":
                messagebox.showerror("Error", "Server not ready")
                return

            with open(filepath, "rb") as file:
                sent = 0

                while True:
                    data = file.read(1024)
                    if not data:
                        break

                    self.client_socket.sendall(data)
                    sent += len(data)

                    progress = (sent / filesize) * 100
                    self.set_status(f"Uploading... {progress:.1f}%")

            server_response = self.client_socket.recv(1024).decode()

            if server_response == "UPLOAD_SUCCESS":
                messagebox.showinfo("Success", "File uploaded successfully")
                self.set_status("Upload complete")

            elif server_response == "FILE_ALREADY_EXISTS":
                messagebox.showerror("Error", "File already exists")
                self.set_status("Upload failed")
                self.list_files()

            else:
                messagebox.showerror("Error", server_response)
                self.set_status("Upload error")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Upload error")

    # ================= DOWNLOAD ================= #

    def download_file(self):

        dialog = ctk.CTkInputDialog(
            text="Enter filename:",
            title="Download File"
        )

        filename = dialog.get_input()
        if not filename:
            return

        try:
            self.set_status("Downloading...")

            self.client_socket.send(f"DOWNLOAD {filename}".encode())

            response = self.client_socket.recv(1024).decode()

            if response == "ACCESS_DENIED":
                messagebox.showerror("Error", "Access denied")
                return

            if response == "FILE_NOT_FOUND":
                messagebox.showerror("Error", "File not found")
                return

            filesize = int(response)
            self.client_socket.send("READY".encode())

            path = os.path.join(DOWNLOAD_FOLDER, filename)

            with open(path, "wb") as file:
                received = 0

                while received < filesize:
                    data = self.client_socket.recv(1024)
                    if not data:
                        break

                    file.write(data)
                    received += len(data)

            messagebox.showinfo("Success", f"Downloaded to:\n{path}")
            self.set_status("Download complete")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Download error")

    # ================= RENAME ================= #

    def rename_file(self):

        old = ctk.CTkInputDialog(text="Old filename:", title="Rename").get_input()
        if not old:
            return

        new = ctk.CTkInputDialog(text="New filename:", title="Rename").get_input()
        if not new:
            return

        try:
            self.client_socket.send(f"RENAME {old} {new}".encode())
            response = self.client_socket.recv(1024).decode()

            if "success" in response.lower():
                messagebox.showinfo("Success", response)
                self.list_files()
            else:
                messagebox.showerror("Error", response)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= DELETE ================= #

    def delete_file(self):

        filename = ctk.CTkInputDialog(
            text="Filename to delete:",
            title="Delete"
        ).get_input()

        if not filename:
            return

        try:
            self.client_socket.send(f"DELETE {filename}".encode())
            response = self.client_socket.recv(1024).decode()

            if "success" in response.lower():
                messagebox.showinfo("Success", response)
                self.list_files()
            else:
                messagebox.showerror("Error", response)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= SHARE ================= #

    def share_file(self):

        filename = ctk.CTkInputDialog(
            text="Filename:",
            title="Share"
        ).get_input()

        if not filename:
            return

        user = ctk.CTkInputDialog(
            text="Share with user:",
            title="Share"
        ).get_input()

        if not user:
            return

        try:
            self.client_socket.send(f"SHARE {filename} {user}".encode())
            response = self.client_socket.recv(1024).decode()

            if "success" in response.lower():
                messagebox.showinfo("Success", response)
            else:
                messagebox.showerror("Error", response)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= HISTORY ================= #

    def view_history(self):

        try:
            self.client_socket.send("HISTORY".encode())
            history = self.client_socket.recv(4096).decode()

            if history == "ACCESS_DENIED":
                messagebox.showerror("Error", "Admin only feature")
                return

            self.files_box.delete("1.0", "end")
            self.files_box.insert("end", "📜 History:\n\n")
            self.files_box.insert("end", history)

        except Exception as e:
            messagebox.showerror("Error", str(e))









