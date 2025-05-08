import base64
import io
from typing import Dict, Any

import matplotlib
matplotlib.use("Agg")  # ← fuerza backend sin GUI
import matplotlib.pyplot as plt
import pandas as pd

from db import db_connection  # helper de conexión SQLite ya utilizado por otros servicios

__all__ = ["generate_dashboard"]

# -----------------------------------------------------------------------------
# utilidades internas
# -----------------------------------------------------------------------------

def _fig_to_uri(fig) -> str:
    """Convierte una figura de Matplotlib en un data‑URI PNG listo para <img>."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _bar_uri(counts: Dict[str, int], title: str) -> str:
    """Genera una gráfica de barras simple y la devuelve como data‑URI."""
    df = pd.DataFrame(counts, index=[0]).melt()
    df["value"] = df["value"].astype(int)  # asegura enteros

    fig, ax = plt.subplots()
    ax.bar(df["variable"], df["value"], width=0.6)
    ax.set_title(title)
    ax.set_ylabel("Certificados")
    
    # Configuración para mostrar sólo valores enteros en el eje Y
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    
    # Establecer límite inferior a 0 para evitar valores negativos
    ax.set_ylim(bottom=0)

    for p in ax.patches:  # etiquetas sobre cada barra
        height = int(p.get_height())
        ax.annotate(f"{height}", (p.get_x() + p.get_width() / 2, height),
                    ha='center', va='bottom', fontsize=8)

    return _fig_to_uri(fig)

# -----------------------------------------------------------------------------
# helpers
# -----------------------------------------------------------------------------

def count_my_inspecciones(conn, user_id: int) -> int:
    """Total de inspecciones del laboratorista conectado."""
    sql = """
        SELECT COUNT(*) AS total
        FROM   INSPECCION
        WHERE  id_laboratorista = ?
    """
    return conn.execute(sql, (user_id,)).fetchone()["total"]


def count_my_certificados(conn, user_id: int) -> int:
    """
    Total de certificados emitidos por el laboratorista conectado.
    Se enlaza CERTIFICADO_CALIDAD → INSPECCION para verificar al autor.
    """
    sql = """
        SELECT COUNT(*) AS total
        FROM   CERTIFICADO_CALIDAD AS c
        JOIN   INSPECCION          AS i ON i.id_inspeccion = c.id_inspeccion
        WHERE  i.id_laboratorista = ?
    """
    return conn.execute(sql, (user_id,)).fetchone()["total"]


def counts_by_dev(conn, user_id: int, months: int) -> dict[str, int]:
    """
    Agrupa certificados del laboratorista por nº de desviaciones
    dentro del intervalo solicitado (meses atrás).
    """
    sql = """
        SELECT c.desviaciones
        FROM   CERTIFICADO_CALIDAD AS c
        JOIN   INSPECCION          AS i ON i.id_inspeccion = c.id_inspeccion
        WHERE  i.id_laboratorista = ?
          AND  c.fecha_envio >= date('now', ?)
    """
    # ?2 = "-3 months", "-6 months", …
    df = pd.read_sql_query(sql, conn, params=(user_id, f"-{months} months"))
    df["dev_int"] = df["desviaciones"].apply(lambda t: len([x for x in (t or "").split(",") if x.strip()]))
    return {
        "3+": (df["dev_int"] >= 3).sum(),
        "2":  (df["dev_int"] == 2).sum(),
        "1":  (df["dev_int"] == 1).sum(),
        "Total": len(df)
    }

# -----------------------------------------------------------------------------
# API público
# -----------------------------------------------------------------------------

def generate_dashboard(user_id: int) -> dict:
    """
    Devuelve el diccionario que consume `dashboard.html`
    con la información **sólo del usuario conectado**.
    """
    with db_connection() as conn:
        result: dict[str, Any] = {}
        # conteos principales
        result["inspecciones_total"] = count_my_inspecciones(conn, user_id)
        result["certificados_total"] = count_my_certificados(conn, user_id)
        # gráficas de desviaciones
        for m in (3, 6, 12):
            counts = counts_by_dev(conn, user_id, m)
            result[f"bar{m}_uri"] = _bar_uri(counts, f"Desviaciones en últimos {m} meses")
        return result