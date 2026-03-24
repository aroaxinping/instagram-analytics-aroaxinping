"""
etl.py — Pipeline de extracción, limpieza y transformación de métricas de Instagram.

Uso:
    python src/etl.py

Lee los CSVs de data/raw/ y genera los datasets procesados en data/processed/.
Ejecutar cada vez que se añadan nuevos CSVs exportados de Meta Business Suite.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

RAW  = Path("data/raw")
PROC = Path("data/processed")
PROC.mkdir(parents=True, exist_ok=True)


# ─── helpers ──────────────────────────────────────────────────────────────────

def read_daily_csv(filepath: Path, col_name: str) -> pd.DataFrame:
    """Lee un CSV diario exportado de Meta Business Suite (encoding utf-16).
    Devuelve un DataFrame con columnas [fecha, col_name].
    """
    rows = []
    with open(filepath, encoding="utf-16") as f:
        lines = [l.strip() for l in f if l.strip()]
    # estructura: sep=, | título | header | datos
    for line in lines[3:]:
        line = line.strip('"')
        parts = line.split('","')
        if len(parts) == 2:
            try:
                date_str = parts[0].split("T")[0]
                value = int(parts[1].replace('"', "").replace(",", ""))
                rows.append({"fecha": date_str, col_name: value})
            except ValueError:
                continue
    df = pd.DataFrame(rows)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.set_index("fecha")


def classify_topic(description: str) -> str:
    """Clasifica un Reel por tema a partir de su descripción y hashtags."""
    d = str(description).lower()
    if "sql" in d or "select" in d:        return "SQL"
    if "python" in d or "pyth" in d:       return "Python"
    if "terminal" in d or "bash" in d:     return "Terminal/Bash"
    if "excel" in d:                        return "Excel"
    if "readme" in d:                       return "Buenas prácticas"
    if "linux" in d:                        return "Linux"
    if "git" in d:                          return "Git"
    if any(x in d for x in ["chico", "relaci", "womanin", "apodo"]):
        return "Humor personal"
    if any(x in d for x in ["programad", "codigo", "code"]):
        return "Programación general"
    if any(x in d for x in ["informatic", "techhumor", "techgirl"]):
        return "Tech humor"
    return "Otro"


def get_franja(hour: int) -> str:
    if 6  <= hour < 12: return "Mañana (6-12h)"
    if 12 <= hour < 18: return "Tarde (12-18h)"
    if 18 <= hour < 24: return "Noche (18-24h)"
    return "Madrugada (0-6h)"


# ─── step 1: daily metrics ────────────────────────────────────────────────────

def build_daily_metrics() -> pd.DataFrame:
    print("→ Procesando métricas diarias...")

    files = {
        "visualizaciones": "Visualizaciones.csv",
        "alcance":         "Alcance.csv",
        "interacciones":   "Interacciones.csv",
        "visitas_perfil":  "Visitas.csv",
        "seguidores_ganados": "Seguidores.csv",
    }

    dfs = []
    for col, fname in files.items():
        path = RAW / fname
        if not path.exists():
            print(f"  ⚠️  {fname} no encontrado, se omite.")
            continue
        dfs.append(read_daily_csv(path, col))

    daily = dfs[0].join(dfs[1:], how="outer").fillna(0).astype(int)
    daily = daily.sort_index()
    daily["dia_semana"] = daily.index.day_name()

    out = PROC / "metricas_diarias.csv"
    daily.reset_index().to_csv(out, index=False)
    print(f"  ✅ metricas_diarias.csv — {len(daily)} días")
    return daily


# ─── step 2: reels metrics ───────────────────────────────────────────────────

def build_reels_metrics() -> pd.DataFrame:
    print("→ Procesando métricas por Reel...")

    # find most recent posts CSV
    posts_files = sorted(RAW.glob("Contenido_Posts_*.csv"), reverse=True)
    if not posts_files:
        raise FileNotFoundError("No se encontró ningún CSV de contenido en data/raw/")

    df = pd.read_csv(posts_files[0], encoding="utf-8-sig")
    df = df.rename(columns={
        "Descripción":                   "descripcion",
        "Duración (segundos)":           "duracion_seg",
        "Hora de publicación":           "hora_publicacion",
        "Enlace permanente":             "enlace",
        "Tipo de publicación":           "tipo",
        "Visualizaciones":               "visualizaciones",
        "Alcance":                       "alcance",
        "Me gusta":                      "me_gustas",
        "Veces que se ha compartido":    "compartidos",
        "Seguidores":                    "seguidores_ganados",
        "Comentarios":                   "comentarios",
        "Veces guardado":                "guardados",
    })

    df["fecha_dt"]    = pd.to_datetime(df["hora_publicacion"], format="%m/%d/%Y %H:%M", errors="coerce")
    df["fecha"]       = df["fecha_dt"].dt.strftime("%Y-%m-%d")
    df["hora"]        = df["fecha_dt"].dt.hour
    df["dia_semana"]  = df["fecha_dt"].dt.day_name()
    df["franja"]      = df["hora"].apply(get_franja)

    num_cols = ["visualizaciones", "alcance", "me_gustas", "compartidos",
                "seguidores_ganados", "comentarios", "guardados", "duracion_seg"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    # calculated metrics
    df["engagement_rate"]    = ((df["me_gustas"] + df["comentarios"] + df["guardados"] + df["compartidos"]) / df["alcance"] * 100).round(2)
    df["save_rate"]          = (df["guardados"]          / df["alcance"]         * 100).round(2)
    df["share_rate"]         = (df["compartidos"]        / df["visualizaciones"] * 100).round(2)
    df["follower_conv_rate"] = (df["seguidores_ganados"] / df["alcance"]         * 100).round(2)

    df["tema"]             = df["descripcion"].apply(classify_topic)
    df["descripcion_corta"] = df["descripcion"].str[:60]

    cols_out = [
        "fecha", "hora", "dia_semana", "franja", "tema", "duracion_seg",
        "visualizaciones", "alcance", "me_gustas", "comentarios",
        "guardados", "compartidos", "seguidores_ganados",
        "engagement_rate", "save_rate", "share_rate", "follower_conv_rate",
        "descripcion_corta", "enlace",
    ]
    out_df = df[cols_out].sort_values("fecha")
    out = PROC / "reels_metricas.csv"
    out_df.to_csv(out, index=False)
    print(f"  ✅ reels_metricas.csv — {len(out_df)} reels")
    return out_df


# ─── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n🔄 ETL iniciado — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    build_daily_metrics()
    build_reels_metrics()
    print("\n✅ ETL completado. Datasets listos en data/processed/\n")
