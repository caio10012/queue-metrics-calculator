import tkinter as tk
from tkinter import messagebox

def calcular_metricas():
    try:
        taxa_chegada = float(entry_lambda.get())
        taxa_servico = float(entry_mu.get())
        if taxa_servico <= taxa_chegada or taxa_chegada <= 0 or taxa_servico <= 0:
            raise ValueError

        # Métricas do modelo M/M/1
        rho = taxa_chegada / taxa_servico             # Utilização
        lq = (rho ** 2) / (1 - rho)                  # Número médio na fila
        wq = rho / (taxa_servico * (1 - rho))        # Tempo médio na fila
        ls = rho / (1 - rho)                         # Número médio no sistema
        ws = 1 / (taxa_servico - taxa_chegada)       # Tempo médio no sistema

        resultado = (
            f"Utilização (ρ): {rho:.2f}\n"
            f"Nº médio na fila (Lq): {lq:.2f}\n"
            f"Tempo médio na fila (Wq): {wq:.2f}\n"
            f"Nº médio no sistema (Ls): {ls:.2f}\n"
            f"Tempo médio no sistema (Ws): {ws:.2f}"
        )
        messagebox.showinfo("Resultados", resultado)
    except:
        messagebox.showerror("Erro", "Informe valores válidos: taxa de serviço deve ser maior que taxa de chegada.")

# Interface Tkinter
root = tk.Tk()
root.title("Calculadora Teoria das Filas M/M/1")

tk.Label(root, text="Taxa de chegada (λ):").grid(row=0, column=0)
tk.Label(root, text="Taxa de serviço (μ):").grid(row=1, column=0)
entry_lambda = tk.Entry(root)
entry_mu = tk.Entry(root)
entry_lambda.grid(row=0, column=1)
entry_mu.grid(row=1, column=1)

btn_calcular = tk.Button(root, text="Calcular Métricas", command=calcular_metricas)
btn_calcular.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
