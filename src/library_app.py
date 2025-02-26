import tkinter as tk
from .database import Database
from .auth_window import AuthWindow
from .main_window import MainWindow


class LibraryApp:
    def __init__(self):
        self.db = Database()
        self.root = tk.Tk()
        self.root.title("Университетская библиотека")
        self.current_user = None

        self.auth_window = AuthWindow(self.db, self.switch_to_main)
        self.main_window = None

        self.auth_window.show_login_window(self.root)

    def switch_to_main(self, user_role, user):
        self.current_user = user
        self.main_window = MainWindow(self.db, self.root, user_role, user)

    def run(self):
        self.root.mainloop()