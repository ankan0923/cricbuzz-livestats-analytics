import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_connection

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Cricket Visualizations",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# COLOR PALETTE
# =========================================================

COLORS = [
    "#7EC8FF",   # Light Blue
    "#1478D4",   # Blue
    "#FF9E9E",   # Pink
    "#FF2B2B",   # Red
    "#9B7EDE",   # Purple
    "#55D6BE",   # Teal
    "#F4B942"    # Gold
]


# =========================================================
# TITLE
# =========================================================

st.title("📊 Cricket Visualizations")

st.write(
    "Explore interactive insights from the cricket database."
)

st.divider()


# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = get_connection()


# =========================================================
# FILTER DATA
# =========================================================

try:

    series_df = pd.read_sql_query(
        """
        SELECT DISTINCT series_name
        FROM matches
        WHERE series_name IS NOT NULL
        AND series_name != ''
        ORDER BY series_name
        """,
        conn
    )

    team_df = pd.read_sql_query(
        """
        SELECT DISTINCT team_name
        FROM teams
        WHERE team_name IS NOT NULL
        AND team_name != ''
        ORDER BY team_name
        """,
        conn
    )

except Exception:

    series_df = pd.DataFrame()
    team_df = pd.DataFrame()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔍 Filters")


series_list = (
    series_df["series_name"].tolist()
    if not series_df.empty
    else []
)

team_list = (
    team_df["team_name"].tolist()
    if not team_df.empty
    else []
)


selected_series = st.sidebar.multiselect(
    "Select Series",
    options=series_list
)


selected_teams = st.sidebar.multiselect(
    "Select Teams",
    options=team_list
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def apply_chart_style(fig):

    fig.update_layout(
        template="plotly_dark",

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            size=14
        ),

        title_font=dict(
            size=20
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    return fig


# =========================================================
# 1. TOP RUN SCORERS
# =========================================================

st.header("🏏 Top Run Scorers")


try:

    query = """
        SELECT
            p.full_name AS Player,
            SUM(b.runs) AS Runs

        FROM batting_stats b

        JOIN players p
            ON b.player_id = p.player_id

        JOIN matches m
            ON b.match_id = m.match_id

        WHERE 1 = 1
    """

    params = []


    if selected_series:

        placeholders = ",".join(
            ["?"] * len(selected_series)
        )

        query += f"""
            AND m.series_name
            IN ({placeholders})
        """

        params.extend(
            selected_series
        )


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND p.team_name
            IN ({placeholders})
        """

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY
            p.player_id,
            p.full_name

        ORDER BY Runs DESC

        LIMIT 10
    """


    top_runs = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not top_runs.empty:

        fig = px.bar(
            top_runs,
            x="Player",
            y="Runs",
            color="Player",
            text="Runs",
            title="Top Run Scorers",
            color_discrete_sequence=COLORS
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Player",
            yaxis_title="Runs"
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No batting statistics available yet."
        )


except Exception as e:

    st.warning(
        f"Top run scorer data unavailable: {e}"
    )


st.divider()


# =========================================================
# 2. RUNS BY TEAM
# =========================================================

st.header("🏏 Runs by Team")


try:

    query = """
        SELECT
            p.team_name,
            SUM(b.runs) AS runs

        FROM batting_stats b

        JOIN players p
            ON b.player_id = p.player_id

        JOIN matches m
            ON b.match_id = m.match_id

        WHERE
            p.team_name IS NOT NULL
    """

    params = []


    if selected_series:

        placeholders = ",".join(
            ["?"] * len(selected_series)
        )

        query += f"""
            AND m.series_name
            IN ({placeholders})
        """

        params.extend(
            selected_series
        )


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND p.team_name
            IN ({placeholders})
        """

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY p.team_name

        ORDER BY runs DESC
    """


    team_runs = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not team_runs.empty:

        fig = px.bar(
            team_runs,
            x="team_name",
            y="runs",
            color="team_name",
            text="runs",
            title="Total Runs Scored by Teams",
            color_discrete_sequence=COLORS
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Team",
            yaxis_title="Runs",
            legend_title="Team"
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No team batting statistics available yet."
        )


except Exception as e:

    st.warning(
        f"Team runs data unavailable: {e}"
    )


st.divider()


# =========================================================
# 3. WICKETS BY TEAM
# =========================================================

st.header("🎯 Wickets by Team")


try:

    query = """
        SELECT
            p.team_name,
            SUM(b.wickets) AS wickets

        FROM bowling_stats b

        JOIN players p
            ON b.player_id = p.player_id

        JOIN matches m
            ON b.match_id = m.match_id

        WHERE
            p.team_name IS NOT NULL
    """

    params = []


    if selected_series:

        placeholders = ",".join(
            ["?"] * len(selected_series)
        )

        query += f"""
            AND m.series_name
            IN ({placeholders})
        """

        params.extend(
            selected_series
        )


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND p.team_name
            IN ({placeholders})
        """

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY p.team_name

        ORDER BY wickets DESC
    """


    team_wickets = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not team_wickets.empty:

        fig = px.bar(
            team_wickets,
            x="team_name",
            y="wickets",
            color="team_name",
            text="wickets",
            title="Total Wickets by Teams",
            color_discrete_sequence=COLORS
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Team",
            yaxis_title="Wickets",
            legend_title="Team"
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No bowling statistics available yet."
        )


except Exception as e:

    st.warning(
        f"Team wickets data unavailable: {e}"
    )


st.divider()


# =========================================================
# 4. PLAYER ROLE DISTRIBUTION
# =========================================================

st.header("👥 Player Roles Distribution")


try:

    query = """
        SELECT
            playing_role AS Role,
            COUNT(*) AS Count

        FROM players

        WHERE
            playing_role IS NOT NULL
            AND playing_role != ''
    """

    params = []


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND team_name
            IN ({placeholders})
        """

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY playing_role

        ORDER BY Count DESC
    """


    role_data = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not role_data.empty:

        fig = px.pie(
            role_data,
            names="Role",
            values="Count",
            title="Player Roles Breakdown",
            color_discrete_sequence=COLORS,
            hole=0
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        fig.update_layout(
            legend_title="Role"
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No player role data available yet."
        )


except Exception as e:

    st.warning(
        f"Player role data unavailable: {e}"
    )


st.divider()


# =========================================================
# 5. MATCHES PLAYED OVER TIME
# =========================================================

st.header("📅 Matches Played Over Time")


try:

    query = """
        SELECT
            DATE(match_date) AS date,
            COUNT(*) AS matches

        FROM matches

        WHERE
            match_date IS NOT NULL
    """

    params = []


    if selected_series:

        placeholders = ",".join(
            ["?"] * len(selected_series)
        )

        query += f"""
            AND series_name
            IN ({placeholders})
        """

        params.extend(
            selected_series
        )


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND (
                team1_name IN ({placeholders})
                OR
                team2_name IN ({placeholders})
            )
        """

        params.extend(
            selected_teams
        )

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY DATE(match_date)

        ORDER BY DATE(match_date)
    """


    matches_time = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not matches_time.empty:

        matches_time["date"] = pd.to_datetime(
            matches_time["date"]
        )


        fig = px.line(
            matches_time,
            x="date",
            y="matches",
            markers=True,
            title="Matches Played Over Time"
        )

        fig.update_traces(
            line=dict(
                color="#7EC8FF",
                width=3
            ),

            marker=dict(
                color="#1478D4",
                size=9
            )
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Matches Played",
            showlegend=False
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No match timeline data available."
        )


except Exception as e:

    st.warning(
        f"Match timeline data unavailable: {e}"
    )


st.divider()


# =========================================================
# ADDITIONAL PLAYER VISUALS
# =========================================================

st.header(
    "📊 Additional Visuals (Player Stats)"
)


# =========================================================
# 6. TOP PLAYER STRIKE RATE
# =========================================================

st.subheader(
    "⚡ Top Batting Strike Rates"
)


try:

    query = """
        SELECT
            p.full_name AS Player,
            ROUND(
                AVG(b.strike_rate),
                2
            ) AS Strike_Rate

        FROM batting_stats b

        JOIN players p
            ON b.player_id = p.player_id

        WHERE
            b.balls_faced > 0
    """

    params = []


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND p.team_name
            IN ({placeholders})
        """

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY
            p.player_id,
            p.full_name

        ORDER BY Strike_Rate DESC

        LIMIT 10
    """


    strike_rate_df = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not strike_rate_df.empty:

        fig = px.bar(
            strike_rate_df,
            x="Player",
            y="Strike_Rate",
            color="Player",
            text="Strike_Rate",
            title="Top Batting Strike Rates",
            color_discrete_sequence=COLORS
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Player",
            yaxis_title="Strike Rate"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No batting strike-rate data available yet."
        )


except Exception as e:

    st.warning(
        f"Strike-rate data unavailable: {e}"
    )


# =========================================================
# 7. TOP WICKET TAKERS
# =========================================================

st.subheader(
    "🔥 Top Wicket Takers"
)


try:

    query = """
        SELECT
            p.full_name AS Player,
            SUM(b.wickets) AS Wickets

        FROM bowling_stats b

        JOIN players p
            ON b.player_id = p.player_id

        WHERE 1 = 1
    """

    params = []


    if selected_teams:

        placeholders = ",".join(
            ["?"] * len(selected_teams)
        )

        query += f"""
            AND p.team_name
            IN ({placeholders})
        """

        params.extend(
            selected_teams
        )


    query += """
        GROUP BY
            p.player_id,
            p.full_name

        ORDER BY Wickets DESC

        LIMIT 10
    """


    wicket_df = pd.read_sql_query(
        query,
        conn,
        params=params
    )


    if not wicket_df.empty:

        fig = px.bar(
            wicket_df,
            x="Player",
            y="Wickets",
            color="Player",
            text="Wickets",
            title="Top Wicket Takers",
            color_discrete_sequence=COLORS
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Player",
            yaxis_title="Wickets"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig = apply_chart_style(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No bowling wicket data available yet."
        )


except Exception as e:

    st.warning(
        f"Wicket data unavailable: {e}"
    )


# =========================================================
# CLOSE DATABASE
# =========================================================

conn.close()