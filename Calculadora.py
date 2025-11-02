import ttkbootstrap as tb
from ttkbootstrap.constants import *
import math
import json 
import ast  
from tkinter import messagebox, Toplevel, Text, Scrollbar, Listbox

# -------------------------------------------------------------------
# Funções de Cálculo (Lógica Matemática - Inalterada)
# ... (Todo o seu bloco de funções de mm1_rho a mm1k_Wq) ...
# ----- M/M/1 -----
def mm1_rho(lambd, mu):
    return lambd / mu
def mm1_p0(lambd, mu):
    return 1 - (lambd / mu)
def mm1_pn(lambd, mu, n):
    rho = lambd / mu
    return (1 - rho) * (rho ** n)
def mm1_L(lambd, mu):
    rho = lambd / mu
    return rho / (1 - rho)
def mm1_Lq(lambd, mu):
    rho = lambd / mu
    return (rho ** 2) / (1 - rho)
def mm1_W(lambd, mu):
    return 1.0 / (mu - lambd)
def mm1_Wq(lambd, mu):
    rho = lambd / mu
    return rho / (mu - lambd)

# ----- M/M/c -----
def mmc_rho(lambd, mu, c):
    return lambd / (c * mu)
def mmc_p0(lambd, mu, c):
    a = lambd / mu
    rho_s = mmc_rho(lambd, mu, c)
    if rho_s >= 1: return 0.0
    sum_part = sum((a ** n) / math.factorial(n) for n in range(c))
    last_part = (a ** c) / (math.factorial(c) * (1 - rho_s))
    return 1.0 / (sum_part + last_part)
def mmc_erlangC(lambd, mu, c):
    a = lambd / mu
    rho_s = mmc_rho(lambd, mu, c)
    if rho_s >= 1: return 1.0
    p0 = mmc_p0(lambd, mu, c)
    numerator = (a ** c) / (math.factorial(c) * (1 - rho_s))
    return numerator * p0
def mmc_Lq(lambd, mu, c):
    a = lambd / mu
    rho_s = mmc_rho(lambd, mu, c)
    if rho_s >= 1: return float('inf')
    p0 = mmc_p0(lambd, mu, c)
    numerator = (a ** c) * rho_s
    denominator = math.factorial(c) * ((1 - rho_s) ** 2)
    return (numerator / denominator) * p0
def mmc_L(lambd, mu, c):
    lq = mmc_Lq(lambd, mu, c)
    return lq + (lambd / mu)
def mmc_Wq(lambd, mu, c):
    lq = mmc_Lq(lambd, mu, c)
    return lq / lambd if lambd > 0 else float('inf')
def mmc_W(lambd, mu, c):
    wq = mmc_Wq(lambd, mu, c)
    return wq + (1.0 / mu)

# ----- M/M/∞ -----
def mminf_rho(lambd, mu):
    return lambd / mu
def mminf_p0(lambd, mu):
    a = lambd / mu
    return math.exp(-a)
def mminf_pn(lambd, mu, n):
    a = lambd / mu
    return math.exp(-a) * (a ** n) / math.factorial(n)
def mminf_L(lambd, mu):
    return lambd / mu
def mminf_W(lambd, mu):
    return 1.0 / mu

# ----- M/M/1/K -----
def mm1k_rho(lambd, mu):
    return lambd / mu
def mm1k_p0(lambd, mu, k):
    rho = lambd / mu
    if abs(rho - 1.0) < 1e-9:
        return 1.0 / (k + 1)
    else:
        return (1 - rho) / (1 - rho ** (k + 1))
def mm1k_pn(lambd, mu, k, n):
    if n > k: return 0.0
    rho = lambd / mu
    p0 = mm1k_p0(lambd, mu, k)
    return p0 * (rho ** n)
def mm1k_pk(lambd, mu, k):
    return mm1k_pn(lambd, mu, k, k)
def mm1k_lambda_eff(lambd, mu, k):
    pk = mm1k_pk(lambd, mu, k)
    return lambd * (1 - pk)
def mm1k_L(lambd, mu, k):
    rho = lambd / mu
    if abs(rho - 1.0) < 1e-9:
        return k / 2.0
    term1 = (1 - (k + 1) * (rho ** k) + k * (rho ** (k + 1)))
    term2 = (1 - rho) * (1 - rho ** (k + 1))
    return rho * (term1 / term2)
def mm1k_Lq(lambd, mu, k):
    L = mm1k_L(lambd, mu, k)
    p0 = mm1k_p0(lambd, mu, k)
    return L - (1 - p0)
def mm1k_W(lambd, mu, k):
    L = mm1k_L(lambd, mu, k)
    lambda_eff = mm1k_lambda_eff(lambd, mu, k)
    return L / lambda_eff if lambda_eff > 0 else float('inf')
def mm1k_Wq(lambd, mu, k):
    Lq = mm1k_Lq(lambd, mu, k)
    lambda_eff = mm1k_lambda_eff(lambd, mu, k)
    return Lq / lambda_eff if lambda_eff > 0 else float('inf')
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Gerenciamento de Fórmulas Customizadas
# -------------------------------------------------------------------
CUSTOM_FORMULAS_FILE = "custom_formulas.json"
ALLOWED_MATH = [
    'log', 'log10', 'exp', 'sqrt', 'pow', 'factorial', 
    'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 
    'pi', 'e'
]
ALLOWED_PARAMS = ['lambd', 'mu', 'c', 'k', 'n']

def load_custom_formulas():
    try:
        with open(CUSTOM_FORMULAS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_custom_formulas(formulas):
    try:
        with open(CUSTOM_FORMULAS_FILE, 'w') as f:
            json.dump(formulas, f, indent=4)
    except IOError as e:
        messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar as fórmulas: {e}")

# -------------------------------------------------------------------
# Textos de Ajuda (Parâmetros)
# -------------------------------------------------------------------
PARAM_HELP_TEXT = {
    "lambda": "Definição: Taxa de Chegada (λ)\n\n"
              "É a frequência média com que os clientes chegam ao sistema (ex: clientes por hora).\n\n"
              "* Exemplo: Se chegam 10 clientes por hora, λ = 10.",
    "lambd":  "Definição: Taxa de Chegada (λ) [Nome: lambd]\n\n"
              "É a frequência média com que os clientes chegam ao sistema (ex: clientes por hora).\n\n"
              "* Exemplo: Se chegam 10 clientes por hora, λ = 10.\n"
              "* IMPORTANTE: Nas fórmulas personalizadas, use o nome 'lambd' (sem o 'a').",
    "mu":     "Definição: Taxa de Serviço (μ)\n\n"
              "É a capacidade média de atendimento de UM ÚNICO servidor (ex: clientes por hora).\n\n"
              "* Exemplo: Se um servidor atende 12 clientes por hora, μ = 12.",
    "c":      "Definição: Número de Servidores (c)\n\n"
              "É o número total de servidores idênticos disponíveis para atender os clientes.\n\n"
              "* Exemplo: Em um banco com 5 caixas, c = 5.",
    "k":      "Definição: Capacidade do Sistema (K)\n\n"
              "É o número máximo de clientes permitidos no sistema (fila + em atendimento).\n\n"
              "* Exemplo: Se K = 10, o 11º cliente é rejeitado (perdido).",
    "n":      "Definição: Número de Clientes (n)\n\n"
              "Um valor inteiro usado para calcular P(n): a probabilidade de haver *exatamente* 'n' clientes no sistema em um dado momento.\n\n"
              "* Exemplo: Se n = 5, você calculará P(5)."
}

# -------------------------------------------------------------------
# Configuração dos Modelos
# -------------------------------------------------------------------
MODELS_CONFIG = {
    "M/M/1": {
        "params": {"lambda": "Taxa de Chegada (λ)", "mu": "Taxa de Serviço (μ)"},
        "optional_params": {"n": "Valor de n para P(n)"},
        "functions": [
            ("ρ (Utilização)", mm1_rho, ["lambda", "mu"]),
            ("P₀ (Prob. sistema vazio)", mm1_p0, ["lambda", "mu"]),
            ("P(n) (Prob. de n clientes)", mm1_pn, ["lambda", "mu", "n"]),
            ("L (Nº médio no sistema)", mm1_L, ["lambda", "mu"]),
            ("Lq (Nº médio na fila)", mm1_Lq, ["lambda", "mu"]),
            ("W (Tempo médio no sistema)", mm1_W, ["lambda", "mu"]),
            ("Wq (Tempo médio na fila)", mm1_Wq, ["lambda", "mu"]),
        ]
    },
    "M/M/c": {
        "params": {"lambda": "Taxa de Chegada (λ)", "mu": "Taxa de Serviço (μ)", "c": "Nº de Servidores (c)"},
        "optional_params": {},
        "functions": [
            ("ρ (Utilização por servidor)", mmc_rho, ["lambda", "mu", "c"]),
            ("P₀ (Prob. sistema vazio)", mmc_p0, ["lambda", "mu", "c"]),
            ("C(c, a) (Prob. de esperar / Erlang C)", mmc_erlangC, ["lambda", "mu", "c"]),
            ("L (Nº médio no sistema)", mmc_L, ["lambda", "mu", "c"]),
            ("Lq (Nº médio na fila)", mmc_Lq, ["lambda", "mu", "c"]),
            ("W (Tempo médio no sistema)", mmc_W, ["lambda", "mu", "c"]),
            ("Wq (Tempo médio na fila)", mmc_Wq, ["lambda", "mu", "c"]),
        ]
    },
    "M/M/∞": {
        "params": {"lambda": "Taxa de Chegada (λ)", "mu": "Taxa de Serviço (μ)"},
        "optional_params": {"n": "Valor de n para P(n)"},
        "functions": [
            ("a = λ/μ (Intensidade de tráfego)", mminf_rho, ["lambda", "mu"]),
            ("P₀ (Prob. sistema vazio)", mminf_p0, ["lambda", "mu"]),
            ("P(n) (Prob. de n clientes)", mminf_pn, ["lambda", "mu", "n"]),
            ("L (Nº médio no sistema)", mminf_L, ["lambda", "mu"]),
            ("W (Tempo médio no sistema)", mminf_W, ["lambda", "mu"]),
        ]
    },
    "M/M/1/K": {
        "params": {"lambda": "Taxa de Chegada (λ)", "mu": "Taxa de Serviço (μ)", "k": "Capacidade do Sistema (K)"},
        "optional_params": {"n": "Valor de n para P(n)"},
        "functions": [
            ("ρ = λ/μ (Intensidade de tráfego)", mm1k_rho, ["lambda", "mu"]),
            ("P₀ (Prob. sistema vazio)", mm1k_p0, ["lambda", "mu", "k"]),
            ("Pₖ (Prob. de perda/bloqueio)", mm1k_pk, ["lambda", "mu", "k"]),
            ("P(n) (Prob. de n clientes)", mm1k_pn, ["lambda", "mu", "k", "n"]),
            ("λ' (Taxa de chegada efetiva)", mm1k_lambda_eff, ["lambda", "mu", "k"]),
            ("L (Nº médio no sistema)", mm1k_L, ["lambda", "mu", "k"]),
            ("Lq (Nº médio na fila)", mm1k_Lq, ["lambda", "mu", "k"]),
            ("W (Tempo médio no sistema)", mm1k_W, ["lambda", "mu", "k"]),
            ("Wq (Tempo médio na fila)", mm1k_Wq, ["lambda", "mu", "k"]),
        ]
    },
    "Comparativo (M/M/1 vs M/M/∞)": {
        "params": {"lambda": "Taxa de Chegada (λ)", "mu": "Taxa de Serviço (μ)"},
        "optional_params": {},
        "functions": [] 
    },
    "Personalizado": {
        "params": {}, 
        "optional_params": {
            "lambd": "Taxa de Chegada (λ)", 
            "mu": "Taxa de Serviço (μ)", 
            "c": "Nº de Servidores (c)",
            "k": "Capacidade (K)",
            "n": "Valor de n"
        },
        "functions": []
    }
}

# -------------------------------------------------------------------
# Classe para a Janela de Ajuda
# -------------------------------------------------------------------
class HelpWindow(Toplevel):
    def __init__(self, parent, title, text_content):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()

        if title == "Sobre os Modelos de Fila":
            self.geometry("550x650")
            self.resizable(False, False)
            frame = tb.Frame(self, padding=10)
            frame.pack(fill=BOTH, expand=True)

            text_frame = tb.Frame(frame) 
            text_frame.pack(fill=BOTH, expand=True)
            
            text_widget = Text(text_frame, wrap=WORD, font=("TkDefaultFont", 10), state=DISABLED, height=20, width=60)
            text_widget.pack(side=LEFT, fill=BOTH, expand=True)
            
            scrollbar = Scrollbar(text_frame, command=text_widget.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            text_widget.config(state=NORMAL)
            text_widget.insert(END, text_content)
            text_widget.config(state=DISABLED)
            
            close_button = tb.Button(frame, text="Fechar", command=self.destroy, bootstyle="secondary")
            close_button.pack(side=BOTTOM, pady=(10,0), fill=X, expand=False)
        else:
            self.geometry("450x250")
            self.resizable(False, False)
            frame = tb.Frame(self, padding=20)
            frame.pack(fill=BOTH, expand=True)
            
            help_label = tb.Label(frame, text=text_content, wraplength=400, justify=LEFT, font=("TkDefaultFont", 10))
            help_label.pack(fill=BOTH, expand=True, anchor="n")
            
            close_button = tb.Button(frame, text="Fechar", command=self.destroy, bootstyle="secondary")
            close_button.pack(side=BOTTOM, pady=(10,0), fill=X, expand=False)
        
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (win_width // 2)
        y = parent_y + (parent_height // 2) - (win_height // 2)
        self.geometry(f'+{x}+{y}')
        self.wait_window(self)

# -------------------------------------------------------------------
# Classe para Adicionar Fórmulas
# -------------------------------------------------------------------
class AddFormulaWindow(Toplevel):
    def __init__(self, app_instance):
        self.app = app_instance 
        parent = app_instance.root
        
        super().__init__(parent)
        self.title("Adicionar Nova Fórmula Personalizada")
        self.geometry("500x350")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        
        frame = tb.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)
        frame.columnconfigure(1, weight=1)

        tb.Label(frame, text="Nome da Métrica:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = tb.Entry(frame, bootstyle="primary")
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        tb.Label(frame, text="Parâmetros:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_params = tb.Entry(frame, bootstyle="primary")
        self.entry_params.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        tb.Label(frame, text="Separados por vírgula (ex: lambd, mu)", bootstyle="secondary").grid(row=2, column=1, sticky="w", padx=5)

        tb.Label(frame, text="Expressão:").grid(row=3, column=0, sticky="nw", pady=5)
        self.entry_expr = tb.Entry(frame, bootstyle="primary")
        self.entry_expr.grid(row=3, column=1, sticky="ew", padx=5, pady=15)
        
        example_text = "Ex: (lambd / mu) / (1 - (lambd / mu))"
        tb.Label(frame, text=example_text, bootstyle="secondary", wraplength=300).grid(row=4, column=1, sticky="w", padx=5)

        save_button = tb.Button(frame, text="Validar e Salvar", command=self._save_formula, bootstyle="success")
        save_button.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(20, 0))

        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (win_width // 2)
        y = parent_y + (parent_height // 2) - (win_height // 2)
        self.geometry(f'+{x}+{y}')
        self.wait_window(self)

    # --- FUNÇÃO DE VALIDAÇÃO CORRIGIDA ---
    def _validate_expression(self, expression, param_list):
        """Valida a expressão matemática usando AST."""
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Erro de sintaxe na expressão: {e}")

        allowed_names = set(param_list) | set(ALLOWED_MATH)
        
        # CORREÇÃO: Removido 'ast.Num'
        allowed_nodes = {
            ast.Expression, ast.Call, ast.Name, ast.Load,
            ast.BinOp, ast.UnaryOp, ast.Compare,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
            ast.USub, ast.UAdd,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
            ast.Constant # 'ast.Num' foi removido
        }

        for node in ast.walk(tree):
            if type(node) not in allowed_nodes:
                raise ValueError(f"Operação não permitida: {type(node).__name__}")
            
            if isinstance(node, ast.Name):
                if node.id not in allowed_names:
                    raise ValueError(f"Nome não permitido: '{node.id}'")
            
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in allowed_names:
                    raise ValueError(f"Função não permitida: '{getattr(node.func, 'id', 'N/A')}'")
        return True


    def _save_formula(self):
        name = self.entry_name.get().strip()
        params_str = self.entry_params.get().strip()
        expr = self.entry_expr.get().strip()

        if not name or not expr:
            messagebox.showerror("Erro", "Nome e Expressão são obrigatórios.", parent=self)
            return

        existing_names = [f["label"] for f in self.app.custom_formulas]
        if name in existing_names:
            messagebox.showerror("Erro", f"Uma fórmula com o nome '{name}' já existe.", parent=self)
            return

        params_list = [p.strip() for p in params_str.split(',') if p.strip()]
        
        for p in params_list:
            if p not in ALLOWED_PARAMS:
                messagebox.showerror("Erro", f"Parâmetro não permitido: '{p}'.\nPermitidos: {', '.join(ALLOWED_PARAMS)}", parent=self)
                return

        try:
            self._validate_expression(expr, params_list)
        except ValueError as e:
            messagebox.showerror("Erro de Validação", f"Expressão inválida: {e}", parent=self)
            return
            
        new_formula = {
            "label": name,
            "params": params_list,
            "expr": expr
        }
        
        self.app.custom_formulas.append(new_formula)
        save_custom_formulas(self.app.custom_formulas)
        
        messagebox.showinfo("Sucesso", f"Fórmula '{name}' salva com sucesso!", parent=self)
        self.destroy()
        
        self.app._on_model_selected()

# -------------------------------------------------------------------
# Classe para Gerenciar Fórmulas
# -------------------------------------------------------------------
class ManageFormulasWindow(Toplevel):
    def __init__(self, app_instance):
        self.app = app_instance
        parent = app_instance.root
        
        super().__init__(parent)
        self.title("Gerenciar Fórmulas Personalizadas")
        self.geometry("450x300")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, True)
        
        frame = tb.Frame(self, padding=10)
        frame.pack(fill=BOTH, expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        list_frame = tb.Frame(frame)
        list_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.listbox = Listbox(list_frame, font=("TkDefaultFont", 10), height=10)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self._populate_list()
        
        delete_button = tb.Button(frame, text="Deletar Selecionada", command=self._delete_formula, bootstyle="danger")
        delete_button.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        
        close_button = tb.Button(frame, text="Fechar", command=self._close_window, bootstyle="secondary-outline")
        close_button.grid(row=1, column=1, sticky="ew", pady=10, padx=5)

        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        win_width = self.winfo_width()
        win_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (win_width // 2)
        y = parent_y + (parent_height // 2) - (win_height // 2)
        self.geometry(f'+{x}+{y}')

        self.protocol("WM_DELETE_WINDOW", self._close_window)
        
    def _close_window(self):
        self.app._on_model_selected()
        self.destroy()

    def _populate_list(self):
        self.listbox.delete(0, END)
        for formula in self.app.custom_formulas:
            self.listbox.insert(END, formula["label"])
            
    def _delete_formula(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma fórmula para deletar.", parent=self)
            return
            
        selected_index = selected_indices[0]
        selected_name = self.listbox.get(selected_index)
        
        if not messagebox.askyesno("Confirmar", f"Tem certeza que quer deletar a fórmula '{selected_name}'?", parent=self):
            return
            
        formula_to_remove = None
        for formula in self.app.custom_formulas:
            if formula["label"] == selected_name:
                formula_to_remove = formula
                break
        
        if formula_to_remove:
            self.app.custom_formulas.remove(formula_to_remove)
            save_custom_formulas(self.app.custom_formulas)
            self._populate_list()
            messagebox.showinfo("Sucesso", f"Fórmula '{selected_name}' deletada.", parent=self)
        else:
            messagebox.showerror("Erro", "Não foi possível encontrar a fórmula para deletar.", parent=self)

# -------------------------------------------------------------------
# Classe Principal da Aplicação
# -------------------------------------------------------------------
class QueueingCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Avançada de Teoria das Filas")
        self.root.minsize(700, 700) 
        
        self.param_widgets = {}
        self.custom_formulas = load_custom_formulas() 
        
        self._create_widgets()

    def _create_widgets(self):
        main_frame = tb.Frame(self.root, padding="15")
        main_frame.pack(fill=BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        input_frame = tb.Labelframe(main_frame, text="Configuração do Modelo", padding="15", bootstyle="primary")
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.columnconfigure(1, weight=1) 
        input_frame.columnconfigure(2, weight=0) 

        tb.Label(input_frame, text="Selecione o Modelo:").grid(row=0, column=0, sticky="w", pady=5, padx=(0,5))
        
        self.model_combo = tb.Combobox(input_frame, values=list(MODELS_CONFIG.keys()), state="readonly", bootstyle="primary", width=30)
        self.model_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)
        self.model_combo.set("M/M/1")

        model_help_button = tb.Button(input_frame, text="?", command=self._show_model_help, bootstyle="primary-outline", width=3)
        model_help_button.grid(row=0, column=2, sticky="e", padx=(5, 0))

        self.params_frame = tb.Frame(input_frame, padding="5")
        self.params_frame.grid(row=1, column=0, columnspan=3, sticky="ew") 
        self.params_frame.columnconfigure(1, weight=1) 
        self.params_frame.columnconfigure(0, weight=0) 
        self.params_frame.columnconfigure(2, weight=0) 
        
        tb.Separator(input_frame, bootstyle="secondary").grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        formula_btn_frame = tb.Frame(input_frame)
        formula_btn_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        formula_btn_frame.columnconfigure(0, weight=1)
        formula_btn_frame.columnconfigure(1, weight=1)
        self.add_formula_button = tb.Button(formula_btn_frame, text="Adicionar Nova Fórmula", command=self._open_add_formula_window, bootstyle="info")
        self.add_formula_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.manage_formula_button = tb.Button(formula_btn_frame, text="Gerenciar Fórmulas", command=self._open_manage_formulas_window, bootstyle="warning-outline")
        self.manage_formula_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        formula_btn_frame.grid_remove() 
        self.formula_btn_frame = formula_btn_frame 

        calc_button = tb.Button(input_frame, text="Calcular Todas as Métricas", command=self._calculate_metrics, bootstyle="success")
        calc_button.grid(row=4, column=0, columnspan=3, pady=(10, 5), sticky="ew")

        output_frame = tb.Labelframe(main_frame, text="Resultados", padding="15", bootstyle="info")
        output_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 5))
        output_frame.rowconfigure(0, weight=1) 
        output_frame.rowconfigure(1, weight=0)
        output_frame.rowconfigure(2, weight=0)
        output_frame.rowconfigure(3, weight=1)
        output_frame.columnconfigure(0, weight=1)
        
        tree_frame = tb.Frame(output_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.results_tree = tb.Treeview(tree_frame, columns=("Metric", "Value"), show="headings", bootstyle="info")
        scrollbar = tb.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview, bootstyle="round")
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        tb.Separator(output_frame, bootstyle="secondary").grid(row=1, column=0, sticky="ew", pady=(15, 5))
        
        tb.Label(output_frame, text="Definições e Fórmulas das Métricas:", bootstyle="inverse-info").grid(
            row=2, column=0, sticky="w", padx=5)
        
        help_text_frame = tb.Frame(output_frame)
        help_text_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=(5,0))
        help_text_frame.rowconfigure(0, weight=1)
        help_text_frame.columnconfigure(0, weight=1)

        self.metric_help_text = Text(
            help_text_frame, 
            wrap=WORD, 
            font=("TkDefaultFont", 10), 
            state=DISABLED,
            height=10 
        )
        self.metric_help_text.grid(row=0, column=0, sticky="nsew")
        help_scrollbar = Scrollbar(help_text_frame, command=self.metric_help_text.yview, orient="vertical")
        help_scrollbar.grid(row=0, column=1, sticky="ns")
        self.metric_help_text.config(yscrollcommand=help_scrollbar.set)
        
        self.metric_help_text.tag_configure("header", font=("TkDefaultFont", 11, "bold", "underline"), spacing1=5)
        self.metric_help_text.tag_configure("def", font=("TkDefaultFont", 10, "bold"), lmargin1=10, lmargin2=10, spacing1=5)
        self.metric_help_text.tag_configure("formula", font=("Courier", 10, "italic"), lmargin1=25, lmargin2=25, foreground="#00529B")
        self.metric_help_text.tag_configure("comment", font=("TkDefaultFont", 9, "italic"), lmargin1=25, lmargin2=25, foreground="#444444")
        
        self._on_model_selected()

    def _open_add_formula_window(self):
        AddFormulaWindow(self) 

    def _open_manage_formulas_window(self):
        ManageFormulasWindow(self)

    def _show_model_help(self):
        title = "Sobre os Modelos de Fila"
        help_text = (
            "Aqui está um guia rápido sobre as diferenças:\n\n"
            "--- M/M/1 ---\n"
            "O modelo mais clássico: 1 servidor, 1 fila infinita.\n"
            "* M: Chegadas de Poisson (taxa λ)\n"
            "* M: Serviço Exponencial (taxa μ)\n"
            "* 1: Um único servidor.\n"
            "* Ex: Um caixa de padaria, um lava-rápido.\n"
            "* Requer: λ < μ para ser estável.\n\n"
            "--- M/M/c ---\n"
            "Múltiplos servidores com uma única fila.\n"
            "* M/M: Chegadas de Poisson, serviço exponencial.\n"
            "* c: 'c' servidores idênticos.\n"
            "* Ex: Banco com vários caixas, central de telemarketing.\n"
            "* Requer: λ < (c * μ) para ser estável.\n\n"
            "--- M/M/∞ (Infinito) ---\n"
            "Modelo de autoatendimento (self-service).\n"
            "* M/M: Chegadas de Poisson, serviço exponencial.\n"
            "* ∞: Servidores infinitos. Ninguém nunca espera na fila.\n"
            "* Ex: Clientes acessando um site, um parque.\n"
            "* Estabilidade: Sempre estável.\n\n"
            "--- M/M/1/K (Capacidade Finita) ---\n"
            "Um servidor com uma sala de espera limitada.\n"
            "* M/M/1: Um servidor.\n"
            "* K: Capacidade máxima do sistema (fila + servidor).\n"
            "* Consequência: Se o sistema está cheio (K clientes), novas chegadas são REJEITADAS (perdidas).\n"
            "* Ex: Uma linha de suporte com 'K' vagas de espera.\n"
            "* Estabilidade: Sempre estável.\n\n"
            "--- Comparativo (M/M/1 vs M/M/∞) ---\n"
            "Uma ferramenta de análise (não um modelo padrão).\n"
            "* Objetivo: Compara o cenário de 1 servidor (M/M/1) contra um cenário ideal sem filas (M/M/∞) usando os mesmos λ e μ.\n"
            "* Utilidade: Mostra o impacto da restrição de servidores.\n\n"
            "--- Personalizado ---\n"
            "Permite que você crie e salve suas próprias fórmulas.\n"
            "* Use o botão 'Adicionar Nova Fórmula' para definir o nome, os parâmetros (lambd, μ, c, k, n) e a expressão matemática."
        )
        HelpWindow(self.root, title, help_text)

    def _show_param_help(self, param_key):
        """Exibe a ajuda correta para 'lambda' ou 'lambd'."""
        
        help_text = PARAM_HELP_TEXT.get(param_key)
        
        title = param_key # Fallback
        for config in MODELS_CONFIG.values():
            all_param_labels = {**config.get("params", {}), **config.get("optional_params", {})}
            if param_key in all_param_labels:
                title = all_param_labels[param_key]
                break
        
        if not help_text:
             help_text = "Nenhuma ajuda disponível para este parâmetro."

        HelpWindow(self.root, title, help_text)

    def _update_metric_help(self, model_key):
        """Preenche a caixa de texto de ajuda com definições e fórmulas formatadas."""
        
        w = self.metric_help_text
        w.config(state=NORMAL)
        w.delete("1.0", END)
        
        if model_key == "M/M/1":
            w.insert(END, "Definições (M/M/1)\n\n", "header")
            w.insert(END, "ρ (Utilização):\n", "def")
            w.insert(END, "  A fração de tempo que o servidor está ocupado.\n", "comment")
            w.insert(END, "  ρ = λ / μ\n\n", "formula")
            w.insert(END, "P₀ (Prob. sistema vazio):\n", "def")
            w.insert(END, "  Probabilidade de não haver ninguém no sistema.\n", "comment")
            w.insert(END, "  P₀ = 1 - ρ\n\n", "formula")
            w.insert(END, "P(n) (Prob. de n clientes):\n", "def")
            w.insert(END, "  Probabilidade de haver exatamente 'n' clientes.\n", "comment")
            w.insert(END, "  Pₙ = (1 - ρ) * ρⁿ\n\n", "formula")
            w.insert(END, "L (Nº médio no sistema):\n", "def")
            w.insert(END, "  Nº médio de clientes na fila + em atendimento.\n", "comment")
            w.insert(END, "  L = ρ / (1 - ρ)\n\n", "formula")
            w.insert(END, "Lq (Nº médio na fila):\n", "def")
            w.insert(END, "  Nº médio de clientes apenas na fila (esperando).\n", "comment")
            w.insert(END, "  Lq = ρ² / (1 - ρ)\n\n", "formula")
            w.insert(END, "W (Tempo médio no sistema):\n", "def")
            w.insert(END, "  Tempo médio na fila + em atendimento.\n", "comment")
            w.insert(END, "  W = 1 / (μ - λ)\n\n", "formula")
            w.insert(END, "Wq (Tempo médio na fila):\n", "def")
            w.insert(END, "  Tempo médio apenas na fila (esperando).\n", "comment")
            w.insert(END, "  Wq = ρ / (μ - λ)\n\n", "formula")

        elif model_key == "M/M/c":
            w.insert(END, "Definições (M/M/c)\n\n", "header")
            w.insert(END, "ρ (Utilização por servidor):\n", "def")
            w.insert(END, "  A utilização média de cada um dos 'c' servidores.\n", "comment")
            w.insert(END, "  ρ = λ / (c * μ)\n\n", "formula")
            w.insert(END, "a (Intensidade de Tráfego):\n", "def")
            w.insert(END, "  Usado nos cálculos de P₀. (a = λ / μ)\n", "comment")
            w.insert(END, "  a = λ / μ\n\n", "formula")
            w.insert(END, "P₀ (Prob. sistema vazio):\n", "def")
            w.insert(END, "  Probabilidade de todos os 'c' servidores estarem livres.\n", "comment")
            w.insert(END, "  P₀ = [ (Σ_{n=0}^{c-1} (aⁿ / n!)) + (aᶜ / (c! * (1-ρ))) ]⁻¹\n\n", "formula")
            w.insert(END, "C(c, a) (Erlang C - Prob. de esperar):\n", "def")
            w.insert(END, "  Probabilidade de um cliente ter que esperar na fila.\n", "comment")
            w.insert(END, "  C(c,a) = [ aᶜ / (c! * (1-ρ)) ] * P₀\n\n", "formula")
            w.insert(END, "Lq (Nº médio na fila):\n", "def")
            w.insert(END, "  Nº médio de clientes apenas na fila (esperando).\n", "comment")
            w.insert(END, "  Lq = [ (ρ * C(c,a)) / (1-ρ) ]\n\n", "formula")
            w.insert(END, "L (Nº médio no sistema):\n", "def")
            w.insert(END, "  Nº médio de clientes na fila + em atendimento.\n", "comment")
            w.insert(END, "  L = Lq + a\n\n", "formula")
            w.insert(END, "Wq (Tempo médio na fila):\n", "def")
            w.insert(END, "  Tempo médio apenas na fila (esperando).\n", "comment")
            w.insert(END, "  Wq = Lq / λ\n\n", "formula")
            w.insert(END, "W (Tempo médio no sistema):\n", "def")
            w.insert(END, "  Tempo médio na fila + em atendimento.\n", "comment")
            w.insert(END, "  W = Wq + (1 / μ)\n\n", "formula")

        elif model_key == "M/M/∞":
            w.insert(END, "Definições (M/M/∞)\n\n", "header")
            w.insert(END, "a (Intensidade de tráfego):\n", "def")
            w.insert(END, "  Representa o número médio de servidores ocupados.\n", "comment")
            w.insert(END, "  a = λ / μ\n\n", "formula")
            w.insert(END, "P₀ (Prob. sistema vazio):\n", "def")
            w.insert(END, "  Probabilidade de não haver ninguém no sistema.\n", "comment")
            w.insert(END, "  P₀ = e⁻ᵃ\n\n", "formula")
            w.insert(END, "P(n) (Prob. de n clientes):\n", "def")
            w.insert(END, "  Probabilidade de haver exatamente 'n' clientes.\n", "comment")
            w.insert(END, "  Pₙ = (e⁻ᵃ * aⁿ) / n!\n\n", "formula")
            w.insert(END, "L (Nº médio no sistema):\n", "def")
            w.insert(END, "  Nº médio de clientes no sistema (L = a).\n", "comment")
            w.insert(END, "  L = a\n\n", "formula")
            w.insert(END, "W (Tempo médio no sistema):\n", "def")
            w.insert(END, "  Tempo médio no sistema (W = 1/μ).\n", "comment")
            w.insert(END, "  W = 1 / μ\n\n", "formula")
            w.insert(END, "Lq e Wq (Fila):\n", "def")
            w.insert(END, "  Não há fila em um sistema M/M/∞.\n", "comment")
            w.insert(END, "  Lq = 0\n  Wq = 0\n", "formula")

        elif model_key == "M/M/1/K":
            w.insert(END, "Definições (M/M/1/K)\n\n", "header")
            w.insert(END, "ρ (Intensidade de tráfego):\n", "def")
            w.insert(END, "  Pode ser > 1, pois o sistema é finito.\n", "comment")
            w.insert(END, "  ρ = λ / μ\n\n", "formula")
            w.insert(END, "P₀ (Prob. sistema vazio):\n", "def")
            w.insert(END, "  Probabilidade de não haver ninguém no sistema.\n", "comment")
            w.insert(END, "  P₀ = (1 - ρ) / (1 - ρ⁽ᵏ⁺¹⁾)   (se ρ ≠ 1)\n", "formula")
            w.insert(END, "  P₀ = 1 / (k + 1)              (se ρ = 1)\n\n", "formula")
            w.insert(END, "P(n) (Prob. de n clientes):\n", "def")
            w.insert(END, "  Probabilidade de haver 'n' clientes (para n ≤ k).\n", "comment")
            w.insert(END, "  Pₙ = P₀ * ρⁿ\n\n", "formula")
            w.insert(END, "Pₖ (Prob. de perda/bloqueio):\n", "def")
            w.insert(END, "  Probabilidade do sistema estar cheio (k clientes).\n", "comment")
            w.insert(END, "  Pₖ = P₀ * ρᵏ\n\n", "formula")
            w.insert(END, "λ' (Taxa de chegada efetiva):\n", "def")
            w.insert(END, "  A taxa real de clientes que *entram* no sistema.\n", "comment")
            w.insert(END, "  λ' = λ * (1 - Pₖ)\n\n", "formula")
            w.insert(END, "L (Nº médio no sistema):\n", "def")
            w.insert(END, "  Nº médio de clientes na fila + em atendimento.\n", "comment")
            w.insert(END, "  L = Σ_{n=0}^{k} n * Pₙ\n\n", "formula")
            w.insert(END, "Lq (Nº médio na fila):\n", "def")
            w.insert(END, "  Nº médio de clientes apenas na fila (esperando).\n", "comment")
            w.insert(END, "  Lq = L - (1 - P₀)\n\n", "formula")
            w.insert(END, "W (Tempo médio no sistema):\n", "def")
            w.insert(END, "  Tempo médio (para clientes que entram).\n", "comment")
            w.insert(END, "  W = L / λ'\n\n", "formula")
            w.insert(END, "Wq (Tempo médio na fila):\n", "def")
            w.insert(END, "  Tempo médio na fila (para clientes que entram).\n", "comment")
            w.insert(END, "  Wq = Lq / λ'\n\n", "formula")

        elif model_key == "Comparativo (M/M/1 vs M/M/∞)":
            w.insert(END, "Definições (Comparativo)\n\n", "header")
            w.insert(END, "Esta tela compara dois cenários com a mesma carga (λ e μ):\n"
                         "* M/M/1 (Coluna 1): O que acontece com 1 servidor.\n"
                         "* M/M/∞ (Coluna 2): O cenário ideal (self-service), onde nenhum cliente espera na fila.\n\n"
                         "As fórmulas e definições são as mesmas dos modelos individuais.", "comment")

        elif model_key == "Personalizado":
            w.insert(END, "Definições (Personalizado)\n\n", "header")
            w.insert(END, "Esta seção exibe os resultados das suas fórmulas personalizadas.\n", "comment")
            w.insert(END, "* Use o botão 'Adicionar Nova Fórmula' para criar a sua.\n"
                         "* As fórmulas salvas aparecerão em " + CUSTOM_FORMULAS_FILE + "\n"
                         "* Parâmetros disponíveis: " + ", ".join(ALLOWED_PARAMS) + "\n"
                         "* Funções disponíveis: " + ", ".join(ALLOWED_MATH) + "\n", "comment")
        
        else:
            w.insert(END, "Selecione um modelo para ver as definições das métricas.", "comment")

        w.config(state=DISABLED)


    def _on_model_selected(self, event=None):
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.param_widgets.clear()
        
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        model_key = self.model_combo.get()
        config = MODELS_CONFIG.get(model_key, {})
        
        if model_key == "Personalizado":
            self.formula_btn_frame.grid()
        else:
            self.formula_btn_frame.grid_remove()

        if model_key == "Comparativo (M/M/1 vs M/M/∞)":
            self.results_tree.config(columns=("Metric", "MM1", "MMInf"))
            self.results_tree.heading("Metric", text="Métrica")
            self.results_tree.heading("MM1", text="M/M/1")
            self.results_tree.heading("MMInf", text="M/M/∞")
            self.results_tree.column("Metric", width=200, anchor="w")
            self.results_tree.column("MM1", anchor="center", width=150)
            self.results_tree.column("MMInf", anchor="center", width=150)
        else:
            self.results_tree.config(columns=("Metric", "Value"))
            self.results_tree.heading("Metric", text="Métrica")
            self.results_tree.heading("Value", text="Valor")
            self.results_tree.column("Metric", width=300, anchor="w")
            self.results_tree.column("Value", anchor="center", width=150)

        all_params = {**config.get("params", {}), **config.get("optional_params", {})}
        row = 0
        for key, label in all_params.items():
            tb.Label(self.params_frame, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
            
            entry = tb.Entry(self.params_frame)
            entry.grid(row=row, column=1, sticky="ew", pady=4, padx=5)
            self.param_widgets[key] = entry
            
            help_cmd = lambda k=key: self._show_param_help(k)
            help_btn = tb.Button(self.params_frame, text="?", command=help_cmd, bootstyle="info-outline", width=3)
            help_btn.grid(row=row, column=2, sticky="e", pady=4, padx=(0, 5))
            
            row += 1
        
        self._update_metric_help(model_key)


    def _run_comparison_calc(self, param_values):
        try:
            lambd = param_values.get("lambda")
            mu = param_values.get("mu")
            
            mm1_stable = True
            if lambd >= mu:
                mm1_stable = False
                messagebox.showwarning("Aviso de Estabilidade", 
                    f"M/M/1 é instável (λ >= μ). Os resultados para M/M/1 serão '∞' (Instável).")

            def format_val(val_mm1, val_mminf, stable):
                res_mm1 = f"{val_mm1:.6g}" if stable else "∞ (Instável)"
                res_mminf = f"{val_mminf:.6g}"
                return (res_mm1, res_mminf)

            rho_mm1 = mm1_rho(lambd, mu)
            rho_mminf = mminf_rho(lambd, mu)
            val1, val2 = format_val(rho_mm1, rho_mminf, mm1_stable)
            self.results_tree.insert("", "end", values=("ρ (Utilização/Intensidade)", val1, val2))
            
            l_mm1 = mm1_L(lambd, mu) if mm1_stable else float('inf')
            l_mminf = mminf_L(lambd, mu)
            val1, val2 = format_val(l_mm1, l_mminf, mm1_stable)
            self.results_tree.insert("", "end", values=("L (Nº médio no sistema)", val1, val2))
            
            lq_mm1 = mm1_Lq(lambd, mu) if mm1_stable else float('inf')
            lq_mminf = 0.0
            val1, val2 = format_val(lq_mm1, lq_mminf, mm1_stable)
            self.results_tree.insert("", "end", values=("Lq (Nº médio na fila)", val1, val2))
            
            w_mm1 = mm1_W(lambd, mu) if mm1_stable else float('inf')
            w_mminf = mminf_W(lambd, mu)
            val1, val2 = format_val(w_mm1, w_mminf, mm1_stable)
            self.results_tree.insert("", "end", values=("W (Tempo médio no sistema)", val1, val2))

            wq_mm1 = mm1_Wq(lambd, mu) if mm1_stable else float('inf')
            wq_mminf = 0.0
            val1, val2 = format_val(wq_mm1, wq_mminf, mm1_stable)
            self.results_tree.insert("", "end", values=("Wq (Tempo médio na fila)", val1, val2))
            
            p0_mm1 = mm1_p0(lambd, mu) if mm1_stable else 0.0
            p0_mminf = mminf_p0(lambd, mu)
            self.results_tree.insert("", "end", values=("P₀ (Prob. sistema vazio)", f"{p0_mm1:.6g}" if mm1_stable else "0.0", f"{p0_mminf:.6g}"))

        except Exception as e:
            messagebox.showerror("Erro no Cálculo Comparativo", str(e))

    def _run_standard_calc(self, config, param_values):
        """Executa os cálculos para os 4 modelos padrão."""
        for label, func, params_needed in config.get("functions", []):
            try:
                if not all(p in param_values for p in params_needed):
                    continue
                
                args = [param_values[p] for p in params_needed]
                result = func(*args)

                if isinstance(result, float):
                    if math.isinf(result): formatted_result = "∞ (Instável)"
                    elif math.isnan(result): formatted_result = "Indefinido (NaN)"
                    else: formatted_result = f"{result:.6g}"
                else: formatted_result = str(result)
                
                self.results_tree.insert("", "end", values=(label, formatted_result))
            
            except Exception as e:
                self.results_tree.insert("", "end", values=(label, f"Erro: {e}"))
                
    def _run_custom_calc(self, param_values):
        """Executa os cálculos para o modelo Personalizado."""
        
        safe_scope = {}
        for func_name in ALLOWED_MATH:
            if hasattr(math, func_name):
                safe_scope[func_name] = getattr(math, func_name)
        
        for key, value in param_values.items():
            safe_scope[key] = value

        for formula in self.custom_formulas:
            label = formula["label"]
            params_needed = formula["params"]
            expr = formula["expr"]
            
            try:
                if not all(p in param_values for p in params_needed):
                    formatted_result = "Parâmetros Faltando"
                else:
                    result = eval(expr, {"__builtins__": {}}, safe_scope)
                    
                    if isinstance(result, float):
                        if math.isinf(result): formatted_result = "∞ (Infinito)"
                        elif math.isnan(result): formatted_result = "Indefinido (NaN)"
                        else: formatted_result = f"{result:.6g}"
                    else: formatted_result = str(result)
                
                self.results_tree.insert("", "end", values=(label, formatted_result))
            
            except Exception as e:
                self.results_tree.insert("", "end", values=(label, f"Erro: {e}"))

    def _calculate_metrics(self):
        """Função principal de cálculo, agora dividida em 3 rotas."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        model_key = self.model_combo.get()
        config = MODELS_CONFIG.get(model_key, {})
        
        param_values = {}
        try:
            all_possible_params = {**config.get("params", {}), **config.get("optional_params", {})}
            
            for key in all_possible_params.keys():
                widget = self.param_widgets.get(key)
                if widget:
                    val_str = widget.get().strip()
                    if not val_str:
                        if key in config.get("params", {}):
                            raise ValueError(f"O parâmetro '{all_possible_params[key]}' é obrigatório.")
                        continue
                    
                    if key in ('c', 'k', 'n'):
                        param_values[key] = int(float(val_str))
                        if param_values[key] < 0: raise ValueError(f"Parâmetro '{key}' deve ser não-negativo.")
                    else:
                        param_values[key] = float(val_str)
                        if param_values[key] <= 0: raise ValueError(f"Taxa '{key}' deve ser positiva.")
        
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", str(e))
            return
            
        if model_key == "Personalizado":
            self._run_custom_calc(param_values)
        
        elif model_key == "Comparativo (M/M/1 vs M/M/∞)":
            if 'lambda' not in param_values or 'mu' not in param_values:
                 messagebox.showerror("Erro", "λ e μ são obrigatórios para a comparação.")
                 return
            self._run_comparison_calc(param_values)
        
        else:
            try:
                lambd, mu = param_values.get("lambda"), param_values.get("mu")
                if model_key == "M/M/1" and lambd >= mu:
                    raise ValueError("Condição de estabilidade violada: λ deve ser menor que μ.")
                if model_key == "M/M/c":
                    c = param_values.get("c", 1)
                    if lambd >= c * mu:
                        raise ValueError(f"Condição de estabilidade violada: λ deve ser menor que c * μ ({c * mu}).")
            except ValueError as e:
                messagebox.showwarning("Aviso de Estabilidade", str(e))
            except TypeError:
                pass 
            
            self._run_standard_calc(config, param_values)

if __name__ == "__main__":
    root = tb.Window(themename="litera") 
    app = QueueingCalculatorApp(root)
    root.mainloop()