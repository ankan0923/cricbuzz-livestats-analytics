import pandas as pd
import streamlit as st

from api import get_live_matches, get_scorecard


st.set_page_config(
    page_title="Live Scorecard",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Live Match Scorecard")
st.caption(
    "Select a live match to view detailed batting and bowling scorecards."
)


# =========================================================
# GET LIVE MATCHES
# =========================================================

live_data = get_live_matches()

if not live_data:
    st.error("Unable to load live matches.")
    st.stop()


# =========================================================
# BUILD MATCH LIST
# =========================================================

match_options = {}

for match_type in live_data.get("typeMatches", []):

    for series in match_type.get("seriesMatches", []):

        wrapper = series.get("seriesAdWrapper")

        if not wrapper:
            continue

        series_name = wrapper.get(
            "seriesName",
            "Unknown Series"
        )

        for match in wrapper.get("matches", []):

            info = match.get(
                "matchInfo",
                {}
            )

            match_id = info.get("matchId")

            if not match_id:
                continue

            team1 = info.get(
                "team1",
                {}
            ).get(
                "teamName",
                "Team 1"
            )

            team2 = info.get(
                "team2",
                {}
            ).get(
                "teamName",
                "Team 2"
            )

            match_desc = info.get(
                "matchDesc",
                ""
            )

            label = (
                f"{team1} vs {team2}"
                f" | {match_desc}"
                f" | {series_name}"
            )

            match_options[label] = match_id


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

match_id = match_options[
    selected_match
]


# =========================================================
# LOAD SCORECARD
# =========================================================

if st.button(
    "🔄 Refresh Scorecard",
    use_container_width=True
):
    st.rerun()


scorecard_data = get_scorecard(
    match_id
)

if not scorecard_data:
    st.error(
        "Unable to load scorecard."
    )
    st.stop()


# =========================================================
# MATCH HEADER
# =========================================================

st.markdown(
    f"### 🏏 {selected_match}"
)

st.caption(
    f"Match ID: {match_id}"
)

st.divider()


# =========================================================
# SCORECARD DATA
# =========================================================

scorecards = scorecard_data.get(
    "scoreCard",
    []
)

if not scorecards:
    st.info(
        "Scorecard data is not available "
        "for this match yet."
    )
    st.stop()


# =========================================================
# DISPLAY EACH INNINGS
# =========================================================

for innings_index, innings in enumerate(
    scorecards,
    start=1
):

    batting_team = innings.get(
        "batTeamDetails",
        {}
    )

    bowling_team = innings.get(
        "bowlTeamDetails",
        {}
    )

    score_details = innings.get(
        "scoreDetails",
        {}
    )


    # =====================================================
    # INNINGS TITLE
    # =====================================================

    team_name = batting_team.get(
        "batTeamName",
        f"Innings {innings_index}"
    )

    st.header(
        f"🏏 {team_name} — Innings {innings_index}"
    )


    # =====================================================
    # SCORE KPIs
    # =====================================================

    runs = score_details.get(
        "runs",
        0
    )

    wickets = score_details.get(
        "wickets",
        0
    )

    overs = score_details.get(
        "overs",
        0
    )

    run_rate = score_details.get(
        "runRate",
        "-"
    )


    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Runs",
        runs
    )

    c2.metric(
        "Wickets",
        wickets
    )

    c3.metric(
        "Overs",
        overs
    )

    c4.metric(
        "Run Rate",
        run_rate
    )


    # =====================================================
    # BATTING TABLE
    # =====================================================

    st.subheader(
        "🏏 Batting"
    )

    batsmen_data = batting_team.get(
        "batsmenData",
        {}
    )

    batting_rows = []

    for _, batsman in batsmen_data.items():

        batting_rows.append(
            {
                "Batsman":
                    batsman.get(
                        "batName",
                        ""
                    ),

                "Dismissal":
                    batsman.get(
                        "outDesc",
                        ""
                    ),

                "Runs":
                    batsman.get(
                        "runs",
                        0
                    ),

                "Balls":
                    batsman.get(
                        "balls",
                        0
                    ),

                "4s":
                    batsman.get(
                        "fours",
                        0
                    ),

                "6s":
                    batsman.get(
                        "sixes",
                        0
                    ),

                "Strike Rate":
                    batsman.get(
                        "strikeRate",
                        0
                    )
            }
        )


    if batting_rows:

        batting_df = pd.DataFrame(
            batting_rows
        )

        st.dataframe(
            batting_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Batting details unavailable."
        )


    # =====================================================
    # EXTRAS
    # =====================================================

    extras = innings.get(
        "extrasData",
        {}
    )

    if extras:

        st.markdown(
            "#### Extras"
        )

        e1, e2, e3, e4, e5 = st.columns(5)

        e1.metric(
            "No Balls",
            extras.get(
                "noBalls",
                0
            )
        )

        e2.metric(
            "Wides",
            extras.get(
                "wides",
                0
            )
        )

        e3.metric(
            "Byes",
            extras.get(
                "byes",
                0
            )
        )

        e4.metric(
            "Leg Byes",
            extras.get(
                "legByes",
                0
            )
        )

        e5.metric(
            "Penalty",
            extras.get(
                "penalty",
                0
            )
        )


    # =====================================================
    # BOWLING TABLE
    # =====================================================

    st.subheader(
        "🎯 Bowling"
    )

    bowlers_data = bowling_team.get(
        "bowlersData",
        {}
    )

    bowling_rows = []

    for _, bowler in bowlers_data.items():

        bowling_rows.append(
            {
                "Bowler":
                    bowler.get(
                        "bowlName",
                        ""
                    ),

                "Overs":
                    bowler.get(
                        "overs",
                        0
                    ),

                "Maidens":
                    bowler.get(
                        "maidens",
                        0
                    ),

                "Runs":
                    bowler.get(
                        "runs",
                        0
                    ),

                "Wickets":
                    bowler.get(
                        "wickets",
                        0
                    ),

                "Economy":
                    bowler.get(
                        "economy",
                        0
                    ),

                "No Balls":
                    bowler.get(
                        "no_balls",
                        0
                    ),

                "Wides":
                    bowler.get(
                        "wides",
                        0
                    )
            }
        )


    if bowling_rows:

        bowling_df = pd.DataFrame(
            bowling_rows
        )

        st.dataframe(
            bowling_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Bowling details unavailable."
        )


    # =====================================================
    # FALL OF WICKETS
    # =====================================================

    wickets_data = innings.get(
        "wicketsData",
        {}
    )

    if wickets_data:

        st.subheader(
            "📉 Fall of Wickets"
        )

        wicket_rows = []

        for _, wicket in wickets_data.items():

            wicket_rows.append(
                {
                    "Batsman":
                        wicket.get(
                            "batName",
                            ""
                        ),

                    "Score":
                        wicket.get(
                            "wktRuns",
                            ""
                        ),

                    "Over":
                        wicket.get(
                            "wktOver",
                            ""
                        )
                }
            )

        if wicket_rows:

            wicket_df = pd.DataFrame(
                wicket_rows
            )

            st.dataframe(
                wicket_df,
                use_container_width=True,
                hide_index=True
            )


    st.divider()


# =========================================================
# RAW JSON
# =========================================================

with st.expander(
    "📄 View Raw Scorecard JSON"
):

    st.json(
        scorecard_data
    )