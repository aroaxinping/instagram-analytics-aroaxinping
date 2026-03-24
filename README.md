# 📊 Instagram Analytics — @aroaxinping

> **Proyecto en curso.** Análisis de mis propias métricas de Instagram para tomar decisiones de contenido basadas en datos.

---

## Sobre el proyecto

Empecé a publicar contenido de forma constante en Instagram el **24 de febrero de 2026**, enfocada en programación, tech humor e informática. En vez de publicar a ciegas, decidí aplicar lo que sé de análisis de datos a mi propio canal: extraer las métricas semanalmente, limpiarlas, analizarlas y usarlas para decidir qué, cuándo y cómo publicar.

Este repositorio documenta ese proceso de forma transparente y se actualiza cada vez que tengo nuevos datos.

---

## Estado actual

| Métrica | Valor (24 feb – 23 mar 2026) |
|--------|------------------------------|
| Período analizado | 4 semanas |
| Reels publicados | 30 |
| Visualizaciones totales | 6,446,377 |
| Seguidores ganados | 3,243 |
| Engagement rate medio | 12.2% |
| Seguidores totales | 8,728 |

---

## Estructura del repositorio

```
instagram-analytics-aroaxinping/
│
├── data/
│   ├── raw/                         # CSVs exportados directamente de Meta Business Suite
│   │   ├── Visualizaciones.csv
│   │   ├── Alcance.csv
│   │   ├── Interacciones.csv
│   │   ├── Visitas.csv
│   │   ├── Seguidores.csv
│   │   └── Contenido_Posts_Feb24_Mar23.csv
│   │
│   └── processed/                   # Datos limpios con métricas calculadas
│       ├── metricas_diarias.csv     # Una fila por día
│       └── reels_metricas.csv       # Una fila por Reel + engagement rate, save rate, etc.
│
├── notebooks/
│   └── 01_analisis_exploratorio.ipynb   # Análisis principal con gráficos
│
├── visuals/                         # Gráficos exportados del notebook
│   ├── 01_crecimiento_diario.png
│   ├── 02_resumen_semanal.png
│   ├── 03_top10_reels.png
│   ├── 04_vistas_vs_engagement.png
│   ├── 05_rendimiento_por_tema.png
│   ├── 06_cuando_publicar.png
│   └── 07_funnel_conversion.png
│
└── README.md
```

---

## Metodología

### Extracción
Los datos se exportan manualmente desde **Meta Business Suite** cada semana en formato CSV. No uso la API de Instagram (requiere verificación de empresa) — la extracción manual me da control total sobre qué datos incluyo.

### Limpieza
- Parseo de fechas y horas de publicación
- Conversión de tipos numéricos
- Eliminación de filas de historias (las métricas son distintas)
- Extracción de tema/categoría a partir de hashtags y descripción

### Métricas calculadas
| Métrica | Fórmula |
|--------|---------|
| `engagement_rate` | (likes + comentarios + guardados + compartidos) / alcance × 100 |
| `save_rate` | guardados / alcance × 100 |
| `share_rate` | compartidos / visualizaciones × 100 |
| `follower_conv_rate` | seguidores ganados / alcance × 100 |

### Análisis
Todo en un único notebook de Python (`notebooks/01_analisis_exploratorio.ipynb`) usando pandas, matplotlib y seaborn.

---

## Hallazgos clave (semanas 1–4)

1. **El humor personal viraliza pero no conecta** — genera alto alcance y muchas vistas, pero bajo engagement rate y poca conversión a seguidores. Llega a mucha gente que no se queda.
2. **La combinación técnico + humor es el formato con mejor conversión** — los Reels que mezclan contenido de programación/informática con un tono divertido tienen el mayor ratio de seguidores ganados por alcance y más conexión real con el espectador. Es el punto diferencial de la cuenta.
3. **Los reels de 30–60s rinden mejor** que los muy cortos (<15s) en términos de retención y seguidores ganados.
4. **Lunes y martes por la tarde-noche** parecen ser las mejores franjas de publicación (a confirmar con más semanas).

---

## Próximas actualizaciones

- [ ] Semanas 5–8 (abril 2026)
- [ ] Análisis de correlación frecuencia de publicación ↔ crecimiento de seguidores
- [ ] Segmentación audiencia seguidores vs no seguidores
- [ ] Modelo predictivo simple (tema + franja + duración → vistas esperadas)
- [ ] Dashboard interactivo con Plotly o Streamlit

---

## Stack

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas)
![matplotlib](https://img.shields.io/badge/matplotlib-3.x-11557c)
![Jupyter](https://img.shields.io/badge/Jupyter-notebook-orange?logo=jupyter)
![Meta Business Suite](https://img.shields.io/badge/Data%20source-Meta%20Business%20Suite-1877F2?logo=meta)

---

*Actualizado: marzo 2026 | [@aroaxinping](https://www.instagram.com/aroaxinping)*
