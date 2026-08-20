"""
Unificación de bases de dinámica forestal: Galeras, Selva Viva, Sumaco.

Estrategia:
1. Cada base tiene nombres de columna distintos para conceptos equivalentes
   (p.ej. 'PlotID' vs 'plot ID'; 'dbh 2024' vs 'dbh 3 2025' vs 'dbh 3').
   Se define un diccionario de mapeo por archivo -> nombre estandar.
2. Se homogenizan tipos de dato:
   - Números con coma decimal ('18,43') -> punto decimal (18.43)
   - IDs de árbol (treeID, new_tree_ID) -> texto, sin decimales falsos
   - Texto (family/genus/species/site/comment) -> se recorta espacios/saltos de línea
3. Valores que no se pueden interpretar de forma segura (p.ej. una fecha
   metida por error en una columna de DAP) NO se adivinan: se dejan en
   blanco y se registran en la hoja "Revisar" para que el equipo de campo
   las verifique contra el archivo original.
4. Se agrega una columna 'dataset' (Galeras/SelvaViva/Sumaco) y 'site' para
   saber siempre de qué base y sitio proviene cada fila.
"""
import re
import unicodedata
import pandas as pd
import openpyxl
from datetime import datetime

UPLOADS = "/mnt/user-data/uploads"

# ---------------------------------------------------------------------------
# 1. Esquema unificado y mapeos columna-original -> columna-estandar
# ---------------------------------------------------------------------------

# Orden final de columnas en la base unificada
COLUMN_ORDER = [
    "dataset", "site", "PlotID", "Plot_num", "subplot",
    "treeID", "new_tree_ID", "dendrometer",
    "family", "genus", "species", "Cambio_sp",
    "Individual_tree_census1", "Individual_tree_census2",
    "new_census2", "dead_census2",
    "date_census1", "dbh_census1",
    "date_census2", "dbh_census2",
    "tree_height_2011_m",
    "ind_tree1_branch0",
    "dead_census1",
    "date_census3", "dbh_census3", "height_census3_m",
    "dead_census3", "new_entry_census3",
    "leaf_sample_census1", "wood_sample_census1",
    "leaf_sample_census3", "wood_sample_census3",
    "JH_herbarium_census1", "JH_herbarium_census3",
    "N_duplicados_muestras_2025",
    "comment", "comment_2024", "comment_taxo", "comment_extra",
    "Select_2024", "Collected_2024",
    "crust_thickness", "wet_length_cm", "wet_wood_weight", "dry_wood_weight",
]

MAP_GALERAS = {
    "Plot": "Plot_num", "site": "site", "PlotID": "PlotID", "treeID": "treeID",
    "Individual tree census 1": "Individual_tree_census1",
    "Individual tree census 2": "Individual_tree_census2",
    "new census 2": "new_census2", "dead census 2": "dead_census2",
    "family": "family", "genus": "genus", "species": "species",
    "date census 1": "date_census1", "dbh 1": "dbh_census1",
    "date census 2": "date_census2", "dbh 2": "dbh_census2",
    "tree height 2011 (m)": "tree_height_2011_m", "comment": "comment",
    "JH herbarium collections": "JH_herbarium_census1",
    "leaf sample tree": "leaf_sample_census1",
    "Select_2024": "Select_2024", "Collected_2024": "Collected_2024",
    "new ID 2024": "new_tree_ID", "ind (1) branch (0)": "ind_tree1_branch0",
    "dead 2011": "dead_census1", "dead 2024": "dead_census3",
    "date census 3": "date_census3", "dbh 2024": "dbh_census3",
    "height (m) 2024": "height_census3_m",
    "leaf sample tree 3": "leaf_sample_census3",
    "new entry 2024": "new_entry_census3", "X/Y": "subplot",
    "Cambio sp": "Cambio_sp",
    "JH herbarium collections 2024": "JH_herbarium_census3",
    "Nº duplicados/ muestras 2025": "N_duplicados_muestras_2025",
    "comment 2024": "comment_2024", "comment taxo 2024": "comment_taxo",
    "crust thickness": "crust_thickness", "wet lenght cm": "wet_length_cm",
    "wet wood weight": "wet_wood_weight", "dry wood weight": "dry_wood_weight",
}

MAP_SELVAVIVA = {
    "site": "site", "PlotID": "PlotID", "treeID": "treeID",
    "new ID 2024": "new_tree_ID",
    "Individual tree census 1": "Individual_tree_census1",
    "new census 2": "new_census2", "dead census 2": "dead_census2",
    "family": "family", "genus": "genus", "species": "species",
    "dendrometer": "dendrometer",
    "date census 1": "date_census1", "dbh 1": "dbh_census1",
    "date census 2": "date_census2", "dbh 2": "dbh_census2",
    "tree height 2011 (m)": "tree_height_2011_m", "comment": "comment",
    "JH herbarium collections": "JH_herbarium_census1",
    "leaf sample 2025": "leaf_sample_census3",
    "wood sample 2025": "wood_sample_census3",
    "ind (1) branch (0)": "ind_tree1_branch0",
    "dead 2011": "dead_census1", "dead 2025": "dead_census3",
    "date census 3 2025": "date_census3", "dbh 3 2025": "dbh_census3",
    "height (m) 2025": "height_census3_m",
    "new entry 2025": "new_entry_census3", "subplot": "subplot",
    "Cambio sp": "Cambio_sp",
    "JH herbarium collections 2025": "JH_herbarium_census3",
    "Nº duplicados/ muestras 2025": "N_duplicados_muestras_2025",
    "comment 2024": "comment_2024", "comment taxo 2024": "comment_taxo",
}

MAP_SUMACO = {
    "plot ID": "PlotID", "treeID": "treeID",
    "new tree ID 2025": "new_tree_ID",
    "Individual tree census 1": "Individual_tree_census1",
    "Individual tree census 2": "Individual_tree_census2",
    "new census 2": "new_census2", "dead census 2": "dead_census2",
    "family": "family", "genus": "genus", "species": "species",
    "date census 1": "date_census1", "dbh 1": "dbh_census1",
    "date census 2": "date_census2", "dbh 2": "dbh_census2",
    "tree height 2011 (m)": "tree_height_2011_m", "comment": "comment",
    "collection": "JH_herbarium_census1", "dendrometer": "dendrometer",
    "leaf sample 2006 or 2011": "leaf_sample_census1",
    "wood sample 2011": "wood_sample_census1",
    "leaf sample 2025": "leaf_sample_census3",
    "wood sample 2025": "wood_sample_census3",
    "ind (1) branch (0)": "ind_tree1_branch0",
    "dead 2025": "dead_census3",
    "date census 3": "date_census3", "dbh 3": "dbh_census3",
    "tree height 2025 (ojo)": "height_census3_m",
    "new entry 2025": "new_entry_census3",
    "comment 2024": "comment_2024", "comment taxo": "comment_taxo",
    "Subplot": "subplot",
    "JH herbarium collections 2025": "JH_herbarium_census3",
}

# columnas que deben tratarse como numericas (para limpieza de coma decimal
# y para detectar valores tipo fecha metidos por error)
NUMERIC_COLS = {
    "dbh_census1", "dbh_census2", "dbh_census3",
    "tree_height_2011_m", "height_census3_m",
    "crust_thickness", "wet_wood_weight", "dry_wood_weight",
}
# columnas de texto libre a las que solo se les recorta espacios/saltos
TEXT_COLS = {"family", "genus", "species", "site", "comment", "comment_2024",
             "comment_taxo", "comment_extra"}
# columnas identificadoras -> se homogenizan a texto (sin '.0' de floats)
ID_COLS = {"treeID", "new_tree_ID", "PlotID", "Plot_num"}

NUMERIC_RE = re.compile(r"^-?\d+([.,]\d+)?$")


def clean_numeric(val):
    """Convierte a float números con coma decimal; deja NaN si es una fecha
    colada por error; deja el texto tal cual si es una categoría (p.ej.
    'tree (5cm<=dbh<10cm)') o una medida múltiple (p.ej. '1.9-3')."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, datetime):
        return None  # se reporta aparte en la hoja "Revisar"
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip()
        if NUMERIC_RE.match(s):
            return float(s.replace(",", "."))
        return s if s else None
    return val


def clean_text(val):
    if val is None:
        return None
    if isinstance(val, str):
        s = unicodedata.normalize("NFC", val).strip()
        s = re.sub(r"\s+", " ", s)
        return s if s else None
    return val


def clean_id(val):
    if val is None:
        return None
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return str(val)
    if isinstance(val, int):
        return str(val)
    if isinstance(val, str):
        return val.strip()
    return str(val)


def load_source(path, sheet, colmap, dataset_name, default_site=None):
    df = pd.read_excel(path, sheet_name=sheet, dtype=object)
    df.columns = [str(c).strip() if c is not None else c for c in df.columns]

    # columnas sin encabezado (p.ej. la ultima de Sumaco) -> comment_extra
    unnamed = [c for c in df.columns if c is None or str(c).startswith("Unnamed")]
    for c in unnamed:
        colmap = {**colmap, c: "comment_extra"}

    rename = {orig: std for orig, std in colmap.items() if orig in df.columns}
    missing_in_file = [orig for orig in colmap if orig not in df.columns]
    df = df.rename(columns=rename)

    # columnas del esquema estandar que este archivo no tiene -> se crean vacias
    for std_col in COLUMN_ORDER:
        if std_col not in df.columns:
            df[std_col] = None

    df["dataset"] = dataset_name
    if default_site is not None and df["site"].isna().all():
        df["site"] = default_site

    # limpieza por tipo
    review_rows = []
    for col in NUMERIC_COLS:
        for i, v in df[col].items():
            if isinstance(v, datetime):
                review_rows.append({
                    "dataset": dataset_name, "fila_excel_original": i + 2,
                    "PlotID": df.at[i, "PlotID"], "treeID": df.at[i, "treeID"],
                    "columna": col, "valor_original": str(v),
                    "motivo": "Valor tipo fecha en columna numerica; revisar archivo original",
                })
        df[col] = df[col].map(clean_numeric)

    for col in TEXT_COLS:
        df[col] = df[col].map(clean_text)

    for col in ID_COLS:
        df[col] = df[col].map(clean_id)

    df = df[COLUMN_ORDER]
    return df, pd.DataFrame(review_rows), missing_in_file


def main():
    gal, gal_rev, gal_missing = load_source(
        f"{UPLOADS}/Base_Galeras_vK.xlsx", "Galeras", MAP_GALERAS, "Galeras")
    sev, sev_rev, sev_missing = load_source(
        f"{UPLOADS}/Base_SelvaViva_v2.xlsx", "SelvaViva2024", MAP_SELVAVIVA,
        "SelvaViva", default_site="Selva Viva")
    sum_, sum_rev, sum_missing = load_source(
        f"{UPLOADS}/Sumaco_17092025.xlsx", "final", MAP_SUMACO, "Sumaco",
        default_site="Sumaco")

    unificado = pd.concat([gal, sev, sum_], ignore_index=True)
    revisar = pd.concat([gal_rev, sev_rev, sum_rev], ignore_index=True)

    # -----------------------------------------------------------------
    # Seguridad: algunas celdas originales (p.ej. columna 'collection' de
    # Sumaco) traen un '=' inicial que Excel/openpyxl interpretaria como
    # formula ('=3620,2526', '=#238', etc.), lo que produce errores
    # #NAME? al guardar. Es texto de campo, no una formula real: se quita
    # el '=' inicial y se deja registro en "Revisar".
    # -----------------------------------------------------------------
    formula_like_rows = []
    for col in unificado.columns:
        if unificado[col].dtype != object:
            continue
        mask = (unificado[col].astype(str).str.strip().str.startswith("=", na=False)
                & unificado[col].notna())
        for i in unificado.index[mask]:
            orig = unificado.at[i, col]
            fixed = orig.strip().lstrip("=").strip()
            formula_like_rows.append({
                "dataset": unificado.at[i, "dataset"], "fila_excel_original": None,
                "PlotID": unificado.at[i, "PlotID"], "treeID": unificado.at[i, "treeID"],
                "columna": col, "valor_original": orig,
                "motivo": "Celda empezaba con '=' (se leeria como formula); se quito el '=' y se dejo el texto",
            })
            unificado.at[i, col] = fixed
    if formula_like_rows:
        revisar = pd.concat([revisar, pd.DataFrame(formula_like_rows)], ignore_index=True)

    # -----------------------------------------------------------------
    # hoja de documentacion del mapeo de columnas
    # -----------------------------------------------------------------
    doc_rows = []
    for orig_map, dataset in [
        (MAP_GALERAS, "Galeras"), (MAP_SELVAVIVA, "SelvaViva"), (MAP_SUMACO, "Sumaco")
    ]:
        for orig, std in orig_map.items():
            doc_rows.append({"dataset": dataset, "columna_original": orig,
                              "columna_unificada": std})
    doc = pd.DataFrame(doc_rows).sort_values(["columna_unificada", "dataset"])

    resumen = pd.DataFrame({
        "dataset": ["Galeras", "SelvaViva", "Sumaco", "TOTAL"],
        "n_filas": [len(gal), len(sev), len(sum_), len(unificado)],
    })

    out_path = "/home/claude/forestal/Base_unificada_dinamica_forestal.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as xw:
        unificado.to_excel(xw, sheet_name="Datos_unificados", index=False)
        doc.to_excel(xw, sheet_name="Mapeo_columnas", index=False)
        resumen.to_excel(xw, sheet_name="Resumen", index=False)
        revisar.to_excel(xw, sheet_name="Revisar", index=False)

    print("Filas por dataset:")
    print(resumen)
    print("\nFilas a revisar (valores tipo fecha en columnas numericas):", len(revisar))
    print(revisar)
    print("\nColumnas del mapeo no encontradas en el archivo (revisar nombre exacto):")
    print(" Galeras:", gal_missing)
    print(" SelvaViva:", sev_missing)
    print(" Sumaco:", sum_missing)
    print("\nGuardado en:", out_path)


if __name__ == "__main__":
    main()
