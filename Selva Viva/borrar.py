SEQ1= pd.read_excel(r"C:\Users\selene.baez\Downloads\NAPO_preliminar\Results_isofys\Andrea_bulk CN_2025.xlsx",sheet_name="SEQ1")
SEQ1["Year"] = 2006
SEQ2 = pd.read_excel(r"C:\Users\selene.baez\Downloads\NAPO_preliminar\Results_isofys\Andrea_bulk CN_2025.xlsx",sheet_name="SEQ2")
SEQ2["Year"] = 2006
SEQ4 = pd.read_excel(r"C:\Users\selene.baez\Downloads\NAPO_preliminar\Results_isofys\Andrea_bulk CN_2025.xlsx",sheet_name="SEQ4")
SEQ4["Year"] = 2025
SEQ5 = pd.read_excel(r"C:\Users\selene.baez\Downloads\NAPO_preliminar\Results_isofys\Andrea_bulk CN_2025.xlsx",sheet_name="SEQ5")
SEQ5["Year"] = 2025
SEQ7 = pd.read_excel(r"C:\Users\selene.baez\Downloads\NAPO_preliminar\Results_isofys\Andrea_bulk CN_2025.xlsx",sheet_name="SEQ7")
SEQ7["Year"] = 2006

bulk = pd.concat([SEQ1,SEQ2,SEQ4,SEQ5,SEQ7])
bulk = bulk.rename(columns={"certified values":"sample-ID", "Unnamed: 2":"[N]",
                            "Unnamed: 4":nameC_bulk,"Unnamed: 6":named15N,
                            "Unnamed: 8":named13C_bulk})


bulk[["Plot","TreeID","add"]] =bulk["sample-ID"].str.split("-",expand=True) #len 182
columns_drop = ["Unnamed: 0", "Unnamed: 3","Unnamed: 5","Unnamed: 7", "Unnamed: 9","Unnamed: 10","Unnamed: 11","Unnamed: 12"]
bulk = bulk.drop(columns=columns_drop)
patrones = ["p68", "p69", "p70","p74","p72"]

df_filtrado_bulk = bulk[bulk["sample-ID"].str.contains("|".join(patrones), na=False)]
df_filtrado_bulk = df_filtrado_bulk.drop(columns = {"Plot","Year","TreeID"}) #la de celulosa tiene la misma informacion.
#Here 43 samples and everything is complete
