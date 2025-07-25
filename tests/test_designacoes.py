from modules.designacoes import criar_designacao, listar_designacoes, atualizar_designacao, remover_designacao

# Criar
criar_designacao(territorio_id=2, saida_id=5, data_inicio="2025-08-01", data_fim="2025-08-30")

# Listar
for d in listar_designacoes():
    print(d)

# Atualizar
atualizar_designacao(1, status="concluída")

# Remover
remover_designacao(1)
