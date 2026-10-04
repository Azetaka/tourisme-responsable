"""Chemins du projet"""
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

DATA_RAW = RACINE / "data" / "raw"
DATA_PROCESSED = RACINE / "data" / "processed"

RAW_FILE = DATA_RAW / "data_tourisme.json"

KEEP_POS = {"NOUN", "VERB", "ADJ", "ADV"}
EXTRA_STOPS = {"être", "avoir", "faire", "devoir", "pouvoir", "falloir", "aller", "mettre","dire", "vouloir", "prendre", "donner", "voir", "plus", "très",
               "tourisme", "touristique", "touriste", "voyage", "voyageur","bien", "tout", "même", "aussi", "ainsi","développer", "proposer", "favoriser", 
               "créer","promouvoir", "encourager", "inciter","place", "lieu", "lieux","ensemble", "long",}

# Reproductibilité
SEED = 42

# Clustering
K = 8

# Noms des thèmes (numéros issus du KMeans avec K = 8 et SEED = 42)
NOMS_THEMES = {
    0: "Équipements de site (plein air)",
    1: "Vélo & véloroutes",
    2: "Acteurs & tourisme local",
    3: "Contraintes & interdictions",
    4: "Protection nature & déchets",
    5: "Transports en commun & rail",
    6: "Maîtrise de la fréquentation",
    7: "Information & sobriété",
}

# Tranches d'âge des auteurs
TRANCHES = {
    "Jeunes (< 30 ans)":         (0,  29),
    "Trentenaires (30–49 ans)":  (30, 49),
    "Seniors (≥ 50 ans)":        (50, 120),
}

# Sorties du pipeline
PROPOSITIONS_FILE = DATA_PROCESSED / "propositions.parquet"
THEMES_FILE = DATA_PROCESSED / "themes.parquet"