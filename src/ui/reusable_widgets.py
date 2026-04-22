from tkinter import ttk


def add_labeled_entry(
    parent,
    *,
    row: int,
    label_col: int,
    entry_col: int,
    label_text: str,
    variable,
    width: int,
    label_style: str = "Muted.TLabel",
    entry_style: str = "App.TEntry",
):
    ttk.Label(parent, text=label_text, style=label_style).grid(
        row=row,
        column=label_col,
        padx=12,
        pady=6,
        sticky="w",
    )
    entry = ttk.Entry(parent, textvariable=variable, width=width, style=entry_style)
    entry.grid(row=row, column=entry_col, padx=6, pady=6, sticky="w")
    return entry


def configure_treeview_columns(tree: ttk.Treeview, columns: list[tuple[str, int]]):
    for col, width in columns:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="w")
