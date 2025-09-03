from __future__ import annotations

"""Perfis econômicos básicos e regras automáticas.

Este módulo define a estrutura ``EconomiaPerfil`` para representar
características econômicas simples de uma localidade e uma função
``apply_rules`` que preenche um perfil com base nas propriedades da
localidade.
"""

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass
class EconomiaPerfil:
    """Informações econômicas derivadas de uma localidade."""

    recursos: List[str] = field(default_factory=list)
    rotas: List[str] = field(default_factory=list)
    impostos: float = 0.0


def apply_rules(localidade: object) -> EconomiaPerfil:
    """Gerar ``EconomiaPerfil`` baseado nas características da localidade.

    A função procura por atributos com nomes comuns (``tipo``, ``bioma``,
    ``clima`` e ``recursos``). Apenas os atributos presentes são usados,
    permitindo que qualquer objeto *similar* à dataclass ``Localidade`` do
    módulo de UI seja fornecido.

    Regras simples:
    * Se ``localidade.tipo`` for ``"porto"`` (case‑insensitive), uma rota
      aquática padrão é adicionada.
    * ``bioma`` e ``clima`` são tratados como *tags* e podem disparar regras
      adicionais.
    * Todos os itens de ``localidade.recursos`` são copiados para o perfil.
    """

    perfil = EconomiaPerfil()

    # Copia recursos existentes, se houver.
    recursos: Iterable[str] | None = getattr(localidade, "recursos", None)
    if recursos:
        perfil.recursos.extend(list(recursos))

    # Imposto base simples.
    perfil.impostos = 5.0

    tipo = getattr(localidade, "tipo", "").lower()
    if tipo == "porto":
        perfil.rotas.append("Rota aquática padrão")

    # Regras extras baseadas em tags de bioma/clima.
    tags: List[str] = []
    for attr in ("bioma", "clima"):
        val = getattr(localidade, attr, None)
        if isinstance(val, str):
            tags.append(val.lower())

    for tag in tags:
        if tag == "litoral":
            perfil.rotas.append("Pesca costeira")
        elif tag == "montanha":
            perfil.recursos.append("minérios")
        elif tag == "deserto":
            perfil.impostos += 2.0

    return perfil
