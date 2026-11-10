import tkinter as tk
from tkinter import ttk, messagebox
from database import fetch_data, execute_query

class Produits(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#F4F6FB")

        self.pack(fill="both", expand=True, padx=30, pady=25)
        self.selected_id = None

        self.create_interface()
        self.load_products()

    def create_interface(self):

        header = tk.Frame(self, bg="#F4F6FB")
        header.pack(fill="x", pady=(0, 20))

        tk.Label(
            header,
            text="Gestion des Produits",
            font=("Segoe UI", 24, "bold"),
            bg="#F4F6FB",
            fg="#20223A"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Gérez votre catalogue et surveillez votre stock.",
            font=("Segoe UI", 10),
            bg="#F4F6FB",
            fg="#85899B"
        ).pack(anchor="w", pady=5)

        search_frame = tk.Frame(self, bg="#F4F6FB")
        search_frame.pack(fill="x", pady=(0, 18))

        tk.Label(
            search_frame,
            text="Rechercher un produit :",
            font=("Segoe UI", 10, "bold"),
            bg="#F4F6FB",
            fg="#20223A"
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
            lambda event: self.load_products()
        )

        form = tk.Frame(
            self,
            bg="white",
            highlightbackground="#E7E9F0",
            highlightthickness=1
        )
        form.pack(fill="x", pady=(0, 20))

        tk.Label(
            form,
            text="Informations du produit",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#20223A"
        ).grid(row=0, column=0, columnspan=4,
            sticky="w", padx=18, pady=15)

        self.nom_entry = self.create_field(form, "Nom du produit", 0)
        self.prix_entry = self.create_field(form, "Prix (DH)", 1)
        self.qtte_entry = self.create_field(form, "Quantité", 2)
        self.seuil_entry = self.create_field(form, "Seuil d'alerte", 3)

        buttons = tk.Frame(form, bg="white")
        buttons.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="w",
            padx=18,
            pady=15
        )

        self.create_button(buttons, "Ajouter", "#269C86", self.add_product)
        self.create_button(buttons, "Modifier", "#635BDB", self.update_product)
        self.create_button(buttons, "Supprimer", "#DC665B", self.delete_product)
        self.create_button(buttons, "Vider", "#85899B", self.clear_fields)

        table_frame = tk.Frame(
            self,
            bg="white",
            highlightbackground="#E7E9F0",
            highlightthickness=1
        )
        table_frame.pack(fill="both", expand=True)

        tk.Label(
            table_frame,
            text="Liste des produits",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#20223A"
        ).pack(anchor="w", padx=18, pady=15)

        columns = ("ID", "Nom", "Prix", "Quantité", "Seuil")

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        headings = {
            "ID": "ID",
            "Nom": "Nom du produit",
            "Prix": "Prix (DH)",
            "Quantité": "Quantité",
            "Seuil": "Seuil d'alerte"
        }

        for col in columns:
            self.table.heading(col, text=headings[col])
            self.table.column(col, anchor="center", width=130)

        self.table.column("Nom", width=250)

        self.table.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.table.bind("<<TreeviewSelect>>", self.select_product)

    def create_field(self, parent, label, column):

        frame = tk.Frame(parent, bg="white")
        frame.grid(
            row=1,
            column=column,
            sticky="ew",
            padx=18,
            pady=5
        )

        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#555A70"
        ).pack(anchor="w", pady=(0, 6))

        entry = tk.Entry(
            frame,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1
        )
        entry.pack(fill="x", ipady=7)

        parent.grid_columnconfigure(column, weight=1)

        return entry

    def create_button(self, parent, text, color, command):

        tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=9,
            command=command
        ).pack(side="left", padx=(0, 8))

    def load_products(self):

        for item in self.table.get_children():
            self.table.delete(item)

        search = self.search_entry.get().strip()

        query = """
            SELECT IDPROD, NOM, PRIX, QTTE, SEUIL_ALERTE
            FROM PRODUIT
            WHERE NOM LIKE %s
            ORDER BY IDPROD DESC
        """

        products = fetch_data(query, (f"%{search}%",))

        for product in products:
            self.table.insert(
                "",
                "end",
                values=(
                    product["IDPROD"],
                    product["NOM"],
                    product["PRIX"],
                    product["QTTE"],
                    product["SEUIL_ALERTE"]
                )
            )

    def select_product(self, event):

        selected = self.table.selection()

        if not selected:
            return

        values = self.table.item(selected[0], "values")
        self.selected_id = values[0]

        self.clear_entries()

        self.nom_entry.insert(0, values[1])
        self.prix_entry.insert(0, values[2])
        self.qtte_entry.insert(0, values[3])
        self.seuil_entry.insert(0, values[4])

    def get_form_data(self):

        nom = self.nom_entry.get().strip()
        prix = self.prix_entry.get().strip()
        qtte = self.qtte_entry.get().strip()
        seuil = self.seuil_entry.get().strip()

        if not nom or not prix or not qtte or not seuil:
            messagebox.showwarning(
                "Champs obligatoires",
                "Veuillez remplir tous les champs."
            )
            return None

        try:
            prix = float(prix)
            qtte = int(qtte)
            seuil = int(seuil)

            if prix <= 0 or qtte < 0 or seuil < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Prix doit être positif et quantité/seuil doivent être des entiers positifs ou nuls."
            )
            return None

        return nom, prix, qtte, seuil

    def add_product(self):

        data = self.get_form_data()

        if data is None:
            return

        query = """
            INSERT INTO PRODUIT (NOM, PRIX, QTTE, SEUIL_ALERTE)
            VALUES (%s, %s, %s, %s)
        """

        success = execute_query(query, data)

        if success:
            messagebox.showinfo("Succès", "Produit ajouté avec succès.")
            self.clear_fields()
            self.load_products()
        else:
            messagebox.showerror(
                "Erreur",
                "Impossible d'ajouter le produit. Vérifiez son nom et les données."
            )

    def update_product(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Sélection",
                "Veuillez sélectionner un produit."
            )
            return

        data = self.get_form_data()

        if data is None:
            return

        query = """
            UPDATE PRODUIT
            SET NOM = %s, PRIX = %s, QTTE = %s, SEUIL_ALERTE = %s
            WHERE IDPROD = %s
        """

        success = execute_query(query, data + (self.selected_id,))

        if success:
            messagebox.showinfo("Succès", "Produit modifié avec succès.")
            self.clear_fields()
            self.load_products()
        else:
            messagebox.showerror(
                "Erreur",
                "Impossible de modifier le produit."
            )

    def delete_product(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Sélection",
                "Veuillez sélectionner un produit."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce produit ?"
        )

        if not confirm:
            return

        query = "DELETE FROM PRODUIT WHERE IDPROD = %s"
        success = execute_query(query, (self.selected_id,))

        if success:
            messagebox.showinfo("Succès", "Produit supprimé avec succès.")
            self.clear_fields()
            self.load_products()
        else:
            messagebox.showerror(
                "Erreur",
                "Impossible de supprimer ce produit. Il peut être utilisé dans une commande."
            )

    def clear_entries(self):

        self.nom_entry.delete(0, tk.END)
        self.prix_entry.delete(0, tk.END)
        self.qtte_entry.delete(0, tk.END)
        self.seuil_entry.delete(0, tk.END)

    def clear_fields(self):

        self.clear_entries()
        self.selected_id = None

        for item in self.table.selection():
            self.table.selection_remove(item)
