"""Sistema de design do app — "Quadro de Despachos".

Direção estética: painel de partidas de aeroporto (despacho, prazo, ATRASADO)
cruzado com a tipografia de um artigo de matemática. Tinta quase preta, âmbar
dominante, vermelho reservado exclusivamente para atraso, verde-menta só para
o ótimo. Serifa editorial para o discurso teórico, monoespaçada para os dados.

Tudo que é cor, espaço ou tipografia nasce aqui. Nenhum outro módulo define
cor literal: importa destes tokens.
"""

from typing import List

import streamlit as st

# ─── tokens ────────────────────────────────────────────────────────────────────

INK = "#0A0C10"          # fundo base
PANEL = "#11151C"        # superfície de painel
PANEL_HI = "#171C25"     # superfície elevada
HAIRLINE = "rgba(240, 180, 41, 0.14)"

AMBER = "#F0B429"        # acento dominante (cromo do quadro)
AMBER_DIM = "#8A6A1E"
LATE = "#FF4A3D"         # atraso — e nada mais
OPTIMAL = "#3FD9A0"      # ótimo / no prazo

TEXT = "#E8E4DA"
TEXT_DIM = "#9A9588"
TEXT_FAINT = "#5E5B52"

# Paleta das tarefas: matizes distinguíveis mas dessaturados, calibrados para
# não competir com o vermelho do atraso nem com o âmbar do cromo.
JOB_PALETTE: List[str] = [
    "#E8C27A",  # areia
    "#7FB8C9",  # geleira
    "#C98B7F",  # argila
    "#9DB87F",  # oliva
    "#B49BC9",  # íris
    "#D9A05B",  # ocre
    "#6F9EA8",  # ardósia
    "#CDA2B6",  # rosa seca
]


def job_color(index: int) -> str:
    return JOB_PALETTE[index % len(JOB_PALETTE)]


def job_color_map(job_ids: List[str]) -> dict:
    """Cor estável por tarefa — a mesma em todas as linhas do quadro."""
    return {job_id: job_color(i) for i, job_id in enumerate(job_ids)}


# ─── CSS global ───────────────────────────────────────────────────────────────

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,wght@0,300..700;1,300..700&family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

:root {
  --ink: #0A0C10;
  --panel: #11151C;
  --panel-hi: #171C25;
  --hairline: rgba(240, 180, 41, 0.14);
  --hairline-soft: rgba(232, 228, 218, 0.08);
  --amber: #F0B429;
  --amber-dim: #8A6A1E;
  --late: #FF4A3D;
  --optimal: #3FD9A0;
  --text: #E8E4DA;
  --text-dim: #9A9588;
  --text-faint: #5E5B52;

  --display: 'Instrument Serif', 'Iowan Old Style', Georgia, serif;
  --prose: 'Newsreader', Georgia, serif;
  --mono: 'IBM Plex Mono', 'SF Mono', ui-monospace, monospace;
}

/* ── casca do app: tinta + textura de grade e scanline ───────────────────── */

.stApp {
  background-color: var(--ink);
  background-image:
    radial-gradient(900px 480px at 12% -8%, rgba(240, 180, 41, 0.10), transparent 70%),
    radial-gradient(700px 420px at 92% 4%, rgba(63, 217, 160, 0.055), transparent 72%),
    repeating-linear-gradient(0deg, rgba(232, 228, 218, 0.022) 0 1px, transparent 1px 3px),
    linear-gradient(180deg, #0C0F14 0%, var(--ink) 38%);
  color: var(--text);
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stToolbar"],
[data-testid="stAppDeployButton"], [data-testid="stStatusWidget"] { display: none; }

[data-testid="stMainBlockContainer"] {
  padding-top: 2.2rem;
  padding-bottom: 5rem;
  max-width: 1360px;
}

/* Tipografia de texto, escopada ao conteúdo. Não vale varrer span/div: os
   ícones do Streamlit são ligaturas de uma fonte própria e viram palavra solta
   ("keyboard_double_arrow_right") se a família for trocada por baixo deles. */
.stApp { color: var(--text); }

/* O :not() isenta as classes próprias do app. Sem ele, o seletor de atributo
   (0,2,1) venceria qualquer `.qd-*` (0,1,0) por especificidade e toda a
   tipografia monoespaçada do quadro cairia para a serifa de corpo. */
[data-testid="stMarkdownContainer"] p:not([class*="qd-"]),
[data-testid="stMarkdownContainer"] li:not([class*="qd-"]),
[data-testid="stCaptionContainer"],
.stApp label {
  font-family: var(--prose);
  color: var(--text);
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
  font-family: var(--display);
  font-weight: 400;
  letter-spacing: -0.01em;
  color: var(--text);
}

/* ── barra lateral ───────────────────────────────────────────────────────── */

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D1016 0%, #0A0C10 100%);
  border-right: 1px solid var(--hairline);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: 1.1rem; }

[data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] label p {
  font-family: var(--mono) !important;
  font-size: 0.66rem !important;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-dim) !important;
}

/* ── widgets ─────────────────────────────────────────────────────────────── */

.stButton button, .stFormSubmitButton button, .stDownloadButton button {
  background: var(--panel-hi);
  color: var(--text);
  border: 1px solid var(--hairline);
  border-radius: 2px;
  text-transform: uppercase;
  transition: background .16s ease, border-color .16s ease, color .16s ease, opacity .16s ease;
}
/* O rótulo vive num <p> dentro do botão — estilizar só o <button> perde para a
   regra de corpo de texto por especificidade. */
.stButton button p, .stFormSubmitButton button p, .stDownloadButton button p {
  font-family: var(--mono) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.1em;
}
.stButton button:hover:not(:disabled),
.stFormSubmitButton button:hover,
.stDownloadButton button:hover {
  background: rgba(240, 180, 41, 0.14);
  border-color: var(--amber);
  color: var(--amber);
}
.stButton button:hover:not(:disabled) p { color: var(--amber) !important; }
.stButton button:disabled {
  opacity: 0.32;
  border-color: var(--hairline-soft);
  cursor: not-allowed;
}

/* Campos: o Streamlit 1.65 usa react-aria, não mais baseweb. */
.react-aria-ComboBox [role="group"],
[data-testid="stNumberInputContainer"],
[data-testid="stTextInputRootElement"] {
  background: var(--panel-hi) !important;
  border-color: var(--hairline) !important;
  border-radius: 2px !important;
}
.stApp input, .stApp [role="combobox"] {
  font-family: var(--mono) !important;
  font-size: 0.8rem !important;
  color: var(--text) !important;
}

[data-testid="stSliderTickBar"] {
  font-family: var(--mono); font-size: 0.6rem; color: var(--text-faint);
}
[data-testid="stSliderThumbValue"] {
  font-family: var(--mono) !important; color: var(--amber) !important; font-size: 0.72rem !important;
}
[data-testid="stRadioOption"] p {
  font-family: var(--mono) !important; font-size: 0.72rem !important; color: var(--text-dim) !important;
}

/* ── abas: guias de quadro, não pílulas de dashboard ────────────────────── */

[data-testid="stTabs"] [role="tablist"] {
  gap: 0;
  border-bottom: 1px solid var(--hairline);
  background: transparent;
}
[data-testid="stTab"] {
  background: transparent;
  padding: 0.8rem 1.4rem;
  border-bottom: 2px solid transparent;
  transition: border-color .18s ease;
}
[data-testid="stTab"] p {
  font-family: var(--mono) !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--text-faint) !important;
  transition: color .18s ease;
}
[data-testid="stTab"]:hover p { color: var(--text-dim) !important; }
[data-testid="stTab"][aria-selected="true"] { border-bottom-color: var(--amber); }
[data-testid="stTab"][aria-selected="true"] p { color: var(--amber) !important; }
/* o indicador animado do react-aria é substituído pela borda acima */
.react-aria-SelectionIndicator { display: none !important; }
[data-testid="stTabPanel"] { padding-top: 1.9rem; }

/* ── cabeçalho editorial ─────────────────────────────────────────────────── */

.qd-hero { position: relative; margin: 0 0 2.4rem; }

.qd-kicker {
  font-family: var(--mono);
  font-size: 0.64rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--amber);
  display: flex; align-items: center; gap: 0.7rem;
  margin-bottom: 1rem;
  animation: qd-fade-up .5s ease both;
}
.qd-kicker::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, var(--hairline), transparent); }
.qd-kicker .qd-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--amber);
  box-shadow: 0 0 10px var(--amber); animation: qd-blink 2.4s steps(1, end) infinite;
}

.qd-title {
  font-family: var(--display);
  font-size: clamp(2.6rem, 5.4vw, 4.4rem);
  line-height: 0.96;
  letter-spacing: -0.025em;
  margin: 0 0 1.1rem;
  max-width: 24ch;
  animation: qd-fade-up .6s ease .06s both;
}
.qd-title em { font-style: italic; color: var(--amber); }

.qd-lede {
  font-family: var(--prose);
  font-size: 1.04rem;
  line-height: 1.62;
  color: var(--text-dim);
  max-width: 62ch;
  margin: 0;
  animation: qd-fade-up .6s ease .12s both;
}
.qd-lede strong { color: var(--text); font-weight: 600; }
.qd-lede code {
  font-family: var(--mono); font-size: 0.88em; color: var(--amber);
  background: rgba(240, 180, 41, 0.08); padding: 0.1em 0.38em; border-radius: 2px;
}

/* ── painéis ─────────────────────────────────────────────────────────────── */

.qd-panel {
  background: linear-gradient(180deg, var(--panel) 0%, rgba(17, 21, 28, 0.6) 100%);
  border: 1px solid var(--hairline);
  border-radius: 3px;
  padding: 1.5rem 1.6rem;
  position: relative;
}
.qd-panel::before {
  content: ""; position: absolute; inset: 0 0 auto 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(240, 180, 41, 0.45), transparent);
}

.qd-eyebrow {
  font-family: var(--mono);
  font-size: 0.62rem;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin: 0 0 1.1rem;
  display: flex; align-items: baseline; gap: 0.75rem;
}
.qd-eyebrow::after { content: ""; flex: 1; height: 1px; background: var(--hairline-soft); }

.qd-note {
  font-family: var(--prose); font-size: 0.92rem; line-height: 1.6;
  color: var(--text-dim); margin: 0.9rem 0 0;
}
.qd-note strong { color: var(--text); }

/* ── quadro / gantt ─────────────────────────────────────────────────────── */

.qd-board { position: relative; }

.qd-row {
  display: grid;
  grid-template-columns: 172px 1fr;
  align-items: center;
  gap: 1.1rem;
  padding: 0.62rem 0;
  transition: opacity .2s ease;
}
.qd-board:hover .qd-row:not(:hover) { opacity: 0.62; }

.qd-row-label { text-align: right; }
.qd-algo {
  font-family: var(--mono); font-size: 0.82rem; font-weight: 500;
  letter-spacing: 0.08em; color: var(--text); display: block;
}
.qd-algo-sub {
  font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--text-faint); display: block; margin-top: 0.22rem;
}
.qd-row-lmax {
  font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.08em;
  margin-top: 0.4rem; display: inline-block; padding: 0.1rem 0.4rem; border-radius: 2px;
}
.qd-row-lmax.is-ok { color: var(--optimal); background: rgba(63, 217, 160, 0.1); }
.qd-row-lmax.is-late { color: var(--late); background: rgba(255, 74, 61, 0.12); }

.qd-track {
  position: relative;
  height: 52px;
  background:
    repeating-linear-gradient(90deg, var(--hairline-soft) 0 1px, transparent 1px var(--tickgap, 10%));
  border-left: 1px solid var(--hairline);
  border-bottom: 1px solid var(--hairline-soft);
}

.qd-bar {
  position: absolute; top: 9px; height: 34px;
  border-radius: 2px;
  overflow: visible;
  clip-path: inset(0 100% 0 0);
  animation: qd-grow .5s cubic-bezier(.22,.85,.2,1) forwards;
  transition: filter .16s ease, transform .16s ease;
  cursor: default;
}
.qd-bar::before {
  content: ""; position: absolute; inset: 0; border-radius: 2px;
  background: linear-gradient(180deg, rgba(255,255,255,0.17), rgba(0,0,0,0.22));
}
.qd-bar:hover { filter: brightness(1.18); transform: translateY(-1px); z-index: 30; }

.qd-bar-id {
  position: absolute; inset: 0; display: grid; place-items: center;
  font-family: var(--mono); font-size: 0.64rem; font-weight: 600;
  letter-spacing: 0.06em; color: rgba(10, 12, 16, 0.82);
  pointer-events: none;
}

/* Filha da barra, não irmã: quando a tarefa inteira está atrasada a faixa
   cobre a barra toda, e opaca ela apagaria a cor e o rótulo da tarefa. Hachura
   translúcida + trilho sólido embaixo preservam as duas leituras. */
.qd-late-zone {
  position: absolute; top: 0; bottom: 0; right: 0;
  border-radius: 0 2px 2px 0;
  background:
    repeating-linear-gradient(135deg, rgba(255,74,61,0.70) 0 3px, rgba(255,74,61,0.10) 3px 7px);
  border-bottom: 3px solid var(--late);
  box-shadow: inset 1px 0 0 rgba(10,12,16,0.45);
  pointer-events: none;
}

.qd-dl {
  position: absolute; top: 0px; height: 52px; width: 0;
  border-left: 2px dashed currentColor;
  opacity: 0.9; pointer-events: none;
  animation: qd-fade-in .4s ease both;
}
.qd-dl::before {
  content: ""; position: absolute; top: -1px; left: -5px;
  border-left: 5px solid transparent; border-right: 5px solid transparent;
  border-top: 7px solid currentColor;
}
.qd-dl.is-missed {
  color: var(--late); opacity: 1; border-left-style: solid;
  filter: drop-shadow(0 0 6px rgba(255, 74, 61, 0.7));
}

/* nota de rodapé para prazos que caem fora da janela do eixo */
.qd-faraway {
  font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.06em;
  color: var(--text-faint); margin-top: 0.9rem;
}
.qd-faraway b { color: var(--text-dim); font-weight: 500; }

/* cursor do tempo no modo passo a passo */
.qd-cursor {
  position: absolute; top: -2px; height: 56px; width: 0;
  border-left: 1px solid var(--amber);
  box-shadow: 0 0 12px rgba(240, 180, 41, 0.6);
  pointer-events: none;
  animation: qd-fade-in .4s ease both;
}
.qd-cursor::after {
  content: attr(data-t); position: absolute; top: -1.05rem; left: 50%;
  transform: translateX(-50%);
  font-family: var(--mono); font-size: 0.56rem; letter-spacing: 0.06em;
  color: var(--amber); white-space: nowrap;
}

/* tooltip nativa estilizada — sem JS, pura CSS */
.qd-bar[data-tip]:hover::after {
  content: attr(data-tip);
  position: absolute; bottom: calc(100% + 11px); left: 50%;
  transform: translateX(-50%);
  white-space: pre-line;
  font-family: var(--mono); font-size: 0.66rem; line-height: 1.55;
  letter-spacing: 0.02em; text-align: left;
  color: var(--text); background: #0A0C10;
  border: 1px solid var(--hairline); border-radius: 3px;
  padding: 0.6rem 0.75rem; min-width: 168px;
  box-shadow: 0 14px 34px rgba(0,0,0,0.7);
  z-index: 60; pointer-events: none;
}

.qd-axis { position: relative; height: 30px; margin-top: 0.1rem; }
.qd-axis-tick {
  position: absolute; top: 0;
  font-family: var(--mono); font-size: 0.6rem; color: var(--text-faint);
  transform: translateX(-50%); padding-top: 0.45rem;
}
.qd-axis-tick::before {
  content: ""; position: absolute; top: 0; left: 50%; width: 1px; height: 4px;
  background: var(--hairline);
}
.qd-axis-title {
  position: absolute; right: 0; top: 0.45rem;
  font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--text-faint);
}

/* ── legenda ─────────────────────────────────────────────────────────────── */

.qd-legend { display: flex; flex-wrap: wrap; gap: 0.45rem 1.1rem; margin-top: 1.2rem; }
.qd-legend-item {
  display: inline-flex; align-items: center; gap: 0.45rem;
  font-family: var(--mono); font-size: 0.66rem; color: var(--text-dim);
}
.qd-swatch { width: 11px; height: 11px; border-radius: 2px; }
.qd-swatch.is-hatch {
  background: repeating-linear-gradient(135deg, rgba(255,74,61,0.95) 0 3px, rgba(140,24,18,0.95) 3px 6px);
}
.qd-swatch.is-dl { width: 0; border-left: 2px dashed var(--text-dim); height: 13px; border-radius: 0; }

/* ── placar ──────────────────────────────────────────────────────────────── */

.qd-score {
  background: linear-gradient(180deg, var(--panel) 0%, rgba(13, 16, 22, 0.75) 100%);
  border: 1px solid var(--hairline-soft);
  border-radius: 3px;
  padding: 1.3rem 1.35rem 1.2rem;
  position: relative; overflow: hidden; height: 100%;
  animation: qd-fade-up .5s ease both;
}
.qd-score.is-best { border-color: rgba(240, 180, 41, 0.55); background: linear-gradient(180deg, rgba(240,180,41,0.07) 0%, rgba(13,16,22,0.8) 100%); }
.qd-score.is-best::after {
  content: "ÓTIMO"; position: absolute; top: 0; right: 0;
  font-family: var(--mono); font-size: 0.55rem; letter-spacing: 0.2em;
  color: var(--ink); background: var(--amber); padding: 0.2rem 0.6rem;
  border-bottom-left-radius: 3px;
}
.qd-score-name {
  font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--text-dim); margin: 0 0 0.1rem;
}
.qd-score-full {
  font-family: var(--prose); font-size: 0.76rem; font-style: italic;
  color: var(--text-faint); margin: 0 0 0.85rem;
}
.qd-score-value {
  font-family: var(--display); font-size: 3.5rem; line-height: 0.88;
  letter-spacing: -0.03em; display: flex; align-items: baseline; gap: 0.45rem;
}
.qd-score-value .qd-unit {
  font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.1em;
  color: var(--text-faint); text-transform: uppercase;
}
.qd-score.is-best .qd-score-value { color: var(--optimal); }
.qd-score.is-worse .qd-score-value { color: var(--late); }
.qd-score-delta {
  font-family: var(--mono); font-size: 0.66rem; letter-spacing: 0.06em;
  margin-top: 0.75rem; color: var(--late);
}
.qd-score-delta.is-ok { color: var(--optimal); }
.qd-score-bar {
  height: 3px; margin-top: 0.75rem; background: rgba(232,228,218,0.08); border-radius: 2px; overflow: hidden;
}
.qd-score-bar span {
  display: block; height: 100%; background: linear-gradient(90deg, var(--amber), var(--late));
  transform-origin: left; animation: qd-grow-x .7s cubic-bezier(.22,.85,.2,1) both;
}
.qd-score-foot {
  font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.08em;
  color: var(--text-faint); margin-top: 0.8rem; text-transform: uppercase;
}

/* ── narração passo a passo ──────────────────────────────────────────────── */

.qd-step {
  border-left: 2px solid var(--hairline);
  padding: 0.1rem 0 0.1rem 1rem;
  animation: qd-fade-up .35s ease both;
}
.qd-step.is-late { border-left-color: var(--late); }
.qd-step.is-ok { border-left-color: var(--optimal); }
.qd-step-head {
  font-family: var(--mono); font-size: 0.66rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--text-dim); margin: 0 0 0.45rem;
}
.qd-step-body { font-family: var(--prose); font-size: 0.95rem; line-height: 1.55; margin: 0; color: var(--text); }
.qd-step-body b { font-family: var(--mono); font-size: 0.86em; font-weight: 600; color: var(--amber); }
.qd-step-verdict {
  font-family: var(--mono); font-size: 0.64rem; letter-spacing: 0.1em;
  text-transform: uppercase; margin-top: 0.5rem; display: inline-block;
  padding: 0.14rem 0.45rem; border-radius: 2px;
}
.qd-step-verdict.is-late { color: var(--late); background: rgba(255,74,61,0.12); }
.qd-step-verdict.is-ok { color: var(--optimal); background: rgba(63,217,160,0.1); }
.qd-step-idle { font-family: var(--prose); font-style: italic; color: var(--text-faint); font-size: 0.9rem; }

/* ── laboratório da prova ────────────────────────────────────────────────── */

.qd-seq { display: flex; align-items: stretch; gap: 0; flex-wrap: wrap; }
.qd-tile {
  min-width: 78px; max-width: 150px; margin: 0 auto;
  padding: 0.6rem 0.7rem; border-radius: 3px;
  background: var(--panel-hi); border: 1px solid var(--hairline-soft);
  font-family: var(--mono); text-align: center;
}
.qd-tile-id { font-size: 0.82rem; font-weight: 600; color: var(--text); }
.qd-tile-meta { font-size: 0.58rem; color: var(--text-faint); margin-top: 0.2rem; letter-spacing: 0.04em; }

.qd-inv-badge {
  font-family: var(--mono); font-size: 0.58rem; letter-spacing: 0.12em;
  text-transform: uppercase; padding: 0.12rem 0.4rem; border-radius: 2px;
  display: inline-block;
}
.qd-inv-badge.is-inv { color: var(--amber); background: rgba(240,180,41,0.13); }
.qd-inv-badge.is-fine { color: var(--text-faint); background: rgba(232,228,218,0.05); }

.qd-inv-math {
  display: block; margin-top: 0.3rem;
  font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.04em;
  color: var(--text-faint); white-space: nowrap;
}

/* roteiro numerado: o "como ler isto" antes dos controles */
.qd-howto {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 1.1rem; margin: 0 0 1.8rem;
  padding: 1.2rem 1.3rem;
  border: 1px solid var(--hairline-soft); border-radius: 3px;
  background: rgba(17, 21, 28, 0.5);
}
.qd-howto-item { display: grid; grid-template-columns: 1.5rem 1fr; gap: 0.7rem; }
.qd-howto-item > span {
  font-family: var(--mono); font-size: 0.68rem; color: var(--ink);
  background: var(--amber); border-radius: 50%;
  width: 1.3rem; height: 1.3rem; display: grid; place-items: center;
  margin-top: 0.1rem;
}
.qd-howto-item.is-caveat > span { background: var(--text-faint); color: var(--ink); }
.qd-howto-item.is-caveat p { color: var(--text-faint); }
.qd-howto-item p {
  font-family: var(--prose); font-size: 0.88rem; line-height: 1.55;
  color: var(--text-dim); margin: 0;
}
.qd-howto-item p b {
  font-family: var(--mono); font-size: 0.82em; color: var(--amber); font-weight: 500;
}
.qd-howto-item p strong { color: var(--text); font-weight: 600; }

/* barra de status ao vivo do laboratório */
.qd-statbar {
  display: flex; flex-wrap: wrap; gap: 0 2.4rem; align-items: baseline;
  padding: 0.85rem 1.1rem; margin: 0 0 1.5rem;
  border-left: 2px solid var(--hairline); border-radius: 0 3px 3px 0;
  background: rgba(17, 21, 28, 0.6);
}
.qd-statbar.is-inv { border-left-color: var(--amber); }
.qd-statbar.is-done { border-left-color: var(--optimal); }
.qd-stat {
  font-family: var(--mono); font-size: 0.92rem; color: var(--text);
  display: inline-flex; align-items: baseline; gap: 0.55rem;
}
.qd-stat i {
  font-style: normal; font-size: 0.58rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--text-faint);
}
.qd-stat b { color: var(--amber); font-weight: 600; }
.qd-stat em { font-style: normal; font-size: 0.72rem; color: var(--text-faint); }
.qd-statbar.is-done .qd-stat b { color: var(--optimal); }

.qd-trail { display: flex; align-items: flex-end; gap: 4px; height: 44px; margin-top: 0.3rem; }
.qd-trail-bar { width: 14px; background: linear-gradient(180deg, var(--amber), var(--amber-dim)); border-radius: 1px 1px 0 0; position: relative; }
.qd-trail-bar.is-last { background: linear-gradient(180deg, var(--optimal), #1E7A5A); }
.qd-trail-bar::after {
  content: attr(data-v); position: absolute; bottom: calc(100% + 3px); left: 50%; transform: translateX(-50%);
  font-family: var(--mono); font-size: 0.55rem; color: var(--text-faint);
}

/* ── teoria: teorema e prova ─────────────────────────────────────────────── */

.qd-theorem {
  border-left: 2px solid var(--amber);
  padding: 0.2rem 0 0.2rem 1.4rem;
  margin: 0 0 2rem;
  max-width: 68ch;
}
.qd-theorem-label {
  font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.24em;
  text-transform: uppercase; color: var(--amber); margin: 0 0 0.6rem;
}
.qd-theorem-body {
  font-family: var(--display); font-size: 1.5rem; line-height: 1.34;
  font-style: italic; color: var(--text); margin: 0;
}

.qd-proof { max-width: 70ch; counter-reset: qd-step; }
.qd-proof-item {
  display: grid; grid-template-columns: 2.1rem 1fr; gap: 0.9rem;
  padding: 0.85rem 0; border-bottom: 1px solid var(--hairline-soft);
}
.qd-proof-item::before {
  counter-increment: qd-step; content: counter(qd-step, decimal-leading-zero);
  font-family: var(--mono); font-size: 0.68rem; color: var(--amber-dim);
  padding-top: 0.28rem;
}
.qd-proof-item p { font-family: var(--prose); font-size: 0.98rem; line-height: 1.64; margin: 0; color: var(--text-dim); }
.qd-proof-item p strong { color: var(--text); font-weight: 600; }
.qd-proof-item.is-qed p { color: var(--text); }
.qd-proof-item.is-qed p::after { content: " ∎"; color: var(--amber); }

.qd-math {
  font-family: var(--mono); font-size: 0.86rem; color: var(--amber);
  background: rgba(240,180,41,0.07); padding: 0.1em 0.4em; border-radius: 2px;
  white-space: nowrap;
}

.qd-fail-card {
  background: var(--panel); border: 1px solid var(--hairline-soft);
  border-radius: 3px; padding: 1.15rem 1.2rem; height: 100%;
}
.qd-fail-card h4 {
  font-family: var(--mono) !important; font-size: 0.68rem !important;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--amber);
  margin: 0 0 0.7rem !important;
}
.qd-fail-card p { font-family: var(--prose); font-size: 0.92rem; line-height: 1.58; color: var(--text-dim); margin: 0; }

/* ── tabela de tarefas ───────────────────────────────────────────────────── */

.qd-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 0.74rem; }
.qd-table th {
  text-align: left; font-weight: 500; font-size: 0.6rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--text-faint);
  padding: 0 0.7rem 0.6rem; border-bottom: 1px solid var(--hairline);
}
.qd-table td { padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--hairline-soft); color: var(--text-dim); }
.qd-table tr:hover td { background: rgba(240,180,41,0.04); color: var(--text); }
.qd-table .qd-cell-id { color: var(--text); font-weight: 500; display: flex; align-items: center; gap: 0.5rem; }
.qd-table .qd-cell-id i { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
.qd-table td.is-tight { color: var(--late); }

/* ── pé ──────────────────────────────────────────────────────────────────── */

.qd-foot {
  margin-top: 3rem; padding-top: 1.1rem; border-top: 1px solid var(--hairline-soft);
  font-family: var(--mono); font-size: 0.6rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--text-faint);
  display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}

/* ── movimento ───────────────────────────────────────────────────────────── */

@keyframes qd-grow { to { clip-path: inset(0 0 0 0); } }
@keyframes qd-grow-x { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes qd-fade-in { from { opacity: 0; } to { opacity: 0.85; } }
@keyframes qd-fade-up { from { opacity: 0; transform: translateY(7px); } to { opacity: 1; transform: none; } }
@keyframes qd-blink { 0%, 62% { opacity: 1; } 63%, 100% { opacity: 0.25; } }

@media (prefers-reduced-motion: reduce) {
  .qd-bar, .qd-late-zone, .qd-dl, .qd-cursor, .qd-score, .qd-step, .qd-kicker,
  .qd-title, .qd-lede, .qd-score-bar span {
    animation: none !important; clip-path: none !important; opacity: 1 !important; transform: none !important;
  }
  .qd-kicker .qd-dot { animation: none !important; }
}

@media (max-width: 900px) {
  .qd-row { grid-template-columns: 1fr; gap: 0.45rem; }
  .qd-row-label { text-align: left; }
}
"""


def inject_theme() -> None:
    """Injeta o CSS global. Chamar uma vez, no topo do app."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def inject_job_highlight_css(job_ids: List[str]) -> None:
    """Realce cruzado: passar o mouse numa tarefa acende essa mesma tarefa nas
    outras linhas do quadro.

    Depende de `:has()`, então precisa de uma regra por tarefa — geradas aqui a
    cada render porque o conjunto de tarefas muda.
    """
    rules = []
    for job_id in job_ids:
        safe = job_id.replace('"', '\\"')
        rules.append(
            f'.qd-board:has(.qd-bar[data-job="{safe}"]:hover) .qd-bar[data-job="{safe}"] '
            "{ box-shadow: 0 0 0 1.5px var(--amber), 0 0 20px rgba(240,180,41,0.45); z-index: 25; }"
            f'.qd-board:has(.qd-bar[data-job="{safe}"]:hover) .qd-dl[data-job="{safe}"] '
            "{ opacity: 1; border-left-width: 2px; }"
        )
    st.markdown("<style>" + "".join(rules) + "</style>", unsafe_allow_html=True)
