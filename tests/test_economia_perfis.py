from dataclasses import dataclass, field

from core.economia.perfis import apply_rules


@dataclass
class FakeLocalidade:
    nome: str
    tipo: str = "cidade"
    bioma: str = "planície"
    clima: str = "temperado"
    recursos: list[str] = field(default_factory=list)


def test_apply_rules_porto_adiciona_rota():
    loc = FakeLocalidade(nome="Porto Azul", tipo="porto")
    perfil = apply_rules(loc)
    assert "Rota aquática padrão" in perfil.rotas


def test_apply_rules_tags_herdam_recursos():
    loc = FakeLocalidade(nome="Vila", bioma="montanha", recursos=["ferro"])
    perfil = apply_rules(loc)
    assert "minérios" in perfil.recursos
    # Recursos originais devem permanecer
    assert "ferro" in perfil.recursos
