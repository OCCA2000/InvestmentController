import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime

def generate_files():
    try:
        payment_frequency = int(entry_payment_frequency.get() or 1)
        deferral_installments = int(entry_deferral_installments.get() or 0)
        amortization_type = entry_amortization_type.get()
        amortization_type = amortization_type.capitalize()
        try:
            capital_repayments_dates = [datetime.strptime(d.strip(), '%Y-%m-%d') for d in entry_capital_repayments_dates.get().split(',')]
        except:
            capital_repayments_dates = []

        principal = float(entry_principal.get())
        first_installment_date = datetime.strptime(entry_first_interest_payment_date.get(), '%Y-%m-%d')
        maturity_date = datetime.strptime(entry_maturity_date.get(), '%Y-%m-%d')
        annual_interest_rate = float(entry_annual_interest_rate.get())
        amount_paid = float(entry_amount_paid.get())

        payment_dates = []
        interest_payments = []
        principal_remaining = []
        principal_returned = []
        actual_principal_returned = []
        prize = []
        monthly_interest_rate = annual_interest_rate / 100 / 12 * payment_frequency
        
        current_date = first_installment_date

        while current_date <= maturity_date:
            payment_dates.append(current_date)
            next_month = current_date.month + payment_frequency if current_date.month + payment_frequency <= 12 else current_date.month + payment_frequency - 12
            next_year = current_date.year if current_date.month + payment_frequency <= 12 else current_date.year + 1
            current_date = datetime(next_year, next_month, maturity_date.day)
        
        if (len(capital_repayments_dates)>0):
            capital_repayments_dates = [d.date() for d in capital_repayments_dates]
        else:
            capital_repayments_dates = payment_dates[deferral_installments:]

        num_capital_repayments = len(capital_repayments_dates)
        
        remaining_principal = principal
        
        repayment_amount = round(principal / num_capital_repayments,2)
        principal_return = repayment_amount
        actual_principal_return = round(amount_paid / num_capital_repayments, 2)
        
        total_payment = (principal * monthly_interest_rate * pow(1+monthly_interest_rate,num_capital_repayments))/(pow(1+monthly_interest_rate,num_capital_repayments)-1)

        for date in payment_dates:
            interest_payment = remaining_principal * monthly_interest_rate
            interest_payments.append(round(interest_payment, 2))
            if date in capital_repayments_dates:
                if(amortization_type=='A'):
                    remaining_principal -= repayment_amount
                    principal_returned.append(repayment_amount)
                    actual_principal_returned.append(actual_principal_return)
                    prize.append(round(repayment_amount-actual_principal_return,2))
                elif(amortization_type=='F'):
                    repayment_amount = total_payment - interest_payment
                    remaining_principal -= repayment_amount
                    principal_returned.append(round(repayment_amount,2))
                    principal_equivalent=round(actual_principal_return*repayment_amount/principal_return,2)
                    actual_principal_returned.append(principal_equivalent)
                    prize.append(round(repayment_amount-principal_equivalent,2))
                else:
                    raise Exception("Tipo de amortización incorrecto.")
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
        
        amortization_table["Fecha de Vencimiento"] = maturity_date.strftime('%Y-%m-%d')
        amortization_table["Tasa nominal de interés anual"] = annual_interest_rate
        amortization_table["Flujo"] = amortization_table["Interés Mensual"] + amortization_table["Capital Devuelto"] + amortization_table["Premio"]
        #amortization_table = amortization_table.drop('Capital de retorno', axis=1)

        # Concatenate tables and sort by Fecha de Pago
        final_table = pd.concat([amortization_table], ignore_index=True)
        final_table = final_table.sort_values(by=["Fecha de Pago"])
        
        file_path_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path_excel:
            final_table.to_excel(file_path_excel, index=False, float_format="%.2f")
            messagebox.showinfo("Éxito", f"Archivo Excel guardado en: {file_path_excel}")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

root = tk.Tk()
root.title("Generador de Tabla de Amortización")

labels = [
          "Capital:",
          "Tasa de interés anual:",
          "Fecha de vencimiento (YYYY-MM-DD):",
          "Primera fecha de pago (YYYY-MM-DD):", 
          "Frecuencia de pago:",
          "Cantidad de cuotas a diferir:",
          "Amortización francesa (f) o alemana (a):",
          "Fechas de retorno de capital (separadas por comas YYYY-MM-DD):",
          "Monto pagado por la inversión:",
         ]
entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

entry_principal, entry_annual_interest_rate, entry_maturity_date, entry_first_interest_payment_date, entry_payment_frequency, entry_deferral_installments, entry_amortization_type, entry_capital_repayments_dates, entry_amount_paid = entries

tk.Button(root, text="Generar Amortización y SQL", command=generate_files).grid(row=len(labels), columnspan=2, pady=10)

root.mainloop()
