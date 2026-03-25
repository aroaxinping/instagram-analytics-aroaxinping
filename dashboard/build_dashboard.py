"""
Instagram Analytics Dashboard — @aroaxinping
Genera un dashboard interactivo HTML con Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_REELS = os.path.join(BASE, "data", "processed", "reels_metricas.csv")
CSV_DAILY = os.path.join(BASE, "data", "processed", "metricas_diarias.csv")
OUT       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instagram_dashboard.html")

# ── Datos ──────────────────────────────────────────────────────────────────
reels = pd.read_csv(CSV_REELS)
daily = pd.read_csv(CSV_DAILY)

reels["fecha"] = pd.to_datetime(reels["fecha"])
daily["fecha"] = pd.to_datetime(daily["fecha"])
reels["title_short"] = reels["descripcion_corta"].astype(str).str[:28] + "…"

# Colores
PURPLE = "#E1306C"
DARK   = "#1a1a2e"
CARD   = "#16213e"
LIGHT  = "#e2e8f0"
MUTED  = "#94a3b8"
ACCENT = "#f093fb"

# ── Figura ──────────────────────────────────────────────────────────────────
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Crecimiento diario de seguidores",
        "Visualizaciones acumuladas",
        "Top 10 Reels por Visualizaciones",
        "Engagement Rate por Reel (%)",
        "Rendimiento por Tematica",
        "Engagement Rate vs Save Rate",
    ),
    vertical_spacing=0.12,
    horizontal_spacing=0.10,
    specs=[[{"type":"xy"},{"type":"xy"}],
           [{"type":"xy"},{"type":"xy"}],
           [{"type":"xy"},{"type":"xy"}]],
)

# 1. Crecimiento diario seguidores
fig.add_trace(go.Scatter(
    x=daily["fecha"],
    y=daily["seguidores_ganados"].cumsum(),
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(225, 48, 108, 0.15)",
    line=dict(color=PURPLE, width=2),
    name="Seguidores acumulados",
), row=1, col=1)

# 2. Visualizaciones acumuladas
fig.add_trace(go.Scatter(
    x=daily["fecha"],
    y=daily["visualizaciones"].cumsum(),
    mode="lines",
    fill="tozeroy",
    fillcolor="rgba(240, 147, 251, 0.15)",
    line=dict(color=ACCENT, width=2),
    name="Vistas acumuladas",
), row=1, col=2)

# 3. Top 10 reels por vistas
top = reels.nlargest(10, "visualizaciones").sort_values("visualizaciones")
fig.add_trace(go.Bar(
    x=top["visualizaciones"],
    y=top["title_short"],
    orientation="h",
    marker=dict(color=top["visualizaciones"], colorscale=[[0,"#f093fb"],[1,"#E1306C"]], showscale=False),
    text=[f'{v/1000:.0f}K' for v in top["visualizaciones"]],
    textposition="outside",
    name="Vistas",
), row=2, col=1)

# 4. Engagement Rate por reel (top 10)
top_er = reels.nlargest(10, "engagement_rate").sort_values("engagement_rate")
fig.add_trace(go.Bar(
    x=top_er["engagement_rate"],
    y=top_er["title_short"],
    orientation="h",
    marker=dict(color=top_er["engagement_rate"], colorscale=[[0,"#4facfe"],[1,"#00f2fe"]], showscale=False),
    text=[f'{v:.1f}%' for v in top_er["engagement_rate"]],
    textposition="outside",
    name="ER",
), row=2, col=2)

# 5. Rendimiento por tematica
tema_stats = reels.groupby("tema").agg(
    reels_count=("engagement_rate","count"),
    er_medio=("engagement_rate","mean"),
    vistas_medias=("visualizaciones","mean"),
    seguidores=("seguidores_ganados","sum"),
).reset_index()
tema_stats = tema_stats[tema_stats["reels_count"] > 1].sort_values("er_medio", ascending=True)

fig.add_trace(go.Bar(
    x=tema_stats["er_medio"],
    y=tema_stats["tema"],
    orientation="h",
    marker=dict(color=tema_stats["er_medio"], colorscale=[[0,"#a18cd1"],[1,"#fbc2eb"]], showscale=False),
    text=[f'{v:.1f}%' for v in tema_stats["er_medio"]],
    textposition="outside",
    name="ER por tema",
), row=3, col=1)

# 6. ER vs Save Rate scatter
fig.add_trace(go.Scatter(
    x=reels["save_rate"],
    y=reels["engagement_rate"],
    mode="markers",
    marker=dict(
        size=10,
        color=reels["visualizaciones"],
        colorscale=[[0,"#f093fb"],[1,"#E1306C"]],
        showscale=True,
        colorbar=dict(title="Vistas", x=1.01, thickness=8, len=0.3, y=0.15),
    ),
    text=reels["title_short"],
    name="ER vs Save",
), row=3, col=2)

# ── Layout ──────────────────────────────────────────────────────────────────
fig.update_layout(
    height=1300,
    paper_bgcolor=DARK,
    plot_bgcolor=CARD,
    font=dict(color=LIGHT, family="Inter, system-ui, sans-serif", size=11),
    title=dict(
        text="<b>Instagram Analytics Dashboard</b> — @aroaxinping · Feb–Mar 2026",
        font=dict(size=20, color=LIGHT),
        x=0.5,
    ),
    showlegend=False,
    margin=dict(t=80, b=40, l=20, r=20),
)

for i in range(1, 4):
    for j in range(1, 3):
        fig.update_xaxes(showgrid=True, gridcolor="#2d3748", gridwidth=0.5,
                         zeroline=False, linecolor="#4a5568",
                         tickfont=dict(color=MUTED, size=9), row=i, col=j)
        fig.update_yaxes(showgrid=False, zeroline=False, linecolor="#4a5568",
                         tickfont=dict(color=MUTED, size=9), row=i, col=j)

for ann in fig.layout.annotations:
    ann.font.color = LIGHT
    ann.font.size = 12

# Axis labels
fig.update_xaxes(title_text="Save Rate (%)", row=3, col=2)
fig.update_yaxes(title_text="Engagement Rate (%)", row=3, col=2)
fig.update_xaxes(title_text="Engagement Rate medio (%)", row=3, col=1)

# KPIs
total_views   = reels["visualizaciones"].sum()
total_follows = reels["seguidores_ganados"].sum()
avg_er        = reels["engagement_rate"].mean()
total_reels   = len(reels)

kpi_text = (
    f"<b>Reels publicados:</b> {total_reels}  |  "
    f"<b>Vistas totales:</b> {total_views/1e6:.2f}M  |  "
    f"<b>ER medio:</b> {avg_er:.1f}%  |  "
    f"<b>Seguidores ganados:</b> {total_follows:,}"
)
fig.add_annotation(
    text=kpi_text, x=0.5, y=1.04, xref="paper", yref="paper",
    showarrow=False, font=dict(size=11, color=ACCENT), align="center",
)

# ── Exportar ─────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.write_html(OUT, include_plotlyjs="cdn", full_html=True)
print(f"Dashboard guardado en: {OUT}")
