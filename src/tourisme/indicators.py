"""Indicateurs par proposition et tableaux par thème."""
from tourisme.config import TRANCHES


def calculer_indicateurs(df_clean):
    """Ajoute adhésion, faisabilité, controverse et taux de like / dislike."""
    df_clean = df_clean.copy()
    df_clean["adhesion"]    = df_clean["vote_agree"] / df_clean["vote_total"]
    df_clean["faisabilite"] = df_clean["qualif_doable"] / df_clean["vote_agree"].clip(lower=1)
    df_clean["controverse"] = df_clean["vote_disagree"] / df_clean["vote_total"]
    df_clean["score_like"]    = df_clean["qualif_likeIt"] / df_clean["vote_total"].clip(lower=1)
    df_clean["score_dislike"] = (
        df_clean["qualif_noWay"] + df_clean["qualif_platitudeDisagree"]
    ) / df_clean["vote_total"].clip(lower=1)
    return df_clean


def assigner_tranche(age):
    for label, (low, high) in TRANCHES.items():
        if low <= age <= high:
            return label
    return "Autre"


def ajouter_tranche_age(df_clean):
    """Ajoute la tranche d'âge de l'auteur. Âge inconnu : la tranche reste vide."""
    df_clean = df_clean.copy()
    df_clean["tranche"] = df_clean["author.age"].map(assigner_tranche, na_action="ignore")
    return df_clean

def tableau_themes(df_clean):
    tab = (df_clean.groupby("theme_nom")
           .agg(n=("content","size"), adhesion=("adhesion","mean"),
                faisabilite=("faisabilite","mean"), controverse=("controverse","mean"))
           .round(3).sort_values("adhesion", ascending=False))
    return tab


def tableau_likes(df_clean):
    tab_like = (
        df_clean.groupby("theme_nom")
        .agg(
            like_brut   = ("qualif_likeIt", "sum"),
            like_taux   = ("score_like",    "mean"),
            dislike_brut= ("qualif_noWay",  "sum"),  
            dislike_taux= ("score_dislike", "mean"),
        )
        .round(4)
        .sort_values("like_taux", ascending=False)
    )
    return tab_like