from modules.relatorios import gerar_relatorio_mensal, exportar_relatorio_excel, relatorio_por_territorio

# Relatório mensal (visualização em terminal)
df = gerar_relatorio_mensal(mes=8, ano=2025)
print(df)

# Exportar para Excel
exportar_relatorio_excel(mes=8, ano=2025)

# Histórico por território específico
df2 = relatorio_por_territorio(territorio_id=3)
print(df2)
