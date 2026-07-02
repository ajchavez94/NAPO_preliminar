co2_dict = { 
    2005:(-8.24, 379.98), 
    2006:(-8.28, 382.09), 
    2007:(-8.27, 384.02), 
    2009: (-8.39, 387.64), 
    2011: (-8.27, 387.64), 
    2023: (-8.6, 423.1142299) }

def formula_iWUE(row, delt13Cair, Cair):
    a = 4.4
    b = 27
    f = 12
    cP = 40
    d13 = 'δ13C (‰ v.s.V-PDB)'

    row["△13C_cell"] = (delt13Cair - row[d13]) / (1 + (row[d13] / 1000))
    row["Ci"] = (Cair * (row["△13C_cell"] - a) + f * cP) / (b - a)
    row["Ci/Ca"] = row["Ci"] / Cair
    row["iWUE (μmol/mol)"] = (Cair / 1.6) * (1 - (row["Ci"] / Cair))

    return row


def calculate_iWUE(row, co2_dict):
    year = row["Year"]

    if year not in co2_dict:
        return row  # evita crash si no hay datos

    delt13Cair, Cair = co2_dict[year]

    return formula_iWUE(row, delt13Cair, Cair)