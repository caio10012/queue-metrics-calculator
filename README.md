# Calculadora de Métricas de Teoria das Filas

Este projeto é uma ferramenta interativa para calcular métricas de sistemas de filas, utilizando uma interface gráfica em Tkinter. Atualmente, suporta múltiplos modelos de filas, permitindo calcular diferentes métricas de forma dinâmica.

## Funcionalidades

- Seleção do modelo de fila entre as opções disponíveis (ex: M/M/1, M/M/c, M/D/1, etc.).
- Escolha da métrica/fórmula desejada (ex: Utilização, Número médio na fila, Tempo médio no sistema, etc.).
- Geração automática dos campos de entrada dos parâmetros necessários para a fórmula selecionada.
- Cálculo das métricas de forma segura, com validação de entradas e mensagens de erro para valores inválidos.
- Exibição do resultado na própria interface gráfica.
- Fácil expansão para outros modelos de filas e fórmulas adicionais.

## Como usar

1. Abra o programa.
2. Selecione o modelo de fila.
3. Escolha a fórmula/métrica que deseja calcular.
4. Preencha os parâmetros exigidos.
5. Clique em "Calcular" para obter o resultado.

## Requisitos

- Python 3.x
- Tkinter 

## Observações

- Para gerar um executável standalone no Windows, utilize o PyInstaller:

```bash
python -m pip install pyinstaller
python -m PyInstaller --onefile --noconsole Teste.py
