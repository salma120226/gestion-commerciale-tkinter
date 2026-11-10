import tkinter as tk
from pages.dashboard import Dashboard
from pages.produits import Produits
from pages.clients import Clients
from pages.commandes import Commandes
from pages.rapport import Rapports    

class NovaCommerce:

    def __init__(self, root):

        self.root = root
        self.root.title("Nova-Commerce | Gestion Commerciale")
        self.root.geometry("1350x800")
        self.root.minsize(1100, 650)
        self.root.configure(bg="#F4F6FB")

        self.create_sidebar()
        self.create_content()
        self.show_dashboard()

    def create_sidebar(self):

        self.sidebar = tk.Frame(
            self.root,
            bg="#20223A",
            width=240
        )

        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="NOVA",
            font=("Segoe UI", 24, "bold"),
            bg="#20223A",
            fg="white"
        ).pack(anchor="w", padx=25, pady=(30, 0))

        tk.Label(
            self.sidebar,
            text="COMMERCE",
            font=("Segoe UI", 10, "bold"),
            bg="#20223A",
            fg="#8B88E8"
        ).pack(anchor="w", padx=27, pady=(0, 35))

        self.nav_buttons = {}

        menu_items = [
            ("Dashboard", "⌂"),
            ("Produits", "▣"),
            ("Clients", "♙"),
            ("Commandes", "▤"),
            ("Rapports", "▥")
        ]

        for name, icon in menu_items:

            button = tk.Button(
                self.sidebar,
                text=f"  {icon}     {name}",
                font=("Segoe UI", 11),
                bg="#20223A",
                fg="#C5C6D4",
                activebackground="#635BDB",
                activeforeground="white",
                anchor="w",
                relief="flat",
                bd=0,
                padx=20,
                pady=14,
                cursor="hand2",
                command=lambda page=name: self.navigate(page)
            )

            button.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[name] = button

        tk.Label(
            self.sidebar,
            text="Version 1.0.0",
            font=("Segoe UI", 9),
            bg="#20223A",
            fg="#85899B"
        ).pack(side="bottom", pady=20)

    def create_content(self):

        self.content = tk.Frame(
            self.root,
            bg="#F4F6FB"
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def navigate(self, page):

        self.clear_content()

        if page == "Dashboard":
            Dashboard(self.content)

        elif page == "Produits":
            Produits(self.content)

        elif page == "Clients":
            Clients(self.content)

        elif page == "Commandes":
            Commandes(self.content)

        elif page == "Rapports":
            Rapports(self.content)

        else:
            self.show_placeholder(page)

        self.update_active_button(page)

    def update_active_button(self, active_page):

        for name, button in self.nav_buttons.items():

            if name == active_page:
                button.config(
                    bg="#635BDB",
                    fg="white"
                )
            else:
                button.config(
                    bg="#20223A",
                    fg="#C5C6D4"
                )

    def show_dashboard(self):

        self.clear_content()
        Dashboard(self.content)
        self.update_active_button("Dashboard")

    def show_placeholder(self, page):

        tk.Label(
            self.content,
            text=page,
            font=("Segoe UI", 25, "bold"),
            bg="#F4F6FB",
            fg="#20223A"
        ).pack(anchor="w", padx=35, pady=(40, 10))

        tk.Label(
            self.content,
            text="Cette section sera développée prochainement.",
            font=("Segoe UI", 11),
            bg="#F4F6FB",
            fg="#85899B"
        ).pack(anchor="w", padx=35)


if __name__ == "__main__":

    root = tk.Tk()
    app = NovaCommerce(root)
    root.mainloop()
