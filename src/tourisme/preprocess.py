"""Lemmatisation des propositions avec spaCy"""
import spacy

from tourisme.config import KEEP_POS, EXTRA_STOPS

nlp = spacy.load("fr_core_news_sm", disable=["parser", "ner"])

def lemmatiser(doc):
    return [t.lemma_.lower() for t in doc
            if t.pos_ in KEEP_POS and not t.is_stop and not t.is_punct
            and not t.like_num and len(t.lemma_) >= 3
            and t.lemma_.lower() not in EXTRA_STOPS]

def preparer_textes(df):
    """Ajoute les tokens lemmatisés et retire les propositions vides après nettoyage."""
    df = df.copy()
    df["tokens"] = [lemmatiser(doc) for doc in nlp.pipe(df["content"].fillna(""), batch_size=256)]
    df_clean = df[df["tokens"].apply(len) > 0].reset_index(drop=True)
    df_clean["clean"] = df_clean["tokens"].apply(lambda x: " ".join(x))
    return df_clean