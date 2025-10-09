import tkinter as tk
from tkinter import ttk, messagebox
import math

# ---------------------------
# Funções de cálculo por fórmula
# ---------------------------

# ----- M/M/1 -----
def mm1_rho(lambd, mu):
    return lambd / mu

def mm1_p0(lambd, mu):
    rho = mm1_rho(lambd, mu)
    return 1 - rho

def mm1_pn(lambd, mu, n):
    rho = mm1_rho(lambd, mu)
    p0 = mm1_p0(lambd, mu)
    return p0 * (rho ** n)

def mm1_L(lambd, mu):
    rho = mm1_rho(lambd, mu)
    return rho / (1 - rho)

def mm1_Lq(lambd, mu):
    rho = mm1_rho(lambd, mu)
    return (rho ** 2) / (1 - rho)

def mm1_W(lambd, mu):
    return 1.0 / (mu - lambd)

def mm1_Wq(lambd, mu):
    rho = mm1_rho(lambd, mu)
    return rho / (mu - lambd)

# ----- M/M/c -----
def mmc_rho_per_server(lambd, mu, c):
    return (lambd / mu) / c  # a/c where a = lambda/mu

def mmc_p0(lambd, mu, c):
    a = lambd / mu
    rho_s = mmc_rho_per_server(lambd, mu, c)
    # sum_{n=0}^{c-1} a^n / n!
    soma = sum((a ** n) / math.factorial(n) for n in range(c))
    last = (a ** c) / (math.factorial(c) * (1 - rho_s))
    return 1.0 / (soma + last)

def mmc_erlangC(lambd, mu, c):
    a = lambd / mu
    rho_s = mmc_rho_per_server(lambd, mu, c)
    p0 = mmc_p0(lambd, mu, c)
    numer = (a ** c) / (math.factorial(c) * (1 - rho_s))
    return numer * p0

def mmc_Lq(lambd, mu, c):
    a = lambd / mu
    rho_s = mmc_rho_per_server(lambd, mu, c)
    p0 = mmc_p0(lambd, mu, c)
    numer = (a ** c) * rho_s
    denom = math.factorial(c) * ((1 - rho_s) ** 2)
    return (numer / denom) * p0

def mmc_Ls(lambd, mu, c):
    a = lambd / mu
    return mmc_Lq(lambd, mu, c) + a

def mmc_Wq(lambd, mu, c):
    return mmc_Lq(lambd, mu, c) / lambd

def mmc_Ws(lambd, mu, c):
    return mmc_Wq(lambd, mu, c) + 1.0 / mu

# ----- M/M/∞ -----
def mminf_L(lambd, mu):
    return lambd / mu

def mminf_W(lambd, mu):
    return 1.0 / mu

def mminf_pn(lambd, mu, n):
    a = lambd / mu
    return math.exp(-a) * (a ** n) / math.factorial(n)

# ----- M/M/1/K -----
def mm1k_p0(lambd, mu, k):
    rho = lambd / mu
    if abs(rho - 1.0) < 1e-12:
        return 1.0 / (k + 1)
    else:
        return (1 - rho) / (1 - rho ** (k + 1))

def mm1k_pn(lambd, mu, k, n):
    p0 = mm1k_p0(lambd, mu, k)
    rho = lambd / mu
    return p0 * (rho ** n)

def mm1k_L(lambd, mu, k):
    rho = lambd / mu
    p0 = mm1k_p0(lambd, mu, k)
    # calcular L por soma direta (seguro para K não gigantesco)
    L = 0.0
    for n in range(k + 1):
        pn = p0 * (rho ** n)
        L += n * pn
    return L

def mm1k_Lq(lambd, mu, k):
    L = mm1k_L(lambd, mu, k)
    p0 = mm1k_p0(lambd, mu, k)
    # Lq = L - (1 - p0)  porque a média em serviço = 1 - p0? cuidado:
    # melhor calcular diretamente: Lq = sum_{n=0}^K (n - 1_{n>0}) * Pn where n>0 => n-1 = queue size when one in service
    # mais simples: Lq = sum_{n=0}^K max(0, n-1) * Pn
    Lq = 0.0
    for n in range(k + 1):
        pn = p0 * (rho ** n)
        qsize = max(0, n - 1)
        Lq += qsize * pn
    return Lq

def mm1k_effective_lambda(lambd, mu, k):
    # taxa efetiva de chegada = lambda * (1 - P_K)
    pk = mm1k_pn(lambd, mu, k, k)
    return lambd * (1 - pk)

def mm1k_W(lambd, mu, k):
    le = mm1k_L(lambd, mu, k)
    lam_eff = mm1k_effective_lambda(lambd, mu, k)
    if lam_eff <= 0:
        return float('inf')
    return le / lam_eff

def mm1k_Wq(lambd, mu, k):
    w = mm1k_W(lambd, mu, k)
    return w - 1.0 / mu

# ---------------------------
# Mapeamento de modelos -> fórmulas (com parâmetros necessários)
# ---------------------------
# cada entrada: (label_formula, [params_keys], function_reference)
# params_keys usam as chaves: 'lambda','mu','c','k','n'
MODELS = {
    "M/M/1": [
        ("Utilização (ρ)", ["lambda", "mu"], lambda a,b: mm1_rho(a,b)),
        ("P0 (sistema vazio)", ["lambda", "mu"], lambda a,b: mm1_p0(a,b)),
        ("Pn (prob. de n clientes)", ["lambda", "mu", "n"], lambda a,b,n: mm1_pn(a,b,int(n))),
        ("L - Nº médio no sistema", ["lambda", "mu"], lambda a,b: mm1_L(a,b)),
        ("Lq - Nº médio na fila", ["lambda", "mu"], lambda a,b: mm1_Lq(a,b)),
        ("W - Tempo médio no sistema", ["lambda", "mu"], lambda a,b: mm1_W(a,b)),
        ("Wq - Tempo médio na fila", ["lambda", "mu"], lambda a,b: mm1_Wq(a,b)),
    ],
    "M/M/c": [
        ("ρ por servidor (a/c)", ["lambda", "mu", "c"], lambda a,b,c: mmc_rho_per_server(a,b,int(c))),
        ("P0 (sistema vazio)", ["lambda", "mu", "c"], lambda a,b,c: mmc_p0(a,b,int(c))),
        ("Erlang C (prob. de esperar)", ["lambda", "mu", "c"], lambda a,b,c: mmc_erlangC(a,b,int(c))),
        ("Lq - Nº médio na fila", ["lambda", "mu", "c"], lambda a,b,c: mmc_Lq(a,b,int(c))),
        ("Ls - Nº médio no sistema", ["lambda", "mu", "c"], lambda a,b,c: mmc_Ls(a,b,int(c))),
        ("Wq - Tempo médio na fila", ["lambda", "mu", "c"], lambda a,b,c: mmc_Wq(a,b,int(c))),
        ("Ws - Tempo médio no sistema", ["lambda", "mu", "c"], lambda a,b,c: mmc_Ws(a,b,int(c))),
    ],
    "M/M/∞": [
        ("Ls - Nº médio no sistema", ["lambda", "mu"], lambda a,b: mminf_L(a,b)),
        ("Ws - Tempo médio no sistema", ["lambda", "mu"], lambda a,b: mminf_W(a,b)),
        ("Pn (Poisson)", ["lambda", "mu", "n"], lambda a,b,n: mminf_pn(a,b,int(n))),
    ],
    "M/M/1/K": [
        ("P0 (sistema vazio)", ["lambda", "mu", "k"], lambda a,b,k: mm1k_p0(a,b,int(k))),
        ("Pn (prob. de n clientes)", ["lambda", "mu", "k", "n"], lambda a,b,k,n: mm1k_pn(a,b,int(k),int(n))),
        ("L - Nº médio no sistema", ["lambda", "mu", "k"], lambda a,b,k: mm1k_L(a,b,int(k))),
        ("Lq - Nº médio na fila", ["lambda", "mu", "k"], lambda a,b,k: mm1k_Lq(a,b,int(k))),
        ("W - Tempo médio no sistema (Little)", ["lambda", "mu", "k"], lambda a,b,k: mm1k_W(a,b,int(k))),
        ("Wq - Tempo médio na fila", ["lambda", "mu", "k"], lambda a,b,k: mm1k_Wq(a,b,int(k))),
    ]
}

# Rótulos amigáveis para os parâmetros
PARAM_LABELS = {
    "lambda": "Taxa de chegada (λ):",
    "mu": "Taxa de serviço (μ):",
    "c": "Número de servidores (c):",
    "k": "Capacidade total (K):",
    "n": "n (inteiro) :"
}

# ---------------------------
# UI
# ---------------------------
root = tk.Tk()
root.title("Calculadora dinâmica - Teoria das Filas")
root.geometry("520x420")
root.resizable(False, False)

tk.Label(root, text="Selecione o modelo de fila:", font=("Arial", 11, "bold")).pack(pady=(10, 4))
combo_modelo = ttk.Combobox(root, values=list(MODELS.keys()), state="readonly", width=20)
combo_modelo.pack()
combo_modelo.set('M/M/1')

tk.Label(root, text="Selecione a fórmula desejada:", font=("Arial", 10, "bold")).pack(pady=(10,4))
combo_formula = ttk.Combobox(root, values=[], state="readonly", width=50)
combo_formula.pack()

frame_parametros = tk.LabelFrame(root, text="Parâmetros", padx=10, pady=10)
frame_parametros.pack(padx=10, pady=10, fill="x")

# dicionário de entries por key param
entries = {}

# --- Substitua a partir daqui até antes do root.mainloop() ---

def limpar_parametros_display():
    for w in frame_parametros.winfo_children():
        w.destroy()
    entries.clear()

def popular_formulas(event=None):
    modelo = combo_modelo.get()
    formulas = MODELS.get(modelo, [])
    labels = [f[0] for f in formulas]
    combo_formula['values'] = labels
    combo_formula.set('')  # limpa seleção anterior
    limpar_parametros_display()

def mostrar_campos_para_formula(event=None):
    limpar_parametros_display()
    modelo = combo_modelo.get()
    formula_label = combo_formula.get()
    if not formula_label:
        return
    # encontrar descrição da fórmula
    formula_list = MODELS.get(modelo, [])
    found = None
    for lbl, params, func in formula_list:
        if lbl == formula_label:
            found = (params, func)
            break
    if not found:
        return
    params, func = found
    # criar campos conforme params
    row = 0
    for p in params:
        lab = PARAM_LABELS.get(p, p)
        tk.Label(frame_parametros, text=lab).grid(row=row, column=0, sticky="w")
        e = tk.Entry(frame_parametros)
        e.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        entries[p] = e
        row += 1
    # espaço para resultado
    tk.Label(frame_parametros, text="Resultado:").grid(row=row, column=0, sticky="nw", pady=(8,0))
    txt_result = tk.Text(frame_parametros, height=6, width=45)
    txt_result.grid(row=row, column=1, pady=(8,0))
    entries['_result_widget'] = txt_result

def calcular_clicked():
    modelo = combo_modelo.get()
    formula_label = combo_formula.get()
    if not modelo or not formula_label:
        messagebox.showwarning("Atenção", "Escolha o modelo e a fórmula primeiro.")
        return
    # encontrar função e params
    formula_list = MODELS.get(modelo, [])
    found = None
    for lbl, params, func in formula_list:
        if lbl == formula_label:
            found = (params, func)
            break
    if not found:
        messagebox.showerror("Erro", "Fórmula não encontrada.")
        return
    params, func = found
    # ler inputs
    try:
        args = []
        for p in params:
            raw = entries.get(p)
            if raw is None:
                raise ValueError(f"Parâmetro {p} não encontrado na interface.")
            val = raw.get().strip()
            if val == "":
                raise ValueError("Preencha todos os parâmetros.")
            if p in ("c", "k", "n"):
                iv = int(float(val))
                if iv < 0:
                    raise ValueError("Parâmetros inteiros devem ser não-negativos.")
                args.append(iv)
            else:
                fv = float(val)
                if fv <= 0:
                    raise ValueError("As taxas devem ser maiores que 0.")
                args.append(fv)
        # validações simples
        if modelo == "M/M/1" and args[0] >= args[1]:
            raise ValueError("λ deve ser menor que μ para estabilidade.")
        if modelo == "M/M/c" and args[2] > 0:
            rho_server = (args[0] / args[1]) / args[2]
            if rho_server >= 1:
                raise ValueError("λ/(c·μ) deve ser < 1 para estabilidade.")

        # calcular
        result = func(*args)
        txt_widget = entries.get('_result_widget')
        if txt_widget:
            txt_widget.config(state='normal')
            txt_widget.delete("1.0", tk.END)
            if isinstance(result, float):
                if math.isinf(result):
                    txt_widget.insert(tk.END, "Resultado: infinito\n")
                else:
                    txt_widget.insert(tk.END, f"Resultado: {result:.6g}\n")
            else:
                txt_widget.insert(tk.END, f"Resultado: {result}\n")
            txt_widget.config(state='disabled')
        else:
            messagebox.showinfo("Resultado", str(result))
    except Exception as ex:
        messagebox.showerror("Erro", f"Erro ao calcular: {ex}")

# ---- Interface final de botões ----
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=6)
btn_calc = tk.Button(frame_buttons, text="Calcular", command=calcular_clicked, bg="#4CAF50", fg="white")
btn_calc.grid(row=0, column=0, padx=6)

# ---- Ligações automáticas ----
combo_modelo.bind("<<ComboboxSelected>>", popular_formulas)
combo_formula.bind("<<ComboboxSelected>>", mostrar_campos_para_formula)

# Preenche automaticamente o modelo inicial
popular_formulas()

root.mainloop()
