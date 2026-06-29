"""Núcleo de regras de negócio do Focus Flow (sem nenhuma dependência de UI)."""

from __future__ import annotations

import copy
import json
import os
from datetime import datetime
from typing import Optional

from .models import DESAFIOS_DIARIOS, SEMENTES_PADRAO, ObjetoVisual

TEMPO_FOCO_PADRAO_MINUTOS = 25


class SistemaFocusFlow:
    """Mantém o estado do jogo (coleção, estatísticas, gemas, desafios) e a
    lógica de regras. Toda a persistência é feita em um único arquivo JSON.
    """

    def __init__(self, caminho_arquivo: str):
        self.caminho_arquivo = caminho_arquivo

        self.colecao: dict[str, list[ObjetoVisual]] = {}
        self.sementes = copy.deepcopy(SEMENTES_PADRAO)
        self.gemas = 0
        self.estatisticas = {
            "ciclos_completos": 0,
            "xp_total": 0,
            "streak_diario": 0,
            "melhor_streak": 0,
            "ultima_sessao": None,
            "sessoes_hoje": 0,
            "data_sessoes_hoje": None,
        }
        self.desafios_concluidos_hoje: list[str] = []

        self.carregar()

    # ------------------------------------------------------------------ #
    # Persistência
    # ------------------------------------------------------------------ #

    def carregar(self):
        if not os.path.exists(self.caminho_arquivo):
            return
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (json.JSONDecodeError, OSError):
            self._criar_backup_corrompido()
            return

        self.colecao = {
            tipo: [ObjetoVisual.from_dict(o) for o in objetos]
            for tipo, objetos in dados.get("colecao", {}).items()
        }
        self.gemas = dados.get("gemas", 0)
        self.estatisticas.update(dados.get("estatisticas", {}))

        sementes_salvas = dados.get("sementes", {})
        for codigo, semente in sementes_salvas.items():
            if codigo in self.sementes:
                self.sementes[codigo]["desbloqueada"] = semente.get("desbloqueada", False)

        self._resetar_progresso_diario_se_necessario()

    def salvar(self):
        dados = {
            "colecao": {
                tipo: [obj.to_dict() for obj in objetos] for tipo, objetos in self.colecao.items()
            },
            "gemas": self.gemas,
            "estatisticas": self.estatisticas,
            "sementes": self.sementes,
            "metadata": {
                "versao": "1.0",
                "salvo_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
        arquivo_temporario = self.caminho_arquivo + ".tmp"
        with open(arquivo_temporario, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=2, ensure_ascii=False)
        os.replace(arquivo_temporario, self.caminho_arquivo)

    def _criar_backup_corrompido(self):
        try:
            backup = f"{self.caminho_arquivo}.corrompido_{datetime.now():%Y%m%d_%H%M%S}.bak"
            os.replace(self.caminho_arquivo, backup)
        except OSError:
            pass

    # ------------------------------------------------------------------ #
    # Streak e progresso diário
    # ------------------------------------------------------------------ #

    def _resetar_progresso_diario_se_necessario(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        if self.estatisticas.get("data_sessoes_hoje") != hoje:
            self.estatisticas["sessoes_hoje"] = 0
            self.estatisticas["data_sessoes_hoje"] = hoje
            self.desafios_concluidos_hoje = []

        ultima = self.estatisticas.get("ultima_sessao")
        if ultima:
            dias = (datetime.now().date() - datetime.strptime(ultima, "%Y-%m-%d").date()).days
            if dias > 1:
                self.estatisticas["streak_diario"] = 0

    def _atualizar_streak(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        ultima = self.estatisticas.get("ultima_sessao")

        if ultima == hoje:
            return  # streak já contabilizado hoje

        if ultima:
            dias = (datetime.now().date() - datetime.strptime(ultima, "%Y-%m-%d").date()).days
            self.estatisticas["streak_diario"] = (
                self.estatisticas["streak_diario"] + 1 if dias == 1 else 1
            )
        else:
            self.estatisticas["streak_diario"] = 1

        self.estatisticas["melhor_streak"] = max(
            self.estatisticas["melhor_streak"], self.estatisticas["streak_diario"]
        )
        self.estatisticas["ultima_sessao"] = hoje

    # ------------------------------------------------------------------ #
    # Sessão de foco concluída
    # ------------------------------------------------------------------ #

    def concluir_sessao_foco(self, tipo_semente: str = "basica") -> tuple[ObjetoVisual, bool, list]:
        """Registra uma sessão de foco concluída.

        Retorna (objeto_atualizado_ou_criado, subiu_de_nivel, desafios_recompensados).
        """
        if tipo_semente not in self.sementes or not self.sementes[tipo_semente]["desbloqueada"]:
            tipo_semente = "basica"

        semente = self.sementes[tipo_semente]
        bonus_streak = min(self.estatisticas["streak_diario"] * 2, 20)
        xp_ganho = semente["xp_por_sessao"] + bonus_streak

        objetos_do_tipo = self.colecao.setdefault(tipo_semente, [])
        if not objetos_do_tipo:
            objetos_do_tipo.append(ObjetoVisual(tipo=tipo_semente, nome=semente["nome"]))

        objeto = objetos_do_tipo[-1]
        subiu_nivel = objeto.adicionar_experiencia(xp_ganho)

        self.estatisticas["ciclos_completos"] += 1
        self.estatisticas["xp_total"] += xp_ganho
        self.estatisticas["sessoes_hoje"] += 1
        self._atualizar_streak()

        recompensas = self._verificar_desafios()

        self.salvar()
        return objeto, subiu_nivel, recompensas

    # ------------------------------------------------------------------ #
    # Loja
    # ------------------------------------------------------------------ #

    def comprar_semente(self, tipo_semente: str) -> tuple[bool, str]:
        if tipo_semente not in self.sementes:
            return False, "Semente não existe."

        semente = self.sementes[tipo_semente]
        if semente["desbloqueada"]:
            return False, "Você já possui esta semente."

        if self.gemas < semente["preco"]:
            faltam = semente["preco"] - self.gemas
            return False, f"Gemas insuficientes (faltam {faltam} 💎)."

        self.gemas -= semente["preco"]
        semente["desbloqueada"] = True
        self.salvar()
        return True, f"{semente['nome']} desbloqueada!"

    # ------------------------------------------------------------------ #
    # Desafios diários
    # ------------------------------------------------------------------ #

    def _verificar_desafios(self) -> list[tuple[str, dict]]:
        recompensas = []
        sessoes_hoje = self.estatisticas["sessoes_hoje"]

        for codigo, desafio in DESAFIOS_DIARIOS.items():
            if codigo in self.desafios_concluidos_hoje:
                continue
            if sessoes_hoje >= desafio["meta"]:
                self.desafios_concluidos_hoje.append(codigo)
                self.gemas += desafio["recompensa"]["gemas"]
                self.estatisticas["xp_total"] += desafio["recompensa"]["xp"]
                recompensas.append((desafio["nome"], desafio["recompensa"]))

        return recompensas

    def status_desafios(self) -> list[dict]:
        sessoes_hoje = self.estatisticas["sessoes_hoje"]
        status = []
        for codigo, desafio in DESAFIOS_DIARIOS.items():
            status.append(
                {
                    "codigo": codigo,
                    "nome": desafio["nome"],
                    "descricao": desafio["descricao"],
                    "meta": desafio["meta"],
                    "progresso": min(sessoes_hoje, desafio["meta"]),
                    "concluido": codigo in self.desafios_concluidos_hoje,
                    "recompensa": desafio["recompensa"],
                }
            )
        return status

    # ------------------------------------------------------------------ #
    # Utilidades de consulta
    # ------------------------------------------------------------------ #

    def total_objetos(self) -> int:
        return sum(len(objetos) for objetos in self.colecao.values())

    def exportar_backup(self, caminho: str) -> bool:
        try:
            dados = {
                "colecao": {
                    tipo: [obj.to_dict() for obj in objetos] for tipo, objetos in self.colecao.items()
                },
                "gemas": self.gemas,
                "estatisticas": self.estatisticas,
                "sementes": self.sementes,
            }
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False
