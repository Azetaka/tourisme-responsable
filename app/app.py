"""Tableau de bord de la consultation sur le tourisme responsable."""
import textwrap
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# L'app lit uniquement les sorties du pipeline : elle ne recalcule rien.
DATA_PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
PROPOSITIONS_FILE = DATA_PROCESSED / "propositions.parquet"
THEMES_FILE = DATA_PROCESSED / "themes.parquet"

COULEUR = "#2E6F5E"
COULEUR_REJET = "#B5533C"
PALETTE_THEMES = px.colors.qualitative.Safe

# Colonnes en pourcentage : libellé affiché dans les tableaux
COLONNES_PCT = {
    "adhesion": "Adhésion",
    "faisabilite": "Faisabilité",
    "controverse": "Controverse",
    "score_like": "Taux de like",
    "score_dislike": "Taux de rejet",
}

st.set_page_config(page_title="Tourisme responsable", layout="wide")


@st.cache_data
def charger_resultats():
    df = pd.read_parquet(PROPOSITIONS_FILE)
    df_themes = pd.read_parquet(THEMES_FILE)
    return df, df_themes


def fmt(n):
    """Entier avec espace comme séparateur de milliers."""
    return f"{n:,.0f}".replace(",", " ")


def tableau_par_theme(d):
    """Indicateurs moyens par thème, triés par adhésion décroissante."""
    tab = (d.groupby("theme_nom")
           .agg(n=("content", "size"), adhesion=("adhesion", "mean"),
                faisabilite=("faisabilite", "mean"), controverse=("controverse", "mean"),
                score_like=("score_like", "mean"), score_dislike=("score_dislike", "mean"))
           .sort_values("adhesion", ascending=False).reset_index())
    return tab


def afficher_tableau(d, colonnes):
    """Affiche un tableau avec les taux en pourcentage."""
    d = d[list(colonnes)].copy()
    config = {col: st.column_config.Column(label) for col, label in colonnes.items()}
    for col in colonnes:
        if col in COLONNES_PCT:
            d[col] = d[col] * 100
            config[col] = st.column_config.NumberColumn(colonnes[col], format="%.1f %%")
    st.dataframe(d, column_config=config, hide_index=True, width="stretch")


if not PROPOSITIONS_FILE.exists():
    st.error("Les résultats sont introuvables. Lance d'abord : uv run python run_pipeline.py")
    st.stop()

df, df_themes = charger_resultats()

# Tranches d'âge classées de la plus jeune à la plus âgée
ordre_tranches = df.groupby("tranche")["author.age"].min().sort_values().index.tolist()

st.title("Tourisme responsable : que proposent les citoyens ?")
st.caption(
    f"Consultation « Comment agir pour un tourisme plus responsable en France ? ». "
    f"{fmt(len(df))} propositions regroupées en {df['theme_nom'].nunique()} thèmes."
)

# ── Filtres ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtres")
    themes_choisis = st.multiselect(
        "Thèmes", sorted(df["theme_nom"].unique()), placeholder="Tous les thèmes"
    )
    tranches_choisies = st.multiselect(
        "Tranches d'âge", ordre_tranches, placeholder="Toutes les tranches",
        help="Choisir une tranche écarte les propositions dont l'auteur n'a pas indiqué son âge.",
    )
    votes_min = st.slider(
        "Nombre minimum de votes",
        min_value=int(df["vote_total"].min()), max_value=int(df["vote_total"].max()),
        value=int(df["vote_total"].min()),
    )

df_f = df[df["vote_total"] >= votes_min]
if themes_choisis:
    df_f = df_f[df_f["theme_nom"].isin(themes_choisis)]
if tranches_choisies:
    df_f = df_f[df_f["tranche"].isin(tranches_choisies)]

if df_f.empty:
    st.warning("Aucune proposition ne correspond à ces filtres. Élargis la sélection.")
    st.stop()

onglet_vue, onglet_themes, onglet_priorites, onglet_explorer = st.tabs(
    ["Vue d'ensemble", "Thèmes", "Priorités", "Explorer"]
)

# ── Onglet 1 : vue d'ensemble ────────────────────────────────────────────────
with onglet_vue:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Propositions", fmt(len(df_f)))
    c2.metric("Votes exprimés", fmt(df_f["vote_total"].sum()))
    c3.metric("Adhésion moyenne", f"{df_f['adhesion'].mean():.0%}")
    age_median = df_f["author.age"].median()
    c4.metric("Âge médian des auteurs", f"{age_median:.0f} ans" if pd.notna(age_median) else "Non renseigné")

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.subheader("Propositions par thème")
        par_theme = df_f["theme_nom"].value_counts().reset_index()
        par_theme.columns = ["theme_nom", "n"]
        fig = px.bar(par_theme, x="n", y="theme_nom", orientation="h", text="n",
                     color_discrete_sequence=[COULEUR])
        fig.update_layout(xaxis_title="Nombre de propositions", yaxis_title=None,
                          yaxis={"categoryorder": "total ascending"},
                          margin=dict(l=0, r=20, t=10, b=0), height=380)
        st.plotly_chart(fig, width="stretch")

    with col_droite:
        st.subheader("Propositions par tranche d'âge")
        par_tranche = df_f["tranche"].value_counts().reindex(ordre_tranches, fill_value=0).reset_index()
        par_tranche.columns = ["tranche", "n"]
        fig = px.bar(par_tranche, x="tranche", y="n", text="n",
                     color_discrete_sequence=[COULEUR])
        fig.update_layout(xaxis_title=None, yaxis_title="Nombre de propositions",
                          margin=dict(l=0, r=20, t=10, b=0), height=380)
        st.plotly_chart(fig, width="stretch")
        sans_age = int(df_f["tranche"].isna().sum())
        if sans_age:
            st.caption(f"{fmt(sans_age)} propositions sans âge renseigné ne figurent pas sur ce graphique.")

# ── Onglet 2 : thèmes ────────────────────────────────────────────────────────
with onglet_themes:
    tab = tableau_par_theme(df_f)

    st.subheader("Indicateurs par thème")
    st.caption(
        "Adhésion : part des votes « d'accord ». "
        "Faisabilité : part des votes « d'accord » accompagnés de la mention « faisable ». "
        "Controverse : part des votes « pas d'accord »."
    )
    afficher_tableau(tab, {"theme_nom": "Thème", "n": "Propositions", "adhesion": "Adhésion",
                           "faisabilite": "Faisabilité", "controverse": "Controverse"})

    st.subheader("Likes et rejets par thème")
    st.caption("Taux moyen de « J'aime » et de rejet (« Pas question » ou « Banalité »), rapportés au total des votes.")
    likes = tab.melt(id_vars="theme_nom", value_vars=["score_like", "score_dislike"],
                     var_name="indicateur", value_name="taux")
    likes["indicateur"] = likes["indicateur"].map({"score_like": "Taux de like", "score_dislike": "Taux de rejet"})
    fig = px.bar(likes, x="taux", y="theme_nom", color="indicateur", barmode="group", orientation="h",
                 color_discrete_map={"Taux de like": COULEUR, "Taux de rejet": COULEUR_REJET})
    fig.update_layout(xaxis_title="Taux moyen", yaxis_title=None, legend_title=None,
                      xaxis_tickformat=".0%", yaxis={"categoryorder": "total ascending"},
                      margin=dict(l=0, r=20, t=10, b=0), height=420)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Thèmes abordés selon l'âge")
    df_age = df_f.dropna(subset=["tranche"])
    if df_age.empty:
        st.info("Aucune proposition de la sélection n'a d'âge renseigné.")
    else:
        tab_age = df_age.groupby(["tranche", "theme_nom"]).size().unstack(fill_value=0)
        tab_age = tab_age.reindex([t for t in ordre_tranches if t in tab_age.index])
        tab_age_pct = tab_age.div(tab_age.sum(axis=1), axis=0) * 100
        st.caption("Part de chaque thème dans les propositions d'une tranche d'âge (chaque ligne totalise 100 %).")
        fig = px.imshow(tab_age_pct.round(1), text_auto=True, aspect="auto",
                        color_continuous_scale="Teal", labels=dict(color="%"))
        fig.update_layout(xaxis_title=None, yaxis_title=None,
                          margin=dict(l=0, r=20, t=10, b=0), height=300)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Carte des propositions")
    st.caption("Projection t-SNE : deux propositions proches emploient un vocabulaire voisin. Survole un point pour lire la proposition.")
    carte = df_f.copy()
    carte["texte"] = carte["content"].apply(lambda c: "<br>".join(textwrap.wrap(c, 60)))
    fig = px.scatter(carte, x="x", y="y", color="theme_nom", custom_data=["texte", "theme_nom"],
                     color_discrete_sequence=PALETTE_THEMES,
                     category_orders={"theme_nom": sorted(df["theme_nom"].unique())})
    fig.update_traces(marker=dict(size=6, opacity=0.7),
                      hovertemplate="<b>%{customdata[1]}</b><br>%{customdata[0]}<extra></extra>")
    fig.update_layout(legend_title=None, margin=dict(l=0, r=0, t=10, b=0), height=560)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    st.plotly_chart(fig, width="stretch")

    with st.expander("Comment lire les thèmes : termes distinctifs et proposition type"):
        st.dataframe(
            df_themes[["theme_nom", "termes", "exemple"]],
            column_config={"theme_nom": "Thème", "termes": "Termes distinctifs", "exemple": "Proposition la plus centrale"},
            hide_index=True, width="stretch",
        )

# ── Onglet 3 : priorités ─────────────────────────────────────────────────────
with onglet_priorites:
    tab = tableau_par_theme(df_f)

    st.subheader("Adhésion et faisabilité par thème")
    st.caption("En haut à droite : les thèmes à la fois soutenus et jugés faisables. La taille d'un point suit le nombre de propositions.")
    fig = px.scatter(tab, x="adhesion", y="faisabilite", size="n", text="theme_nom",
                     color_discrete_sequence=[COULEUR], size_max=40)
    fig.update_traces(textposition="top center")
    fig.update_layout(xaxis_title="Adhésion moyenne", yaxis_title="Faisabilité moyenne",
                      xaxis_tickformat=".0%", yaxis_tickformat=".0%",
                      margin=dict(l=0, r=20, t=30, b=0), height=480)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Propositions les mieux notées")
    col_critere, col_nombre = st.columns([2, 1])
    criteres = {"Adhésion": "adhesion", "Faisabilité": "faisabilite", "Taux de like": "score_like"}
    critere = col_critere.selectbox("Classer par", list(criteres))
    nombre = col_nombre.slider("Nombre de propositions", min_value=5, max_value=30, value=10)
    st.caption(
        f"Classement parmi les propositions ayant reçu au moins {fmt(votes_min)} votes. "
        "Ce seuil se règle dans la barre latérale : plus il est haut, plus les taux sont fiables."
    )
    top = df_f.sort_values(criteres[critere], ascending=False).head(nombre)
    afficher_tableau(top, {"content": "Proposition", "theme_nom": "Thème", "vote_total": "Votes",
                           "adhesion": "Adhésion", "faisabilite": "Faisabilité",
                           "controverse": "Controverse", "score_like": "Taux de like"})

# ── Onglet 4 : explorer ──────────────────────────────────────────────────────
with onglet_explorer:
    recherche = st.text_input("Rechercher dans les propositions", placeholder="Par exemple : train, plastique, camping")
    resultat = df_f
    if recherche:
        resultat = df_f[df_f["content"].str.contains(recherche, case=False, regex=False)]

    if resultat.empty:
        st.info(f"Aucune proposition ne contient « {recherche} ». Essaie un autre mot.")
    else:
        st.caption(f"{fmt(len(resultat))} propositions, triées par nombre de votes.")
        afficher_tableau(resultat.sort_values("vote_total", ascending=False),
                         {"content": "Proposition", "theme_nom": "Thème", "tranche": "Tranche d'âge",
                          "vote_total": "Votes", "adhesion": "Adhésion", "faisabilite": "Faisabilité",
                          "controverse": "Controverse", "score_like": "Taux de like"})