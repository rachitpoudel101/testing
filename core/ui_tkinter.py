import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from create_purchase_order import PurchaseOrder  # Your automation class with BaseCanteenAutomation

# --- Logging callback for UI ---
def append_log(msg):
    log_text.config(state='normal')
    log_text.insert(tk.END, msg + "\n")
    log_text.see(tk.END)
    log_text.config(state='disabled')

# --- Run Automation ---
def run_automation():
    try:
        # Collect values from the UI
        username = username_var.get()
        password = password_var.get()
        supplier = supplier_var.get()
        store = store_var.get()
        delivery_date = delivery_date_var.get()
        prepared_by = prepared_by_var.get()
        credit_days = credit_days_var.get()
        payment_term = payment_term_var.get()
        cc_charge = cc_charge_var.get()
        discount_on = discount_on_var.get()
        tax_active = tax_var.get()
        catalogue = catalogue_var.get()

        # Clear previous logs
        log_text.config(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.config(state='disabled')

        # Run automation in a separate thread
        def task():
            try:
                bot = PurchaseOrder(username, password, log_callback=append_log)
                bot.load_dashboard()
                append_log("[SUCCESS] Automation completed successfully!")
                messagebox.showinfo("Done", "Automation completed successfully!")
            except Exception as e:
                append_log(f"[ERROR] {e}")
                messagebox.showerror("Error", str(e))

        threading.Thread(target=task).start()

    except Exception as e:
        append_log(f"[ERROR] {e}")
        messagebox.showerror("Error", str(e))

# --- Tkinter UI ---
root = tk.Tk()
root.title("Purchase Order Automation")
root.geometry("600x700")

# Variables
username_var = tk.StringVar()
password_var = tk.StringVar()
supplier_var = tk.StringVar()
store_var = tk.StringVar()
delivery_date_var = tk.StringVar()
prepared_by_var = tk.StringVar()
credit_days_var = tk.StringVar()
payment_term_var = tk.StringVar()
cc_charge_var = tk.StringVar()
discount_on_var = tk.StringVar()
tax_var = tk.BooleanVar()
catalogue_var = tk.StringVar()

# Input fields
fields = [
    ("Username", username_var),
    ("Password", password_var, True),
    ("Supplier", supplier_var),
    ("Store", store_var),
    ("Delivery Date (YYYY-MM-DD)", delivery_date_var),
    ("Prepared By", prepared_by_var),
    ("Credit Days", credit_days_var),
    ("Payment Term", payment_term_var),
    ("CC Charge", cc_charge_var),
    ("Discount On", discount_on_var),
    ("Catalogue", catalogue_var),
]

for i, field in enumerate(fields):
    tk.Label(root, text=field[0]).grid(row=i, column=0, padx=10, pady=5, sticky="w")
    entry = tk.Entry(root, textvariable=field[1], show="*" if len(field) > 2 and field[2] else "")
    entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")

# Tax Checkbox
tk.Checkbutton(root, text="Tax Active", variable=tax_var).grid(row=len(fields), column=0, columnspan=2, pady=5)

# Buttons
tk.Button(root, text="Run Automation", command=run_automation, bg="green", fg="white").grid(row=len(fields)+1, column=0, padx=10, pady=10)
tk.Button(root, text="Exit", command=root.quit, bg="red", fg="white").grid(row=len(fields)+1, column=1, padx=10, pady=10)

# Log Text Area
tk.Label(root, text="Logs:").grid(row=len(fields)+2, column=0, columnspan=2, sticky="w", padx=10)
log_text = scrolledtext.ScrolledText(root, width=70, height=20, state='disabled', bg="#f0f0f0")
log_text.grid(row=len(fields)+3, column=0, columnspan=2, padx=10, pady=5)

# Run UI
root.mainloop()
