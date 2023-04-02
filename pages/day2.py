import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import math

st.set_page_config(
    page_title="#30DayChartChallenge, Day 2: Waffle Chart by Oleh Omelchenko", 
    # page_icon=None, 
    layout="wide", 
    # initial_sidebar_state="auto", 
    # menu_items=None
)


df_init = pd.read_csv("data/share-elec-by-source.csv")

"""
# #30DayChartChallenge, Day 2: Waffle Chart
"""

ENTITIES, YEARS = st.columns(2)

ENTITIES = ENTITIES.multiselect(
    "Entities", list(df_init.Entity.unique()), default=["Ukraine", "Europe", "World"]
)

YEARS = YEARS.multiselect(
    "Years", sorted(list(df_init.Year.unique())), default=[2000, 2021]
)

df = df_init.copy()
df = (
    df.query("Entity in @ENTITIES")
    .query("Year in @YEARS")
    .melt(id_vars=["Entity", "Year"])
)
df = df[df["variable"].str.contains("%")].reset_index(drop=True)
df['value'] = df['value'].fillna(0.)
df['value_precise'] = df['value'] / 100
df["value"] = (df["value"].apply(float) * 1).apply(round)

df_raw = df.copy()


repeat_indices = np.repeat(df.index, df["value"])
result = df.loc[repeat_indices].reset_index(drop=True)
result["cnt"] = 1
result = result.sort_values(["Entity", "Year", "value"], ascending=[True, True, True])

df = result.copy()

lists = []
for _, g in df.groupby(["Entity", "Year"]):
    g = g.sort_values(["value", "variable"], ascending=False)
    g["x"] = [i % 10 for i, val in enumerate(range(len(g)))]
    g["y"] = [math.floor(i / 10) for i, val in enumerate(range(len(g)))]
    lists.append(g)
df = pd.concat(lists)

domains = [
    "Oil (% electricity)",
    "Hydro (% electricity)",
    "Gas (% electricity)",
    "Coal (% electricity)",
    "Nuclear (% electricity)",
    "Bioenergy (% electricity)",
    "Solar (% electricity)",
    "Wind (% electricity)",
    "Other renewables excluding bioenergy (% electricity)"
]

emo = ["🛢️", "🌊", "🟦", "⬛️", "☢️", "🌿", "☀️", "💨", "⚪️"]

df["emoji"] = df["variable"].map(dict(zip(domains, emo)))
with st.expander("Code for the graph"): 
    with st.echo():
        chart = (
            alt.Chart(df)
            .mark_text(size=18)
            .encode(
                x=alt.X("y:O", title=None, axis=None),
                y=alt.Y("x:O", title=None, axis=None, scale=alt.Scale(reverse=True)),
                text="emoji:O",
                column=alt.Column(
                    "Entity",
                    title=None,
                    header=alt.Header(
                        labelFont="Lucida Console",
                        labelFontSize=20,
                        labelColor="#074985",
                    ),
                    sort=list(ENTITIES),
                ),
                row=alt.Row(
                    "Year",
                    header=alt.Header(
                        labelAngle=0,
                        labelAlign="left",
                        # labelOrient='right',
                        labelFont="Lucida Console",
                        labelFontSize=20,
                        labelColor="#074985",
                    ),
                    title=None,
                ),
                tooltip=["Entity", "Year", "variable", alt.Tooltip("value_precise", format=".2%")],
            )
            .properties(
                title={
                    "text": [
                        "Share of electricity production by source", 
                    ", ".join(ENTITIES), 
                    ", ".join([str(_) for _ in YEARS])
                    ],
                    "subtitle": [
                        "Each emoji represents 1% of corresponding energy source's contribution",
                        "to the total electricity production in a given entity in a given year.",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "Oil 🛢️",
                        "Hydro 🌊",
                        "Gas 🟦",
                        "Coal ⬛️",
                        "Nuclear ☢️",
                        "Bioenergy 🌿",
                        "Solar ☀️",
                        "Wind 💨",
                        "Other ⚪️"
                    ]
                },
                width=200,
                height=200,
            )
            .configure(background="#DDEEFF", padding=30)
            .configure_title(
                orient="top",
                fontSize=20,
                color="#074985",
                subtitleColor="#074985",
                # font='Impact',
                subtitleFont="Lucida Console",
                subtitlePadding=10,
                dy=250,
                dx=100,
                anchor="end",
            )
            # .configure_view(strokeWidth=0)
        )

st.altair_chart(chart)


with st.expander("raw data"):
    df_raw