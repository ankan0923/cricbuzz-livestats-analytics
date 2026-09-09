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

    for series_item in match_type.get(
        "seriesMatches",
        []
    ):

        series_wrapper = series_item.get(
            "seriesAdWrapper"
        )

        if not series_wrapper:
            continue


        series_name = series_wrapper.get(
            "seriesName",
            "Unknown Series"
        )


        for match in series_wrapper.get(
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
# VALIDATE MATCH OPTIONS
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
# GET PLAYERS
# =========================================================

if st.button(
    "👥 Get Players",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Loading squad information..."
    ):

        squad_data = get_match_team(
            match_id,
            team_id
        )


    if not squad_data:

        st.error(
            "Unable to load squad information."
        )

        st.stop()


    # =====================================================
    # FIND SELECTED TEAM SECTION
    # =====================================================

    selected_team_section = None
    api_team_name = selected_team


    for team_key in [
        "team1",
        "team2"
    ]:

        team_section = squad_data.get(
            team_key,
            {}
        )

        team_information = team_section.get(
            "team",
            {}
        )

        api_team_id = team_information.get(
            "teamid"
        )


        if str(api_team_id) == str(team_id):

            selected_team_section = team_section

            api_team_name = team_information.get(
                "teamname",
                selected_team
            )

            break


    # =====================================================
    # CHECK SELECTED TEAM
    # =====================================================

    if selected_team_section is None:

        st.warning(
            "The selected team was not found "
            "inside the squad response."
        )

        with st.expander(
            "📄 View Raw Squad Response",
            expanded=True
        ):

            st.json(squad_data)

        st.stop()


    # =====================================================
    # EXTRACT PLAYERS
    # =====================================================

    players_list = []


    player_groups = selected_team_section.get(
        "players",
        []
    )


    for player_group in player_groups:

        if not isinstance(
            player_group,
            dict
        ):
            continue


        group_players = player_group.get(
            "player",
            []
        )


        for player in group_players:

            if not isinstance(
                player,
                dict
            ):
                continue


            player_id = player.get(
                "id"
            )

            player_name = player.get(
                "name"
            )


            if not player_id or not player_name:
                continue


            players_list.append(
                {
                    "Player ID":
                        player_id,

                    "Player Name":
                        player_name,

                    "Role":
                        player.get(
                            "role",
                            "Unknown"
                        ),

                    "Batting Style":
                        player.get(
                            "battingStyle",
                            "-"
                        )
                        or "-",

                    "Bowling Style":
                        player.get(
                            "bowlingStyle",
                            "-"
                        )
                        or "-",

                    "Team":
                        api_team_name,

                    "Captain":
                        (
                            "Yes"
                            if player.get(
                                "captain",
                                False
                            )
                            else "No"
                        ),

                    "Wicketkeeper":
                        (
                            "Yes"
                            if player.get(
                                "keeper",
                                False
                            )
                            else "No"
                        )
                }
            )


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    unique_players = {}


    for player in players_list:

        unique_players[
            str(player["Player ID"])
        ] = player


    players_list = list(
        unique_players.values()
    )


    # =====================================================
    # HANDLE EMPTY PLAYER LIST
    # =====================================================

    if not players_list:

        st.warning(
            "No player records were found "
            "for the selected team."
        )

        with st.expander(
            "📄 View Selected Team Response",
            expanded=True
        ):

            st.json(
                selected_team_section
            )

        st.stop()


    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    player_df = pd.DataFrame(
        players_list
    )


    st.success(
        f"{len(player_df)} players loaded "
        f"for {api_team_name}."
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
            r"batter|batsman",
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
            role_series
            .str.contains(
                r"wk|wicket.?keeper",
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
    # KPI SECTION
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
        f"🏏 {api_team_name} Squad"
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
    # DOWNLOAD CSV
    # =====================================================

    csv_data = (
        player_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    safe_team_name = (
        api_team_name
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
    # RAW RESPONSE
    # =====================================================

    with st.expander(
        "📄 View Raw Squad Response"
    ):

        st.json(
            squad_data
        )
