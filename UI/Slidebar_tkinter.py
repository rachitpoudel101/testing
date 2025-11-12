import tkinter as tk
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading

# Import your PurchaseOrder automation class
from Purchase_Order.create_purchase_order import PurchaseOrder 
class AutomationDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1400x800")
        self.configure(bg="#F8F9FA")

        # Colors
        self.colors = self.get_colors()

        # Styles
        self.init_styles()

        # Sidebar
        self.sidebar_width = 300
        self.current_open_module = None
        self.module_frames = {}
        self.submenus = {}
        self.module_icons = {"Pharmacy": "💊", "Inventory": "📦", "Finance": "💰"}
        self.modules = {
            "Pharmacy": ["Purchase Order", "Attendance", "Leave", "Holiday"],
            "Inventory": ["Stock", "Purchase", "Sales", "Reports"],
            "Finance": ["Invoices", "Payments", "Budgets"],
        }

        self.create_sidebar()
        self.create_main_area()

    def get_colors(self):
        return {
            'sidebar_bg': '#0A1929', 'sidebar_active': '#1E3A5F', 'sidebar_hover': '#132F4C',
            'submenu_bg': '#061321', 'submenu_hover': '#1A2B3C', 'main_bg': '#F8F9FA',
            'card_bg': '#FFFFFF', 'header_bg': '#FFFFFF', 'text_dark': '#1E293B',
            'text_medium': '#475569', 'text_light': '#94A3B8', 'primary': '#2563EB',
            'primary_hover': '#1D4ED8', 'success': '#10B981', 'success_hover': '#059669',
            'danger': '#EF4444', 'warning': '#F59E0B', 'border': '#E2E8F0',
            'border_light': '#F1F5F9', 'accent': '#8B5CF6'
        }

    def init_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(16, 10),
                        background=self.colors['primary'], foreground="white", relief="flat")
        style.map("TButton", background=[("active", self.colors['primary_hover'])])
        style.configure("Sidebar.TButton", background=self.colors['sidebar_bg'], foreground="white",
                        anchor="w", padding=(18, 14), relief="flat")
        style.map("Sidebar.TButton", background=[("active", self.colors['sidebar_hover'])])

    # ---------------- Sidebar ---------------- #
    def create_sidebar(self):
        sidebar_container = tk.Frame(self, bg=self.colors['sidebar_bg'], width=self.sidebar_width)
        sidebar_container.pack(side="left", fill="y")
        sidebar_container.pack_propagate(False)

        self.create_logo(sidebar_container)
        self.create_scrollable_sidebar(sidebar_container)

    def create_logo(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['sidebar_bg'], height=150)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        logo_container = tk.Frame(header_frame, bg="#102A43", height=120)
        logo_container.pack(fill="x", padx=25, pady=15)
        logo_container.pack_propagate(False)

        shadow = tk.Frame(logo_container, bg="#0D2847", highlightthickness=2, highlightbackground="#1E3A5F")
        shadow.pack(expand=True, fill="both", padx=3, pady=3)
        shadow.pack_propagate(False)

        logo_content = tk.Frame(shadow, bg="#102A43")
        logo_content.pack(expand=True)

        # Load logo
        try:
            logo_img = Image.open("logo.png").resize((100, 100), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(logo_content, image=self.logo_photo, bg="#102A43").pack(expand=True)
        except:
            tk.Label(logo_content, text="🐬", bg="#102A43", fg="white", font=("Segoe UI", 28)).pack(expand=True)

    def create_scrollable_sidebar(self, parent):
        canvas = tk.Canvas(parent, bg=self.colors['sidebar_bg'], width=self.sidebar_width, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.sidebar = tk.Frame(canvas, bg=self.colors['sidebar_bg'])
        canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=self.sidebar_width)

        # Create modules
        for module, subs in self.modules.items():
            self.create_module_section(module, subs)

    def create_module_section(self, module, submodules):
        container = tk.Frame(self.sidebar, bg=self.colors['sidebar_bg'])
        container.pack(fill="x", padx=15, pady=4)
        inner = tk.Frame(container, bg=self.colors['sidebar_bg'], cursor="hand2")
        inner.pack(fill="x")

        # Left side (icon + text)
        left = tk.Frame(inner, bg=self.colors['sidebar_bg'])
        left.pack(side="left", fill="x", expand=True)
        icon = tk.Label(left, text=self.module_icons.get(module, "📁"), bg=self.colors['sidebar_bg'],
                        fg="white", font=("Segoe UI", 16))
        icon.pack(side="left", padx=(0, 12))
        text = tk.Label(left, text=module, bg=self.colors['sidebar_bg'], fg="white",
                        font=("Segoe UI", 12, "bold"), anchor="w")
        text.pack(side="left", fill="x", expand=True)
        arrow = tk.Label(inner, text="›", bg=self.colors['sidebar_bg'], fg="#64B5F6",
                         font=("Segoe UI", 18, "bold"))
        arrow.pack(side="right")

        self.module_frames[module] = {'container': container, 'inner': inner, 'icon': icon, 'text': text, 'arrow': arrow}

        # Hover and click effects
        for w in [container, inner, left, icon, text, arrow]:
            w.bind("<Enter>", lambda e, m=module: self.on_module_hover(m, True))
            w.bind("<Leave>", lambda e, m=module: self.on_module_hover(m, False))
            w.bind("<Button-1>", lambda e, m=module: self.toggle_submenu(m))

        # Submenu
        submenu_frame = tk.Frame(self.sidebar, bg=self.colors['submenu_bg'])
        for sub in submodules:
            self.create_submenu_item(submenu_frame, module, sub)
        self.submenus[module] = {"frame": submenu_frame}

    def on_module_hover(self, module, enter):
        if self.current_open_module != module:
            color = self.colors['sidebar_hover'] if enter else self.colors['sidebar_bg']
            for k in self.module_frames[module].values():
                if isinstance(k, tk.Widget):
                    k.config(bg=color)

    def create_submenu_item(self, parent, module, sub):
        cont = tk.Frame(parent, bg=self.colors['submenu_bg'], cursor="hand2")
        cont.pack(fill="x", padx=8, pady=2)
        inner = tk.Frame(cont, bg=self.colors['submenu_bg'])
        inner.pack(fill="x", padx=12, pady=8)
        bullet = tk.Label(inner, text="●", bg=self.colors['submenu_bg'], fg="#64B5F6", font=("Segoe UI", 8))
        bullet.pack(side="left", padx=(20, 10))
        txt = tk.Label(inner, text=sub, bg=self.colors['submenu_bg'], fg="#B0BEC5", font=("Segoe UI", 10))
        txt.pack(side="left", fill="x", expand=True)

        # Hover & click
        for w in [cont, inner, bullet, txt]:
            w.bind("<Enter>", lambda e, c=cont, i=inner, b=bullet, t=txt: self.on_sub_hover(c, i, b, t, True))
            w.bind("<Leave>", lambda e, c=cont, i=inner, b=bullet, t=txt: self.on_sub_hover(c, i, b, t, False))
            w.bind("<Button-1>", lambda e, m=module, s=sub: self.load_features(m, s))

    def on_sub_hover(self, cont, inner, bullet, txt, enter):
        bg = self.colors['submenu_hover'] if enter else self.colors['submenu_bg']
        fg = "white" if enter else "#B0BEC5"
        bullet_fg = "#90CAF9" if enter else "#64B5F6"
        cont.config(bg=bg)
        inner.config(bg=bg)
        bullet.config(bg=bg, fg=bullet_fg)
        txt.config(bg=bg, fg=fg)

    def toggle_submenu(self, module):
        if self.current_open_module and self.current_open_module != module:
            self.submenus[self.current_open_module]["frame"].pack_forget()
            self.module_frames[self.current_open_module]['arrow'].config(text="›")
            self.on_module_hover(self.current_open_module, False)

        submenu = self.submenus[module]["frame"]
        arrow = self.module_frames[module]['arrow']
        if submenu.winfo_ismapped():
            submenu.pack_forget()
            arrow.config(text="›")
            self.current_open_module = None
            self.on_module_hover(module, False)
        else:
            submenu.pack(fill="x", after=self.module_frames[module]['container'])
            arrow.config(text="▾", fg="white")
            self.current_open_module = module
            for k in self.module_frames[module].values():
                if isinstance(k, tk.Widget):
                    k.config(bg=self.colors['sidebar_active'])

    # ---------------- Main Area ---------------- #
    def create_main_area(self):
        self.main_area = tk.Frame(self, bg=self.colors['main_bg'])
        self.main_area.pack(side="right", expand=True, fill="both")

        self.create_header()
        self.feature_navbar = tk.Frame(self.main_area, bg=self.colors['main_bg'], height=65)
        self.feature_navbar.pack(fill="x", padx=35, pady=(15, 0))

        content_wrapper = tk.Frame(self.main_area, bg=self.colors['main_bg'])
        content_wrapper.pack(pady=20, padx=35, fill="both", expand=True)
        card_shadow = tk.Frame(content_wrapper, bg="#E2E8F0")
        card_shadow.pack(fill="both", expand=True)
        self.feature_frame = tk.Frame(card_shadow, bg=self.colors['card_bg'])
        self.feature_frame.pack(fill="both", expand=True, padx=1, pady=1)

    def create_header(self):
        header_outer = tk.Frame(self.main_area, bg=self.colors['header_bg'])
        header_outer.pack(fill="x")
        header_frame = tk.Frame(header_outer, bg=self.colors['header_bg'], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Left title
        left_header = tk.Frame(header_frame, bg=self.colors['header_bg'])
        left_header.pack(side="left", padx=35, pady=20)
        self.title_label = tk.Label(left_header, text="Select a Module",
                                    font=("Segoe UI", 24, "bold"), bg=self.colors['header_bg'],
                                    fg=self.colors['text_dark'])
        self.title_label.pack(side="left")

    # ---------------- Feature Loading ---------------- #
    def load_features(self, module, submodule):
        for w in self.feature_navbar.winfo_children():
            w.destroy()
        self.title_label.config(text=f"{module}  ›  {submodule}")
        self.features = {
            "Purchase Order": ["Create Purchase Order", "View Details", "Edit Purchase Order", "Delete Purchase Order"],
            "Stock": ["Add Stock", "Update Stock", "Low Stock Alert"],
        }
        current_features = self.features.get(submodule, ["No features defined"])
        tabs_container = tk.Frame(self.feature_navbar, bg=self.colors['card_bg'])
        tabs_container.pack(fill="x")

        for f in current_features:
            self.create_tab(tabs_container, f)

        # Placeholder content
        for w in self.feature_frame.winfo_children():
            w.destroy()
        placeholder = tk.Frame(self.feature_frame, bg=self.colors['card_bg'])
        placeholder.pack(expand=True)
        tk.Label(placeholder, text="📋", bg=self.colors['card_bg'], font=("Segoe UI", 50)).pack(pady=(0, 15))
        tk.Label(placeholder, text="Choose a feature from above", font=("Segoe UI", 14),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack()

    def create_tab(self, parent, feature):
        tab_btn = tk.Frame(parent, bg=self.colors['card_bg'], cursor="hand2")
        tab_btn.pack(side="left", padx=3)
        tab_content = tk.Frame(tab_btn, bg=self.colors['card_bg'])
        tab_content.pack(padx=18, pady=14)
        tab_label = tk.Label(tab_content, text=feature, bg=self.colors['card_bg'],
                             fg=self.colors['text_medium'], font=("Segoe UI", 10, "bold"))
        tab_label.pack()
        indicator = tk.Frame(tab_btn, bg=self.colors['primary'], height=3)

        def on_tab_click(e):
            for child in parent.winfo_children():
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Frame) and sub.winfo_height() == 3:
                        sub.pack_forget()
            indicator.pack(side="bottom", fill="x")
            tab_label.config(fg=self.colors['primary'])
            self.show_feature_inputs(feature)

        for w in [tab_btn, tab_content, tab_label]:
            w.bind("<Button-1>", on_tab_click)

    # ---------------- Feature UI ---------------- #
    def show_feature_inputs(self, feature):
        for w in self.feature_frame.winfo_children():
            w.destroy()
        content = tk.Frame(self.feature_frame, bg=self.colors['card_bg'])
        content.pack(fill="both", expand=True, padx=45, pady=35)
        tk.Label(content, text=f"📝 {feature}", font=("Segoe UI", 20, "bold"), bg=self.colors['card_bg']).pack()

        if feature == "Create Purchase Order":
            self.create_purchase_order_form(content)
        else:
            tk.Label(content, text="Feature UI under development", bg=self.colors['card_bg'],
                     fg=self.colors['text_light'], font=("Segoe UI", 12)).pack(pady=50)

    def create_purchase_order_form(self, parent):
        fields = ["Username", "Password", "Supplier Name", "Order Date", "Payment Terms", "Remarks"]
        self.entries = {}
        form_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        form_frame.pack(fill="both", expand=True, pady=20)

        max_rows_per_column = 5
        num_columns = (len(fields) + max_rows_per_column - 1) // max_rows_per_column  # ceil division

        for index, f in enumerate(fields):
            col = index // max_rows_per_column
            row = index % max_rows_per_column

            field_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
            field_frame.grid(row=row, column=col, padx=20, pady=10, sticky="nsew")

            tk.Label(field_frame, text=f, bg=self.colors['card_bg'], fg=self.colors['text_dark'],
                    font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
            entry_frame = tk.Frame(field_frame, bg="white", highlightbackground=self.colors['border'],
                                highlightcolor=self.colors['primary'], highlightthickness=2)
            entry_frame.pack(fill="x")
            entry = tk.Entry(entry_frame, font=("Segoe UI", 11), bg="white", fg=self.colors['text_dark'], relief="flat")
            entry.pack(fill="x", padx=15, pady=12)
            self.entries[f] = entry
            if f == "Password":
                entry.config(show="*")

        # Make columns expand equally
        for col in range(num_columns):
            form_frame.grid_columnconfigure(col, weight=1)

        # Submit Button (span across all columns)
        submit_frame = tk.Frame(parent, bg=self.colors['success'], cursor="hand2")
        submit_frame.pack(pady=30)
        submit_label = tk.Label(submit_frame, text=" Submit Purchase Order",
                                bg=self.colors['success'], fg="white", font=("Segoe UI", 10, "bold"))
        submit_label.pack(padx=35, pady=14)

        submit_frame.bind("<Button-1>", lambda e: self.submit_purchase_order())
        submit_label.bind("<Button-1>", lambda e: self.submit_purchase_order())

    def submit_purchase_order(self):
        data = {f: self.entries[f].get() for f in self.entries}
        username = data.get("Username")
        password = data.get("Password")

        # Run automation in a separate thread to avoid freezing the GUI
        threading.Thread(target=self.run_purchase_order_bot, args=(username, password)).start()

    def run_purchase_order_bot(self, username, password):
        try:
            bot = PurchaseOrder(username, password)
            bot.load_dashboard()
            messagebox.showinfo("Success", "Purchase Order automation completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Automation failed:\n{e}")


if __name__ == "__main__":
    app = AutomationDashboard()
    app.mainloop()
