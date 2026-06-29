"""Modelos de dados do Focus Flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ObjetoVisual:
    """Representa um objeto colecionável (planta, cristal, etc.) que evolui com XP."""

    tipo: str
    nome: str
    nivel: int = 1
    xp: int = 0
    xp_para_proximo_nivel: int = 50
    criado_em: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def adicionar_experiencia(self, quantidade: int) -> bool:
        """Adiciona XP ao objeto. Retorna True se o objeto subiu de nível."""
        self.xp += quantidade
        evoluiu = False
        while self.xp >= self.xp_para_proximo_nivel:
            self.xp -= self.xp_para_proximo_nivel
            self.nivel += 1
            self.xp_para_proximo_nivel = int(self.xp_para_proximo_nivel * 1.4)
            evoluiu = True
        return evoluiu

    def progresso_percentual(self) -> float:
        return round((self.xp / self.xp_para_proximo_nivel) * 100, 1)

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "nome": self.nome,
            "nivel": self.nivel,
            "xp": self.xp,
            "xp_para_proximo_nivel": self.xp_para_proximo_nivel,
            "criado_em": self.criado_em,
        }

    @staticmethod
    def from_dict(dados: dict) -> "ObjetoVisual":
        return ObjetoVisual(
            tipo=dados["tipo"],
            nome=dados["nome"],
            nivel=dados.get("nivel", 1),
            xp=dados.get("xp", 0),
            xp_para_proximo_nivel=dados.get("xp_para_proximo_nivel", 50),
            criado_em=dados.get("criado_em", ""),
        )


# Sementes (tipos de objetos colecionáveis) disponíveis no jogo.
SEMENTES_PADRAO = {
    "basica": {
        "nome": "Árvore da Produtividade",
        "preco": 0,
        "desbloqueada": True,
        "raridade": "comum",
        "descricao": "Cresce com cada sessão de foco.",
        "xp_por_sessao": 10,
        "cor": "#4caf50",
    },
    "cristal": {
        "nome": "Cristal de Quartzo",
        "preco": 50,
        "desbloqueada": False,
        "raridade": "raro",
        "descricao": "Brilha com foco constante.",
        "xp_por_sessao": 15,
        "cor": "#42a5f5",
    },
    "cidade": {
        "nome": "Mini Metrópole",
        "preco": 120,
        "desbloqueada": False,
        "raridade": "épico",
        "descricao": "Uma cidade que cresce com sua produtividade.",
        "xp_por_sessao": 20,
        "cor": "#ab47bc",
    },
    "oceano": {
        "nome": "Recife de Coral",
        "preco": 220,
        "desbloqueada": False,
        "raridade": "lendário",
        "descricao": "Vida marinha que floresce com seu trabalho.",
        "xp_por_sessao": 25,
        "cor": "#26c6da",
    },
    "cosmos": {
        "nome": "Nebulosa Estelar",
        "preco": 350,
        "desbloqueada": False,
        "raridade": "mítico",
        "descricao": "Universo em expansão baseado em seu foco.",
        "xp_por_sessao": 30,
        "cor": "#ffa726",
    },
}


# Desafios diários simples, avaliados a partir das estatísticas do dia.
DESAFIOS_DIARIOS = {
    "primeira_sessao": {
        "nome": "Primeiro Passo",
        "descricao": "Complete 1 sessão de foco hoje.",
        "meta": 1,
        "recompensa": {"xp": 20, "gemas": 10},
    },
    "tres_sessoes": {
        "nome": "Em Ritmo",
        "descricao": "Complete 3 sessões de foco hoje.",
        "meta": 3,
        "recompensa": {"xp": 50, "gemas": 25},
    },
    "cinco_sessoes": {
        "nome": "Imparável",
        "descricao": "Complete 5 sessões de foco hoje.",
        "meta": 5,
        "recompensa": {"xp": 100, "gemas": 50},
    },
}
