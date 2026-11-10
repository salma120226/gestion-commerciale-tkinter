import tkinter as tk
from tkinter import ttk
from database import fetch_data


class Dashboard(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#F4F6FB")

        self.pack(fill="both", expand=True)

        self.create_interface()
        self.load_data()


    def create_interface(self):

        # Main container
        container = tk.Frame(self, bg="#F4F6FB")
        container.pack(fill="both", expand=True, padx=30, pady=25)

        # Header
        header = tk.Frame(container, bg="#F4F6FB")
        header.pack(fill="x", pady=(0, 25))

        tk.Label(
            header,
            text="Dashboard",
            font=("Segoe UI", 25, "bold"),
            bg="#F4F6FB",
            fg="#20223A"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Bienvenue dans votre espace de gestion commerciale",
            font=("Segoe UI", 10),
            bg="#F4F6FB",
            fg="#85899B"
        ).pack(anchor="w", pady=(5, 0))

        # Statistics cards
        self.cards_frame = tk.Frame(container, bg="#F4F6FB")
        self.cards_frame.pack(fill="x", pady=(0, 25))

        self.cards = {}

        cards_data = [
            ("Produits", "0", "#635BDB"),
            ("Clients", "0", "#269C86"),
            ("Commandes", "0", "#E99B42"),
            ("Chiffre d'affaires", "0 DH", "#3287C9")
        ]

        for title, value, color in cards_data:

            card = tk.Frame(
                self.cards_frame,
                bg="white",
                highlightbackground="#E7E9F0",
                highlightthickness=1
            )

            card.pack(side="left", fill="both", expand=True, padx=(0, 12))

            tk.Frame(
                card,
                bg=color,
                height=4
            ).pack(fill="x")

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 10),
                bg="white",
                fg="#85899B"
            ).pack(anchor="w", padx=18, pady=(15, 5))

            value_label = tk.Label(
                card,
                text=value,
                font=("Segoe UI", 22, "bold"),
                bg="white",
                fg="#20223A"
            )

            value_label.pack(anchor="w", padx=18, pady=(0, 18))

            self.cards[title] = value_label

        # Content section
        content = tk.Frame(container, bg="#F4F6FB")
        content.pack(fill="both", expand=True)

        # Recent orders
        orders_frame = tk.Frame(
            content,
            bg="white",
            highlightbackground="#E7E9F0",
            highlightthickness=1
        )

        orders_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        tk.Label(
            orders_frame,
            text="Dernières commandes",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#20223A"
        ).pack(anchor="w", padx=18, pady=18)

        columns = ("ID", "Client", "Date", "Statut", "Montant")

        self.orders_table = ttk.Treeview(
            orders_frame,
            columns=columns,
            show="headings",
            height=9
        )

        for col in columns:
            self.orders_table.heading(col, text=col)
            self.orders_table.column(col, anchor="center", width=100)

        self.orders_table.column("Client", width=140)

        self.orders_table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # Low stock
        stock_frame = tk.Frame(
            content,
            bg="white",
            width=280,
            highlightbackground="#E7E9F0",
            highlightthickness=1
        )

        stock_frame.pack(
            side="right",
            fill="y"
        )

        stock_frame.pack_propagate(False)

        tk.Label(
            stock_frame,
            text="Alertes de stock",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#20223A"
        ).pack(anchor="w", padx=18, pady=18)

        self.stock_container = tk.Frame(
            stock_frame,
            bg="white"
        )

        self.stock_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # Refresh button
        tk.Button(
            container,
            text="Actualiser les données",
            font=("Segoe UI", 10, "bold"),
            bg="#635BDB",
            fg="white",
            activebackground="#5048BD",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=9,
            command=self.load_data
        ).pack(anchor="e", pady=(15, 0))

    # ================= LOAD DATA =================

    def get_value(self, query):

        result = fetch_data(query)

        if result:
            return list(result[0].values())[0]

        return 0

    def load_data(self):

        # Statistics
        products = self.get_value(
            "SELECT COUNT(*) AS total FROM PRODUIT"
        )

        clients = self.get_value(
            "SELECT COUNT(*) AS total FROM CLIENT"
        )

        orders = self.get_value(
            "SELECT COUNT(*) AS total FROM COMMANDE"
        )

        revenue = self.get_value("""
            SELECT COALESCE(
                SUM(L.QTTECMD * L.PRIXVENTE), 0
            ) AS total
            FROM LIGNE_COMMANDE L
            INNER JOIN COMMANDE C
                ON L.IDCMD = C.IDCMD
            WHERE C.STATUT = 'Validée'
        """)

        self.cards["Produits"].config(text=str(products))
        self.cards["Clients"].config(text=str(clients))
        self.cards["Commandes"].config(text=str(orders))
        self.cards["Chiffre d'affaires"].config(
            text=f"{float(revenue):,.2f} DH"
        )

        self.load_orders()
        self.load_stock_alerts()

    # ================= RECENT ORDERS =================

    def load_orders(self):

        for item in self.orders_table.get_children():
            self.orders_table.delete(item)

        query = """
            SELECT
                C.IDCMD,
                CL.NOMCL,
                C.DATECMD,
                C.STATUT,
                COALESCE(SUM(L.QTTECMD * L.PRIXVENTE), 0) AS MONTANT
            FROM COMMANDE C
            INNER JOIN CLIENT CL
                ON C.IDCL = CL.IDCL
            LEFT JOIN LIGNE_COMMANDE L
                ON C.IDCMD = L.IDCMD
            GROUP BY
                C.IDCMD, CL.NOMCL, C.DATECMD, C.STATUT
            ORDER BY C.DATECMD DESC, C.IDCMD DESC
            LIMIT 5
        """

        orders = fetch_data(query)

        for order in orders:

            self.orders_table.insert(
                "",
                "end",
                values=(
                    order["IDCMD"],
                    order["NOMCL"],
                    order["DATECMD"],
                    order["STATUT"],
                    f'{float(order["MONTANT"]):.2f} DH'
                )
            )


    def load_stock_alerts(self):

        for widget in self.stock_container.winfo_children():
            widget.destroy()

        query = """
            SELECT IDPROD, NOM, QTTE, SEUIL_ALERTE
            FROM PRODUIT
            WHERE QTTE < SEUIL_ALERTE
            ORDER BY QTTE ASC
            LIMIT 6
        """

        products = fetch_data(query)

        if not products:

            tk.Label(
                self.stock_container,
                text="Aucune alerte de stock",
                font=("Segoe UI", 10),
                bg="white",
                fg="#269C86"
            ).pack(anchor="w", pady=10)

            return

        for product in products:

            item = tk.Frame(
                self.stock_container,
                bg="#FFF5F3",
                padx=10,
                pady=10
            )

            item.pack(fill="x", pady=5)

            tk.Label(
                item,
                text=product["NOM"],
                font=("Segoe UI", 10, "bold"),
                bg="#FFF5F3",
                fg="#20223A",
                wraplength=220
            ).pack(anchor="w")

            tk.Label(
                item,
                text=f'Stock : {product["QTTE"]}  |  Seuil : {product["SEUIL_ALERTE"]}',
                font=("Segoe UI", 9),
                bg="#FFF5F3",
                fg="#DC665B"
            ).pack(anchor="w", pady=(4, 0))
