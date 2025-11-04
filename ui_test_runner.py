import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time

# Import the test functions and LOG_FILE from your existing module
# Make sure test_canteen_ui.py is in the same folder or in PYTHONPATH
from test_canteen_ui import add_employee, LOG_FILE, employee_meal_schedule_test


def clear_log_file():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")  # Clear existing log


# --- Helper to append logs to the UI and (optionally) scroll ---
def append_log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
    log_text.insert(tk.END, timestamp + msg + "\n")
    log_text.see(tk.END)


# --- Run Selected Test ---
def run_selected_test():
    test_name = test_var.get()
    status_label.config(text="Running test...", fg="blue")
    run_button.config(state=tk.DISABLED)
    log_text.delete(1.0, tk.END)

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    def task():
        try:
            if test_name == "Add Employee Test":
                emp_id = employee_id_entry.get().strip()
                first_name = first_name_entry.get().strip()
                middle_name = middle_name_entry.get().strip()
                last_name = last_name_entry.get().strip()
                departments = [d.strip() for d in departments_entry.get().split(",") if d.strip()]
                is_active = is_active_var.get()

                # Basic validation
                if not username or not password or not emp_id or not first_name or not last_name:
                    messagebox.showwarning("Input Error", "Please fill required fields: username, password, employee id, first and last names.")
                    status_label.config(text="Idle...", fg="black")
                    run_button.config(state=tk.NORMAL)
                    return

                success, logs = add_employee(
                    username=username,
                    password=password,
                    employee_id=emp_id,
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                    department_list=departments,
                    is_active=is_active,
                    log_callback=lambda m: append_log(m)
                )

                status_label.config(text=("Employee Added!" if success else "Add Employee Failed!"),
                                    fg=("green" if success else "red"))

            elif test_name == "Employee Meal Schedule Test":
                # date_str = ems_date_entry.get().strip()
                # schedule_for_tomorrow = ems_schedule_tomorrow_var.get()
                # tomorrow_meals = [m.strip() for m in ems_tomorrow_meals_entry.get().split(",") if m.strip()]
                meal_schedule_list = [m.strip() for m in ems_meal_schedule_entry.get().split(",") if m.strip()]
                departments = [d.strip() for d in ems_departments_entry.get().split(",") if d.strip()]
                employee_ids = [e.strip() for e in ems_employee_ids_entry.get().split(",") if e.strip()]

                # Basic validation
                if not username or not password:
                    messagebox.showwarning("Input Error", "Please fill required fields: username, password, and date.")
                    status_label.config(text="Idle...", fg="black")
                    run_button.config(state=tk.NORMAL)
                    return

                success, logs = employee_meal_schedule_test(
                    username=username,
                    password=password,
                    # date_str=date_str,
                    # schedule_for_tomorrow=schedule_for_tomorrow,
                    # tomorrow_meals=tomorrow_meals,
                    meal_schedule_list=meal_schedule_list,
                    department_list=departments,
                    employee_id_list=employee_ids,
                    log_callback=lambda m: append_log(m)
                )

                status_label.config(text=("Meal Schedule Created!" if success else "Meal Schedule Failed!"),
                                    fg=("green" if success else "red"))

            else:
                append_log(f"{test_name} is not implemented.")
                status_label.config(text="Test Not Implemented", fg="orange")

        except Exception as exc:
            append_log(f"Unexpected error: {exc}")
            status_label.config(text="Test Error!", fg="red")
        finally:
            run_button.config(state=tk.NORMAL)

    threading.Thread(target=task, daemon=True).start()


# --- Dynamic Form Update ---
def update_form(*args):
    for widget in form_frame.winfo_children():
        widget.destroy()

    test_name = test_var.get()

    # --- Username / Password ---
    tk.Label(form_frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", pady=2)
    globals()["username_entry"] = tk.Entry(form_frame, font=("Arial", 12))
    username_entry.grid(row=0, column=1, pady=2)

    tk.Label(form_frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", pady=2)
    globals()["password_entry"] = tk.Entry(form_frame, font=("Arial", 12), show="*")
    password_entry.grid(row=1, column=1, pady=2)

    if test_name == "Add Employee Test":
        tk.Label(form_frame, text="Employee ID:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", pady=2)
        globals()["employee_id_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        employee_id_entry.grid(row=2, column=1, pady=2)

        tk.Label(form_frame, text="First Name:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", pady=2)
        globals()["first_name_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        first_name_entry.grid(row=3, column=1, pady=2)

        tk.Label(form_frame, text="Middle Name:", font=("Arial", 12)).grid(row=4, column=0, sticky="e", pady=2)
        globals()["middle_name_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        middle_name_entry.grid(row=4, column=1, pady=2)

        tk.Label(form_frame, text="Last Name:", font=("Arial", 12)).grid(row=5, column=0, sticky="e", pady=2)
        globals()["last_name_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        last_name_entry.grid(row=5, column=1, pady=2)

        tk.Label(form_frame, text="Departments (comma separated):", font=("Arial", 12)).grid(row=6, column=0, sticky="e", pady=2)
        globals()["departments_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        departments_entry.grid(row=6, column=1, pady=2)

        tk.Label(form_frame, text="Active?", font=("Arial", 12)).grid(row=7, column=0, sticky="e", pady=2)
        global is_active_var
        is_active_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form_frame, variable=is_active_var).grid(row=7, column=1, pady=2)

    elif test_name == "Employee Meal Schedule Test":
        # tk.Label(form_frame, text="Date (YYYY-MM-DD):", font=("Arial", 12)).grid(row=2, column=0, sticky="e", pady=2)
        # globals()["ems_date_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        # ems_date_entry.grid(row=2, column=1, pady=2)

        # tk.Label(form_frame, text="Schedule for Tomorrow?", font=("Arial", 12)).grid(row=3, column=0, sticky="e", pady=2)
        # global ems_schedule_tomorrow_var
        # ems_schedule_tomorrow_var = tk.BooleanVar(value=False)
        # tk.Checkbutton(form_frame, variable=ems_schedule_tomorrow_var).grid(row=3, column=1, pady=2)

        # tk.Label(form_frame, text="Tomorrow Meals (comma separated):", font=("Arial", 12)).grid(row=4, column=0, sticky="e", pady=2)
        # globals()["ems_tomorrow_meals_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        # ems_tomorrow_meals_entry.grid(row=4, column=1, pady=2)

        tk.Label(form_frame, text="Meal Schedule (comma separated):", font=("Arial", 12)).grid(row=5, column=0, sticky="e", pady=2)
        globals()["ems_meal_schedule_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        ems_meal_schedule_entry.grid(row=5, column=1, pady=2)

        tk.Label(form_frame, text="Departments (comma separated):", font=("Arial", 12)).grid(row=6, column=0, sticky="e", pady=2)
        globals()["ems_departments_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        ems_departments_entry.grid(row=6, column=1, pady=2)

        tk.Label(form_frame, text="Employee IDs (comma separated):", font=("Arial", 12)).grid(row=7, column=0, sticky="e", pady=2)
        globals()["ems_employee_ids_entry"] = tk.Entry(form_frame, font=("Arial", 12))
        ems_employee_ids_entry.grid(row=7, column=1, pady=2)

    # small spacer
    form_frame.grid_columnconfigure(0, minsize=10)


# --- Tkinter UI ---
root = tk.Tk()
clear_log_file()
root.title("Automation Test Runner with Logs")
root.geometry("820x740")

tk.Label(root, text="Select Test to Run", font=("Arial", 14, "bold")).pack(pady=10)

# List of tests (add more if you implement them in test_canteen_ui)
tests = ["Add Employee Test",
          "Employee Meal Schedule Test"
          ]

test_var = tk.StringVar(root)
test_var.set(tests[0])

test_menu = tk.OptionMenu(root, test_var, *tests)
test_menu.pack(pady=5)

form_frame = tk.Frame(root)
form_frame.pack(pady=10)

update_form()
# trace to redraw the form when the selected test changes
test_var.trace("w", update_form)

run_button = tk.Button(root, text="▶ Run Test", font=("Arial", 12), bg="#4CAF50", fg="white", command=run_selected_test)
run_button.pack(pady=8)

status_label = tk.Label(root, text="Idle...", font=("Arial", 12))
status_label.pack(pady=5)

# Controls row for clearing logs and saving logs
controls_frame = tk.Frame(root)
controls_frame.pack(pady=6)

tk.Label(root, text="Test Logs:", font=("Arial", 12, "bold")).pack(pady=5)
log_text = scrolledtext.ScrolledText(root, height=18, width=100, font=("Courier", 10))
log_text.pack(pady=5)

root.mainloop()
