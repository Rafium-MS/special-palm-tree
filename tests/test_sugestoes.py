from modules.sugestoes import gerar_sugestoes_automaticas, listar_sugestoes

# Gerar automaticamente
novas = gerar_sugestoes_automaticas(dias_limite=90)
print("Sugestões geradas:")
for s in novas:
    print(s)

# Listar todas
for linha in listar_sugestoes():
    print(linha)
