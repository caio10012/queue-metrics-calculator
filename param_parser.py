# Este é o NOVO arquivo: param_parser.py
# (Versão 2.7 - Corrigido o bug que confundia 'atendente' com 'atendimento')

import re
from tkinter import messagebox

# Mapeia todas as possíveis entradas do usuário (incluindo símbolos)
# para as chaves de sistema que o seu programa usa.
KEY_MAP = {
    'lambda': 'lambda', 'λ': 'lambda', 'taxa de chegada': 'lambda', 'taxa_chegada': 'lambda',
    'lambd': 'lambd', 
    'mu': 'mu', 'μ': 'mu', 'taxa de servico': 'mu', 'taxa_servico': 'mu',
    'c': 'c', 'servidores': 'c', 'atendentes': 'c', 'barbeiro': 'c', 'caixa': 'c',
    'k': 'k', 'capacidade': 'k',
    'n': 'n',
}

# --- PADRÕES DE REGEX (CORRIGIDOS E ROBUSTOS) ---
# ([\d\.,]+) é o grupo que captura o número
# [^0-9\n]* -> Pega qualquer texto que NÃO seja um número ou quebra de linha
PARAM_REGEX_PATTERNS = [
    # 1. Busca por Lambda (chegada)
    # Procura (chegada OU chegam) ... (texto que não é número) ... (o número)
    ('lambda', re.compile(r"(?:taxa de chegada|chegam)(?:[^0-9\n]*)([\d\.,]+)", re.IGNORECASE)),
    ('lambda', re.compile(r"(?:lambda|λ)\s*[=:]\s*([\d\.,]+)", re.IGNORECASE)),
    
    # 2. Busca por Mu (atendimento)
    # --- ESTA É A LINHA CORRIGIDA ---
    # Procura (atende OU taxa de atendimento OU taxa de serviço) ... (texto que não é número) ... (o número)
    ('mu', re.compile(r"(?:atende|taxa de atendimento|taxa de serviço)(?:[^0-9\n]*)([\d\.,]+)", re.IGNORECASE)),
    ('mu', re.compile(r"(?:mu|μ)\s*[=:]\s*([\d\.,]+)", re.IGNORECASE)),
    
    # 3. Busca por C (servidores, plural)
    ('c', re.compile(r"([\d\.,]+)\s+(?:atendentes|servidores|caixas|barbeiros)", re.IGNORECASE)),
    ('c', re.compile(r"(?:c|servidores)\s*[=:]\s*([\d\.,]+)", re.IGNORECASE)),
    
    # 4. Busca por K (capacidade)
    ('k', re.compile(r"(?:capacidade|limite)\s+(?:de\s+)?([\d\.,]+)", re.IGNORECASE)),
    ('k', re.compile(r"k\s*[=:]\s*([\d\.,]+)", re.IGNORECASE)),
    
    # 5. Busca por N (valor de Pn)
    ('n', re.compile(r"n\s*[=:]\s*([\d\.,]+)", re.IGNORECASE)),
]

# Padrões que não têm números (como "um atendente")
FIXED_VALUE_PATTERNS = [
    ('c', re.compile(r"(?:um|um único|o)\s+(?:atendente|servidor|caixa|barbeiro|consultório)", re.IGNORECASE), '1')
]


def parse_param_file(filepath):
    """
    Lê um arquivo de texto simples, IGNORA LINHAS COMENTADAS, 
    extrai parâmetros por RegEx e retorna um dicionário com as chaves normalizadas.
    """
    parsed_data = {}
    try:
        active_text_lines = [] # Lista para guardar as linhas válidas
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line_stripped = line.strip()
                
                # Se a linha for vazia ou começar com #, pula ela
                if not line_stripped or line_stripped.startswith('#'):
                    continue
                
                # Se a linha for válida, adiciona ela (já em minúsculo e limpa)
                active_text_lines.append(line_stripped.lower())
        
        # Junta todas as linhas ativas com um ESPAÇO
        active_text = " ".join(active_text_lines)
        
        # Substitui o "espaço invisível" (non-breaking space) por um espaço normal
        active_text = active_text.replace(u'\xa0', ' ')
        
        # 1. Procura pelos padrões com números
        for key, pattern in PARAM_REGEX_PATTERNS:
            # Procura apenas se a chave ainda não foi encontrada
            if key not in parsed_data:
                match = pattern.search(active_text)
                if match:
                    # Pega o último grupo capturado (o número)
                    value = match.group(match.lastindex).replace(',', '.')
                    parsed_data[key] = value
                
        # 2. Procura por padrões com valor fixo (ex: c = 1)
        if 'c' not in parsed_data:
            for key, pattern, value in FIXED_VALUE_PATTERNS:
                if pattern.search(active_text):
                    parsed_data[key] = value

    except FileNotFoundError:
        messagebox.showerror("Erro", f"Arquivo não encontrado:\n{filepath}")
        return {}
    except Exception as e:
        messagebox.showerror("Erro ao Ler Arquivo", f"Não foi possível processar o arquivo:\n{e}")
        return {}
        
    return parsed_data