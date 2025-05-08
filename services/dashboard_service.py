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

# helpers -------------------------------------------------------------
def _is_manager(role: str) -> bool:
    return role in {"Admin",
                    "Gerencia de laboratorio",
                    "Gerencia de Control de Calidad"}

def count_inspecciones(conn, *, user_id: int, is_manager: bool) -> int:
    sql = """
        SELECT COUNT(*) AS total
        FROM   INSPECCION
        {where}
    """.format(where="" if is_manager else "WHERE id_laboratorista = ?")
    params = () if is_manager else (user_id,)
    return conn.execute(sql, params).fetchone()["total"]

def count_certificados(conn, *, user_id: int, is_manager: bool) -> int:
    sql = """
        SELECT COUNT(*) AS total
        FROM   CERTIFICADO_CALIDAD  AS c
        JOIN   INSPECCION           AS i USING (id_inspeccion)
        {where}
    """.format(where="" if is_manager else "WHERE i.id_laboratorista = ?")
    params = () if is_manager else (user_id,)
    return conn.execute(sql, params).fetchone()["total"]

# --------------------------------------------------------------------
def counts_by_dev(conn, *, user_id: int, is_manager: bool, months: int) -> dict[str, int]:
    """
    Devuelve cuántos certificados tienen 3+, 2, 1 ó 0 desviaciones
    en los últimos *months* meses.  Si *is_manager* es False, filtra
    además por el laboratorista.
    """
    sql = """
        SELECT c.desviaciones
        FROM   CERTIFICADO_CALIDAD AS c
        JOIN   INSPECCION         AS i USING (id_inspeccion)
        WHERE  c.fecha_envio >= date('now', ?)
    """
    params: list[Any] = [f"-{months} months"]

    if not is_manager:
        sql += " AND i.id_laboratorista = ?"
        params.append(user_id)

    df = pd.read_sql_query(sql, conn, params=params)

    df["dev_int"] = df["desviaciones"].apply(
        lambda t: len([x for x in (t or "").split(",") if x.strip()])
    )

    return {
        "3+": (df["dev_int"] >= 3).sum(),
        "2":  (df["dev_int"] == 2).sum(),
        "1":  (df["dev_int"] == 1).sum(),
        "Total": len(df),
    }
# --------------------------------------------------------------------


# API público ---------------------------------------------------------
def generate_dashboard(user) -> dict:
    """
    Devuelve la info del dashboard ajustada a los permisos del *user*.
    - Laboratorista => sólo sus datos
    - Roles de supervisión => datos globales
    """
    is_manager = _is_manager(user.rol)          # type: ignore[attr-defined]
    with db_connection() as conn:
        result = {
            "inspecciones_total": count_inspecciones(conn,
                                                     user_id=user.id,
                                                     is_manager=is_manager),
            "certificados_total": count_certificados(conn,
                                                     user_id=user.id,
                                                     is_manager=is_manager),
        }
        for m in (3, 6, 12):
            result[f"bar{m}_uri"] = _bar_uri(
                counts_by_dev(conn,
                              user_id=user.id,
                              is_manager=is_manager,
                              months=m),
                f"Desviaciones en últimos {m} meses"
            )
        return result
