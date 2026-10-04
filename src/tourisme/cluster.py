"""Clustering KMeans des propositions et description des thèmes"""
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

from tourisme.config import K, NOMS_THEMES, SEED


def scores_silhouette(emb):
    scores = []
    for k in range(4, 11):
        km_test = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(emb)
        scores.append((k, silhouette_score(emb, km_test.labels_)))
    df_sil = pd.DataFrame(scores, columns=["k", "silhouette"])
    return df_sil


def attribuer_themes(df_clean, emb):
    """Ajoute la colonne theme et renvoie aussi le modèle KMeans."""
    km = KMeans(n_clusters=K, random_state=SEED, n_init=10).fit(emb)
    df_clean = df_clean.copy()
    df_clean["theme"] = km.labels_
    df_clean["theme_nom"] = df_clean["theme"].map(NOMS_THEMES)
    return df_clean, km


def termes_distinctifs(df_clean, theme, n=8, min_occ=8):
    freq_glob = Counter(m for toks in df_clean["tokens"] for m in toks)
    total_glob = sum(freq_glob.values())
    toks = df_clean.loc[df_clean["theme"] == theme, "tokens"]
    fc = Counter(m for l in toks for m in l)
    tc = sum(fc.values())
    sc = {m: (v / tc) / (freq_glob[m] / total_glob) for m, v in fc.items() if v >= min_occ}
    return [m for m, _ in sorted(sc.items(), key=lambda x: -x[1])[:n]]


def resumer_themes(df_clean, emb, km):
    """Une ligne par thème : effectif, termes distinctifs, proposition la plus centrale."""
    resume = []
    for t in range(K):
        sub = df_clean[df_clean["theme"] == t]
        idx = np.where(km.labels_ == t)[0]
        central = idx[(emb[idx] @ km.cluster_centers_[t]).argmax()]
        resume.append({"theme": t, "n": len(sub),
                       "termes": ", ".join(termes_distinctifs(df_clean, t)),
                       "exemple": df_clean["content"].iloc[central][:95]})
    df_themes = pd.DataFrame(resume)
    return df_themes


def projeter_tsne(df_clean, emb):
    """Ajoute les coordonnées x et y de la projection t-SNE."""
    coords = TSNE(n_components=2, random_state=SEED, perplexity=30, init="pca").fit_transform(emb)
    df_clean = df_clean.copy()
    df_clean["x"], df_clean["y"] = coords[:, 0], coords[:, 1]
    return df_clean