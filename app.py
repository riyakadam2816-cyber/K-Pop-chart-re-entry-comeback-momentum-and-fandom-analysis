import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="South Korea K-Pop Analytics",
    page_icon="🎵",
    layout="wide"
)

# =========================================================
# PROFESSIONAL DASHBOARD STYLE
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b0f19;
    color: #f8fafc;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #171426 0%,
        #211b38 100%
    );
    border-right: 1px solid #34304a;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff;
}

h1 {
    color: #ffffff !important;
    font-weight: 800 !important;
}

h2 {
    color: #f8fafc !important;
    font-weight: 750 !important;
}

h3 {
    color: #e2e8f0 !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #171d2b,
        #111622
    );
    border: 1px solid #30394d;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.25);
}

div[data-testid="stMetricLabel"] {
    color: #aeb8ca !important;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800;
}

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #30394d;
}

hr {
    border-color: #30394d !important;
}

</style>
""", unsafe_allow_html=True)
# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    clean = pd.read_csv("kpop_cleaned_data.csv")
    reentry = pd.read_csv("kpop_reentry_analysis.csv")
    momentum = pd.read_csv("kpop_comeback_momentum.csv")
    fandom = pd.read_csv("kpop_fandom_intensity.csv")
    album = pd.read_csv("kpop_album_analysis.csv")
    content = pd.read_csv("kpop_content_analysis.csv")

    return clean, reentry, momentum, fandom, album, content


df, reentry_df, momentum_df, fandom_df, album_df, content_df = load_data()

# =========================================================
# GLOBAL FILTERS
# =========================================================

# Convert date column
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Sidebar filters
st.sidebar.markdown("### 🔎 Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply date filter
if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered_df = df[
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ].copy()

else:

    filtered_df = df.copy()

    # =========================================================
# SONG & ARTIST FILTER
# =========================================================

artist_options = ["All Artists"] + sorted(
    df["artist"].dropna().unique().tolist()
)

selected_artist = st.sidebar.selectbox(
    "👤 Artist",
    artist_options
)

song_search = st.sidebar.text_input(
    "🎵 Search Song",
    placeholder="Type a song name..."
)

# Apply artist filter
if selected_artist != "All Artists":
    filtered_df = filtered_df[
        filtered_df["artist"] == selected_artist
    ]

# Apply song search
if song_search:
    filtered_df = filtered_df[
        filtered_df["song"].str.contains(
            song_search,
            case=False,
            na=False
        )
    ]
    # =========================================================
# ALBUM TYPE FILTER
# =========================================================

album_options = ["All"] + sorted(
    df["album_type"].dropna().unique().tolist()
)

selected_album_type = st.sidebar.selectbox(
    "💿 Album Type",
    album_options
)

# Apply album type filter
if selected_album_type != "All":
    filtered_df = filtered_df[
        filtered_df["album_type"] == selected_album_type
    ]

    # =========================================================
# APPLY FILTERS TO ALL ANALYSIS DATA
# =========================================================

# Keep only selected song IDs
selected_song_ids = set(
    filtered_df["song_id"].dropna().unique()
)

# -----------------------------
# Filter Re-Entry Analysis
# -----------------------------

reentry_df = reentry_df[
    reentry_df["song_id"].isin(selected_song_ids)
].copy()

# =========================================================
# KEY INSIGHTS
# =========================================================
#
st.divider()

st.subheader("💡 Key Insights")

insight_col1, insight_col2, insight_col3 = st.columns(3)

# Insight 1 - Re-entry
with insight_col1:
    st.markdown("### 🔄 Chart Re-Entry")

    if len(reentry_df) > 0:
        top_reentry = reentry_df.loc[
            reentry_df["reentry_count"].idxmax()
        ]

        st.write(
            f"**{top_reentry['song']}** by "
            f"**{top_reentry['artist']}** has the highest "
            f"observed chart re-entry frequency with "
            f"**{int(top_reentry['reentry_count'])} re-entries**."
        )
    else:
        st.write("No re-entry records available for the selected filters.")


# Insight 2 - Momentum
with insight_col2:
    st.markdown("### 🚀 Comeback Momentum")

    if len(momentum_df) > 0:
        top_momentum = momentum_df.loc[
            momentum_df["momentum_score"].idxmax()
        ]

        st.write(
            f"**{top_momentum['song']}** by "
            f"**{top_momentum['artist']}** recorded the highest "
            f"comeback momentum score of "
            f"**{top_momentum['momentum_score']:.2f}**."
        )
    else:
        st.write("No comeback events available for the selected filters.")


# Insight 3 - Retention
with insight_col3:
    st.markdown("### ⏳ Sustainability")

    if len(momentum_df) > 0:
        avg_retention = momentum_df["retention_days"].mean()

        st.write(
            f"The selected comeback events remained on the chart "
            f"for an average of **{avg_retention:.1f} days** "
            f"after re-entry."
        )
    else:
        st.write("No retention data available for the selected filters.")

# -----------------------------
# Filter Comeback Momentum
# -----------------------------

momentum_df = momentum_df[
    momentum_df["song_id"].isin(selected_song_ids)
].copy()

# Convert comeback date
momentum_df["reentry_date"] = pd.to_datetime(
    momentum_df["reentry_date"],
    errors="coerce"
)

# Apply selected date range
if len(date_range) == 2:

    momentum_df = momentum_df[
        (momentum_df["reentry_date"] >= start_date) &
        (momentum_df["reentry_date"] <= end_date)
    ].copy()


# -----------------------------
# Filter Fandom Analysis
# -----------------------------

fandom_df = fandom_df[
    fandom_df["song_id"].isin(selected_song_ids)
].copy()


# -----------------------------
# Filter Album Analysis
# -----------------------------

if selected_album_type != "All":

    album_df = album_df[
        album_df["album_type"] == selected_album_type
    ].copy()


# -----------------------------
# Filter Content Analysis
# -----------------------------

if selected_album_type != "All":

    # Content analysis is aggregated,
    # so no album filtering is applied here.
    pass


# Replace main dataset with filtered data
df = filtered_df.copy()
# =========================================================
# HEADER
# =========================================================

st.title("🎵 South Korea K-Pop Analytics")

st.markdown(
    """
    ### Chart Re-Entry, Comeback Momentum & Fandom Analysis
    Explore K-Pop chart behavior using re-entry frequency,
    comeback momentum, retention, content attributes and
    fandom intensity.
    """
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎵 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Executive Overview",
        "🔄 Chart Re-Entry",
        "🚀 Comeback Momentum",
        "⏳ Sustainability",
        "💿 Single vs Album",
        "🔞 Explicit vs Clean",
        "👥 Fandom Intensity",
        "🎵 Song Explorer"
    ]
)


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

if page == "🏠 Executive Overview":

    st.header("📊 Executive Overview")

    total_songs = df["song_id"].nunique()
    total_artists = df["artist"].nunique()
    total_reentries = int(reentry_df["reentry_count"].sum())
    avg_momentum = momentum_df["momentum_score"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🎵 Unique Songs",
        f"{total_songs:,}"
    )

    col2.metric(
        "👤 Artists",
        f"{total_artists:,}"
    )

    col3.metric(
        "🔄 Re-Entry Events",
        f"{total_reentries:,}"
    )

    col4.metric(
        "💥 Avg Momentum",
        f"{avg_momentum:.2f}"
    )

    st.divider()

    # Top artists
    artist_counts = (
        df["artist"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    artist_counts.columns = [
        "Artist",
        "Chart Appearances"
    ]

    fig = px.bar(
        artist_counts,
        x="Chart Appearances",
        y="Artist",
        orientation="h",
        title="Top 10 Artists by Chart Appearances"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# CHART RE-ENTRY
# =========================================================

elif page == "🔄 Chart Re-Entry":

    st.header("🔄 Chart Re-Entry Analysis")

    total_reentries = int(
        reentry_df["reentry_count"].sum()
    )

    songs_with_reentry = int(
        (reentry_df["reentry_count"] > 0).sum()
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Re-Entries",
        f"{total_reentries:,}"
    )

    col2.metric(
        "Songs With Re-Entry",
        f"{songs_with_reentry:,}"
    )

    st.divider()

    top_reentries = (
        reentry_df
        .sort_values(
            "reentry_count",
            ascending=False
        )
        .head(15)
        .copy()
    )

    top_reentries["Label"] = (
        top_reentries["song"].str[:30]
        + " — "
        + top_reentries["artist"].str[:20]
    )

    fig = px.bar(
        top_reentries,
        x="reentry_count",
        y="Label",
        orientation="h",
        title="Songs With the Most Chart Re-Entries"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# COMEBACK MOMENTUM
# =========================================================

elif page == "🚀 Comeback Momentum":

    st.header("🚀 Comeback Momentum Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Comeback Events",
        f"{len(momentum_df):,}"
    )

    col2.metric(
        "Avg Momentum",
        f"{momentum_df['momentum_score'].mean():.2f}"
    )

    col3.metric(
        "Avg Popularity Change",
        f"{momentum_df['popularity_change'].mean():.2f}"
    )

    st.divider()

    top = (
        momentum_df
        .sort_values(
            "momentum_score",
            ascending=False
        )
        .head(15)
        .copy()
    )

    top["Label"] = (
        top["song"].str[:30]
        + " — "
        + top["artist"].str[:20]
    )

    fig = px.bar(
        top,
        x="momentum_score",
        y="Label",
        orientation="h",
        title="Top Comeback Momentum Events"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.scatter(
        momentum_df,
        x="momentum_score",
        y="retention_days",
        hover_data=[
            "song",
            "artist",
            "comeback_position"
        ],
        title="Momentum vs Post-Comeback Retention"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# =========================================================
# SUSTAINABILITY
# =========================================================

elif page == "⏳ Sustainability":

    st.header("⏳ Momentum Sustainability")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Retention",
        f"{momentum_df['retention_days'].mean():.2f} days"
    )

    col2.metric(
        "Median Retention",
        f"{momentum_df['retention_days'].median():.0f} days"
    )

    col3.metric(
        "Maximum Retention",
        f"{momentum_df['retention_days'].max():.0f} days"
    )

    st.divider()

    retention = (
        momentum_df["retention_category"]
        .value_counts()
        .reset_index()
    )

    retention.columns = [
        "Retention Category",
        "Comeback Events"
    ]

    fig = px.bar(
        retention,
        x="Retention Category",
        y="Comeback Events",
        title="Post-Comeback Retention Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SINGLE VS ALBUM
# =========================================================

elif page == "💿 Single vs Album":

    st.header("💿 Single vs Album Analysis")

    st.dataframe(
        album_df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        album_df,
        x="album_type",
        y="avg_momentum",
        title="Average Comeback Momentum by Album Type"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.bar(
        album_df,
        x="album_type",
        y="avg_retention_days",
        title="Post-Comeback Retention by Album Type"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# =========================================================
# EXPLICIT VS CLEAN
# =========================================================

elif page == "🔞 Explicit vs Clean":

    st.header("🔞 Explicit vs Clean Content")

    st.dataframe(
        content_df,
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        content_df,
        x="content_type",
        y="avg_momentum",
        title="Average Momentum: Explicit vs Clean"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig2 = px.bar(
        content_df,
        x="content_type",
        y="avg_retention_days",
        title="Average Retention: Explicit vs Clean"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


# =========================================================
# FANDOM INTENSITY
# =========================================================

elif page == "👥 Fandom Intensity":

    st.header("👥 Fandom Intensity Analysis")

    avg_fandom = fandom_df[
        "fandom_intensity_score"
    ].mean()

    max_fandom = fandom_df[
        "fandom_intensity_score"
    ].max()

    col1, col2 = st.columns(2)

    col1.metric(
        "Average Fandom Intensity",
        f"{avg_fandom:.2f}"
    )

    col2.metric(
        "Highest Fandom Intensity",
        f"{max_fandom:.2f}"
    )

    st.divider()

    top_fandom = (
        fandom_df
        .sort_values(
            "fandom_intensity_score",
            ascending=False
        )
        .head(15)
        .copy()
    )

    top_fandom["Label"] = (
        top_fandom["song"].str[:30]
        + " — "
        + top_fandom["artist"].str[:20]
    )

    fig = px.bar(
        top_fandom,
        x="fandom_intensity_score",
        y="Label",
        orientation="h",
        title="Top Songs by Fandom Intensity"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SONG EXPLORER
# =========================================================

elif page == "🎵 Song Explorer":

    st.header("🎵 Song Explorer")

    st.markdown(
        "Search a song to explore its chart history, "
        "re-entry activity and comeback performance."
    )

    st.divider()

    # -----------------------------------------
    # Song selection
    # -----------------------------------------

    song_options = sorted(
        df["song"].dropna().unique().tolist()
    )

    selected_song = st.selectbox(
        "🎵 Select a Song",
        ["Select a song..."] + song_options
    )

    if selected_song != "Select a song...":

        # -----------------------------------------
        # Song chart history
        # -----------------------------------------

        song_history = df[
            df["song"] == selected_song
        ].copy()

        song_history["date"] = pd.to_datetime(
            song_history["date"],
            errors="coerce"
        )

        # -----------------------------------------
        # Song re-entry information
        # -----------------------------------------

        song_reentry = reentry_df[
            reentry_df["song"] == selected_song
        ].copy()

        # -----------------------------------------
        # Song momentum information
        # -----------------------------------------

        song_momentum = momentum_df[
            momentum_df["song"] == selected_song
        ].copy()

        # -----------------------------------------
        # KPI calculations
        # -----------------------------------------

        artist_name = (
            song_history["artist"].iloc[0]
            if len(song_history) > 0
            else "Unknown"
        )

        chart_entries = len(song_history)

        best_position = (
            int(song_history["position"].min())
            if len(song_history) > 0
            else 0
        )

        reentry_count = (
            int(song_reentry["reentry_count"].sum())
            if len(song_reentry) > 0
            else 0
        )

        avg_momentum = (
            song_momentum["momentum_score"].mean()
            if len(song_momentum) > 0
            else 0
        )

        # -----------------------------------------
        # KPI cards
        # -----------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "👤 Artist",
            artist_name
        )

        col2.metric(
            "📊 Chart Entries",
            f"{chart_entries:,}"
        )

        col3.metric(
            "🏆 Best Position",
            f"#{best_position}"
        )

        col4.metric(
            "🔄 Re-Entries",
            f"{reentry_count:,}"
        )

        st.divider()

        # -----------------------------------------
        # Chart history
        # -----------------------------------------

        st.subheader("📈 Chart Position History")

        if len(song_history) > 0:

            history = (
                song_history
                .sort_values("date")
            )

            fig = px.line(
                history,
                x="date",
                y="position",
                markers=True,
                title=f"{selected_song} — Chart Position"
            )

            # Rank 1 should appear at the top
            fig.update_yaxes(
                autorange="reversed",
                title="Chart Position"
            )

            fig.update_xaxes(
                title="Date"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------------------
        # Momentum
        # -----------------------------------------

        st.subheader("🚀 Comeback Momentum")

        if len(song_momentum) > 0:

            momentum_display = song_momentum[
                [
                    col for col in [
                        "reentry_date",
                        "comeback_position",
                        "momentum_score",
                        "retention_days"
                    ]
                    if col in song_momentum.columns
                ]
            ]

            st.dataframe(
                momentum_display,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No comeback momentum event was detected "
                "for this song."
            )

    else:

        st.info(
            "👆 Select a song above to explore its performance."
        )