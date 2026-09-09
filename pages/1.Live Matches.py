import streamlit as st
import pandas as pd
from api import get_live_matches

st.set_page_config(page_title="Live Matches", page_icon="🏏")

st.title("🔴 Live Cricket Matches")
st.caption("Real-time live match updates from Cricbuzz API")

# ---------------- Refresh Button ----------------
refresh = st.button("🔄 Refresh Live Matches")

data = get_live_matches()

if not data:
    st.error("Unable to load live matches from API.")
    st.stop()

type_matches = data.get("typeMatches", [])

# ---------------- Collect KPI Data ----------------
total_matches = 0
total_series = 0
formats = set()
teams = set()

for match_type in type_matches:

    formats.add(match_type.get("matchType", ""))

    for series in match_type.get("seriesMatches", []):

        wrapper = series.get("seriesAdWrapper")

        if wrapper:
            total_series += 1

            for match in wrapper.get("matches", []):

                total_matches += 1

                info = match.get("matchInfo", {})

                teams.add(info.get("team1", {}).get("teamName", ""))
                teams.add(info.get("team2", {}).get("teamName", ""))

# ---------------- KPI Section ----------------

k1, k2, k3, k4 = st.columns(4)

k1.metric("🏏 Live Matches", total_matches)
k2.metric("📺 Live Series", total_series)
k3.metric("🎯 Match Formats", len(formats))
k4.metric("🌍 Teams Playing", len(teams))

st.divider()

# =========================================================
# LIVE MATCHES
# =========================================================

for match_type in type_matches:

    st.markdown(f"## 🏆 {match_type.get('matchType','Unknown')}")

    for series in match_type.get("seriesMatches", []):

        wrapper = series.get("seriesAdWrapper")

        if not wrapper:
            continue

        st.markdown(f"### 📌 {wrapper.get('seriesName','Unknown Series')}")

        for match in wrapper.get("matches", []):

            info = match.get("matchInfo", {})
            score = match.get("matchScore", {})

            team1 = info.get("team1", {}).get("teamName", "Team 1")
            team2 = info.get("team2", {}).get("teamName", "Team 2")

            venue = info.get("venueInfo", {}).get("ground", "Unknown Venue")
            city = info.get("venueInfo", {}).get("city", "")

            status = info.get("status", "Status Not Available")

            match_desc = info.get("matchDesc", "")
            state = info.get("state", "")
            toss = info.get("tossResults", {}).get("tossWinnerName", "-")

            team1_score = score.get("team1Score", {}).get("inngs1", {})
            team2_score = score.get("team2Score", {}).get("inngs1", {})

            t1_runs = team1_score.get("runs", "-")
            t1_wkts = team1_score.get("wickets", "-")
            t1_overs = team1_score.get("overs", "-")

            t2_runs = team2_score.get("runs", "-")
            t2_wkts = team2_score.get("wickets", "-")
            t2_overs = team2_score.get("overs", "-")

            # -------- Match Card --------

            with st.container(border=True):

                st.markdown(f"### 🏏 {team1} vs {team2}")

                c1, c2 = st.columns([3,2])

                with c1:

                    st.write(f"**Match:** {match_desc}")
                    st.write(f"**Venue:** {venue}, {city}")

                with c2:

                    if state == "In Progress":
                        st.success("🟢 LIVE")

                    elif state == "Complete":
                        st.error("🔴 COMPLETED")

                    else:
                        st.warning(state)

                st.info(status)

                # ---------------- SCOREBOARD ----------------

                s1, s2 = st.columns(2)

                with s1:

                    st.markdown(f"### 🇮🇳 {team1}")
                    st.metric(
                        "Score",
                        f"{t1_runs}/{t1_wkts}"
                    )
                    st.caption(f"Overs : {t1_overs}")

                with s2:

                    st.markdown(f"### 🇦🇺 {team2}")
                    st.metric(
                        "Score",
                        f"{t2_runs}/{t2_wkts}"
                    )
                    st.caption(f"Overs : {t2_overs}")

                st.write(f"**Toss Winner:** {toss}")

                with st.expander("📄 View Match JSON"):
                    st.json(match)
