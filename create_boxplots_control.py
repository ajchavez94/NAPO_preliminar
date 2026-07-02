def create_boxplots_control(var, data):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from matplotlib.patches import Rectangle

    # -----------------------------
    # Data preparation
    # -----------------------------
    #if var == "Narea":
    #       print("Cleaning outliers of Narea")
    #       data = data[data["Narea"] <= 0.5] #only maintain values lower than 0.5
    
    #elif var == "[N]":
    #       print("Cleaning outliers of Narea")
    #       data = data[data["[N]"] <= 0.025] #only maintain values lower than 0.025
    

    df_long = pd.melt(
        data,
        id_vars=["name", "Sub"],
        value_vars=[var],
        var_name="variable",
        value_name="valor"
    )

    orden = ["C", "N", "NP","P"]
    df_long["Sub"] = pd.Categorical(df_long["Sub"], categories=orden, ordered=True)

    altitud_map = {
        "Weinmania  loxensis": "3000",
        "Hedyosmun  purpurascens": "3000",
        "Myrcia sp nov": "2000",
        "Alchornea lojaensis": "2000",
        "Pouteria torta": "1000",
        "Clarisia  racemosa": "1000"
    }
    df_long["altitud"] = df_long["name"].map(altitud_map)

    # -----------------------------
    # FIXED ORDER OF 6 PANELS
    # -----------------------------
    final_order = [
        "Pouteria torta",       # 1000
        "Clarisia  racemosa",   # 1000
        "Myrcia sp nov",        # 2000
        "Alchornea lojaensis",  # 2000
        "Hedyosmun  purpurascens",  # 3000
        "Weinmania  loxensis"   # 3000
    ]

    final_order_23 = [
        "Pouteria torta",       # 1000
        "Myrcia sp nov",        # 2000
        "Hedyosmun  purpurascens",  # 3000
        "Clarisia  racemosa",   # 1000
        "Alchornea lojaensis",  # 2000
        "Weinmania  loxensis",   # 3000
    ]

    df_long["name"] = pd.Categorical(df_long["name"], categories=final_order_23, ordered=True)

    # -----------------------------
    # Color palette
    # -----------------------------
    palette_Sub = {
        "C": "#A3A3A3",
        "N": "#4619eb",
        "P": "#FFFC40FF",
        "NP": "#ff2b47",
    }

    sns.set(style="whitegrid")

    # -----------------------------
    # CREATE EXACTLY 6 AXES (2 × 3)
    # -----------------------------
    fig, axes = plt.subplots(2, 3, figsize=(10, 7), sharey=True,sharex=True)
    axes = axes.flatten()

    # -----------------------------
    # PLOT EACH SPECIES
    # -----------------------------
    for i, sp in enumerate(final_order_23):
        ax = axes[i]
        subdf = df_long[df_long["name"] == sp]
        
        sns.boxplot(
            data=subdf,
            x="Sub", y="valor",
            #palette=palette_Sub,
            color=".9", 
            linecolor="black", linewidth=.85,
            showmeans=True,
            meanprops={"marker": "s",
                       "markerfacecolor": "black",
                        "markeredgecolor":"black",
                       "markersize": "4"},
            width = 0.65,
            ax=ax
        )

        sns.swarmplot(
            data=subdf,
            x="Sub", y="valor",
            palette=palette_Sub,
            color="grey",
            dodge=False,
            ax=ax,
            alpha=0.9
        )


        # Mean control
        control_mean = subdf[subdf["Sub"] == "C"]["valor"].mean()
        if not pd.isna(control_mean):
            ax.axhline(control_mean, linestyle="--", color="black", linewidth=1)

        # Italic species name
        formatted_name = sp.replace(' ', '.') # e.g.
        ax.set_title(f"$\\it{{{formatted_name}}}$", fontsize=10, loc= "left")

        # Elevation box
        elev = subdf["altitud"].iloc[0]
        ax.text(
            0.95, 1.25, f"{elev} m",
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=10,
            bbox=dict(facecolor="white", edgecolor="black"),
            clip_on=False                    # IMPORTANT: allow drawing outside axes
        )
        #if name = Pouteria then 
        # sig. 
        # ax.text(
        #0.4, 0.955,  # x=0.5 centers horizontally, y>1 is above the axes
        #"35%\n***",      # your text (e.g., % from model)
        #transform=ax.transAxes,
        #ha="center",  # center text above the axis
        #va="bottom",  # align the bottom of text to this y
        #fontsize=10,
        #clip_on=False  # ensures text appears outside the axis
        # )

        ax.set_xlabel("")


    # LABELS
    # -----------------------------
    fig.supxlabel("Treatment", fontsize=13)
    fig.supylabel(var, fontsize=13)

    fig.tight_layout()
    return fig


