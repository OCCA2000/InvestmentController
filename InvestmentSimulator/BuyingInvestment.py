import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime, timedelta

def generate_files():
    try:
        investment_id = entry_investment_id.get()
        owner = entry_owner.get()
        investment_type = entry_investment_type.get()  # Nuevo campo
        investment_enterprise = entry_investment_enterprise.get()  # Nuevo campo
        yield_value = float(entry_yield_value.get())
        principal = float(entry_principal.get())
        purchase_date = datetime.strptime(entry_purchase_date.get(), '%Y-%m-%d')
        maturity_date = datetime.strptime(entry_maturity_date.get(), '%Y-%m-%d')
        annual_interest_rate = float(entry_annual_interest_rate.get())
        capital_repayments_dates = [datetime.strptime(d.strip(), '%Y-%m-%d') for d in entry_capital_repayments_dates.get().split(',')]
        amount_paid = float(entry_amount_paid.get())
        first_interest_payment_date = datetime.strptime(entry_first_interest_payment_date.get(), '%Y-%m-%d')
        
        num_capital_repayments = len(capital_repayments_dates)
        payment_dates = []
        interest_payments = []
        principal_remaining = []
        principal_returned = []
        monthly_interest_rate = annual_interest_rate / 100 / 12
        
        current_date = first_interest_payment_date
        while current_date <= maturity_date:
            payment_dates.append(current_date)
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year if current_date.month < 12 else current_date.year + 1
            current_date = datetime(next_year, next_month, maturity_date.day)
        
        remaining_principal = principal
        repayment_amount = principal / num_capital_repayments
        for date in payment_dates:
            interest_payment = remaining_principal * monthly_interest_rate
            interest_payments.append(round(interest_payment, 2))
            principal_returned.append(0)
            if date in capital_repayments_dates:
                remaining_principal -= repayment_amount
            principal_remaining.append(round(remaining_principal, 2))
        
        amortization_table = pd.DataFrame({
            "Fecha de Pago": payment_dates,
            "Principal Restante": principal_remaining,
            "Interés Mensual": interest_payments,
            "Principal Devuelto": principal_returned
        })
        
        amortization_table["ID"] = investment_id
        amortization_table["Propietario"] = owner
        amortization_table["Tipo de Inversión"] = investment_type  # Nuevo campo agregado
        amortization_table["Empresa de Inversión"] = investment_enterprise  # Nuevo campo agregado
        amortization_table["Rendimiento"] = yield_value
        amortization_table["Fecha de Compra"] = purchase_date.strftime('%Y-%m-%d')
        amortization_table["Fecha de Vencimiento"] = maturity_date.strftime('%Y-%m-%d')
        amortization_table["Tasa nominal de interés anual"] = annual_interest_rate
        
        amortization_table["Fecha de Pago"] = amortization_table["Fecha de Pago"].dt.strftime('%Y-%m-%d')
        amortization_table = amortization_table.sort_values(by=["Fecha de Pago"]).drop_duplicates()
        
        # Add additional rows based on amount paid
        additional_principal_value = round(amount_paid / num_capital_repayments, 2)
        additional_interest_value = round((principal - amount_paid) / num_capital_repayments, 2)
        additional_rows = pd.DataFrame({
            "ID": [investment_id] * num_capital_repayments,
            "Fecha de Compra": [purchase_date.strftime('%Y-%m-%d')] * num_capital_repayments,
            "Propietario": [owner] * num_capital_repayments,
            "Rendimiento": [yield_value] * num_capital_repayments,
            "Fecha de Pago": [date.strftime('%Y-%m-%d') for date in capital_repayments_dates],
            "Fecha de Vencimiento": [maturity_date.strftime('%Y-%m-%d')] * num_capital_repayments,
            "Tasa nominal de interés anual": [annual_interest_rate] * num_capital_repayments,
            "Principal Restante": [additional_principal_value] * num_capital_repayments,
            "Interés Mensual": [additional_interest_value] * num_capital_repayments,
            "Principal Devuelto": [additional_principal_value] * num_capital_repayments
        })
        
        # Concatenate tables and sort by Fecha de Pago
        final_table = pd.concat([amortization_table, additional_rows], ignore_index=True)
        final_table = final_table.sort_values(by=["Fecha de Pago"])
        
        file_path_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path_excel:
            final_table.to_excel(file_path_excel, index=False, float_format="%.2f")
            messagebox.showinfo("Éxito", f"Archivo Excel guardado en: {file_path_excel}")
        
        file_path_sql = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
        if file_path_sql:
            sql_statements = []
            for _, row in final_table.iterrows():
                sql_statements.append(f"INSERT INTO amortization (inv_id, am_purchase_date, am_expiration_date, am_owner, am_enterprise, am_months, am_days, am_rate, am_return, am_interest, am_principal, am_retention, am_interest_total, am_sold_date, am_expired, is_active, is_deleted) VALUES ({row['ID']}, '{row['Fecha de Compra']}', '{row['Fecha de Pago']}', '{row['Propietario']}', 'BONOS DEL ESTADO {row['Fecha de Vencimiento']}', 0, 0, {round(row['Tasa nominal de interés anual'], 2)}, {round(row['Rendimiento'], 2)}, {round(row['Interés Mensual'], 2)}, {round(row['Principal Devuelto'], 2)}, 0, {round(row['Interés Mensual'], 2)}, NULL, 0, 0, 0);\n")
            sql_statements.append(f"update amortization set is_active = 1 where am_expiration_date between curdate() and LAST_DAY(DATE_ADD(NOW(), INTERVAL 11 MONTH)) and inv_id = {row['ID']};\n")
            with open(file_path_sql, "w") as sql_file:
                sql_file.writelines(sql_statements)
            messagebox.showinfo("Éxito", f"Archivo SQL guardado en: {file_path_sql}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Creación de la interfaz con Tkinter
root = tk.Tk()
root.title("Generador de Tabla de Amortización")

labels = [
    "Investment ID:", 
    "Owner:", 
    "Purchase Date (YYYY-MM-DD):", 
    "First Interest Payment Date (YYYY-MM-DD):",
    "Issue Date (YYYY-MM-DD):",
    "Maturity Date (YYYY-MM-DD):", 
    "Annual Interest Rate:", 
    "Actual Interest Rate:", 
    "Yield Value:", 
    "Monthly interest",
    "First month's interest",
    "Principal:",     
    "Purchased price",
    "Net Purchased price",
    "Value without commission",
    "Amount Paid:",
    "Amount Paid with interest:",
    "Previous interest:",
    "Brokerage Commission",
    "Stock exchange commission",
    "Total commision",
    "SEB code",
    "BCE code",
    "Liquidation",
    "Investment Type:", 
    "Investment Enterprise:",
    "Capital Repayment Dates (comma-separated YYYY-MM-DD):", 
]

entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries.append(entry)

(
    entry_investment_id, 
    entry_owner, 
    entry_purchase_date, 
    entry_first_interest_payment_date,
    entry_issue_date, 
    entry_maturity_date, 
    entry_annual_interest_rate, 
    entry_actual_interest_rate, 
    entry_yield_value, 
    entry_monthly_interest, 
    entry_first_month_interest,
    entry_principal, 
    entry_purchased_price,
    entry_net_purchased_price,
    entry_value_without_commission,
    entry_amount_paid,
    entry_amount_paid_with_interest,    
    entry_previous_interest,
    entry_brokerage_commission,
    entry_stock_exchange_commission,
    entry_total_commission,
    entry_SEB_code,
    entry_BCE_code,
    entry_liquidation,
    entry_investment_type, 
    entry_investment_enterprise, 
    entry_capital_repayments_dates, 

) = entries

# Botón para generar la amortización y el archivo SQL
#tk.Button(root, text="Generar Amortización y SQL", command=generate_files).grid(row=len(labels), columnspan=2, pady=10)
tk.Button(root, text="Generar Amortización y SQL", command=generate_files).grid(row=len(labels), column=0, padx=5, pady=10)



# Nuevo botón agregado para "Generar Registro Inversión" (Aún sin funcionalidad)
def generate_investment_record():
    try:
        # Obtener valores de la pantalla
        investment_type = entry_investment_type.get()
        purchase_date = entry_purchase_date.get()
        maturity_date = entry_maturity_date.get()
        owner = entry_owner.get()
        investment_enterprise = entry_investment_enterprise.get()
        annual_interest_rate = float(entry_annual_interest_rate.get())
        yield_value = float(entry_yield_value.get())
        amount_paid = float(entry_amount_paid.get())

        # Construir la sentencia SQL
        sql_statement = f"""INSERT INTO investment
(
`inv_type`,
`inv_purchase_date`,
`inv_expiration_date`,
`inv_owner`,
`inv_enterprise`,
`inv_months`,
`inv_days`,
`inv_rate`,
`inv_return`,
`inv_principal`,
`inv_retention`,
`inv_received`,
`inv_sold_date`,
`inv_expired`,
`inv_paid`,
`is_active`,
`is_deleted`
)
VALUES
(
'{investment_type}',
'{purchase_date}',
'{maturity_date}',
'{owner}',
'{investment_enterprise}',
0.00,
0.00,
{annual_interest_rate},
{yield_value},
{amount_paid},
0.00,
0.00,
NULL,
0,
0,
1,
0
);"""

        # Pedir la ubicación para guardar el archivo SQL
        file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")], initialfile="InsertInvestment.sql")
        if file_path:
            with open(file_path, "w") as file:
                file.write(sql_statement)
            messagebox.showinfo("Éxito", f"Archivo SQL guardado en: {file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")
# Botón para generar el registro de inversión
#tk.Button(root, text="Generar Registro Inversión", command=generate_investment_record).grid(row=len(labels) + 1, columnspan=2, pady=10)
tk.Button(root, text="Generar Registro Inversión", command=generate_investment_record).grid(row=len(labels), column=1, padx=5, pady=10)




# Nuevo botón agregado para "Generar Registro Bonos" (Aún sin funcionalidad)
def generate_Bonds_record():
    try:
        # Obtener valores de la pantalla
        propietario = entry_owner.get()
        fecha_compra = entry_purchase_date.get()
        fecha_primer_pago = entry_first_interest_payment_date.get()
        fecha_emision = entry_issue_date.get()
        fecha_vencimiento = entry_maturity_date.get()
        tasa_mensual = float(entry_annual_interest_rate.get())
        tasa_mensual_real = float(entry_actual_interest_rate.get())
        rendimiento = float(entry_yield_value.get())
        interes_mensual = float(entry_monthly_interest.get())
        interes_primer_mes = float(entry_first_month_interest.get())
        valor_nominal = float(entry_principal.get())
        precio_comprado = float(entry_purchased_price.get())
        precio_neto_comprado = float(entry_net_purchased_price.get())
        valor_sin_comision = float(entry_value_without_commission.get())
        valor_con_comision = float(entry_amount_paid.get())
        pagado = float(entry_amount_paid_with_interest.get())
        interes_acumulado_previo = float(entry_previous_interest.get())
        comision_casa = float(entry_brokerage_commission.get())
        comision_bolsa = float(entry_stock_exchange_commission.get())
        total_comisiones = float(entry_total_commission.get())
        codigo_SEB = entry_SEB_code.get()
        codigo_BCE = entry_BCE_code.get()
        liquidacion = entry_liquidation.get()

        # Construcción de la sentencia SQL
        sql_statement = f"""INSERT INTO `bonos`
(
`propietario`,
`fechaCompra`,
`fechaPrimerPago`,
`fechaEmision`,
`fechaVencimiento`,
`tasaMensual`,
`tasaMensualReal`,
`rendimiento`,
`interesMensual`,
`interesPrimerMes`,
`valorNominal`,
`precioComprado`,
`precioNetoComprado`,
`valorSinComision`,
`valorConComision`,
`pagado`,
`interesAcumuladoPrevio`,
`comisionCasa`,
`comisionBolsa`,
`totalComisiones`,
`codigoSEB`,
`codigoBCE`,
`liquidacion`,
`is_active`,
`is_deleted`
)
VALUES
(
'{propietario}',
'{fecha_compra}',
'{fecha_primer_pago}',
'{fecha_emision}',
'{fecha_vencimiento}',
{tasa_mensual},
{tasa_mensual_real},
{rendimiento},
{interes_mensual},
{interes_primer_mes},
{valor_nominal},
{precio_comprado},
{precio_neto_comprado},
{valor_sin_comision},
{valor_con_comision},
{pagado},
{interes_acumulado_previo},
{comision_casa},
{comision_bolsa},
{total_comisiones},
'{codigo_SEB}',
'{codigo_BCE}',
'{liquidacion}',
1,
0
);"""

        # Pedir la ubicación para guardar el archivo SQL
        file_path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")], initialfile="InsertBond.sql")
        if file_path:
            with open(file_path, "w") as file:
                file.write(sql_statement)
            messagebox.showinfo("Éxito", f"Archivo SQL guardado en: {file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# Botón para generar el registro de bono
#tk.Button(root, text="Generar Registro Bono", command=generate_Bonds_record).grid(row=len(labels) + 2, columnspan=2, pady=10)
tk.Button(root, text="Generar Registro Bono", command=generate_Bonds_record).grid(row=len(labels), column=2, padx=5, pady=10)



root.mainloop()
