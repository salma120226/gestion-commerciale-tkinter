import tkinter as tk
from tkinter import messagebox
from database import fetch_data, execute_query, run_procedure
from pages.Ui import (
    BG, DARK, GREY, GREEN, PURPLE, RED,
    page_header, card, card_title, action_button, form_field, form_combo,
    make_table, fill_table, selected_values, fmt_money
)


class Commandes(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        self.pack(fill="both", expand=True, padx=30, pady=25)

        self.cart = {}
        self.clients_map = {}
        self.products_map = {}

        self.create_interface()
        self.load_lists()
        self.load_orders()

    def create_interface(self):

        page_header(
            self,
            "Gestion des Commandes",
            "Créez des commandes, validez-les ou annulez-les."
        )

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        body.grid_columnconfigure(0, weight=1, uniform="col")
        body.grid_columnconfigure(1, weight=1, uniform="col")
        body.grid_rowconfigure(0, weight=1)

        left = card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        card_title(left, "Nouvelle commande")

        fields = tk.Frame(left, bg="white")
        fields.pack(fill="x")

        self.client_combo = form_combo(fields, "Client", 0, 0, columnspan=2)
        self.product_combo = form_combo(fields, "Produit", 1, 0, columnspan=2)
        self.qty_entry = form_field(fields, "Quantité", 2, 0)
        self.qty_entry.insert(0, "1")

        add_frame = tk.Frame(fields, bg="white")
        add_frame.grid(row=2, column=1, sticky="sw", padx=18, pady=5)
        action_button(add_frame, "Ajouter au panier", PURPLE, self.add_to_cart)

        self.cart_table = make_table(
            left,
            [
                ("ID", "ID", 45),
                ("Produit", "Produit", 170),
                ("Qté", "Qté", 55),
                ("Prix", "Prix (DH)", 80),
                ("Sous-total", "Sous-total", 95)
            ],
            6
        )

        footer = tk.Frame(left, bg="white")
        footer.pack(fill="x", padx=18, pady=(0, 15))

        action_button(footer, "Enregistrer", GREEN, self.save_order)
        action_button(footer, "Retirer", RED, self.remove_from_cart)
        action_button(footer, "Vider", GREY, self.clear_cart)

        self.total_label = tk.Label(
            footer,
            text="Total : 0.00 DH",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg=DARK
        )
        self.total_label.pack(side="right")

        right = card(body)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        card_title(right, "Liste des commandes")

        actions = tk.Frame(right, bg="white")
        actions.pack(fill="x", padx=18, pady=(0, 10))

        action_button(actions, "Valider", GREEN, self.validate_order)
        action_button(actions, "Annuler", RED, self.cancel_order)
        action_button(actions, "Actualiser", GREY, self.refresh)

        self.orders_table = make_table(
            right,
            [
                ("ID", "N°", 45),
                ("Client", "Client", 150),
                ("Date", "Date", 95),
                ("Statut", "Statut", 90),
                ("Montant", "Montant", 100)
            ],
            7
        )
        self.orders_table.bind("<<TreeviewSelect>>", self.load_detail)

        tk.Label(
            right,
            text="Détail de la commande sélectionnée",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=DARK
        ).pack(anchor="w", padx=18, pady=(0, 8))

        self.detail_table = make_table(
            right,
            [
                ("Produit", "Produit", 170),
                ("Qté", "Qté", 55),
                ("Prix", "Prix de vente", 100),
                ("Sous-total", "Sous-total", 100)
            ],
            5
        )

    def refresh(self):

        self.load_lists()
        self.load_orders()

    def load_lists(self):

        clients = fetch_data("SELECT IDCL, NOMCL FROM CLIENT ORDER BY NOMCL")
        products = fetch_data("SELECT IDPROD, NOM, PRIX, QTTE FROM PRODUIT ORDER BY NOM")

        self.clients_map = {}
        for client in clients:
            label = f'{client["NOMCL"]} (#{client["IDCL"]})'
            self.clients_map[label] = client["IDCL"]

        self.products_map = {}
        for product in products:
            label = f'{product["NOM"]}  ({float(product["PRIX"]):.2f} DH | stock : {product["QTTE"]})'
            self.products_map[label] = {
                "id": product["IDPROD"],
                "name": product["NOM"],
                "price": float(product["PRIX"]),
                "stock": int(product["QTTE"])
            }

        self.client_combo["values"] = list(self.clients_map.keys())
        self.product_combo["values"] = list(self.products_map.keys())

    def add_to_cart(self):

        label = self.product_combo.get()

        if label not in self.products_map:
            messagebox.showwarning("Produit", "Veuillez choisir un produit.")
            return

        try:
            quantity = int(self.qty_entry.get().strip())
        except ValueError:
            quantity = 0

        if quantity <= 0:
            messagebox.showwarning(
                "Quantité invalide",
                "La quantité doit être un entier supérieur à 0."
            )
            return

        product = self.products_map[label]
        already = self.cart.get(product["id"], {}).get("qty", 0)

        if already + quantity > product["stock"]:
            messagebox.showwarning(
                "Stock insuffisant",
                f'Stock disponible : {product["stock"]}.'
            )
            return

        if product["id"] in self.cart:
            self.cart[product["id"]]["qty"] += quantity
        else:
            self.cart[product["id"]] = {
                "name": product["name"],
                "qty": quantity,
                "price": product["price"]
            }

        self.refresh_cart()

    def refresh_cart(self):

        rows = []
        total = 0

        for product_id, line in self.cart.items():
            subtotal = line["qty"] * line["price"]
            total += subtotal
            rows.append((
                product_id,
                line["name"],
                line["qty"],
                f'{line["price"]:.2f}',
                f"{subtotal:.2f}"
            ))

        fill_table(self.cart_table, rows)
        self.total_label.config(text=f"Total : {total:,.2f} DH")

    def remove_from_cart(self):

        values = selected_values(self.cart_table)

        if values is None:
            messagebox.showwarning("Sélection", "Sélectionnez une ligne du panier.")
            return

        self.cart.pop(int(values[0]), None)
        self.refresh_cart()

    def clear_cart(self):

        self.cart = {}
        self.refresh_cart()

    def save_order(self):

        client_label = self.client_combo.get()

        if client_label not in self.clients_map:
            messagebox.showwarning("Client", "Veuillez choisir un client.")
            return

        if not self.cart:
            messagebox.showwarning("Panier", "Ajoutez au moins un produit au panier.")
            return

        client_id = self.clients_map[client_label]

        response = run_procedure("CreerCommande", (client_id, 0))

        if not response["ok"]:
            messagebox.showerror("Erreur", response["error"])
            return

        order_id = response["args"][1]

        for product_id, line in self.cart.items():

            response = run_procedure(
                "AjouterLigneCommande",
                (order_id, product_id, line["qty"])
            )

            if not response["ok"]:
                execute_query("DELETE FROM COMMANDE WHERE IDCMD = %s", (order_id,))
                messagebox.showerror("Erreur", response["error"])
                return

        self.clear_cart()
        self.load_orders()

        validate_now = messagebox.askyesno(
            "Commande enregistrée",
            f"La commande n°{order_id} a été créée (en attente).\nVoulez-vous la valider maintenant ?"
        )

        if validate_now:
            self.run_order_action("ValiderCommande", order_id, "validée")

    def selected_order(self):

        values = selected_values(self.orders_table)

        if values is None:
            messagebox.showwarning(
                "Sélection",
                "Veuillez sélectionner une commande dans la liste."
            )
            return None

        return int(values[0])

    def run_order_action(self, procedure, order_id, label):

        response = run_procedure(procedure, (order_id,))

        if response["ok"]:
            messagebox.showinfo("Succès", f"Commande n°{order_id} {label}.")
        else:
            messagebox.showerror("Erreur", response["error"])

        self.refresh()

    def validate_order(self):

        order_id = self.selected_order()

        if order_id is None:
            return

        self.run_order_action("ValiderCommande", order_id, "validée")

    def cancel_order(self):

        order_id = self.selected_order()

        if order_id is None:
            return

        confirm = messagebox.askyesno(
            "Confirmation",
            f"Voulez-vous vraiment annuler la commande n°{order_id} ?"
        )

        if confirm:
            self.run_order_action("AnnulerCommande", order_id, "annulée")

    def load_orders(self):

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
            GROUP BY C.IDCMD, CL.NOMCL, C.DATECMD, C.STATUT
            ORDER BY C.IDCMD DESC
        """

        orders = fetch_data(query)

        fill_table(
            self.orders_table,
            [
                (o["IDCMD"], o["NOMCL"], o["DATECMD"], o["STATUT"], fmt_money(o["MONTANT"]))
                for o in orders
            ],
            tag_column=3
        )

        fill_table(self.detail_table, [])

    def load_detail(self, event):

        values = selected_values(self.orders_table)

        if values is None:
            return

        query = """
            SELECT
                P.NOM,
                L.QTTECMD,
                L.PRIXVENTE,
                L.QTTECMD * L.PRIXVENTE AS SOUS_TOTAL
            FROM LIGNE_COMMANDE L
            INNER JOIN PRODUIT P
                ON P.IDPROD = L.IDPROD
            WHERE L.IDCMD = %s
            ORDER BY P.NOM
        """

        lines = fetch_data(query, (int(values[0]),))

        fill_table(
            self.detail_table,
            [
                (l["NOM"], l["QTTECMD"], fmt_money(l["PRIXVENTE"]), fmt_money(l["SOUS_TOTAL"]))
                for l in lines
            ]
        )
