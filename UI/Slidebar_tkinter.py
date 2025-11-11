import tkinter as tk
from tkinter import ttk, messagebox
import functools

class AutomationDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automation Dashboard")
        self.geometry("1300x750")
        self.configure(bg="#F0F2F5")

        self.sidebar_width = 280
        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        sidebar_container = tk.Frame(self, bg="#2F3E50", width=self.sidebar_width)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        canvas = tk.Canvas(sidebar_container, bg="#2F3E50", width=self.sidebar_width, highlightthickness=0)
        canvas.pack(side="left", fill="y", expand=True)

        scrollbar = ttk.Scrollbar(sidebar_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.sidebar = tk.Frame(canvas, bg="#2F3E50")
        canvas.create_window((0,0), window=self.sidebar, anchor="nw")

        tk.Label(self.sidebar, text="Modules", bg="#2F3E50", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=15)

        self.modules = {
            "Pharmacy": ["Purchase Order", "Attendance", "Leave", "Holiday"],
            "Inventory": ["Stock", "Purchase", "Sales", "Reports"],
            "Finance": ["Invoices", "Payments", "Budgets"],
        }

        self.submenus = {}
        self.current_open_module = None

        for module, submodules in self.modules.items():
            # Module button
            module_btn = tk.Button(self.sidebar, text=f"▶ {module}", 
                                   bg="#34495E", fg="white", anchor="w",
                                   relief="flat", padx=20, pady=10,
                                   font=("Segoe UI", 12, "bold"),
                                   width=25,
                                   command=functools.partial(self.toggle_submenu, module))
            module_btn.pack(fill="x", padx=0, pady=0)
            module_btn.bind("<Enter>", lambda e, b=module_btn: b.config(bg="#3E5870"))
            module_btn.bind("<Leave>", lambda e, b=module_btn: b.config(bg="#34495E"))

            # Submenu frame directly under module button
            submenu_frame = tk.Frame(self.sidebar, bg="#3B4C63")
            submenu_frame.pack(fill="x", padx=0)
            submenu_frame.pack_forget()  # hidden by default

            for sub in submodules:
                sub_btn = tk.Button(submenu_frame, text=f"• {sub}",
                                    bg="#3B4C63", fg="white", anchor="w",
                                    relief="flat", padx=35, pady=8,
                                    font=("Segoe UI", 11),
                                    width=25,
                                    command=functools.partial(self.load_features, module, sub))
                sub_btn.pack(fill="x", padx=0, pady=1)
                sub_btn.bind("<Enter>", lambda e, b=sub_btn: b.config(bg="#4B5D7A"))
                sub_btn.bind("<Leave>", lambda e, b=sub_btn: b.config(bg="#3B4C63"))

            self.submenus[module] = submenu_frame  # Add submenu properly

    def toggle_submenu(self, module):
        # Close previously open module submenu
        if self.current_open_module and self.current_open_module != module:
            self.submenus[self.current_open_module].pack_forget()

        submenu = self.submenus[module]

        # Toggle current module
        if submenu.winfo_ismapped():
            submenu.pack_forget()
            self.current_open_module = None
        else:
            submenu.pack(fill="x")
            self.current_open_module = module

    def create_main_area(self):
        self.main_area = tk.Frame(self, bg="#F0F2F5")
        self.main_area.pack(side="right", expand=True, fill="both")

        self.title_label = tk.Label(self.main_area, text="Select a Module", 
                                    font=("Segoe UI", 20, "bold"), bg="#F0F2F5", fg="#2C3E50")
        self.title_label.pack(pady=20)

        self.feature_navbar = tk.Frame(self.main_area, bg="#ECF0F1")
        self.feature_navbar.pack(fill="x", padx=20, pady=5)

        self.feature_frame = tk.Frame(self.main_area, bg="#F0F2F5")
        self.feature_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def load_features(self, module, submodule):
        for widget in self.feature_navbar.winfo_children():
            widget.destroy()

        self.title_label.config(text=f"{module} → {submodule}")

        self.features = {
            "Purchase Order": ["Create Purchase Order", "View Details", "Edit Purchase Order", "Delete Purchase Order"],
            "Attendance": ["Mark Attendance", "View Report", "Export CSV"],
            "Holiday": ["Add Holiday", "View Holidays", "Delete Holiday"],
            "Stock": ["Add Stock", "Update Stock", "Low Stock Alert"],
        }

        current_features = self.features.get(submodule, ["No features defined"])

        for f in current_features:
            btn = ttk.Button(self.feature_navbar, text=f, command=lambda feat=f: self.show_feature_inputs(feat))
            btn.pack(side="left", padx=5, pady=5)

        for widget in self.feature_frame.winfo_children():
            widget.destroy()

    def show_feature_inputs(self, feature):
        for widget in self.feature_frame.winfo_children():
            widget.destroy()

        tk.Label(self.feature_frame, text=f"{feature} Inputs", font=("Segoe UI", 16, "bold"), bg="#F0F2F5").pack(pady=10)

        if feature == "Create Purchase Order":
            # Create a frame to hold inputs in one row
            input_row = tk.Frame(self.feature_frame, bg="#F0F2F5")
            input_row.pack(fill="x", pady=5)

            # List of input labels
            labels = ["Supplier Name", "Order Date", "Total Amount", "Payment Terms", "Remarks"]
            entries = []

            for i, label_text in enumerate(labels):
                # Create a subframe for each label+entry
                sub_frame = tk.Frame(input_row, bg="#F0F2F5")
                sub_frame.grid(row=0, column=i, padx=5, sticky="nsew")

                tk.Label(sub_frame, text=label_text+":", bg="#F0F2F5").pack(anchor="w")
                entry = tk.Entry(sub_frame, width=20)
                entry.pack()
                entries.append(entry)

            # Make columns expand evenly
            for i in range(len(labels)):
                input_row.grid_columnconfigure(i, weight=1)

            # Submit button below
            ttk.Button(self.feature_frame, text="Submit", command=lambda: messagebox.showinfo("Submit", "Purchase Order Created")).pack(pady=10)

        else:
            tk.Label(self.feature_frame, text="Feature not implemented yet.", bg="#F0F2F5").pack(pady=20)


if __name__ == "__main__":
    app = AutomationDashboard()
    app.mainloop()
