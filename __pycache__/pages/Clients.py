import tkinter as tk
from tkinter import messagebox
from database import fetch_data, run_query, run_procedure
from pages.ui import (
    BG, DARK, GREY, GREEN, PURPLE, RED,
    page_header, card, card_title, action_button, form_field,
    make_table, fill_table, selected_values, fmt_money
)


class Clients(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        self.pack(fill="both", expand=True, padx=30, pady=25)
        self.selected_id = None

        self.create_interface()
        self.load_clients()

    def create_interface(self):

        page_header(
            self,
            "Gestion des Clients",
            "Gérez vos clients et consultez l'historique de leurs commandes."
        )

        search_frame = tk.Frame(self, bg=BG)
        search_frame.pack(fill="x", pady=(0, 18))

        tk.Label(
            search_frame,
            text="Rechercher un client :",
            font=("Segoe UI", 10, "bold"),
            bg=BG,
            fg=DARK
        ).pack(side="left", padx=(0, 10))

        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 11),
            width=30,
            relief="flat",
            bd=0
        )
        self.search_entry.pack(side="left", ipady=8)
        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.load_clients()
        )

        form = card(self)
        form.pack(fill="x", pady=(0, 20))

        card_title(form, "Informations du client")

        fields = tk.Frame(form, bg="white")
        fields.pack(fill="x")

        self.nom_entry = form_field(fields, "Nom du client", 0, 0)
        self.email_entry = form_field(fields, "Email", 0, 1)
        self.ville_entry = form_field(fields, "Ville", 0, 2)

        buttons = tk.Frame(form, bg="white")
        buttons.pack(fill="x", padx=18, pady=15)

        action_button(buttons, "Ajouter", GREEN, self.add_client)
        action_button(buttons, "Modifier", PURPLE, self.update_client)
        action_button(buttons, "Supprimer", RED, self.delete_client)
        action_button(buttons, "Vider", GREY, self.clear_fields)

        table_card = card(self)
        table_card.pack(fill="both", expand=True)

        card_title(table_card, "Liste des clients")

        self.table = make_table(
            table_card,
            [
                ("ID", "ID", 70),
                ("Nom", "Nom du client", 240),
                ("Email", "Email", 300),
                ("Ville", "Ville", 160)
            ],
            5
        )
        self.table.bind("<<TreeviewSelect>>", self.select_client)

        history_card = card(self)
        history_card.pack(fill="both", expand=True, pady=(20, 0))

        card_title(history_card, "Historique des commandes")

        self.summary_label = tk.Label(
            history_card,
            text="Sélectionnez un client pour afficher son historique.",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg=GREY
        )
        self.summary_label.pack(anchor="w", padx=18, pady=(0, 8))

        self.history_table = make_table(
            history_card,
            [
                ("ID", "N° commande", 130),
                ("Date", "Date", 150),
                ("Statut", "Statut", 150),
                ("Montant", "Montant", 150)
            ],
            4
        )

    def load_clients(self):

        search = self.search_entry.get().strip()

        query = """
            SELECT IDCL, NOMCL, EMAIL, VILLE
            FROM CLIENT
            WHERE NOMCL LIKE %s OR EMAIL LIKE %s OR VILLE LIKE %s
            ORDER BY IDCL DESC
        """

        pattern = f"%{search}%"
        clients = fetch_data(query, (pattern, pattern, pattern))

        fill_table(
            self.table,
            [(c["IDCL"], c["NOMCL"], c["EMAIL"], c["VILLE"]) for c in clients]
        )

    def select_client(self, event):

        values = selected_values(self.table)

        if values is None:
            return

        self.selected_id = int(values[0])

        self.clear_entries()
        self.nom_entry.insert(0, values[1])
        self.email_entry.insert(0, values[2])
        self.ville_entry.insert(0, values[3])

        self.load_history()

    def load_history(self):

        query = """
            SELECT
                C.IDCMD,
                C.DATECMD,
                C.STATUT,
                COALESCE(SUM(L.QTTECMD * L.PRIXVENTE), 0) AS MONTANT
            FROM COMMANDE C
            LEFT JOIN LIGNE_COMMANDE L
                ON L.IDCMD = C.IDCMD
            WHERE C.IDCL = %s
            GROUP BY C.IDCMD, C.DATECMD, C.STATUT
            ORDER BY C.DATECMD DESC, C.IDCMD DESC
        """

        orders = fetch_data(query, (self.selected_id,))

        revenue = sum(
            float(o["MONTANT"]) for o in orders if o["STATUT"] == "Validée"
        )

        fill_table(
            self.history_table,
            [
                (o["IDCMD"], o["DATECMD"], o["STATUT"], fmt_money(o["MONTANT"]))
                for o in orders
            ],
            tag_column=2
        )

        self.summary_label.config(
            text=f"Commandes : {len(orders)}   |   Chiffre d'affaires (commandes validées) : {fmt_money(revenue)}",
            fg=DARK
        )

    def get_form_data(self):

        nom = self.nom_entry.get().strip()
        email = self.email_entry.get().strip()
        ville = self.ville_entry.get().strip()

        if not nom or not email or not ville:
            messagebox.showwarning(
                "Champs obligatoires",
                "Veuillez remplir tous les champs."
            )
            return None

        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showerror(
                "Erreur",
                "L'adresse email n'est pas valide."
            )
            return None

        return nom, email, ville

    def show_write_error(self, response):

        if response["errno"] == 1062:
            messagebox.showerror("Erreur", "Cet email existe déjà.")
        else:
            messagebox.showerror("Erreur", response["error"])

    def add_client(self):

        data = self.get_form_data()

        if data is None:
            return

        response = run_query(
            "INSERT INTO CLIENT (NOMCL, EMAIL, VILLE) VALUES (%s, %s, %s)",
            data
        )

        if response["ok"]:
            messagebox.showinfo("Succès", "Client ajouté avec succès.")
            self.clear_fields()
            self.load_clients()
        else:
            self.show_write_error(response)

    def update_client(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Sélection",
                "Veuillez sélectionner un client."
            )
            return

        data = self.get_form_data()

        if data is None:
            return

        response = run_query(
            "UPDATE CLIENT SET NOMCL = %s, EMAIL = %s, VILLE = %s WHERE IDCL = %s",
            data + (self.selected_id,)
        )

        if response["ok"]:
            messagebox.showinfo("Succès", "Client modifié avec succès.")
            self.clear_fields()
            self.load_clients()
        else:
            self.show_write_error(response)

    def delete_client(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Sélection",
                "Veuillez sélectionner un client."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce client ?"
        )

        if not confirm:
            return

        response = run_procedure("SupprimerClient", (self.selected_id,))

        if response["ok"]:
            messagebox.showinfo("Succès", "Client supprimé avec succès.")
            self.clear_fields()
            self.load_clients()
        else:
            messagebox.showerror("Erreur", response["error"])

    def clear_entries(self):

        self.nom_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.ville_entry.delete(0, tk.END)

    def clear_fields(self):

        self.clear_entries()
        self.selected_id = None

        for item in self.table.selection():
            self.table.selection_remove(item)

        for item in self.history_table.get_children():
            self.history_table.delete(item)

        self.summary_label.config(
            text="Sélectionnez un client pour afficher son historique.",
            fg=GREY
        )
