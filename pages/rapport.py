import tkinter as tk
from tkinter import messagebox
from database import run_procedure
from pages.Ui import (
    BG, DARK, GREY, PURPLE, GREEN, ORANGE, BLUE,
    page_header, card, card_title, action_button,
    make_table, fill_dict_table
)


class Rapports(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        self.pack(fill="both", expand=True, padx=30, pady=25)

        self.create_interface()

    def create_interface(self):

        page_header(
            self,
            "Rapports et Statistiques",
            "Analysez votre stock, vos clients, vos ventes et les anomalies."
        )

        actions = card(self)
        actions.pack(fill="x", pady=(0, 20))

        card_title(actions, "Rapports disponibles")

        row1 = tk.Frame(actions, bg="white")
        row1.pack(fill="x", padx=18, pady=(0, 10))

        action_button(
            row1, "Rapport des stocks", PURPLE,
            lambda: self.run_report("RapportStock", (), "Rapport des stocks")
        )
        action_button(
            row1, "Classement des clients", GREEN,
            lambda: self.run_report("RapportClients", (), "Classement des clients")
        )
        action_button(
            row1, "Produits les plus vendus", BLUE,
            lambda: self.run_report("ClassementProduits", (), "Produits les plus vendus")
        )

        row2 = tk.Frame(actions, bg="white")
        row2.pack(fill="x", padx=18, pady=(0, 15))

        tk.Label(
            row2,
            text="Attente max (jours) :",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#555A70"
        ).pack(side="left", padx=(0, 6))

        self.days_entry = tk.Entry(
            row2,
            font=("Segoe UI", 10),
            width=6,
            relief="solid",
            bd=1
        )
        self.days_entry.insert(0, "30")
        self.days_entry.pack(side="left", ipady=5, padx=(0, 10))

        action_button(row2, "Détecter les anomalies", ORANGE, self.run_anomalies)

        tk.Label(
            row2,
            text="Année :",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#555A70"
        ).pack(side="left", padx=(20, 6))

        self.year_entry = tk.Entry(
            row2,
            font=("Segoe UI", 10),
            width=8,
            relief="solid",
            bd=1
        )
        self.year_entry.insert(0, "2025")
        self.year_entry.pack(side="left", ipady=5, padx=(0, 10))

        action_button(row2, "Rapport annuel", PURPLE, self.run_annual)

        result = card(self)
        result.pack(fill="both", expand=True)

        self.result_title = tk.Label(
            result,
            text="Choisissez un rapport ci-dessus",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg=DARK
        )
        self.result_title.pack(anchor="w", padx=18, pady=(15, 5))

        self.message_label = tk.Label(
            result,
            text="",
            font=("Segoe UI", 10),
            bg="white",
            fg=GREY
        )
        self.message_label.pack(anchor="w", padx=18)

        self.table = make_table(result, [("a", "", 100)], 10)

        self.summary_title = tk.Label(
            result,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=DARK
        )
        self.summary_title.pack(anchor="w", padx=18, pady=(0, 6))

        self.summary_table = make_table(result, [("a", "", 100)], 4)

    def run_report(self, procedure, values, title):

        response = run_procedure(procedure, values)

        if not response["ok"]:
            messagebox.showerror("Erreur", response["error"])
            return

        results = response["results"]
        main_rows = results[0] if results else []
        summary_rows = results[1] if len(results) > 1 else []

        self.result_title.config(text=title)
        self.message_label.config(
            text="" if main_rows else "Aucun résultat pour ce rapport."
        )
        self.summary_title.config(text="Synthèse" if summary_rows else "")

        fill_dict_table(self.table, main_rows)
        fill_dict_table(self.summary_table, summary_rows)

    def run_anomalies(self):

        try:
            days = int(self.days_entry.get().strip())
        except ValueError:
            messagebox.showwarning(
                "Saisie invalide",
                "Le nombre de jours doit être un entier."
            )
            return

        self.run_report(
            "DetecterAnomalies",
            (days,),
            "Commandes présentant des anomalies"
        )

    def run_annual(self):

        try:
            year = int(self.year_entry.get().strip())
        except ValueError:
            messagebox.showwarning(
                "Saisie invalide",
                "L'année doit être un nombre entier."
            )
            return

        self.run_report("RapportAnnuel", (year,), f"Rapport annuel {year}")
