import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime, timedelta
import pymysql
from dateutil.relativedelta import relativedelta

def connect_to_database():
    database='inversiones'
    conn = pymysql.connect(host="localhost",user="root",passwd="",db=database)
    return conn

def generate_files():
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        investment_id = entry_investment_id.get()
        first_interest_payment_date = datetime.strptime(entry_first_interest_payment_date.get(), '%Y-%m-%d')
        payment_frequency = int(entry_payment_frequency.get() or 1)
        deferral_installments = int(entry_deferral_installments.get() or 0)
        amortization_type = entry_amortization_type.get()
        amortization_type = amortization_type.capitalize()
        try:
            capital_repayments_dates = [datetime.strptime(d.strip(), '%Y-%m-%d') for d in entry_capital_repayments_dates.get().split(',')]
        except:
            capital_repayments_dates = []

        sql="SELECT * FROM inversion WHERE id = %s"
        valores=(investment_id)
        cursor.execute(sql, valores)
        values = cursor.fetchone()
        columns = [i[0] for i in cursor.description]
        investment = pd.DataFrame([values], columns=columns)
        principal = investment['inv_valor_nominal'][0]
        first_installment_date = investment['inv_fecha_emision'][0] + relativedelta(months=payment_frequency)
        maturity_date = investment['inv_fecha_vencimiento'][0]
        annual_interest_rate = investment['inv_tasa_interes'][0]
        amount_paid = investment['inv_capital_invertido'][0]-investment['inv_valor_interes'][0]

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
            current_date = current_date.date()
        
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
        
        amortization_table["ID"] = investment_id
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
        
        sql="SELECT * FROM amortizacion WHERE inv_id = %s"
        valores=(investment_id)
        cursor.execute(sql, valores)
        values = cursor.fetchall()
        
        if(len(values)>0):
            raise Exception(f"Ya existe una tabla de amortización para la inversión {investment_id} en la base de datos.") 
        else:
            for _, row in final_table.iterrows():
                if row['Fecha de Pago'] >= first_interest_payment_date.date():
                    sql="INSERT INTO amortizacion (inv_id, am_fecha_pago, am_interes, am_capital, am_descuento, am_devuelto, am_retention, am_fecha_venta, am_pagada, is_active, is_deleted) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    valores=(row['ID'], row['Fecha de Pago'], row['Interés Mensual'], row['Capital de retorno'], row['Premio'], row['Capital Devuelto'], 0, '0000-00-00', 0, 1, 0)
                    cursor.execute(sql, valores)
                    conn.commit()
                    
            messagebox.showinfo("Éxito", "Tabla generada en la base de datos.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

root = tk.Tk()
root.title("Generador de Tabla de Amortización")

labels = ["ID:",
          "Primera fecha de pago (YYYY-MM-DD):", 
          "Frecuencia de pago:",
          "Cantidad de cuotas a diferir:",
          "Amortización francesa (f) o alemana (a):",
          "Fechas de retorno de capital (separadas por comas YYYY-MM-DD):",
         ]
entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

entry_investment_id, entry_first_interest_payment_date, entry_payment_frequency, entry_deferral_installments, entry_amortization_type, entry_capital_repayments_dates = entries

tk.Button(root, text="Generar Amortización y SQL", command=generate_files).grid(row=len(labels), columnspan=2, pady=10)

root.mainloop()
