from modules.territorios import adicionar_territorio, listar_territorios, atualizar_territorio, remover_territorio, buscar_por_nome

# Criar
adicionar_territorio("Território 123", url="http://exemplo.com/t123")

# Listar
for t in listar_territorios():
    print(t)

# Atualizar
atualizar_territorio(1, status="designado", observacoes="Entregue ao Grupo 1")

# Buscar
resultados = buscar_por_nome("123")
for r in resultados:
    print(r)

# Remover
remover_territorio(1)
