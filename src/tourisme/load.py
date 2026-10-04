"""Chargement du JSON brut et mise à plat des votes"""
import json

import pandas as pd

from tourisme.config import RAW_FILE


# Les votes sont imbriqués (vote principal + qualifications). On les met à plat.
def extraire_votes(liste_votes):
    res = {"vote_agree": 0, "vote_neutral": 0, "vote_disagree": 0,
           "qualif_likeIt": 0, "qualif_platitudeAgree": 0, "qualif_doable": 0,
           "qualif_noOpinion": 0, "qualif_doNotUnderstand": 0, "qualif_doNotCare": 0,
           "qualif_impossible": 0, "qualif_noWay": 0, "qualif_platitudeDisagree": 0,
           }
    if isinstance(liste_votes, list):
        for v in liste_votes:
            k = v.get("voteKey")
            if f"vote_{k}" in res:
                res[f"vote_{k}"] = v.get("count", 0)
            for q in v.get("qualifications", []):
                qk = q.get("qualificationKey")
                if f"qualif_{qk}" in res:
                    res[f"qualif_{qk}"] = q.get("count", 0)
    return pd.Series(res)


def charger_donnees(chemin=RAW_FILE):
    """Lit le JSON et renvoie une ligne par proposition."""
    with open(chemin, "r", encoding="utf-8") as f:
        data = json.load(f)

    df_raw = pd.json_normalize(data["results"])
    votes_flat = df_raw["votes"].apply(extraire_votes)
    df = pd.concat([df_raw[["content", "author.age"]], votes_flat], axis=1)

    # Nettoyage léger : retrait de l'amorce "Il faut", total des votes, longueur.
    df["content"] = df["content"].str.replace(r"^[Ii]l faut\s*", "", regex=True)
    df["vote_total"] = df["vote_agree"] + df["vote_neutral"] + df["vote_disagree"]
    df["nb_mots"] = df["content"].str.split().str.len()
    df["nb_car"] = df["content"].str.len()
    return df