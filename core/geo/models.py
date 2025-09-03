"""Geographic hierarchy models: Regiao -> Reino/Imperio -> Cidade/Aldeia."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

SettlementType = Literal["Cidade", "Aldeia"]
RealmType = Literal["Reino", "Imperio"]


class Settlement(BaseModel):
    """Representa uma cidade ou aldeia."""

    name: str
    tipo: SettlementType = "Cidade"
    population: int = Field(default=0, ge=0)


class Realm(BaseModel):
    """Reino ou Império dentro de uma região."""

    name: str
    tipo: RealmType = "Reino"
    capital: Optional[str] = None
    settlements: List[Settlement] = Field(default_factory=list)

    def add_settlement(self, settlement: Settlement) -> None:
        self.settlements.append(settlement)


class Region(BaseModel):
    """Conjunto de reinos/impérios."""

    name: str
    realms: List[Realm] = Field(default_factory=list)

    def add_realm(self, realm: Realm) -> None:
        self.realms.append(realm)

    @property
    def settlements(self) -> List[Settlement]:
        """Convenience access to all settlements in the region."""
        return [s for realm in self.realms for s in realm.settlements]
