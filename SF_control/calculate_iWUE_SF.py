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


def calculate_iWUE(row):

    if row["Year"] == 2009:
        delt13Cair = -8.27
        Cair = 387.64

    elif row["Year"] == 2011:
        delt13Cair = -8.27
        Cair = 387.64

    elif row["Year"] == 2023:
        delt13Cair = -8.6
        Cair = 423.1142299

    else:
        return row  # importante evitar crash

    row = formula_iWUE(row, delt13Cair, Cair)

    return row

co2_dict = {
    2009: (-8.27, 387.64),
    2011: (-8.27, 387.64),
    2024: (-8.6, 423.1142299)
}