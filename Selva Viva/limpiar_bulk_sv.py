import pandas as pd
import pandas as pd

def limpiar_bulk(bulk_2026, herb):
    # Trabajar sobre copias para no modificar los DataFrames originales
    bulk_2026 = bulk_2026.copy()
    herb = herb.copy()

    bulk_2026["Sample-ID"] = bulk_2026["Sample-ID"].replace({
        "pxx: 8669": "p48-8669",
        "pxx-8640": "p24-8640",
        "jh3621": "jh-3621",
        "jh-pxx-3708": "jh-p48-3708",
    })  # REVISAR tapirila

    # --- Herbario (2006) ---
    herb_2006 = bulk_2026[bulk_2026["Sample-ID"].str.contains("jh", na=False)].copy()

    # reindex evita ValueError si algún ID tiene 2 partes en vez de 3
    partes = herb_2006["Sample-ID"].str.split("-", expand=True).reindex(columns=range(3))
    herb_2006["Type"] = partes[0]
    herb_2006["numeroCampo"] = partes[2].combine_first(partes[1])  # jh-3621 -> 3621; jh-p48-3708 -> 3708

    herb["numeroCampo"] = pd.to_numeric(herb["JH"], errors="coerce")
    herb_2006["numeroCampo"] = pd.to_numeric(herb_2006["numeroCampo"], errors="coerce")

    # --- Merge ---
    df2026_herb = herb_2006.merge(herb, on="numeroCampo", how="left")

    # --- Separar description ---
    split_plot = df2026_herb["description"].str.split("#", n=1, expand=True).reindex(columns=range(2))
    df2026_herb["Plot"] = split_plot[0].str.replace("plot", "", regex=False).str.strip()
    tree_info = split_plot[1].str.split(",", n=2, expand=True)
    df2026_herb["old_treeID"] = tree_info[0]

    # --- Filtrar Galeras ---
    patrones = ["68", "69", "70", "72", "74"]
    mask_galeras = df2026_herb["Plot"].astype(str).str.contains("|".join(patrones), na=False)
    herb_galeras = df2026_herb.loc[mask_galeras].copy()
    herb_galeras["Year"] = 2006

    # --- Pulverizados (2025) ---
    pulv2026 = bulk_2026[~bulk_2026["Sample-ID"].str.contains("jh", na=False)]
    regex = r"p(" + "|".join(patrones) + r")\b"
    pulv2026 = pulv2026[pulv2026["Sample-ID"].str.contains(regex, na=False)].copy()
    partes = pulv2026["Sample-ID"].str.split("-", n=1, expand=True).reindex(columns=range(2))
    pulv2026["Plot"] = partes[0]
    pulv2026["new_TreeID"] = partes[1]
    pulv2026["Year"] = 2025

    # --- Concatenar ---
    bulklimpio_2026 = pd.concat([herb_galeras, pulv2026], ignore_index=True)
    bulklimpio_2026 = bulklimpio_2026.rename(
        columns={"familia": "family", "genero": "genus", "especie": "species"}
    )
    return bulklimpio_2026[[
        "Sample-ID", "[N]", "[C_b]%", "δ15N (‰ v.s. V-PDB)", "bulk_δ13C (‰ v.s.V-PDB)",
        "numeroCampo", "description", "family", "genus", "species",
        "old_treeID", "new_TreeID", "Plot",
    ]]


excluir = [
    "parkia-8634", #son muestras controles de otros lados
    "46093-my",
    "46185-my",
    "46145-my",
    "46232-my",
    "46144-my",
    "46152-my",
    "46186-al",
    "46143-al",
    "46237-al",
    "46094-al",
    "46142-al",
    "46097-al",
    "46229-al",
    "46189-al",
    "56127",
    "56074",
    "56078",
    "tapirila"
 ]



