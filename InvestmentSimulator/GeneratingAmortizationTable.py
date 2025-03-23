import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime, timedelta

def generate_files():
    try:
        investment_id = entry_investment_id.get()
        owner = entry_owner.get()
        yield_value = float(entry_yield_value.get())
        principal = float(entry_principal.get())
        purchase_date = datetime.strptime(entry_purchase_date.get(), '%Y-%m-%d')
        maturity_date = datetime.strptime(entry_maturity_date.get(), '%Y-%m-%d')
        annual_interest_rate = float(entry_annual_interest_rate.get())
        capital_repayments_dates = [datetime.strptime(d.strip(), '%Y-%m-%d') for d in entry_capital_repayments_dates.get().split(',')]
        amount_paid = float(entry_amount_paid.get())
        first_interest_payment_date = datetime.strptime(entry_first_interest_payment_date.get(), '%Y-%m-%d')
        payment_frequency = int(entry_payment_frequency.get())
        
        num_capital_repayments = len(capital_repayments_dates)
        actual_principal_return = round(amount_paid / num_capital_repayments, 2)
        payment_dates = []
        interest_payments = []
        principal_remaining = []
        principal_returned = []
        actual_principal_returned = []
        prize = []
        monthly_interest_rate = annual_interest_rate / 100 / 12
        
        current_date = first_interest_payment_date
        while current_date <= maturity_date:
            payment_dates.append(current_date)
            next_month = current_date.month + payment_frequency if current_date.month + payment_frequency <= 12 else current_date.month + payment_frequency - 12
            next_year = current_date.year if current_date.month + payment_frequency <= 12 else current_date.year + 1
            print(f'{next_year}-{next_month}-{maturity_date.day}')
            current_date = datetime(next_year, next_month, maturity_date.day)
        
        remaining_principal = principal
        repayment_amount = principal / num_capital_repayments
        for date in payment_dates:
            interest_payment = remaining_principal * monthly_interest_rate
            interest_payments.append(round(interest_payment, 2))
            if date in capital_repayments_dates:
                remaining_principal -= repayment_amount
                principal_returned.append(repayment_amount)
                actual_principal_returned.append(actual_principal_return)
                prize.append(repayment_amount-actual_principal_return)
            else:
                principal_returned.append(0)
                actual_principal_returned.append(0)
                prize.append(0)
            principal_remaining.append(round(remaining_principal, 2))

        
        amortization_table = pd.DataFrame({
            "Fecha de Pago": payment_dates,
            "Capital Restante": principal_remaining,
            "Interés Mensual": interest_payments,
            "Capital de retorno": principal_returned,
            "Capital Devuelto": actual_principal_returned,
            "Premio": prize
        })
        
        amortization_table["ID"] = investment_id
        amortization_table["Propietario"] = owner
        amortization_table["Rendimiento"] = yield_value
        amortization_table["Fecha de Compra"] = purchase_date.strftime('%Y-%m-%d')
        amortization_table["Fecha de Vencimiento"] = maturity_date.strftime('%Y-%m-%d')
        amortization_table["Tasa nominal de interés anual"] = annual_interest_rate
        amortization_table["Amortización"] = amortization_table["Interés Mensual"] + amortization_table["Capital Devuelto"] + amortization_table["Premio"]
        
        amortization_table["Fecha de Pago"] = amortization_table["Fecha de Pago"].dt.strftime('%Y-%m-%d')
        amortization_table = amortization_table.sort_values(by=["Fecha de Pago"]).drop_duplicates()
        amortization_table = amortization_table.drop('Capital de retorno', axis=1)

        # Concatenate tables and sort by Fecha de Pago
        final_table = pd.concat([amortization_table], ignore_index=True)
        final_table = final_table.sort_values(by=["Fecha de Pago"])
        
        file_path_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path_excel:
            final_table.to_excel(file_path_excel, index=False, float_format="%.2f")
            messagebox.showinfo("Éxito", f"Archivo Excel guardado en: {file_path_excel}")
        
        file_path_sql = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
        if file_path_sql:
            sql_statements = []
            for _, row in final_table.iterrows():
                sql_statements.append(f"INSERT INTO amortization (inv_id, am_purchase_date, am_expiration_date, am_owner, am_enterprise, am_months, am_days, am_rate, am_return, am_interest, am_principal, am_retention, am_interest_total, am_sold_date, am_expired, is_active, is_deleted) VALUES ({row['ID']}, '{row['Fecha de Compra']}', '{row['Fecha de Pago']}', '{row['Propietario']}', 'BONOS DEL ESTADO {row['Fecha de Vencimiento']}', 0, 0, {round(row['Tasa nominal de interés anual'], 2)}, {round(row['Rendimiento'], 2)}, {round(row['Interés Mensual'], 2)}, {round(row['Capital Devuelto'], 2)}, 0, {round(row['Interés Mensual'], 2)}, NULL, 0, 0, 0);\n")
            
            with open(file_path_sql, "w") as sql_file:
                sql_file.writelines(sql_statements)
            messagebox.showinfo("Éxito", f"Archivo SQL guardado en: {file_path_sql}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

root = tk.Tk()
root.title("Generador de Tabla de Amortización")

labels = ["Investment ID:", "Owner:", "Yield Value:", "Principal:", "Purchase Date (YYYY-MM-DD):", "Maturity Date (YYYY-MM-DD):", "Annual Interest Rate:", "Capital Repayment Dates (comma-separated YYYY-MM-DD):", "Amount Paid:", "First Interest Payment Date (YYYY-MM-DD):", "Payment frequency:"]
entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

entry_investment_id, entry_owner, entry_yield_value, entry_principal, entry_purchase_date, entry_maturity_date, entry_annual_interest_rate, entry_capital_repayments_dates, entry_amount_paid, entry_first_interest_payment_date, entry_payment_frequency = entries

tk.Button(root, text="Generar Amortización y SQL", command=generate_files).grid(row=len(labels), columnspan=2, pady=10)

root.mainloop()
