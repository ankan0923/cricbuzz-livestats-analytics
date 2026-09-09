import streamlit as st
import pandas as pd

from api import get_recent_matches
from database import (
    save_api_matches,
    save_api_teams,
    save_api_venues,
    save_api_series
)

st.title("🏏 Recent Matches")

st.caption(
    "View recently completed cricket matches from the Cricbuzz API."
)


# =========================================================
# FETCH DATA
# =========================================================

try:
    data = get_recent_matches()

except Exception as e:
    st.error(f"API Error: {e}")
    data = None


# =========================================================
# CHECK API RESPONSE
# =========================================================

if not data:

    st.warning("No recent match data available.")

else:

    # =====================================================
    # TOP BUTTONS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔄 Refresh Matches",
            use_container_width=True
        ):
            st.rerun()

    with col2:

        if st.button(
                "💾 Save Recent Matches to Database",
                use_container_width=True
        ):

            try:

                match_count = save_api_matches(
                    data
                )

                team_count = save_api_teams(
                    data
                )

                venue_count = save_api_venues(
                    data
                )

                series_count = save_api_series(
                    data
                )

                st.success(
                    f"{match_count} matches, "
                    f"{team_count} team records, "
                    f"{venue_count} venue records and "
                    f"{series_count} series records "
                    f"processed successfully!"
                )

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )

    st.divider()


    # =====================================================
    # EXTRACT MATCH DATA
    # =====================================================

    recent_matches = []

    for match_type in data.get("typeMatches", []):

        match_category = match_type.get(
            "matchType",
            ""
        )

        for series_item in match_type.get(
            "seriesMatches",
            []
        ):

            wrapper = series_item.get(
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

                team1 = (
                    info
                    .get("team1", {})
                    .get("teamName", "")
                )

                team2 = (
                    info
                    .get("team2", {})
                    .get("teamName", "")
                )

                venue_info = info.get(
                    "venueInfo",
                    {}
                )

                ground = venue_info.get(
                    "ground",
                    ""
                )

                city = venue_info.get(
                    "city",
                    ""
                )

                venue = ", ".join(
                    value
                    for value in [ground, city]
                    if value
                )

                recent_matches.append({

                    "Match ID":
                        info.get(
                            "matchId",
                            ""
                        ),

                    "Series":
                        series_name,

                    "Match":
                        f"{team1} vs {team2}",

                    "Description":
                        info.get(
                            "matchDesc",
                            ""
                        ),

                    "Format":
                        info.get(
                            "matchFormat",
                            ""
                        ),

                    "Category":
                        match_category,

                    "Venue":
                        venue,

                    "Status":
                        info.get(
                            "status",
                            ""
                        )
                })


    # =====================================================
    # CONVERT TO DATAFRAME
    # =====================================================

    df = pd.DataFrame(
        recent_matches
    )


    # =====================================================
    # KPI CARDS
    # =====================================================

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        with st.container(border=True):
            st.metric(
                label="🏏 Recent Matches",
                value=len(df)
            )

    with kpi2:
        with st.container(border=True):
            st.metric(
                label="📋 Formats",
                value=df["Format"].nunique()
            )

    with kpi3:
        with st.container(border=True):
            st.metric(
                label="🏆 Series",
                value=df["Series"].nunique()
            )
    # =====================================================
    # FILTERS
    # =====================================================

    st.subheader("🔎 Filter Matches")

    filter_col1, filter_col2 = st.columns(2)


    # -----------------------------
    # FORMAT FILTER
    # -----------------------------

    with filter_col1:

        if not df.empty:

            formats = [
                "All"
            ] + sorted(
                df["Format"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_format = st.selectbox(
                "Match Format",
                formats
            )

        else:

            selected_format = "All"


    # -----------------------------
    # SERIES FILTER
    # -----------------------------

    with filter_col2:

        if not df.empty:

            series_list = [
                "All"
            ] + sorted(
                df["Series"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_series = st.selectbox(
                "Series",
                series_list
            )

        else:

            selected_series = "All"


    # =====================================================
    # APPLY FILTERS
    # =====================================================

    filtered_df = df.copy()


    if selected_format != "All":

        filtered_df = filtered_df[
            filtered_df["Format"]
            == selected_format
        ]


    if selected_series != "All":

        filtered_df = filtered_df[
            filtered_df["Series"]
            == selected_series
        ]


    # =====================================================
    # DISPLAY TABLE
    # =====================================================

    st.subheader("📋 Recent Match Details")

    st.write(
        f"Showing **{len(filtered_df)}** matches"
    )

    if filtered_df.empty:

        st.info(
            "No matches found for the selected filters."
        )

    else:

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )


        # =================================================
        # DOWNLOAD CSV
        # =================================================

        csv = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Recent Matches",
            data=csv,
            file_name="recent_matches.csv",
            mime="text/csv"
        )
