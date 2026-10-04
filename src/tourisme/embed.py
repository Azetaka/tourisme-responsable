"""Embeddings Word2Vec des propositions """
import numpy as np
from gensim.models import Word2Vec

from tourisme.config import SEED

"""
Transformation des mots en vecteurs numériques, puis moyenne des vecteurs de mots pour representer une proposition ;
"""

def entrainer_w2v(corpus):
    w2v = Word2Vec(sentences=corpus,vector_size=100, window=5, min_count=3, sg=1, epochs=30,workers=1,seed=SEED)
    return w2v
# Vecteur de doc = moyenne des vecteurs de ses mots
def doc_vector_w2v(tokens, w2v):
    vecs = [w2v.wv[t] for t in tokens if t in w2v.wv]
    return np.mean(vecs, axis=0) if vecs else np.zeros(w2v.vector_size)

def calculer_embeddings(df_clean):
    """Renvoie une matrice (n_propositions, 100) de vecteurs normalisés."""
    corpus = df_clean["tokens"].tolist()
    w2v = entrainer_w2v(corpus)
    emb = np.vstack([doc_vector_w2v(t, w2v) for t in corpus])
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)
    return emb