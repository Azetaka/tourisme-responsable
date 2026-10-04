"""Exécute le pipeline complet et écrit les résultats dans data/processed/."""
from tourisme.cluster import attribuer_themes, projeter_tsne, resumer_themes
from tourisme.config import DATA_PROCESSED, NOMS_THEMES, PROPOSITIONS_FILE, THEMES_FILE
from tourisme.embed import calculer_embeddings
from tourisme.indicators import ajouter_tranche_age, calculer_indicateurs
from tourisme.load import charger_donnees
from tourisme.preprocess import preparer_textes


def main():
    print("1/5 Chargement des données")
    df = charger_donnees()

    print("2/5 Lemmatisation")
    df_clean = preparer_textes(df)

    print("3/5 Embeddings Word2Vec")
    emb = calculer_embeddings(df_clean)

    print("4/5 Clustering et projection t-SNE")
    df_clean, km = attribuer_themes(df_clean, emb)
    df_themes = resumer_themes(df_clean, emb, km)
    df_themes["theme_nom"] = df_themes["theme"].map(NOMS_THEMES)
    df_clean = projeter_tsne(df_clean, emb)

    print("5/5 Indicateurs")
    df_clean = calculer_indicateurs(df_clean)
    df_clean = ajouter_tranche_age(df_clean)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(PROPOSITIONS_FILE, index=False)
    df_themes.to_parquet(THEMES_FILE, index=False)
    print(f"{len(df_clean)} propositions -> {PROPOSITIONS_FILE}")
    print(f"{len(df_themes)} thèmes -> {THEMES_FILE}")


if __name__ == "__main__":
    main()