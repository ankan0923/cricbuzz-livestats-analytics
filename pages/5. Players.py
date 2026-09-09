import streamlit as st
import pandas as pd

from api import get_live_matches, get_match_team



# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Match Players",
    page_icon="👤",
    layout="wide"
)

st.title("👤 Match Players")

st.caption(
    "Select a live match and team to view the squad."
)


# =========================================================
# GET LIVE MATCHES
# =========================================================

data = get_live_matches()

if not data:

    st.error(
        "Unable to load live matches."
    )

    st.stop()


# =========================================================
# CREATE MATCH OPTIONS
# =========================================================

match_options = {}

for match_type in data.get(
    "typeMatches",
    []
):

    for series in match_type.get(
        "seriesMatches",
        []
    ):

        wrapper = series.get(
            "seriesAdWrapper"
        )

        if not wrapper:
            continue

        series_name = wrapper.get(
            "seriesName",
            "Unknown Series"
        )

        for match in wrapper.get(
            "matches",
            []
        ):

            info = match.get(
                "matchInfo",
                {}
            )

            match_id = info.get(
                "matchId"
            )

            if not match_id:
                continue

            team1 = info.get(
                "team1",
                {}
            )

            team2 = info.get(
                "team2",
                {}
            )

            team1_name = team1.get(
                "teamName",
                "Team 1"
            )

            team2_name = team2.get(
                "teamName",
                "Team 2"
            )

            match_desc = info.get(
                "matchDesc",
                ""
            )

            label = (
                f"{team1_name} vs {team2_name}"
                f" | {match_desc}"
                f" | {series_name}"
            )

            match_options[label] = {
                "match_id": match_id,
                "team1_id": team1.get(
                    "teamId"
                ),
                "team1_name": team1_name,
                "team2_id": team2.get(
                    "teamId"
                ),
                "team2_name": team2_name
            }


# =========================================================
# CHECK MATCHES
# =========================================================

if not match_options:

    st.warning(
        "No live matches are currently available."
    )

    st.stop()


# =========================================================
# MATCH DROPDOWN
# =========================================================

selected_match = st.selectbox(
    "Choose Match",
    list(
        match_options.keys()
    )
)

match_data = match_options[
    selected_match
]

match_id = match_data[
    "match_id"
]


# =========================================================
# TEAM DROPDOWN
# =========================================================

team_options = {
    match_data["team1_name"]:
        match_data["team1_id"],

    match_data["team2_name"]:
        match_data["team2_id"]
}

selected_team = st.selectbox(
    "Choose Team",
    list(
        team_options.keys()
    )
)

team_id = team_options[
    selected_team
]


# =========================================================
# MATCH INFORMATION
# =========================================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Match ID",
    match_id
)

col2.metric(
    "Selected Team",
    selected_team
)

col3.metric(
    "Team ID",
    team_id
)


# =========================================================
# GET PLAYERS
# =========================================================

if st.button(
    "👥 Get Players",
    type="primary",
    use_container_width=True
):

    if not team_id:

        st.error(
            "Team ID is not available "
            "for this match."
        )

        st.stop()

    with st.spinner(
        "Loading players..."
    ):

        player_data = get_match_team(
            match_id,
            team_id
        )


    # =====================================================
    # CHECK API RESPONSE
    # =====================================================

    if not player_data:

        st.error(
            "Unable to load players."
        )

        st.stop()


    # =====================================================
    # EXTRACT PLAYERS
    # =====================================================

    players_list = []

    player_groups = player_data.get(
        "player",
        []
    )

    for group in player_groups:

        players = group.get(
            "player",
            []
        )

        for player in players:

            players_list.append(
                {
                    "Player ID":
                        player.get(
                            "id"
                        ),

                    "Player Name":
                        player.get(
                            "name"
                        ),

                    "Role":
                        player.get(
                            "role"
                        ),

                    "Team":
                        player.get(
                            "teamname"
                        )
                }
            )


    # =====================================================
    # DISPLAY RESULTS
    # =====================================================

    if players_list:

        st.success(
            "Players loaded successfully!"
        )

        df = pd.DataFrame(
            players_list
        )


        # =================================================
        # PLAYER ROLE KPIs
        # =================================================

        role_series = (
            df["Role"]
            .fillna("")
            .str.lower()
        )

        batsman_count = (
            role_series
            .str.contains(
                "batsman"
            )
            .sum()
        )

        bowler_count = (
            role_series
            .eq(
                "bowler"
            )
            .sum()
        )

        allrounder_count = (
            role_series
            .str.contains(
                "allrounder"
            )
            .sum()
        )


        # =================================================
        # KPI CARDS
        # =================================================

        k1, k2, k3 = st.columns(3)

        k1.metric(
            "🏏 Batsmen",
            int(
                batsman_count
            )
        )

        k2.metric(
            "🎯 Bowlers",
            int(
                bowler_count
            )
        )

        k3.metric(
            "⚡ All-Rounders",
            int(
                allrounder_count
            )
        )


        st.divider()


        # =================================================
        # PLAYER TABLE
        # =================================================

        st.subheader(
            f"🏏 {selected_team} Players"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # ROLE SUMMARY
        # =================================================

        st.subheader(
            "📊 Squad Role Distribution"
        )

        role_summary = (
            df["Role"]
            .fillna(
                "Unknown"
            )
            .value_counts()
            .reset_index()
        )

        role_summary.columns = [
            "Role",
            "Players"
        ]

        st.dataframe(
            role_summary,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # DOWNLOAD CSV
        # =================================================

        csv = df.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "⬇️ Download Player List",
            data=csv,
            file_name=(
                f"{selected_team}_players.csv"
            ),
            mime="text/csv"
        )


        # =================================================
        # RAW JSON
        # =================================================

        with st.expander(
            "📄 View Raw Player JSON"
        ):

            st.json(
                player_data
            )


    else:

        st.warning(
            "No players found for "
            "the selected team."
        )
