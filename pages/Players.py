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
# HELPER: CASE-INSENSITIVE FIELD ACCESS
# =========================================================

def get_field(data, *possible_names):

    if not isinstance(data, dict):
        return None

    normalized_data = {
        str(key).lower().replace("_", ""): value
        for key, value in data.items()
    }

    for name in possible_names:

        normalized_name = (
            name.lower()
            .replace("_", "")
        )

        if normalized_name in normalized_data:
            return normalized_data[
                normalized_name
            ]

    return None


# =========================================================
# HELPER: EXTRACT PLAYERS
# =========================================================

def extract_players(
    value,
    selected_team_name,
    selected_team_id,
    current_team_name=None,
    current_team_id=None
):

    extracted_players = []

    if isinstance(value, dict):

        # ---------------------------------------------
        # CHECK FOR NESTED TEAM OBJECT
        # ---------------------------------------------

        team_object = get_field(
            value,
            "team"
        )

        if isinstance(team_object, dict):

            nested_team_name = get_field(
                team_object,
                "teamname",
                "team_name",
                "name"
            )

            nested_team_id = get_field(
                team_object,
                "teamid",
                "team_id",
                "id"
            )

            if nested_team_name:
                current_team_name = nested_team_name

            if nested_team_id is not None:
                current_team_id = nested_team_id


        # ---------------------------------------------
        # CHECK DIRECT TEAM FIELDS
        # ---------------------------------------------

        direct_team_name = get_field(
            value,
            "teamname",
            "team_name"
        )

        direct_team_id = get_field(
            value,
            "teamid",
            "team_id"
        )

        if direct_team_name:
            current_team_name = direct_team_name

        if direct_team_id is not None:
            current_team_id = direct_team_id


        # ---------------------------------------------
        # PLAYER FIELDS
        # ---------------------------------------------

        player_id = get_field(
            value,
            "playerid",
            "player_id",
            "id"
        )

        player_name = get_field(
            value,
            "playername",
            "player_name",
            "fullname",
            "full_name",
            "name"
        )

        player_role = get_field(
            value,
            "playingrole",
            "playing_role",
            "role"
        )

        batting_style = get_field(
            value,
            "battingstyle",
            "batting_style",
            "batstyle"
        )

        bowling_style = get_field(
            value,
            "bowlingstyle",
            "bowling_style",
            "bowlstyle"
        )

        is_captain = get_field(
            value,
            "iscaptain",
            "is_captain",
            "captain"
        )

        is_keeper = get_field(
            value,
            "iskeeper",
            "is_keeper",
            "keeper"
        )


        # ---------------------------------------------
        # CHECK WHETHER OBJECT IS A PLAYER
        # ---------------------------------------------

        specific_player_id = get_field(
            value,
            "playerid",
            "player_id"
        )

        is_player = (
            player_name is not None
            and (
                player_role is not None
                or specific_player_id is not None
            )
        )


        if is_player:

            team_name_matches = (
                current_team_name is None
                or str(current_team_name).lower()
                == str(selected_team_name).lower()
            )

            team_id_matches = (
                current_team_id is None
                or str(current_team_id)
                == str(selected_team_id)
            )


            if team_name_matches and team_id_matches:

                extracted_players.append(
                    {
                        "Player ID":
                            player_id,

                        "Player Name":
                            player_name,

                        "Role":
                            player_role
                            or "Unknown",

                        "Batting Style":
                            batting_style
                            or "-",

                        "Bowling Style":
                            bowling_style
                            or "-",

                        "Team":
                            current_team_name
                            or selected_team_name,

                        "Captain":
                            "Yes"
                            if is_captain
                            else "No",

                        "Wicketkeeper":
                            "Yes"
                            if is_keeper
                            else "No"
                    }
                )


        # ---------------------------------------------
        # SEARCH NESTED VALUES
        # ---------------------------------------------

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
                        current_team_name,
                        current_team_id
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
# LOAD LIVE MATCHES
# =========================================================

with st.spinner("Loading live matches..."):

    live_data = get_live_matches()


if not live_data:

    st.error(
        "Unable to load live matches."
    )

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

            match_info = match.get(
                "matchInfo",
                {}
            )

            match_id = match_info.get(
                "matchId"
            )

            if not match_id:
                continue


            team1 = match_info.get(
                "team1",
                {}
            )

            team2 = match_info.get(
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


            match_description = match_info.get(
                "matchDesc",
                ""
            )


            match_label = (
                f"{team1_name} vs {team2_name}"
                f" | {match_description}"
                f" | {series_name}"
            )


            match_options[match_label] = {
                "match_id":
                    match_id,

                "team1_id":
                    team1.get("teamId"),

                "team1_name":
                    team1_name,

                "team2_id":
                    team2.get("teamId"),

                "team2_name":
                    team2_name
            }


# =========================================================
# CHECK MATCH OPTIONS
# =========================================================

if not match_options:

    st.warning(
        "No live matches are currently available."
    )

    st.stop()


# =========================================================
# SELECT MATCH
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
# SELECT TEAM
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

column1, column2, column3 = st.columns(3)


with column1:

    st.metric(
        "Match ID",
        match_id
    )


with column2:

    st.metric(
        "Selected Team",
        selected_team
    )


with column3:

    st.metric(
        "Team ID",
        team_id
        if team_id is not None
        else "Unavailable"
    )


# =========================================================
# GET PLAYERS BUTTON
# =========================================================

if st.button(
    "👥 Get Players",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Loading squad information..."
    ):

        player_data = get_match_team(
            match_id,
            team_id
        )


    # =====================================================
    # VALIDATE API RESPONSE
    # =====================================================

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


    # =====================================================
    # REMOVE DUPLICATE PLAYERS
    # =====================================================

    unique_players = {}


    for player in players_list:

        unique_key = (
            player.get("Player ID")
            or player.get("Player Name")
        )

        if unique_key is not None:

            unique_players[
                str(unique_key)
            ] = player


    players_list = list(
        unique_players.values()
    )


    # =====================================================
    # CHECK PLAYER RESULTS
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

            st.json(
                player_data
            )

        st.stop()


    # =====================================================
    # CREATE PLAYER DATAFRAME
    # =====================================================

    player_df = pd.DataFrame(
        players_list
    )


    st.success(
        f"{len(player_df)} players loaded "
        f"for {selected_team}."
    )


    # =====================================================
    # PLAYER ROLE COUNTS
    # =====================================================

    role_series = (
        player_df["Role"]
        .fillna("")
        .astype(str)
        .str.lower()
    )


    batter_count = (
        role_series
        .str.contains(
            r"batsman|batter",
            regex=True
        )
        .sum()
    )


    bowler_count = (
        role_series
        .str.contains(
            "bowler"
        )
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
        |
        (
            player_df["Wicketkeeper"]
            == "Yes"
        )
    ).sum()


    # =====================================================
    # KPI CARDS
    # =====================================================

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)


    with kpi1:

        st.metric(
            "🏏 Batters",
            int(batter_count)
        )


    with kpi2:

        st.metric(
            "🎯 Bowlers",
            int(bowler_count)
        )


    with kpi3:

        st.metric(
            "⚡ All-Rounders",
            int(allrounder_count)
        )


    with kpi4:

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
        player_df,
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
        player_df["Role"]
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

    csv_data = (
        player_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    safe_team_name = (
        selected_team
        .replace(" ", "_")
        .lower()
    )


    st.download_button(
        "⬇️ Download Player List",
        data=csv_data,
        file_name=(
            f"{safe_team_name}_players.csv"
        ),
        mime="text/csv"
    )


    # =====================================================
    # RAW JSON RESPONSE
    # =====================================================

    with st.expander(
        "📄 View Raw Squad Response"
    ):

        st.json(
            player_data
        )
