import pandas as pd
import streamlit as st

from api import get_live_matches, get_match_team


# =========================================================
# PAGE CONFIGURATION
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
# PLAYER EXTRACTION FUNCTION
# =========================================================

def extract_players(
    value,
    selected_team_name,
    selected_team_id,
    current_team_name=None,
    current_team_id=None
):
    """
    Recursively extracts players from different squad
    response structures.
    """

    extracted_players = []

    if isinstance(value, dict):

        # Detect team information in the current object
        detected_team_name = (
            value.get("teamName")
            or value.get("teamname")
            or value.get("team_name")
            or current_team_name
        )

        detected_team_id = (
            value.get("teamId")
            or value.get("team_id")
            or current_team_id
        )

        # Possible player fields
        player_id = (
            value.get("id")
            or value.get("playerId")
            or value.get("player_id")
        )

        player_name = (
            value.get("name")
            or value.get("playerName")
            or value.get("fullName")
        )

        player_role = (
            value.get("role")
            or value.get("playingRole")
            or value.get("playing_role")
        )

        # A player must have a name and a player-related field
        is_player = (
            player_name
            and (
                player_role is not None
                or "battingStyle" in value
                or "bowlingStyle" in value
                or "isCaptain" in value
                or "isKeeper" in value
            )
        )

        if is_player:

            player_team_name = (
                value.get("teamname")
                or value.get("teamName")
                or detected_team_name
            )

            player_team_id = (
                value.get("teamId")
                or value.get("team_id")
                or detected_team_id
            )

            team_name_matches = (
                player_team_name is None
                or str(player_team_name).lower()
                == str(selected_team_name).lower()
            )

            team_id_matches = (
                player_team_id is None
                or str(player_team_id)
                == str(selected_team_id)
            )

            if team_name_matches and team_id_matches:

                extracted_players.append(
                    {
                        "Player ID": player_id,
                        "Player Name": player_name,
                        "Role": player_role or "Unknown",
                        "Team": (
                            player_team_name
                            or selected_team_name
                        ),
                        "Captain": (
                            "Yes"
                            if value.get("isCaptain")
                            else "No"
                        ),
                        "Wicketkeeper": (
                            "Yes"
                            if value.get("isKeeper")
                            else "No"
                        )
                    }
                )

        # Recursively inspect nested objects
        for nested_value in value.values():

            if isinstance(
                nested_value,
                (dict, list)
            ):

                extracted_players.extend(
                    extract_players(
                        nested_value,
                        selected_team_name,
                        selected_team_id,
                        detected_team_name,
                        detected_team_id
                    )
                )

    elif isinstance(value, list):

        for item in value:

            extracted_players.extend(
                extract_players(
                    item,
                    selected_team_name,
                    selected_team_id,
                    current_team_name,
                    current_team_id
                )
            )

    return extracted_players


# =========================================================
# REFRESH BUTTON
# =========================================================

if st.button("🔄 Refresh Match Data"):

    st.cache_data.clear()
    st.rerun()


# =========================================================
# GET LIVE MATCHES
# =========================================================

with st.spinner("Loading live matches..."):
    live_data = get_live_matches()


if not live_data:

    st.error("Unable to load live matches.")
    st.stop()


# =========================================================
# CREATE MATCH OPTIONS
# =========================================================

match_options = {}


for match_type in live_data.get(
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
                "team1_id": team1.get("teamId"),
                "team1_name": team1_name,
                "team2_id": team2.get("teamId"),
                "team2_name": team2_name
            }


if not match_options:

    st.warning(
        "No live matches are currently available."
    )

    st.stop()


# =========================================================
# MATCH SELECTION
# =========================================================

selected_match = st.selectbox(
    "Choose Match",
    list(match_options.keys())
)

selected_match_data = match_options[
    selected_match
]

match_id = selected_match_data[
    "match_id"
]


# =========================================================
# TEAM SELECTION
# =========================================================

team_options = {
    selected_match_data["team1_name"]:
        selected_match_data["team1_id"],

    selected_match_data["team2_name"]:
        selected_match_data["team2_id"]
}

selected_team = st.selectbox(
    "Choose Team",
    list(team_options.keys())
)

team_id = team_options[
    selected_team
]


# =========================================================
# MATCH INFORMATION
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Match ID",
        match_id
    )

with col2:
    st.metric(
        "Selected Team",
        selected_team
    )

with col3:
    st.metric(
        "Team ID",
        team_id or "Unavailable"
    )


# =========================================================
# GET PLAYERS
# =========================================================

if st.button(
    "👥 Get Players",
    type="primary",
    use_container_width=True
):

    with st.spinner("Loading players..."):

        player_data = get_match_team(
            match_id,
            team_id
        )


    if not player_data:

        st.error(
            "Unable to load squad information."
        )

        st.stop()


    # =====================================================
    # EXTRACT PLAYERS
    # =====================================================

    players_list = extract_players(
        player_data,
        selected_team,
        team_id
    )


    # Remove duplicate players
    unique_players = {}

    for player in players_list:

        unique_key = (
            player.get("Player ID")
            or player.get("Player Name")
        )

        if unique_key:
            unique_players[
                str(unique_key)
            ] = player

    players_list = list(
        unique_players.values()
    )


    # =====================================================
    # DISPLAY PLAYERS
    # =====================================================

    if not players_list:

        st.warning(
            "The API returned squad data, but no players "
            "could be matched to the selected team."
        )

        with st.expander(
            "📄 View Raw Squad Response",
            expanded=True
        ):
            st.json(player_data)

        st.stop()


    df = pd.DataFrame(
        players_list
    )


    st.success(
        f"{len(df)} players loaded for {selected_team}."
    )


    # =====================================================
    # ROLE COUNTS
    # =====================================================

    role_series = (
        df["Role"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    batsmen_count = (
        role_series
        .str.contains(
            r"batsman|batter",
            regex=True
        )
        .sum()
    )

    bowler_count = (
        role_series
        .str.contains("bowler")
        .sum()
    )

    allrounder_count = (
        role_series
        .str.contains(
            r"all.?rounder",
            regex=True
        )
        .sum()
    )

    wicketkeeper_count = (
        (
            role_series.str.contains(
                r"wicket.?keeper|wk",
                regex=True
            )
        )
        | (
            df["Wicketkeeper"] == "Yes"
        )
    ).sum()


    # =====================================================
    # KPI CARDS
    # =====================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "🏏 Batters",
            int(batsmen_count)
        )

    with k2:
        st.metric(
            "🎯 Bowlers",
            int(bowler_count)
        )

    with k3:
        st.metric(
            "⚡ All-Rounders",
            int(allrounder_count)
        )

    with k4:
        st.metric(
            "🧤 Wicketkeepers",
            int(wicketkeeper_count)
        )


    st.divider()


    # =====================================================
    # PLAYER TABLE
    # =====================================================

    st.subheader(
        f"🏏 {selected_team} Squad"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # ROLE SUMMARY
    # =====================================================

    st.subheader(
        "📊 Squad Role Distribution"
    )

    role_summary = (
        df["Role"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("Role")
        .reset_index(name="Players")
    )

    st.dataframe(
        role_summary,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # CSV DOWNLOAD
    # =====================================================

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Player List",
        data=csv_data,
        file_name=(
            f"{selected_team}_players.csv"
        ),
        mime="text/csv"
    )


    # =====================================================
    # RAW API RESPONSE
    # =====================================================

    with st.expander(
        "📄 View Raw Squad Response"
    ):
        st.json(player_data)
