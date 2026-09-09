import streamlit as st
from api import get_live_matches

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Live Matches",
    page_icon="🏏",
    layout="wide")


# =========================================================
# PAGE TITLE
# =========================================================

st.title("🔴 Live Cricket Matches")

st.caption(
    "Real-time live match updates from Crickbuzz API"
)


# =========================================================
# REFRESH BUTTON
# =========================================================

if st.button("🔄 Refresh Live Matches"):
    st.rerun()


# =========================================================
# FETCH LIVE MATCHES
# =========================================================

with st.spinner("Loading live matches..."):
    data = get_live_matches()


if data is None:
    st.error("Unable to load live matches from API.")
    st.stop()


if not isinstance(data, dict):
    st.error("The API returned an unexpected response.")
    st.json(data)
    st.stop()


# =========================================================
# VALIDATE RESPONSE STRUCTURE
# =========================================================

if "typeMatches" not in data:
    st.warning(
        "The API returned data, but its structure is different "
        "from the expected Cricbuzz match format."
    )

    st.write("Response keys:", list(data.keys()))

    with st.expander("View API Response"):
        st.json(data)

    st.stop()


type_matches = data.get("typeMatches", [])


if not type_matches:
    st.warning("No live matches are available right now.")
    st.stop()


# =========================================================
# COLLECT KPI DATA
# =========================================================

total_matches = 0
total_series = 0

formats = set()
teams = set()


for match_type in type_matches:

    match_format = match_type.get("matchType")

    if match_format:
        formats.add(match_format)

    for series in match_type.get("seriesMatches", []):

        wrapper = series.get("seriesAdWrapper")

        if not wrapper:
            continue

        total_series += 1

        for match in wrapper.get("matches", []):

            total_matches += 1

            info = match.get("matchInfo", {})

            team1 = (
                info.get("team1", {})
                .get("teamName")
            )

            team2 = (
                info.get("team2", {})
                .get("teamName")
            )

            if team1:
                teams.add(team1)

            if team2:
                teams.add(team2)


# =========================================================
# KPI SECTION
# =========================================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("🏏 Live Matches", total_matches)

with k2:
    st.metric("📺 Live Series", total_series)

with k3:
    st.metric("🎯 Match Formats", len(formats))

with k4:
    st.metric("🌍 Teams Playing", len(teams))


st.divider()


# =========================================================
# DISPLAY LIVE MATCHES
# =========================================================

for match_type in type_matches:

    match_format = match_type.get(
        "matchType",
        "Unknown Format"
    )

    st.markdown(f"## 🏆 {match_format}")

    series_matches = match_type.get(
        "seriesMatches",
        []
    )

    for series in series_matches:

        wrapper = series.get("seriesAdWrapper")

        if not wrapper:
            continue

        series_name = wrapper.get(
            "seriesName",
            "Unknown Series"
        )

        st.markdown(f"### 📌 {series_name}")

        matches = wrapper.get("matches", [])

        for match in matches:

            info = match.get("matchInfo", {})
            score = match.get("matchScore", {})

            # -----------------------------------------
            # MATCH INFORMATION
            # -----------------------------------------

            team1 = (
                info.get("team1", {})
                .get("teamName", "Team 1")
            )

            team2 = (
                info.get("team2", {})
                .get("teamName", "Team 2")
            )

            venue_info = info.get("venueInfo", {})

            venue = venue_info.get(
                "ground",
                "Unknown Venue"
            )

            city = venue_info.get("city", "")

            match_desc = info.get(
                "matchDesc",
                "Match"
            )

            state = str(
                info.get("state", "Unknown")
            )

            status = info.get(
                "status",
                "Status not available"
            )

            toss = (
                info.get("tossResults", {})
                .get("tossWinnerName", "-")
            )

            # -----------------------------------------
            # TEAM 1 SCORE
            # -----------------------------------------

            team1_score = (
                score.get("team1Score", {})
                .get("inngs1", {})
            )

            t1_runs = team1_score.get("runs", "-")
            t1_wickets = team1_score.get("wickets", "-")
            t1_overs = team1_score.get("overs", "-")

            # -----------------------------------------
            # TEAM 2 SCORE
            # -----------------------------------------

            team2_score = (
                score.get("team2Score", {})
                .get("inngs1", {})
            )

            t2_runs = team2_score.get("runs", "-")
            t2_wickets = team2_score.get("wickets", "-")
            t2_overs = team2_score.get("overs", "-")

            # -----------------------------------------
            # MATCH CARD
            # -----------------------------------------

            with st.container(border=True):

                st.markdown(
                    f"### 🏏 {team1} vs {team2}"
                )

                info_col, state_col = st.columns([3, 2])

                with info_col:

                    st.write(f"**Match:** {match_desc}")

                    if city:
                        st.write(
                            f"**Venue:** {venue}, {city}"
                        )
                    else:
                        st.write(
                            f"**Venue:** {venue}"
                        )

                with state_col:

                    state_lower = state.lower()

                    if (
                        "progress" in state_lower
                        or "live" in state_lower
                    ):
                        st.success("🟢 LIVE")

                    elif (
                        "complete" in state_lower
                        or "finished" in state_lower
                    ):
                        st.error("🔴 COMPLETED")

                    else:
                        st.warning(state)

                st.info(status)

                # -------------------------------------
                # SCOREBOARD
                # -------------------------------------

                score_col1, score_col2 = st.columns(2)

                with score_col1:

                    st.markdown(f"### {team1}")

                    if t1_wickets == "-":
                        team1_display = str(t1_runs)
                    else:
                        team1_display = (
                            f"{t1_runs}/{t1_wickets}"
                        )

                    st.metric(
                        "Score",
                        team1_display
                    )

                    st.caption(f"Overs: {t1_overs}")

                with score_col2:

                    st.markdown(f"### {team2}")

                    if t2_wickets == "-":
                        team2_display = str(t2_runs)
                    else:
                        team2_display = (
                            f"{t2_runs}/{t2_wickets}"
                        )

                    st.metric(
                        "Score",
                        team2_display
                    )

                    st.caption(f"Overs: {t2_overs}")

                st.write(f"**Toss Winner:** {toss}")

                with st.expander("📄 View Match JSON"):
                    st.json(match)
