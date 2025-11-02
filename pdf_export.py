# Este é o NOVO arquivo: pdf_export.py
# (Versão Corrigida: Bug do 'Title', Alinhamento da Tabela, e Seção de Ajuda Removida)

import math
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from tkinter import messagebox # Usado para o erro

# A função _build_help_story() foi REMOVIDA, como solicitado.

def create_results_pdf(filename, model_name, params_data, results_data):
    """
    Cria e salva um PDF com os resultados da calculadora.
    
    :param filename: O caminho completo para salvar o PDF.
    :param model_name: O nome do modelo (ex: "M/M/1").
    :param params_data: Uma lista de tuplas [('Parâmetro', 'Valor'), ...].
    :param results_data: Uma lista de tuplas [('Métrica', 'Valor'), ...].
    """
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4,
                                rightMargin=inch/2, leftMargin=inch/2,
                                topMargin=inch/2, bottomMargin=inch/2)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- CORREÇÃO 1: Bug do 'Title' ---
        # 'Title' já existe, então vamos modificá-lo
        styles['Title'].alignment = TA_CENTER
        styles['Title'].fontSize = 16
        styles['Title'].spaceAfter = 14
        
        styles.add(ParagraphStyle(name='SectionHeader', 
                                  parent=styles['h2'], 
                                  fontSize=12,
                                  spaceAfter=6))
        
        # (Os outros estilos de Def, Comment, Formula foram removidos pois não são mais usados)
        
        # Tabela (Cabeçalho de Parâmetros)
        params_header = [("Parâmetro de Entrada", "Valor Fornecido")]
        params_full_data = params_header + params_data
        
        # Tabela (Cabeçalho de Resultados)
        if model_name == "Comparativo (M/M/1 vs M/M/∞)":
            results_header = [("Métrica", "M/M/1", "M/M/∞")]
        else:
             results_header = [("Métrica", "Valor")]
        results_full_data = results_header + results_data

        # --- CORREÇÃO 2: Estilo da Tabela (Alinhamento) ---
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4682B4")), # Azul Aço
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F0F8FF")), # AliceBlue
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alinhamento Geral (Centralizado)
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            
            # Alinhamento Específico (Sobrescreve a regra acima)
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),      # Coluna 1 (Métrica) alinhada à ESQUERDA
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinha tudo ao meio verticalmente
            ('LEFTPADDING', (0, 1), (0, -1), 6),    # Adiciona um espaço na esquerda da Coluna 1
            
            # Fontes
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica')
        ])
        
        # --- Construção do Documento ---
        story.append(Paragraph(f"Relatório de Teoria das Filas: {model_name}", styles['Title']))

        # Tabela de Parâmetros
        story.append(Paragraph("Parâmetros de Entrada", styles['SectionHeader']))
        params_table = Table(params_full_data, colWidths=[doc.width/2.0]*2)
        params_table.setStyle(table_style) # Usa o mesmo estilo corrigido
        story.append(params_table)
        story.append(Spacer(1, 0.25*inch))

        # Tabela de Resultados
        story.append(Paragraph("Resultados das Métricas", styles['SectionHeader']))
        
        # --- CORREÇÃO 3: Bug do 'list assignment index out of range' ---
        # (Corrigido para calcular o número de colunas corretamente)
        
        num_cols = len(results_header[0]) # Pega o número de colunas (ex: 2 ou 3)
        
        if num_cols == 2:
            # Modelo padrão (2 colunas)
            col_widths = [doc.width * 0.6, doc.width * 0.4] # Coluna 1 = 60%, Coluna 2 = 40%
        elif num_cols == 3:
            # Modelo comparativo (3 colunas)
            col_widths = [doc.width * 0.5, doc.width * 0.25, doc.width * 0.25] # 50%, 25%, 25%
        else:
            # Caso de 1 coluna (não deve acontecer, mas é seguro)
            col_widths = [doc.width]
                
        results_table = Table(results_full_data, colWidths=col_widths)
        results_table.setStyle(table_style)
        story.append(results_table)

        # A seção de ajuda de fórmulas foi REMOVIDA, como solicitado.
        # (A chamada 'story.extend(help_story)' não existe mais)

        # Salva o PDF
        doc.build(story)
        return True
    
    except Exception as e:
        messagebox.showerror("Erro ao Gerar PDF", f"Não foi possível criar o PDF: {e}")
        return False