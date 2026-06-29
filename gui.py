"""Interface gráfica do Focus Flow, construída com Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from .core import SistemaFocusFlow, TEMPO_FOCO_PADRAO_MINUTOS

COR_FUNDO = "#0f1117"
COR_CARTAO = "#1a1d29"
COR_TEXTO = "#f4f4f6"
COR_TEXTO_FRACO = "#8a8fa3"
COR_DESTAQUE = "#7c5cff"
COR_OK = "#34d1bf"


class FocusFlowApp(tk.Tk):
    def __init__(self, caminho_dados: str = "dados_usuario.json"):
        super().__init__()
        self.title("Focus Flow")
        self.geometry("520x640")
        self.configure(bg=COR_FUNDO)

        self.sistema = SistemaFocusFlow(caminho_dados)

        self.tempo_restante_segundos = TEMPO_FOCO_PADRAO_MINUTOS * 60
        self.timer_ativo = False
        self._tarefa_timer = None
        self.semente_selecionada = tk.StringVar(value="basica")

        self._montar_estilo_abas()
        self._montar_layout()
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    # ------------------------------------------------------------------ #
    # Layout geral
    # ------------------------------------------------------------------ #

    def _montar_estilo_abas(self):
        estilo = ttk.Style(self)
        estilo.theme_use("default")
        estilo.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        estilo.configure(
            "TNotebook.Tab",
            background=COR_CARTAO,
            foreground=COR_TEXTO,
            padding=(14, 8),
        )
        estilo.map("TNotebook.Tab", background=[("selected", COR_DESTAQUE)])

    def _montar_layout(self):
        cabecalho = tk.Frame(self, bg=COR_FUNDO, pady=12, padx=16)
        cabecalho.pack(fill="x")
        tk.Label(
            cabecalho, text="🌱 Focus Flow", font=("Segoe UI", 18, "bold"),
            bg=COR_FUNDO, fg=COR_TEXTO,
        ).pack(side="left")
        self.label_gemas = tk.Label(
            cabecalho, text="", font=("Segoe UI", 12, "bold"), bg=COR_FUNDO, fg=COR_OK,
        )
        self.label_gemas.pack(side="right")

        abas = ttk.Notebook(self)
        abas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.aba_timer = tk.Frame(abas, bg=COR_FUNDO)
        self.aba_colecao = tk.Frame(abas, bg=COR_FUNDO)
        self.aba_loja = tk.Frame(abas, bg=COR_FUNDO)
        self.aba_desafios = tk.Frame(abas, bg=COR_FUNDO)
        self.aba_estatisticas = tk.Frame(abas, bg=COR_FUNDO)

        abas.add(self.aba_timer, text="⏱ Foco")
        abas.add(self.aba_colecao, text="🪴 Coleção")
        abas.add(self.aba_loja, text="🛒 Loja")
        abas.add(self.aba_desafios, text="🏅 Desafios")
        abas.add(self.aba_estatisticas, text="📊 Estatísticas")

        abas.bind("<<NotebookTabChanged>>", lambda e: self._atualizar_aba_atual())

        self._montar_aba_timer()
        self._atualizar_gemas()

    def _atualizar_gemas(self):
        self.label_gemas.config(text=f"💎 {self.sistema.gemas}")

    def _atualizar_aba_atual(self):
        self._montar_aba_colecao()
        self._montar_aba_loja()
        self._montar_aba_desafios()
        self._montar_aba_estatisticas()

    # ------------------------------------------------------------------ #
    # Aba: Timer de foco
    # ------------------------------------------------------------------ #

    def _montar_aba_timer(self):
        container = tk.Frame(self.aba_timer, bg=COR_FUNDO, pady=24)
        container.pack(expand=True)

        tk.Label(
            container, text="Escolha o que vai crescer com seu foco:",
            bg=COR_FUNDO, fg=COR_TEXTO_FRACO, font=("Segoe UI", 10),
        ).pack(pady=(0, 8))

        opcoes = [
            f"{dados['nome']} ({codigo})"
            for codigo, dados in self.sistema.sementes.items()
            if dados["desbloqueada"]
        ]
        self.combo_semente = ttk.Combobox(container, values=opcoes, state="readonly", width=30)
        self.combo_semente.set(opcoes[0])
        self.combo_semente.pack(pady=(0, 24))

        self.label_timer = tk.Label(
            container, text=self._formatar_tempo(), font=("Consolas", 48, "bold"),
            bg=COR_FUNDO, fg=COR_TEXTO,
        )
        self.label_timer.pack(pady=(0, 24))

        linha_botoes = tk.Frame(container, bg=COR_FUNDO)
        linha_botoes.pack()

        self.botao_iniciar = tk.Button(
            linha_botoes, text="Iniciar Foco", command=self._alternar_timer,
            relief="flat", bg=COR_DESTAQUE, fg="white", font=("Segoe UI", 11, "bold"),
            width=14,
        )
        self.botao_iniciar.pack(side="left", padx=6)

        tk.Button(
            linha_botoes, text="Reiniciar", command=self._reiniciar_timer,
            relief="flat", bg=COR_CARTAO, fg=COR_TEXTO, width=10,
        ).pack(side="left", padx=6)

        self.label_status_timer = tk.Label(
            container, text="", bg=COR_FUNDO, fg=COR_OK, font=("Segoe UI", 11), wraplength=380,
        )
        self.label_status_timer.pack(pady=(20, 0))

    def _formatar_tempo(self) -> str:
        minutos, segundos = divmod(self.tempo_restante_segundos, 60)
        return f"{minutos:02d}:{segundos:02d}"

    def _alternar_timer(self):
        if self.timer_ativo:
            self._pausar_timer()
        else:
            self._iniciar_timer()

    def _iniciar_timer(self):
        self.timer_ativo = True
        self.botao_iniciar.config(text="Pausar")
        self._tique_timer()

    def _pausar_timer(self):
        self.timer_ativo = False
        self.botao_iniciar.config(text="Iniciar Foco")
        if self._tarefa_timer is not None:
            self.after_cancel(self._tarefa_timer)
            self._tarefa_timer = None

    def _reiniciar_timer(self):
        self._pausar_timer()
        self.tempo_restante_segundos = TEMPO_FOCO_PADRAO_MINUTOS * 60
        self.label_timer.config(text=self._formatar_tempo())
        self.label_status_timer.config(text="")

    def _tique_timer(self):
        if not self.timer_ativo:
            return
        if self.tempo_restante_segundos <= 0:
            self._finalizar_sessao()
            return
        self.tempo_restante_segundos -= 1
        self.label_timer.config(text=self._formatar_tempo())
        self._tarefa_timer = self.after(1000, self._tique_timer)

    def _finalizar_sessao(self):
        self._pausar_timer()
        self.tempo_restante_segundos = TEMPO_FOCO_PADRAO_MINUTOS * 60
        self.label_timer.config(text=self._formatar_tempo())

        codigo_semente = self.combo_semente.get().split("(")[-1].rstrip(")")
        objeto, subiu_nivel, recompensas = self.sistema.concluir_sessao_foco(codigo_semente)

        mensagens = [f"✅ Sessão concluída! {objeto.nome} agora tem {objeto.xp} XP (nível {objeto.nivel})."]
        if subiu_nivel:
            mensagens.append(f"🎉 {objeto.nome} subiu de nível!")
        for nome_desafio, recompensa in recompensas:
            mensagens.append(f"🏅 Desafio '{nome_desafio}' completo: +{recompensa['xp']} XP, +{recompensa['gemas']} 💎")

        self.label_status_timer.config(text="\n".join(mensagens))
        self._atualizar_gemas()

    # ------------------------------------------------------------------ #
    # Aba: Coleção
    # ------------------------------------------------------------------ #

    def _montar_aba_colecao(self):
        for widget in self.aba_colecao.winfo_children():
            widget.destroy()

        if self.sistema.total_objetos() == 0:
            tk.Label(
                self.aba_colecao, text="Complete uma sessão de foco para começar sua coleção 🌱",
                bg=COR_FUNDO, fg=COR_TEXTO_FRACO, wraplength=400,
            ).pack(pady=40)
            return

        for tipo, objetos in self.sistema.colecao.items():
            dados_semente = self.sistema.sementes.get(tipo, {})
            for objeto in objetos:
                cartao = tk.Frame(self.aba_colecao, bg=COR_CARTAO)
                cartao.pack(fill="x", padx=12, pady=6)

                cor = dados_semente.get("cor", COR_DESTAQUE)
                tk.Label(
                    cartao, text="●", fg=cor, bg=COR_CARTAO, font=("Segoe UI", 20),
                ).grid(row=0, column=0, rowspan=2, padx=12, pady=8)

                tk.Label(
                    cartao, text=f"{objeto.nome} — Nível {objeto.nivel}",
                    bg=COR_CARTAO, fg=COR_TEXTO, font=("Segoe UI", 11, "bold"), anchor="w",
                ).grid(row=0, column=1, sticky="w", pady=(8, 0))

                tk.Label(
                    cartao, text=f"{objeto.xp}/{objeto.xp_para_proximo_nivel} XP  ·  {dados_semente.get('raridade', '')}",
                    bg=COR_CARTAO, fg=COR_TEXTO_FRACO, font=("Segoe UI", 9), anchor="w",
                ).grid(row=1, column=1, sticky="w", pady=(0, 8))

    # ------------------------------------------------------------------ #
    # Aba: Loja
    # ------------------------------------------------------------------ #

    def _montar_aba_loja(self):
        for widget in self.aba_loja.winfo_children():
            widget.destroy()

        for codigo, semente in self.sistema.sementes.items():
            cartao = tk.Frame(self.aba_loja, bg=COR_CARTAO)
            cartao.pack(fill="x", padx=12, pady=6)

            tk.Label(
                cartao, text=semente["nome"], bg=COR_CARTAO, fg=COR_TEXTO,
                font=("Segoe UI", 11, "bold"), anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))

            tk.Label(
                cartao, text=semente["descricao"], bg=COR_CARTAO, fg=COR_TEXTO_FRACO,
                anchor="w", wraplength=300, justify="left",
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))

            if semente["desbloqueada"]:
                tk.Label(
                    cartao, text="✅ Desbloqueada", bg=COR_CARTAO, fg=COR_OK,
                ).grid(row=0, column=1, rowspan=2, padx=12)
            else:
                tk.Button(
                    cartao, text=f"Comprar — {semente['preco']} 💎",
                    command=lambda c=codigo: self._ao_comprar(c),
                    relief="flat", bg=COR_DESTAQUE, fg="white",
                ).grid(row=0, column=1, rowspan=2, padx=12)

    def _ao_comprar(self, codigo: str):
        ok, mensagem = self.sistema.comprar_semente(codigo)
        if ok:
            messagebox.showinfo("Loja", mensagem)
        else:
            messagebox.showwarning("Loja", mensagem)
        self._atualizar_gemas()
        self._montar_aba_loja()

    # ------------------------------------------------------------------ #
    # Aba: Desafios
    # ------------------------------------------------------------------ #

    def _montar_aba_desafios(self):
        for widget in self.aba_desafios.winfo_children():
            widget.destroy()

        for desafio in self.sistema.status_desafios():
            cartao = tk.Frame(self.aba_desafios, bg=COR_CARTAO)
            cartao.pack(fill="x", padx=12, pady=6)

            status = "✅" if desafio["concluido"] else "◻️"
            tk.Label(
                cartao, text=f"{status} {desafio['nome']}", bg=COR_CARTAO, fg=COR_TEXTO,
                font=("Segoe UI", 11, "bold"), anchor="w",
            ).pack(fill="x", padx=12, pady=(8, 0))

            tk.Label(
                cartao, text=desafio["descricao"], bg=COR_CARTAO, fg=COR_TEXTO_FRACO, anchor="w",
            ).pack(fill="x", padx=12)

            tk.Label(
                cartao,
                text=f"Progresso: {desafio['progresso']}/{desafio['meta']}  ·  "
                     f"Recompensa: {desafio['recompensa']['xp']} XP + {desafio['recompensa']['gemas']} 💎",
                bg=COR_CARTAO, fg=COR_OK, anchor="w",
            ).pack(fill="x", padx=12, pady=(0, 8))

    # ------------------------------------------------------------------ #
    # Aba: Estatísticas
    # ------------------------------------------------------------------ #

    def _montar_aba_estatisticas(self):
        for widget in self.aba_estatisticas.winfo_children():
            widget.destroy()

        estatisticas = self.sistema.estatisticas
        linhas = [
            ("Ciclos completos", estatisticas["ciclos_completos"]),
            ("XP total acumulado", estatisticas["xp_total"]),
            ("Sequência atual (streak)", f"{estatisticas['streak_diario']} dia(s)"),
            ("Melhor sequência", f"{estatisticas['melhor_streak']} dia(s)"),
            ("Sessões hoje", estatisticas["sessoes_hoje"]),
            ("Objetos na coleção", self.sistema.total_objetos()),
            ("Gemas", self.sistema.gemas),
        ]

        for rotulo, valor in linhas:
            linha = tk.Frame(self.aba_estatisticas, bg=COR_CARTAO)
            linha.pack(fill="x", padx=12, pady=4)
            tk.Label(linha, text=rotulo, bg=COR_CARTAO, fg=COR_TEXTO_FRACO).pack(
                side="left", padx=12, pady=8
            )
            tk.Label(
                linha, text=str(valor), bg=COR_CARTAO, fg=COR_TEXTO, font=("Segoe UI", 11, "bold"),
            ).pack(side="right", padx=12, pady=8)

    # ------------------------------------------------------------------ #

    def _ao_fechar(self):
        self.sistema.salvar()
        self.destroy()


def main():
    app = FocusFlowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
