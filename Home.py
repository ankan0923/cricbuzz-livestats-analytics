import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
from api import get_live_matches
from database import create_tables, get_connection


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)

create_tables()

# =========================================================
# SIDEBAR LOGO + DESIGNED BY
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logo is in the same folder as Home.py
logo_path = os.path.join(BASE_DIR, "cricket_logo.png")


# Logo
if os.path.exists(logo_path):
    col1, col2, col3 = st.sidebar.columns([0.3, 3, 0.3])

    with col2:
        st.image(
            logo_path,
            use_container_width=True
        )

# =========================================================
# DESIGNED BY - ANKAN
# =========================================================

credit_html = (
    '<div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-top:12px;">'
    '<div style="width:55px;height:2px;background:#7EC8FF;"></div>'
    '<span style="color:#AAB2BF;font-size:14px;white-space:nowrap;">Designed By</span>'
    '<div style="width:55px;height:2px;background:#7EC8FF;"></div>'
    '</div>'
    '<div style="text-align:center;color:#7EC8FF;font-size:22px;font-weight:700;margin-top:8px;">'
    'Ankan'
    '</div>'
)

st.sidebar.markdown(
    credit_html,
    unsafe_allow_html=True
)

# =========================================================
# COLORS
# =========================================================

COLORS = [
    "#7EC8FF",
    "#1478D4",
    "#FF9E9E",
    "#FF2B2B",
    "#9B7EDE",
    "#55D6BE",
    "#F4B942"
]


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 28px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 32px;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* KPI CARDS */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        min-height: 130px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 16px;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: 700;
    }

    /* FEATURED PERFORMERS */
    .performer-green {
        background-color: rgba(34, 197, 94, 0.20);
        padding: 18px;
        border-radius: 10px;
        font-size: 18px;
        color: #4ade80;
        font-weight: 600;
    }

    .performer-blue {
        background-color: rgba(59, 130, 246, 0.20);
        padding: 18px;
        border-radius: 10px;
        font-size: 18px;
        color: #60a5fa;
        font-weight: 600;
    }

    .performer-gold {
        background-color: rgba(202, 138, 4, 0.25);
        padding: 18px;
        border-radius: 10px;
        font-size: 18px;
        color: #fde047;
        font-weight: 600;
    }

    .performer-name {
        margin-top: 20px;
        font-size: 17px;
        font-weight: 600;
    }

    .performer-value {
        font-size: 38px;
        font-weight: 500;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_query(query):

    conn = get_connection()

    try:
        return pd.read_sql_query(
            query,
            conn
        )

    except Exception:
        return pd.DataFrame()

    finally:
        conn.close()


def style_chart(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig


def get_value(df):

    if (
        not df.empty
        and "total" in df.columns
    ):

        return int(
            df.iloc[0]["total"]
            or 0
        )

    return 0


# =========================================================
# LIVE API
# =========================================================

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

headers = {
        "Content-Type": "application/json",
    "X-RapidAPI-Key": st.secrets["API_KEY"],
    "X-RapidAPI-Host": st.secrets["API_HOST"]
}

live_matches_count = 0
live_data = {}
response = None

try:
    response = requests.get(
        f"{BASE_URL}/matches/v1/live",
        headers=headers,
        timeout=15
    )

    st.write("API Status:", response.status_code)

    if response.status_code == 200:
        live_data = response.json()

        for match_type in live_data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                wrapper = series.get("seriesAdWrapper")

                if wrapper:
                    live_matches_count += len(
                        wrapper.get("matches", [])
                    )

    elif response.status_code == 429:
        st.warning("API request limit reached.")

    else:
        st.error(f"API request failed: {response.status_code}")
        st.code(response.text[:500])

except requests.exceptions.RequestException as e:
    st.error(f"API connection error: {e}")


# =========================================================
# DATABASE KPI DATA
# =========================================================

player_count_df = safe_query(
    """
    SELECT COUNT(*) AS total
    FROM players
    """
)

team_count_df = safe_query(
    """
    SELECT COUNT(*) AS total
    FROM teams
    """
)

match_count_df = safe_query(
    """
    SELECT COUNT(*) AS total
    FROM matches
    """
)

venue_count_df = safe_query(
    """
    SELECT COUNT(*) AS total
    FROM venues
    """
)

runs_df = safe_query(
    """
    SELECT
        COALESCE(SUM(runs), 0) AS total
    FROM batting_stats
    """
)

wickets_df = safe_query(
    """
    SELECT
        COALESCE(SUM(wickets), 0) AS total
    FROM bowling_stats
    """
)

highest_score_df = safe_query(
    """
    SELECT
        COALESCE(MAX(runs), 0) AS total
    FROM batting_stats
    """
)


players = get_value(player_count_df)
teams = get_value(team_count_df)
matches = get_value(match_count_df)
venues = get_value(venue_count_df)

total_runs = get_value(runs_df)
total_wickets = get_value(wickets_df)
highest_score = get_value(highest_score_df)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">🏏 Cricbuzz LiveStats</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Real-Time Cricket Insights & SQL-Based Analytics
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# KPI ROW 1
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Players",
        value=f"{players:,}"
    )

with col2:
    st.metric(
        label="🏆 Teams",
        value=f"{teams:,}"
    )

with col3:
    st.metric(
        label="🏏 Matches",
        value=f"{matches:,}"
    )

with col4:
    st.metric(
        label="📍 Venues",
        value=f"{venues:,}"
    )


# =========================================================
# KPI ROW 2
# =========================================================

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        label="🏃 Total Runs",
        value=f"{total_runs:,}"
    )

with col6:
    st.metric(
        label="🎯 Total Wickets",
        value=f"{total_wickets:,}"
    )

with col7:
    st.metric(
        label="🔥 Highest Score",
        value=f"{highest_score:,}"
    )

with col8:
    st.metric(
        label="🔴 Live Matches",
        value=f"{live_matches_count:,}"
    )

st.divider()


# =========================================================
# FEATURED PERFORMERS
# =========================================================

st.markdown(
    """
    <div class="section-title">
        ⭐ Featured Performers
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TOP BATTER
# =========================================================

top_batter = safe_query(
    """
    SELECT
        p.full_name,
        SUM(b.runs) AS total_runs

    FROM batting_stats b

    JOIN players p
        ON b.player_id = p.player_id

    GROUP BY
        p.player_id,
        p.full_name

    ORDER BY total_runs DESC

    LIMIT 1
    """
)

if not top_batter.empty:

    batter_name = top_batter.iloc[0][
        "full_name"
    ]

    batter_runs = int(
        top_batter.iloc[0][
            "total_runs"
        ]
        or 0
    )

else:

    batter_name = "No Data"
    batter_runs = 0


# =========================================================
# TOP BOWLER
# =========================================================

top_bowler = safe_query(
    """
    SELECT
        p.full_name,
        SUM(b.wickets) AS total_wickets

    FROM bowling_stats b

    JOIN players p
        ON b.player_id = p.player_id

    GROUP BY
        p.player_id,
        p.full_name

    ORDER BY total_wickets DESC

    LIMIT 1
    """
)

if not top_bowler.empty:

    bowler_name = top_bowler.iloc[0][
        "full_name"
    ]

    bowler_wickets = int(
        top_bowler.iloc[0][
            "total_wickets"
        ]
        or 0
    )

else:

    bowler_name = "No Data"
    bowler_wickets = 0


# =========================================================
# TOP TEAM
# =========================================================

top_team = safe_query(
    """
    SELECT
        winner_name,
        COUNT(*) AS wins

    FROM matches

    WHERE
        winner_name IS NOT NULL
        AND winner_name != ''

    GROUP BY winner_name

    ORDER BY wins DESC

    LIMIT 1
    """
)

if not top_team.empty:

    team_name = top_team.iloc[0][
        "winner_name"
    ]

    team_wins = int(
        top_team.iloc[0][
            "wins"
        ]
        or 0
    )

else:

    team_name = "No Data"
    team_wins = 0


# =========================================================
# FEATURE CARDS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        """
        <div class="performer-green">
            🏏 Top Batter
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="performer-name">
            {batter_name}
        </div>

        <div class="performer-value">
            {batter_runs:,} Runs
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="performer-blue">
            🎯 Top Bowler
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="performer-name">
            {bowler_name}
        </div>

        <div class="performer-value">
            {bowler_wickets:,} Wickets
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="performer-gold">
            🏆 Top Team
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="performer-name">
            {team_name}
        </div>

        <div class="performer-value">
            {team_wins:,} Wins
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()


# =========================================================
# CRICKET OVERVIEW
# =========================================================

st.markdown(
    """
    <div class="section-title">
        📈 Cricket Overview
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MATCHES PER YEAR
# =========================================================

matches_year = safe_query(
    """
    SELECT
        CAST(
            STRFTIME(
                '%Y',
                match_date
            )
            AS INTEGER
        ) AS Year,

        COUNT(*) AS Matches

    FROM matches

    WHERE
        match_date IS NOT NULL

    GROUP BY Year

    HAVING Year IS NOT NULL

    ORDER BY Year
    """
)


# =========================================================
# FORMAT DISTRIBUTION
# =========================================================

format_df = safe_query(
    """
    SELECT
        match_format AS Format,
        COUNT(*) AS Matches

    FROM matches

    WHERE
        match_format IS NOT NULL
        AND match_format != ''

    GROUP BY match_format

    ORDER BY Matches DESC
    """
)


col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Matches per Year"
    )

    if not matches_year.empty:

        fig = px.line(
            matches_year,
            x="Year",
            y="Matches",
            markers=True
        )

        fig.update_traces(
            line=dict(
                color="#7EC8FF",
                width=3
            ),
            marker=dict(
                color="#7EC8FF",
                size=8
            )
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Year",
            yaxis_title="Matches"
        )

        style_chart(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No match-year data available."
        )


with col2:

    st.subheader(
        "Format Distribution"
    )

    if not format_df.empty:

        fig = px.pie(
            format_df,
            names="Format",
            values="Matches",
            hole=0.48,
            color_discrete_sequence=COLORS
        )

        fig.update_traces(
            textinfo="percent"
        )

        style_chart(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No format data available."
        )


# =========================================================
# TEAM PLAYER DISTRIBUTION
# =========================================================

team_distribution = safe_query(
    """
    SELECT
        team_name AS Team,
        COUNT(*) AS Players

    FROM players

    WHERE
        team_name IS NOT NULL
        AND team_name != ''

    GROUP BY team_name

    ORDER BY Players DESC

    LIMIT 10
    """
)


# =========================================================
# TEAM WINS
# =========================================================

win_df = safe_query(
    """
    SELECT
        winner_name AS Team,
        COUNT(*) AS Wins

    FROM matches

    WHERE
        winner_name IS NOT NULL
        AND winner_name != ''

    GROUP BY winner_name

    ORDER BY Wins DESC

    LIMIT 10
    """
)


col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Team Player Distribution"
    )

    if not team_distribution.empty:

        fig = px.bar(
            team_distribution,
            x="Team",
            y="Players",
            color="Players",
            color_continuous_scale=[
                "#07519c",
                "#4292c6",
                "#9ecae1",
                "#deebf7"
            ]
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Players",
            coloraxis_colorbar_title="Players"
        )

        style_chart(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No player-team data available."
        )


with col2:

    st.subheader(
        "Team Wins"
    )

    if not win_df.empty:

        fig = px.bar(
            win_df,
            x="Team",
            y="Wins",
            color="Wins",
            color_continuous_scale=[
                "#07519c",
                "#4292c6",
                "#9ecae1",
                "#deebf7"
            ]
        )

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Wins",
            coloraxis_colorbar_title="Wins"
        )

        style_chart(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No team win data available."
        )
