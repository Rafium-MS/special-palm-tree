from modules.saidas import criar_saida, listar_saidas, atualizar_saida, remover_saida

# Criar uma saída
criar_saida("2025-08-01", "Grupo 1", "João da Silva", dirigente_fixo=True)

# Listar saídas
for saida in listar_saidas():
    print(saida)

# Atualizar
atualizar_saida(1, dirigente="Maria Oliveira")

# Remover
remover_saida(1)
