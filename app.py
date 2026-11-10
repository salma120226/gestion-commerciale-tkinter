import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk

import db

COULEURS = {
    "produits": "#dbeafe",
    "clients": "#dcfce7",
    "valides": "#ffedd5",
    "alertes": "#ede9fe",
}


def fmt_dh(v):
    return f"{float(v):,.2f} DH".replace(",", " ")


def show_table(parent, title, rows):
    
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry("720x380")
    if not rows:
        ttk.Label(win, text="Aucun résultat.", padding=20).pack()
        return
    cols = list(rows[0].keys())
    frame = ttk.Frame(win, padding=8)
    frame.pack(fill="both", expand=True)
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=110, anchor="center")
    for r in rows:
        tree.insert("", "end", values=[r[c] for c in cols])
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")


class Dashboard(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=15)
        self.app = app

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Tableau de bord", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Label(top, text=f"Aujourd'hui : {date.today():%d/%m/%Y}").pack(side="right")
        ttk.Label(self, text="Vue d'ensemble de votre activité commerciale").pack(anchor="w")

        cards = ttk.Frame(self)
        cards.pack(fill="x", pady=12)
        self.valeurs = {}
        specs = [
            ("produits", "Nombre de produits"),
            ("clients", "Nombre de clients"),
            ("valides", "Commandes validées"),
            ("alertes", "Produits en alerte"),
        ]
        for i, (cle, libelle) in enumerate(specs):
            bg = COULEURS[cle]
            card = tk.Frame(cards, bg=bg, padx=16, pady=10)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            cards.columnconfigure(i, weight=1)
            tk.Label(card, text=libelle, bg=bg, font=("Segoe UI", 10)).pack(anchor="w")
            lbl = tk.Label(card, text="-", bg=bg, font=("Segoe UI", 24, "bold"))
            lbl.pack(anchor="w")
            self.valeurs[cle] = lbl

        self.lbl_stock = ttk.Label(self, text="Valeur totale du stock : -", font=("Segoe UI", 11, "bold"))
        self.lbl_stock.pack(anchor="w", pady=(0, 8))

        box = ttk.LabelFrame(self, text="Produits en alerte", padding=8)
        box.pack(fill="both", expand=True)
        cols = ("id", "nom", "stock", "seuil", "statut")
        self.tree = ttk.Treeview(box, columns=cols, show="headings", height=8)
        for c, t, w in [("id", "ID Produit", 80), ("nom", "Nom", 260), ("stock", "Stock", 80),
                        ("seuil", "Seuil d'alerte", 110), ("statut", "Statut", 100)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center" if c != "nom" else "w")
        self.tree.tag_configure("rupture", background="#fde2e2")
        self.tree.tag_configure("faible", background="#fff3cd")
        self.tree.pack(fill="both", expand=True)

        actions = ttk.LabelFrame(self, text="Actions rapides", padding=8)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Ajouter un produit", command=app.action_ajouter_produit).pack(side="left", padx=4)
        ttk.Button(actions, text="Ajouter un client", command=app.action_ajouter_client).pack(side="left", padx=4)
        ttk.Button(actions, text="Nouvelle commande", command=lambda: app.goto(3)).pack(side="left", padx=4)
        ttk.Button(actions, text="Voir les rapports", command=lambda: app.goto(4)).pack(side="left", padx=4)

    def refresh(self):
        nb_prod = db.query("SELECT COUNT(*) AS n FROM PRODUIT")[0]["n"]
        nb_cli = db.query("SELECT COUNT(*) AS n FROM CLIENT")[0]["n"]
        nb_val = db.query("SELECT COUNT(*) AS n FROM COMMANDE WHERE STATUT = 'VALIDEE'")[0]["n"]
        valeur = db.query("SELECT ValeurStock() AS v")[0]["v"]
        _, res = db.call_proc("ProduitsEnAlerte")
        alertes = res[0] if res else []

        self.valeurs["produits"].config(text=str(nb_prod))
        self.valeurs["clients"].config(text=str(nb_cli))
        self.valeurs["valides"].config(text=str(nb_val))
        self.valeurs["alertes"].config(text=str(len(alertes)))
        self.lbl_stock.config(text=f"Valeur totale du stock : {fmt_dh(valeur)}")

        self.tree.delete(*self.tree.get_children())
        for a in alertes:
            tag = "rupture" if a["STATUT"] == "Rupture" else "faible"
            self.tree.insert("", "end", values=(a["IDPROD"], a["NOM"], a["STOCK"],
                                                a["SEUIL_ALERTE"], a["STATUT"]), tags=(tag,))


class ProductDialog(tk.Toplevel):
    def __init__(self, parent, titre, initial=None, avec_stock=True):
        super().__init__(parent)
        self.title(titre)
        self.resizable(False, False)
        self.transient(parent)
        self.result = None

        champs = [("Nom", "nom"), ("Prix (DH)", "prix")]
        if avec_stock:
            champs.append(("Quantité en stock", "qtte"))
        champs.append(("Seuil d'alerte", "seuil"))

        self.vars = {}
        for i, (libelle, cle) in enumerate(champs):
            ttk.Label(self, text=libelle).grid(row=i, column=0, sticky="w", padx=12, pady=6)
            var = tk.StringVar(value=str(initial.get(cle, "")) if initial else "")
            ttk.Entry(self, textvariable=var, width=32).grid(row=i, column=1, padx=12, pady=6)
            self.vars[cle] = var

        btns = ttk.Frame(self)
        btns.grid(row=len(champs), column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Enregistrer", command=self._ok).pack(side="left", padx=6)
        ttk.Button(btns, text="Annuler", command=self.destroy).pack(side="left", padx=6)

        self.grab_set()
        self.wait_window(self)

    def _ok(self):
        try:
            nom = self.vars["nom"].get().strip()
            prix = float(self.vars["prix"].get().replace(",", "."))
            seuil = int(self.vars["seuil"].get())
            qtte = int(self.vars["qtte"].get()) if "qtte" in self.vars else None
        except ValueError:
            messagebox.showwarning("Saisie invalide",
                                   "Le prix, la quantité et le seuil doivent être des nombres.",
                                   parent=self)
            return
        self.result = {"nom": nom, "prix": prix, "qtte": qtte, "seuil": seuil}
        self.destroy()


class ProduitsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=15)
        self.app = app
        self.rows = {}

        ttk.Label(self, text="Gestion des produits", font=("Segoe UI", 18, "bold")).pack(anchor="w")

        barre = ttk.Frame(self)
        barre.pack(fill="x", pady=10)
        ttk.Label(barre, text="Rechercher :").pack(side="left")
        self.var_recherche = tk.StringVar()
        entry = ttk.Entry(barre, textvariable=self.var_recherche, width=30)
        entry.pack(side="left", padx=6)
        entry.bind("<Return>", lambda e: self.refresh())
        ttk.Button(barre, text="Rechercher", command=self.refresh).pack(side="left")
        ttk.Button(barre, text="Réinitialiser", command=self._reset).pack(side="left", padx=4)
        ttk.Button(barre, text="Produits en alerte", command=self.voir_alertes).pack(side="right")

        cols = ("id", "nom", "prix", "stock", "seuil", "statut")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        for c, t, w, a in [("id", "ID", 60, "center"), ("nom", "Nom", 280, "w"),
                           ("prix", "Prix (DH)", 100, "e"), ("stock", "Stock", 80, "center"),
                           ("seuil", "Seuil", 80, "center"), ("statut", "Statut", 100, "center")]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor=a)
        self.tree.tag_configure("rupture", background="#fde2e2")
        self.tree.tag_configure("faible", background="#fff3cd")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")

        actions = ttk.Frame(self, padding=(10, 0, 0, 0))
        actions.pack(side="left", fill="y")
        for texte, cmd in [("Ajouter", self.ajouter), ("Modifier", self.modifier),
                           ("Ajuster le stock", self.ajuster_stock), ("Supprimer", self.supprimer),
                           ("Actualiser", self.app.refresh_all)]:
            ttk.Button(actions, text=texte, command=cmd, width=18).pack(pady=4)

    def refresh(self):
        terme = self.var_recherche.get().strip()
        rows = db.query(
            "SELECT IDPROD, NOM, PRIX, QTTE, SEUIL_ALERTE, "
            "CASE WHEN QTTE = 0 THEN 'Rupture' "
            "     WHEN QTTE <= SEUIL_ALERTE THEN 'Faible' ELSE 'OK' END AS STATUT "
            "FROM PRODUIT WHERE NOM LIKE %s ORDER BY IDPROD",
            (f"%{terme}%",),
        )
        self.rows = {r["IDPROD"]: r for r in rows}
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            tag = {"Rupture": "rupture", "Faible": "faible"}.get(r["STATUT"], "")
            self.tree.insert("", "end", iid=str(r["IDPROD"]),
                             values=(r["IDPROD"], r["NOM"], f"{r['PRIX']:.2f}", r["QTTE"],
                                     r["SEUIL_ALERTE"], r["STATUT"]),
                             tags=(tag,) if tag else ())

    def _reset(self):
        self.var_recherche.set("")
        self.refresh()

    def _selection(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord un produit dans la liste.")
            return None
        return int(sel[0])

    def ajouter(self):
        dlg = ProductDialog(self, "Ajouter un produit")
        if not dlg.result:
            return
        r = dlg.result
        try:
            out, _ = db.call_proc("AjouterProduit", (r["nom"], r["prix"], r["qtte"], r["seuil"], 0))
        except db.DBError as e:
            messagebox.showerror("Ajout impossible", str(e))
            return
        messagebox.showinfo("Produit ajouté", f"Produit créé avec l'identifiant {out[4]}.")
        self.app.refresh_all()

    def modifier(self):
        idp = self._selection()
        if idp is None:
            return
        cur = self.rows[idp]
        initial = {"nom": cur["NOM"], "prix": cur["PRIX"], "seuil": cur["SEUIL_ALERTE"]}
        dlg = ProductDialog(self, f"Modifier le produit {idp}", initial, avec_stock=False)
        if not dlg.result:
            return
        r = dlg.result
        if not r["nom"] or r["prix"] < 0 or r["seuil"] < 0:
            messagebox.showwarning("Saisie invalide", "Nom obligatoire, prix et seuil positifs.")
            return
        try:
            db.execute("UPDATE PRODUIT SET NOM = %s, PRIX = %s, SEUIL_ALERTE = %s WHERE IDPROD = %s",
                       (r["nom"], r["prix"], r["seuil"], idp))
        except db.DBError as e:
            messagebox.showerror("Modification impossible", str(e))
            return
        self.app.refresh_all()

    def ajuster_stock(self):
        idp = self._selection()
        if idp is None:
            return
        delta = simpledialog.askinteger(
            "Ajuster le stock",
            f"{self.rows[idp]['NOM']}\nQuantité à ajouter (positive) ou à retirer (négative) :",
            parent=self)
        if delta is None:
            return
        try:
            db.call_proc("ModifierStock", (idp, delta))
        except db.DBError as e:
            messagebox.showerror("Stock", str(e))
            return
        self.app.refresh_all()

    def supprimer(self):
        idp = self._selection()
        if idp is None:
            return
        if not messagebox.askyesno("Confirmation", f"Supprimer « {self.rows[idp]['NOM']} » ?"):
            return
        try:
            db.call_proc("SupprimerProduit", (idp,))
        except db.DBError as e:
            messagebox.showerror("Suppression impossible", str(e))
            return
        self.app.refresh_all()

    def voir_alertes(self):
        try:
            _, res = db.call_proc("ProduitsEnAlerte")
        except db.DBError as e:
            messagebox.showerror("Erreur", str(e))
            return
        show_table(self, "Produits en alerte", res[0] if res else [])


def fmt_cell(v):
    if isinstance(v, float):
        return f"{v:,.2f}".replace(",", " ")
    return "" if v is None else v


def make_tree(parent, specs, height=8):
    """specs : liste de (id, titre, largeur, ancrage). Retourne (frame, tree)."""
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=[s[0] for s in specs], show="headings",
                        height=height, selectmode="browse")
    for cid, titre, w, a in specs:
        tree.heading(cid, text=titre)
        tree.column(cid, width=w, anchor=a)
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    style_tags(tree)
    return frame, tree


TAGS_COULEUR = {
    "RUPTURE": "rupture", "FAIBLE": "faible", "VIP": "vip", "INACTIF": "inactif",
    "VALIDEE": "valide", "EN_ATTENTE": "attente", "ANNULEE": "annule",
}


def style_tags(tree):
    for tag, bg in [("rupture", "#fde2e2"), ("faible", "#fff3cd"), ("vip", "#dcfce7"),
                    ("inactif", "#eeeeee"), ("valide", "#e7f6ea"), ("attente", "#fff3cd"),
                    ("annule", "#fde2e2")]:
        tree.tag_configure(tag, background=bg)


def fill_tree(tree, rows):
    """Remplit un Treeview dont les colonnes sont déduites des clés des lignes."""
    tree.delete(*tree.get_children())
    if not rows:
        tree["columns"] = ()
        return
    cols = list(rows[0].keys())
    tree["columns"] = cols
    for c in cols:
        tree.heading(c, text=c)
        long = c == "ANOMALIE"
        tree.column(c, width=400 if long else 125, anchor="w" if long else "center")
    for r in rows:
        tag = next((TAGS_COULEUR[v] for v in r.values()
                    if isinstance(v, str) and v in TAGS_COULEUR), "")
        tree.insert("", "end", values=[fmt_cell(r[c]) for c in cols],
                    tags=(tag,) if tag else ())


# ======================================================================
# Interface 2 : Clients
# ======================================================================
class ClientDialog(tk.Toplevel):
    def __init__(self, parent, titre, initial=None):
        super().__init__(parent)
        self.title(titre)
        self.resizable(False, False)
        self.transient(parent)
        self.result = None

        self.vars = {}
        for i, (libelle, cle) in enumerate([("Nom", "nom"), ("Email", "email"), ("Ville", "ville")]):
            ttk.Label(self, text=libelle).grid(row=i, column=0, sticky="w", padx=12, pady=6)
            var = tk.StringVar(value=(initial.get(cle) or "") if initial else "")
            ttk.Entry(self, textvariable=var, width=34).grid(row=i, column=1, padx=12, pady=6)
            self.vars[cle] = var

        btns = ttk.Frame(self)
        btns.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Enregistrer", command=self._ok).pack(side="left", padx=6)
        ttk.Button(btns, text="Annuler", command=self.destroy).pack(side="left", padx=6)

        self.grab_set()
        self.wait_window(self)

    def _ok(self):
        nom = self.vars["nom"].get().strip()
        email = self.vars["email"].get().strip()
        ville = self.vars["ville"].get().strip()
        if not nom:
            messagebox.showwarning("Saisie invalide", "Le nom est obligatoire.", parent=self)
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showwarning("Saisie invalide", "Adresse email invalide.", parent=self)
            return
        self.result = {"nom": nom, "email": email, "ville": ville or None}
        self.destroy()


class ClientsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=15)
        self.app = app
        self.rows = {}

        ttk.Label(self, text="Gestion des clients", font=("Segoe UI", 18, "bold")).pack(anchor="w")

        barre = ttk.Frame(self)
        barre.pack(fill="x", pady=10)
        ttk.Label(barre, text="Rechercher :").pack(side="left")
        self.var_recherche = tk.StringVar()
        entry = ttk.Entry(barre, textvariable=self.var_recherche, width=30)
        entry.pack(side="left", padx=6)
        entry.bind("<Return>", lambda e: self.refresh())
        ttk.Button(barre, text="Rechercher", command=self.refresh).pack(side="left")
        ttk.Button(barre, text="Réinitialiser", command=self._reset).pack(side="left", padx=4)
        for texte, cmd in [("Supprimer", self.supprimer), ("Modifier", self.modifier),
                           ("Ajouter", self.ajouter)]:
            ttk.Button(barre, text=texte, command=cmd).pack(side="right", padx=3)

        frame, self.tree = make_tree(self, [
            ("id", "ID", 60, "center"), ("nom", "Nom", 240, "w"),
            ("email", "Email", 260, "w"), ("ville", "Ville", 140, "w")], 8)
        frame.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.afficher_historique)

        box = ttk.LabelFrame(self, text="Historique des commandes", padding=8)
        box.pack(fill="both", expand=True, pady=(10, 0))
        self.lbl_resume = ttk.Label(box, text="Sélectionnez un client.", font=("Segoe UI", 10, "bold"))
        self.lbl_resume.pack(anchor="w", pady=(0, 6))
        frame2, self.hist = make_tree(box, [
            ("id", "N° commande", 110, "center"), ("date", "Date", 120, "center"),
            ("statut", "Statut", 120, "center"), ("montant", "Montant (DH)", 140, "e")], 6)
        frame2.pack(fill="both", expand=True)

    def refresh(self):
        t = f"%{self.var_recherche.get().strip()}%"
        rows = db.query(
            "SELECT IDCL, NOMCL, EMAIL, VILLE FROM CLIENT "
            "WHERE NOMCL LIKE %s OR EMAIL LIKE %s OR VILLE LIKE %s ORDER BY IDCL", (t, t, t))
        ancien = self.tree.selection()
        self.rows = {r["IDCL"]: r for r in rows}
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", iid=str(r["IDCL"]),
                             values=(r["IDCL"], r["NOMCL"], r["EMAIL"], r["VILLE"] or ""))
        if ancien and ancien[0] in self.tree.get_children():
            self.tree.selection_set(ancien[0])
        else:
            self.afficher_historique()

    def _reset(self):
        self.var_recherche.set("")
        self.refresh()

    def _selection(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord un client dans la liste.")
            return None
        return int(sel[0])

    def _erreur(self, titre, e):
        m, low = str(e), str(e).lower()
        if "duplicate" in low:
            m = "Un client avec cet email existe déjà."
        elif "foreign key" in low:
            m = "Suppression impossible : ce client a des commandes."
        elif "check constraint" in low:
            m = "Adresse email invalide."
        messagebox.showerror(titre, m)

    def afficher_historique(self, _e=None):
        self.hist.delete(*self.hist.get_children())
        sel = self.tree.selection()
        if not sel:
            self.lbl_resume.config(text="Sélectionnez un client.")
            return
        idcl = int(sel[0])
        try:
            cmds = db.query(
                "SELECT IDCMD, DATECMD, STATUT, CalculerMontantCommande(IDCMD) AS MONTANT "
                "FROM COMMANDE WHERE IDCL = %s ORDER BY DATECMD DESC, IDCMD DESC", (idcl,))
            nb = db.query("SELECT NombreCommandesClient(%s) AS n", (idcl,))[0]["n"]
            ca = db.query(
                "SELECT IFNULL(SUM(L.QTTECMD * L.PRIXVENTE), 0) AS ca "
                "FROM COMMANDE C JOIN LIGNE_COMMANDE L ON L.IDCMD = C.IDCMD "
                "WHERE C.IDCL = %s AND C.STATUT = 'VALIDEE'", (idcl,))[0]["ca"]
        except db.DBError as e:
            messagebox.showerror("Erreur", str(e))
            return
        for c in cmds:
            self.hist.insert("", "end", values=(c["IDCMD"], c["DATECMD"], c["STATUT"],
                                                f"{c['MONTANT']:,.2f}".replace(",", " ")),
                             tags=(TAGS_COULEUR[c["STATUT"]],))
        nom = self.rows[idcl]["NOMCL"]
        self.lbl_resume.config(
            text=f"{nom} - {nb} commande(s) - Chiffre d'affaires (validées) : {fmt_dh(ca)}")

    def ajouter(self):
        dlg = ClientDialog(self, "Ajouter un client")
        if not dlg.result:
            return
        r = dlg.result
        try:
            db.execute("INSERT INTO CLIENT (NOMCL, EMAIL, VILLE) VALUES (%s, %s, %s)",
                       (r["nom"], r["email"], r["ville"]))
        except db.DBError as e:
            self._erreur("Ajout impossible", e)
            return
        self.app.refresh_all()

    def modifier(self):
        idcl = self._selection()
        if idcl is None:
            return
        cur = self.rows[idcl]
        dlg = ClientDialog(self, f"Modifier le client {idcl}",
                           {"nom": cur["NOMCL"], "email": cur["EMAIL"], "ville": cur["VILLE"]})
        if not dlg.result:
            return
        r = dlg.result
        try:
            db.execute("UPDATE CLIENT SET NOMCL = %s, EMAIL = %s, VILLE = %s WHERE IDCL = %s",
                       (r["nom"], r["email"], r["ville"], idcl))
        except db.DBError as e:
            self._erreur("Modification impossible", e)
            return
        self.app.refresh_all()

    def supprimer(self):
        idcl = self._selection()
        if idcl is None:
            return
        if not messagebox.askyesno("Confirmation", f"Supprimer « {self.rows[idcl]['NOMCL']} » ?"):
            return
        try:
            db.execute("DELETE FROM CLIENT WHERE IDCL = %s", (idcl,))
        except db.DBError as e:
            self._erreur("Suppression impossible", e)
            return
        self.app.refresh_all()


# ======================================================================
# Interface 3 : Commandes
# ======================================================================
class CommandesFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=15)
        self.app = app
        self.panier = {}                  # idprod -> {"nom", "prix", "qte"}
        self.client_ids, self.prod_ids, self.produits = [], [], {}

        ttk.Label(self, text="Gestion des commandes", font=("Segoe UI", 18, "bold")).pack(anchor="w")

        # --- nouvelle commande
        nouv = ttk.LabelFrame(self, text="Nouvelle commande", padding=8)
        nouv.pack(fill="x", pady=8)
        l1 = ttk.Frame(nouv)
        l1.pack(fill="x")
        ttk.Label(l1, text="Client").pack(side="left")
        self.cb_client = ttk.Combobox(l1, state="readonly", width=28)
        self.cb_client.pack(side="left", padx=(4, 12))
        ttk.Label(l1, text="Produit").pack(side="left")
        self.cb_produit = ttk.Combobox(l1, state="readonly", width=46)
        self.cb_produit.pack(side="left", padx=(4, 12))
        ttk.Label(l1, text="Qté").pack(side="left")
        self.sp_qte = ttk.Spinbox(l1, from_=1, to=10000, width=6)
        self.sp_qte.set(1)
        self.sp_qte.pack(side="left", padx=(4, 8))
        ttk.Button(l1, text="Ajouter au panier", command=self.ajouter_panier).pack(side="left")

        frame, self.tree_panier = make_tree(nouv, [
            ("nom", "Produit", 300, "w"), ("qte", "Quantité", 90, "center"),
            ("prix", "Prix unitaire", 120, "e"), ("st", "Sous-total", 130, "e")], 4)
        frame.pack(fill="x", pady=6)

        l3 = ttk.Frame(nouv)
        l3.pack(fill="x")
        ttk.Button(l3, text="Retirer la ligne", command=self.retirer).pack(side="left")
        ttk.Button(l3, text="Vider le panier", command=self.vider_panier).pack(side="left", padx=4)
        self.lbl_total = ttk.Label(l3, text="Total : 0.00 DH", font=("Segoe UI", 11, "bold"))
        self.lbl_total.pack(side="left", padx=20)
        ttk.Button(l3, text="Créer et valider", command=lambda: self.creer(True)).pack(side="right")
        ttk.Button(l3, text="Créer (en attente)", command=lambda: self.creer(False)).pack(side="right", padx=4)

        # --- liste des commandes
        liste = ttk.LabelFrame(self, text="Commandes", padding=8)
        liste.pack(fill="both", expand=True)
        barre = ttk.Frame(liste)
        barre.pack(fill="x")
        ttk.Label(barre, text="Statut :").pack(side="left")
        self.var_filtre = tk.StringVar(value="Tous")
        cb = ttk.Combobox(barre, textvariable=self.var_filtre, state="readonly", width=14,
                          values=["Tous", "EN_ATTENTE", "VALIDEE", "ANNULEE"])
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.charger_commandes())
        ttk.Button(barre, text="Annuler la commande", command=self.annuler).pack(side="right", padx=3)
        ttk.Button(barre, text="Valider la commande", command=self.valider).pack(side="right", padx=3)

        frame2, self.tree_cmd = make_tree(liste, [
            ("id", "N°", 60, "center"), ("client", "Client", 220, "w"),
            ("date", "Date", 110, "center"), ("statut", "Statut", 110, "center"),
            ("montant", "Montant (DH)", 130, "e")], 6)
        frame2.pack(fill="both", expand=True, pady=6)
        self.tree_cmd.bind("<<TreeviewSelect>>", self.afficher_detail)

        self.lbl_detail = ttk.Label(liste, text="Détail de la commande : sélectionnez une commande.",
                                    font=("Segoe UI", 10, "bold"))
        self.lbl_detail.pack(anchor="w")
        frame3, self.tree_det = make_tree(liste, [
            ("nom", "Produit", 300, "w"), ("qte", "Quantité", 90, "center"),
            ("prix", "Prix de vente", 120, "e"), ("st", "Sous-total", 130, "e")], 4)
        frame3.pack(fill="both", expand=True)

    # ---- chargement ---------------------------------------------------
    def _recharger_combo(self, combo, ids, labels, ancien_id):
        combo["values"] = labels
        if ancien_id in ids:
            combo.current(ids.index(ancien_id))
        else:
            combo.set("")

    def refresh(self):
        ic, ip = self.cb_client.current(), self.cb_produit.current()
        ancien_cl = self.client_ids[ic] if ic >= 0 else None
        ancien_pr = self.prod_ids[ip] if ip >= 0 else None

        clients = db.query("SELECT IDCL, NOMCL FROM CLIENT ORDER BY NOMCL")
        self.client_ids = [c["IDCL"] for c in clients]
        self._recharger_combo(self.cb_client, self.client_ids,
                              [f"{c['IDCL']} - {c['NOMCL']}" for c in clients], ancien_cl)

        prods = db.query("SELECT IDPROD, NOM, PRIX, QTTE FROM PRODUIT ORDER BY NOM")
        self.produits = {p["IDPROD"]: p for p in prods}
        self.prod_ids = [p["IDPROD"] for p in prods]
        self._recharger_combo(self.cb_produit, self.prod_ids,
                              [f"{p['NOM']} - {fmt_dh(p['PRIX'])} (stock : {p['QTTE']})" for p in prods],
                              ancien_pr)
        self.charger_commandes()

    def charger_commandes(self):
        sql = ("SELECT C.IDCMD, CL.NOMCL, C.DATECMD, C.STATUT, "
               "CalculerMontantCommande(C.IDCMD) AS MONTANT "
               "FROM COMMANDE C JOIN CLIENT CL ON CL.IDCL = C.IDCL")
        params = ()
        if self.var_filtre.get() != "Tous":
            sql += " WHERE C.STATUT = %s"
            params = (self.var_filtre.get(),)
        rows = db.query(sql + " ORDER BY C.IDCMD DESC", params)

        ancien = self.tree_cmd.selection()
        self.tree_cmd.delete(*self.tree_cmd.get_children())
        for r in rows:
            self.tree_cmd.insert("", "end", iid=str(r["IDCMD"]), tags=(TAGS_COULEUR[r["STATUT"]],),
                                 values=(r["IDCMD"], r["NOMCL"], r["DATECMD"], r["STATUT"],
                                         f"{r['MONTANT']:,.2f}".replace(",", " ")))
        if ancien and ancien[0] in self.tree_cmd.get_children():
            self.tree_cmd.selection_set(ancien[0])
        else:
            self.afficher_detail()

    def afficher_detail(self, _e=None):
        self.tree_det.delete(*self.tree_det.get_children())
        sel = self.tree_cmd.selection()
        if not sel:
            self.lbl_detail.config(text="Détail de la commande : sélectionnez une commande.")
            return
        idc = int(sel[0])
        try:
            lignes = db.query(
                "SELECT P.NOM, L.QTTECMD, L.PRIXVENTE, L.QTTECMD * L.PRIXVENTE AS ST "
                "FROM LIGNE_COMMANDE L JOIN PRODUIT P ON P.IDPROD = L.IDPROD "
                "WHERE L.IDCMD = %s ORDER BY P.NOM", (idc,))
            total = db.query("SELECT CalculerMontantCommande(%s) AS m", (idc,))[0]["m"]
        except db.DBError as e:
            messagebox.showerror("Erreur", str(e))
            return
        for l in lignes:
            self.tree_det.insert("", "end", values=(l["NOM"], l["QTTECMD"], fmt_dh(l["PRIXVENTE"]),
                                                    fmt_dh(l["ST"])))
        self.lbl_detail.config(text=f"Détail de la commande n°{idc} - Montant total : {fmt_dh(total)}")

    # ---- panier -------------------------------------------------------
    def maj_panier(self):
        self.tree_panier.delete(*self.tree_panier.get_children())
        total = 0.0
        for idp, l in self.panier.items():
            st = l["qte"] * l["prix"]
            total += st
            self.tree_panier.insert("", "end", iid=str(idp),
                                    values=(l["nom"], l["qte"], fmt_dh(l["prix"]), fmt_dh(st)))
        self.lbl_total.config(text=f"Total : {fmt_dh(total)}")

    def ajouter_panier(self):
        ip = self.cb_produit.current()
        if ip < 0:
            messagebox.showinfo("Commande", "Sélectionnez un produit.")
            return
        try:
            qte = int(self.sp_qte.get())
        except ValueError:
            qte = 0
        if qte <= 0:
            messagebox.showwarning("Quantité invalide", "La quantité doit être un entier positif.")
            return
        idp = self.prod_ids[ip]
        p = self.produits[idp]
        deja = self.panier.get(idp, {}).get("qte", 0)
        if deja + qte > p["QTTE"]:
            if not messagebox.askyesno(
                    "Stock insuffisant",
                    f"Stock disponible pour « {p['NOM']} » : {p['QTTE']}.\n"
                    f"Quantité demandée : {deja + qte}.\n\nAjouter quand même ?"):
                return
        if idp in self.panier:
            self.panier[idp]["qte"] += qte
        else:
            self.panier[idp] = {"nom": p["NOM"], "prix": p["PRIX"], "qte": qte}
        self.maj_panier()

    def retirer(self):
        sel = self.tree_panier.selection()
        if sel:
            self.panier.pop(int(sel[0]), None)
            self.maj_panier()

    def vider_panier(self):
        self.panier.clear()
        self.maj_panier()

    # ---- création / validation / annulation ---------------------------
    def creer(self, valider):
        ic = self.cb_client.current()
        if ic < 0:
            messagebox.showinfo("Commande", "Sélectionnez un client.")
            return
        if not self.panier:
            messagebox.showinfo("Commande", "Le panier est vide.")
            return

        idcmd = None
        try:
            out, _ = db.call_proc("CreerCommande", (self.client_ids[ic], 0))
            idcmd = out[1]
            for idp, l in self.panier.items():
                db.call_proc("AjouterLigneCommande", (idcmd, idp, l["qte"]))
        except db.DBError as e:
            if idcmd is not None:     # on ne laisse pas de commande partielle
                try:
                    db.execute("DELETE FROM COMMANDE WHERE IDCMD = %s AND STATUT = 'EN_ATTENTE'", (idcmd,))
                except db.DBError:
                    pass
            messagebox.showerror("Création impossible", str(e))
            return

        message = f"Commande n°{idcmd} créée (EN_ATTENTE)."
        if valider:
            try:
                db.call_proc("ValiderCommande", (idcmd,))
                message = f"Commande n°{idcmd} créée et validée. Les stocks ont été mis à jour."
            except db.DBError as e:
                messagebox.showwarning(
                    "Validation impossible",
                    f"La commande n°{idcmd} a été créée mais reste en attente.\n\n{e}")
                message = None
        if message:
            messagebox.showinfo("Commande", message)
        self.vider_panier()
        self.app.refresh_all()

    def _commande_selectionnee(self):
        sel = self.tree_cmd.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord une commande dans la liste.")
            return None, None
        return int(sel[0]), self.tree_cmd.set(sel[0], "statut")

    def valider(self):
        idc, _ = self._commande_selectionnee()
        if idc is None:
            return
        try:
            db.call_proc("ValiderCommande", (idc,))
        except db.DBError as e:
            messagebox.showerror("Validation impossible", str(e))
            return
        messagebox.showinfo("Commande", f"Commande n°{idc} validée. Les stocks ont été mis à jour.")
        self.app.refresh_all()

    def annuler(self):
        idc, statut = self._commande_selectionnee()
        if idc is None:
            return
        texte = f"Annuler la commande n°{idc} ?"
        if statut == "VALIDEE":
            texte += "\n\nElle est validée : les quantités seront remises en stock."
        if not messagebox.askyesno("Confirmation", texte):
            return
        try:
            db.call_proc("AnnulerCommande", (idc,))
        except db.DBError as e:
            messagebox.showerror("Annulation impossible", str(e))
            return
        self.app.refresh_all()


# ======================================================================
# Interface 4 : Rapports et statistiques
# ======================================================================
class StatsFrame(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master, padding=15)
        self.app = app

        ttk.Label(self, text="Rapports et statistiques", font=("Segoe UI", 18, "bold")).pack(anchor="w")

        barre = ttk.Frame(self)
        barre.pack(fill="x", pady=10)
        for texte, cmd in [("Rapport des stocks", self.rapport_stock),
                           ("Classement des clients", self.rapport_clients),
                           ("Produits les plus vendus", self.classement_produits),
                           ("Détecter les anomalies", self.anomalies)]:
            ttk.Button(barre, text=texte, command=cmd).pack(side="left", padx=3)
        ttk.Label(barre, text="Année :").pack(side="left", padx=(20, 4))
        self.sp_annee = ttk.Spinbox(barre, from_=2000, to=2100, width=6)
        self.sp_annee.set(2025)           # les données d'exemple sont de 2025
        self.sp_annee.pack(side="left")
        ttk.Button(barre, text="Rapport annuel", command=self.rapport_annuel).pack(side="left", padx=4)

        self.lbl = ttk.Label(self, text="Choisissez un rapport.", font=("Segoe UI", 11, "bold"))
        self.lbl.pack(anchor="w", pady=(0, 6))

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(frame, show="headings", selectmode="browse")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        style_tags(self.tree)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.box = ttk.LabelFrame(self, text="Synthèse", padding=8)
        self.tree_resume = ttk.Treeview(self.box, show="headings", height=6, selectmode="none")
        self.tree_resume.pack(fill="x")

    def lancer(self, proc, args, titre):
        try:
            _, res = db.call_proc(proc, args)
        except db.DBError as e:
            messagebox.showerror("Erreur", str(e))
            return
        principal = res[0] if res else []
        resume = res[1] if len(res) > 1 else []
        fill_tree(self.tree, principal)
        fill_tree(self.tree_resume, resume)
        if resume:
            self.box.pack(fill="x", pady=(8, 0))
        else:
            self.box.pack_forget()
        suffixe = f"{len(principal)} ligne(s)" if principal else "aucun résultat"
        self.lbl.config(text=f"{titre} - {suffixe}")

    def rapport_stock(self):
        self.lancer("RapportStock", (), "Rapport des stocks")

    def rapport_clients(self):
        seuil = simpledialog.askfloat(
            "Seuil VIP", "Chiffre d'affaires minimum pour être client VIP (DH) :",
            initialvalue=10000, minvalue=0, parent=self)
        if seuil is None:
            return
        self.lancer("RapportClients", (seuil,), f"Classement des clients (VIP ≥ {fmt_dh(seuil)})")

    def classement_produits(self):
        self.lancer("ClassementProduits", (), "Produits les plus vendus")

    def anomalies(self):
        self.lancer("DetecterAnomalies", (), "Commandes présentant des anomalies")

    def rapport_annuel(self):
        try:
            annee = int(self.sp_annee.get())
        except ValueError:
            messagebox.showwarning("Année invalide", "Saisissez une année valide (ex. 2025).")
            return
        self.lancer("RapportAnnuel", (annee,), f"Rapport annuel {annee}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion Commerciale")
        self.geometry("1100x800")
        self.minsize(960, 680)
        try:
            ttk.Style(self).theme_use("clam")
        except tk.TclError:
            pass

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self.dashboard = Dashboard(self.nb, self)
        self.produits = ProduitsFrame(self.nb, self)
        self.nb.add(self.dashboard, text="  Tableau de bord  ")
        self.nb.add(self.produits, text="  Produits  ")
        self.clients = ClientsFrame(self.nb, self)
        self.commandes = CommandesFrame(self.nb, self)
        self.stats = StatsFrame(self.nb, self)
        self.nb.add(self.clients, text="  Clients  ")
        self.nb.add(self.commandes, text="  Commandes  ")
        self.nb.add(self.stats, text="  Statistiques  ")

        self.nb.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all())
        self.after(100, self.refresh_all)

    def goto(self, index):
        self.nb.select(index)

    def action_ajouter_produit(self):
        self.goto(1)
        self.produits.ajouter()

    def action_ajouter_client(self):
        self.goto(2)
        self.clients.ajouter()

    def refresh_all(self):
        try:
            self.dashboard.refresh()
            self.produits.refresh()
            self.clients.refresh()
            self.commandes.refresh()
        except db.DBError as e:
            messagebox.showerror(
                "Erreur base de données",
                f"{e}\n\nVérifiez MySQL et les paramètres CONFIG dans db.py.")


if __name__ == "__main__":
    App().mainloop()
