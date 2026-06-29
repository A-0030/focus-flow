# 🌱 Focus Flow

Aplicativo de produtividade gamificado: a cada sessão de foco concluída (técnica Pomodoro), o usuário ganha XP para evoluir uma coleção de "objetos visuais" (plantas, cristais, cidades, recifes, nebulosas), além de gemas para desbloquear novos itens na loja. Inclui sistema de sequência diária (streak) e desafios diários.

Reescrito com **interface gráfica em Tkinter**, separando claramente a lógica de negócio da apresentação — o que facilita testes automatizados e futura migração para outra interface (ex.: web).

## ✨ Funcionalidades

- ⏱️ **Timer de foco** (Pomodoro de 25 minutos) com início/pausa/reinício
- 🪴 **Coleção evolutiva**: cada sessão de foco gera XP para o item escolhido, que sobe de nível
- 🛒 **Loja**: desbloqueie novos tipos de coleção usando gemas conquistadas
- 🏅 **Desafios diários**: metas de sessões com recompensas em XP e gemas
- 🔥 **Streak diário**: bônus de XP por manter sequência de dias consecutivos
- 💾 **Persistência automática** em JSON, com proteção contra arquivos corrompidos (escrita atômica + backup automático)

## 🖥️ Pré-requisitos

- Python 3.10+ (usa sintaxe de type hints moderna, como `dict[str, list]`)
- Tkinter (incluso na instalação padrão do Python)

## ▶️ Como executar

```bash
python main.py
```

Os dados do usuário (coleção, XP, gemas, estatísticas) são salvos automaticamente em `dados_usuario.json`, na mesma pasta do projeto.

## 📁 Estrutura do projeto

```
focus-flow/
├── main.py                  # Ponto de entrada
├── focus_flow/
│   ├── __init__.py
│   ├── models.py             # ObjetoVisual, sementes e desafios (dados puros)
│   ├── core.py               # SistemaFocusFlow: regras de negócio e persistência
│   └── gui.py                # Interface gráfica (Tkinter)
└── README.md
```

A separação entre `core.py` (regras) e `gui.py` (interface) permite testar toda a lógica do jogo sem precisar abrir nenhuma janela.

## 🛠️ Tecnologias

- Python 3
- Tkinter
- JSON (persistência local)

## 📌 Possíveis melhorias futuras

- Sons e animações de evolução
- Exportar/importar backup pela própria interface
- Versão web (Flask) reaproveitando o módulo `core.py` sem alterações
- Notificações do sistema ao concluir uma sessão

---

Projeto desenvolvido como parte de um portfólio de aplicações Python.
