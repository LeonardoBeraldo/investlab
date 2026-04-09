# InvestLab — Painel de Decisão de Investimentos

Aplicativo multiplataforma (PC + Android) desenvolvido com **Python 3.10+** e **Flet 0.83+**.

## Requisitos

| Ferramenta | Versão mínima |
|-----------|---------------|
| Python | 3.10 |
| Flet | 0.83.0 |
| Flutter SDK | instalado automaticamente pelo `flet build` |
| JDK | 17 (instalado automaticamente para APK) |
| Android SDK | instalado automaticamente para APK |

## Instalação e execução (desktop)

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# 2. Instale as dependências
pip install "flet>=0.83.0"

# 3. Execute o app
flet run src/main.py
```

## Build — Desktop (executável standalone)

```bash
flet build windows   # Windows (.exe)
flet build macos     # macOS (.app)
flet build linux     # Linux (binário)
```

## Build — Android APK

```bash
flet build apk
# Saída: build/apk/app-release.apk
# Instalar no dispositivo: adb install build/apk/app-release.apk
```

## Build — Android App Bundle (Google Play)

```bash
flet build aab
```

## Estrutura do projeto

```
investlab/
├── pyproject.toml          ← configuração do projeto e build
├── README.md
├── assets/                 ← ícones, imagens, fontes
│   └── icon.png
└── src/
    ├── main.py             ← ponto de entrada do app
    ├── theme.py            ← cores, tipografia, constantes visuais
    ├── models/
    │   └── ativo.py        ← dataclasses: Ativo, TipoAtivo, etc.
    ├── services/
    │   └── storage.py      ← persistência em JSON local (cross-platform)
    ├── components/
    │   ├── nav_bar.py      ← barra de navegação inferior
    │   ├── top_bar.py      ← barra superior com logo e mercado
    │   ├── metric_card.py  ← card de métrica mini
    │   └── badge.py        ← badges coloridos (COMPRAR/MANTER/VENDER)
    ├── views/
    │   ├── visao_geral.py  ← aba Visão Geral
    │   ├── acoes.py        ← aba Ações
    │   ├── fiis.py         ← aba FIIs
    │   ├── renda_fixa.py   ← aba Renda Fixa
    │   ├── macro.py        ← aba Macro / Cenário
    │   ├── carteira.py     ← aba Minha Carteira
    │   └── cadastro.py     ← tela Cadastro de Ativo
    └── utils/
        └── formatters.py   ← formatação de moeda, %, datas
```
