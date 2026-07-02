import pandas as pd
def limpiar_bulk(bulk_2026,herb):
 bulk_2026["Sample-ID"] = bulk_2026["Sample-ID"].replace({"pxx: 8669":"p48-8669","pxx-8640":"p24-8640","jh3621":"jh-3621"}) ### REVISAR tapirila

 herb_2006 = bulk_2026[bulk_2026["Sample-ID"].str.contains("jh", na=False)]
 herb_2006[["Type","Plot","numeroCampo"]] = herb_2006["Sample-ID"].str.split("-",expand=True)
 herb_2006["numeroCampo"]=herb_2006["numeroCampo"].combine_first(herb_2006["Plot"])
 herb_2006 = herb_2006.drop(columns="Plot")
 herb["numeroCampo"] = pd.to_numeric(herb["numeroCampo"], errors="coerce")
 herb_2006["numeroCampo"] = pd.to_numeric(herb_2006["numeroCampo"], errors="coerce")

  # --- Merge ---
 df2026_herb = herb_2006.merge(herb, on="numeroCampo", how="left")
 # --- Separar columnas de description ---
 split_plot = df2026_herb["description"].str.split("#", n=1, expand=True)
 df2026_herb["Plot"] = split_plot[0]
 tree_info = split_plot[1].str.split(",", n=2, expand=True)

 df2026_herb["old_treeID"] = tree_info[0]
 df2026_herb["Plot"] = df2026_herb["Plot"].str.replace("plot", "", regex=False)

 # --- Filtrar Galeras ---
 patrones = ["60", "62", "22", "23", "24", "28", "48", "50", "29"]

 mask_galeras = df2026_herb["Plot"].astype(str).str.contains("|".join(patrones), na=False)
 herb_galeras = df2026_herb.loc[mask_galeras]
 herb_galeras["Year"] = 2006

 pulv2026 = bulk_2026[~bulk_2026["Sample-ID"].str.contains("jh", na=False)]#todo lo que no es herbario
 regex = r"p(" + "|".join(patrones) + r")\b"
 pulv2026 = pulv2026[pulv2026["Sample-ID"].str.contains(regex, na=False)] #Solo los que ya tienen plot aqui son del 2025
 pulv2026 [["Plot","new_TreeID"]] = pulv2026["Sample-ID"].str.split("-",expand=True)
 pulv2026["Year"]= 2025
 # --- Concatenar resultados ---
 bulklimpio_2026 = pd.concat([herb_galeras, pulv2026], ignore_index=True)
 return bulklimpio_2026


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
