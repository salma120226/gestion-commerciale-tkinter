import tkinter as tk
from tkinter import ttk
from decimal import Decimal

BG = "#F4F6FB"
DARK = "#20223A"
GREY = "#85899B"
PURPLE = "#635BDB"
GREEN = "#269C86"
RED = "#DC665B"
ORANGE = "#E99B42"
BLUE = "#3287C9"
BORDER = "#E7E9F0"


def format_value(value):
    if value is None:
        return ""
    if isinstance(value, Decimal):
        if value.as_tuple().exponent >= 0:
            return str(int(value))
        return f"{value:.2f}"
    return str(value)


def fmt_money(value):
    return f"{float(value):,.2f} DH"


def page_header(parent, title, subtitle):
    header = tk.Frame(parent, bg=BG)
    header.pack(fill="x", pady=(0, 20))

    tk.Label(
        header,
        text=title,
        font=("Segoe UI", 24, "bold"),
        bg=BG,
        fg=DARK
    ).pack(anchor="w")

    tk.Label(
        header,
        text=subtitle,
        font=("Segoe UI", 10),
        bg=BG,
        fg=GREY
    ).pack(anchor="w", pady=5)

    return header


def card(parent):
    return tk.Frame(
        parent,
        bg="white",
        highlightbackground=BORDER,
        highlightthickness=1
    )


def card_title(parent, text):
    label = tk.Label(
        parent,
        text=text,
        font=("Segoe UI", 13, "bold"),
        bg="white",
        fg=DARK
    )
    label.pack(anchor="w", padx=18, pady=(15, 10))
    return label


def action_button(parent, text, color, command):
    button = tk.Button(
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
    )
    button.pack(side="left", padx=(0, 8))
    return button


def field_frame(parent, label, row, column, columnspan):
    frame = tk.Frame(parent, bg="white")
    frame.grid(
        row=row,
        column=column,
        columnspan=columnspan,
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

    for i in range(column, column + columnspan):
        parent.grid_columnconfigure(i, weight=1)

    return frame


def form_field(parent, label, row, column, columnspan=1):
    frame = field_frame(parent, label, row, column, columnspan)

    entry = tk.Entry(
        frame,
        font=("Segoe UI", 10),
        relief="solid",
        bd=1
    )
    entry.pack(fill="x", ipady=7)

    return entry


def form_combo(parent, label, row, column, columnspan=1):
    frame = field_frame(parent, label, row, column, columnspan)

    combo = ttk.Combobox(
        frame,
        font=("Segoe UI", 10),
        state="readonly"
    )
    combo.pack(fill="x", ipady=5)

    return combo


def make_table(parent, columns, height=8):
    frame = tk.Frame(parent, bg="white")
    frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    table = ttk.Treeview(
        frame,
        columns=[column[0] for column in columns],
        show="headings",
        height=height
    )

    for key, heading, width in columns:
        table.heading(key, text=heading)
        table.column(key, anchor="center", width=width)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    table.tag_configure("Validée", foreground=GREEN)
    table.tag_configure("Annulée", foreground=RED)
    table.tag_configure("En attente", foreground=ORANGE)

    return table


def clear_table(table):
    for item in table.get_children():
        table.delete(item)


def fill_table(table, rows, tag_column=None):
    clear_table(table)

    for row in rows:
        values = [format_value(value) for value in row]
        tags = (values[tag_column],) if tag_column is not None else ()
        table.insert("", "end", values=values, tags=tags)


def fill_dict_table(table, rows):
    clear_table(table)

    if not rows:
        return

    columns = list(rows[0].keys())
    table.configure(columns=columns, show="headings")

    for column in columns:
        table.heading(column, text=column)
        table.column(column, anchor="center", width=120)

    for row in rows:
        table.insert("", "end", values=[format_value(row[column]) for column in columns])


def selected_values(table):
    selection = table.selection()

    if not selection:
        return None

    return table.item(selection[0], "values")