import streamlit as st
import pandas as pd

from datetime import datetime
from api import get_upcoming_matches

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Upcoming Matches",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Upcoming Matches")

st.caption(
    "Select a date to view scheduled cricket matches."
)


# =========================================================
# REFRESH BUTTON
# =========================================================

if st.button(
    "🔄 Refresh Upcoming Matches",
    use_container_width=True
):
    st.rerun()


# =========================================================
# FETCH UPCOMING MATCHES
# =========================================================

data = get_upcoming_matches()


if not data:

    st.error(
        "Unable to load upcoming matches."
    )

    st.stop()


# =========================================================
# FLATTEN API DATA
# =========================================================

rows = []


for match_type in data.get(
    "typeMatches",
    []
):

    match_type_name = match_type.get(
        "matchType",
        "Other"
    )


    for series in match_type.get(
        "seriesMatches",
        []
    ):

        series_data = series.get(
            "seriesAdWrapper"
        )


        if not series_data:
            continue


        series_name = series_data.get(
            "seriesName",
            "Unknown Series"
        )


        for match in series_data.get(
            "matches",
            []
        ):

            info = match.get(
                "matchInfo",
                {}
            )


            # =================================================
            # START DATE
            # =================================================

            start_date = info.get(
                "startDate"
            )


            if not start_date:
                continue


            try:

                timestamp = (
                    int(start_date)
                    / 1000
                )

                match_datetime = (
                    datetime.fromtimestamp(
                        timestamp
                    )
                )

            except Exception:

                continue


            # =================================================
            # TEAMS
            # =================================================

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


            # =================================================
            # VENUE
            # =================================================

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


            country = venue_info.get(
                "country",
                ""
            )


            venue_parts = []


            if ground:
                venue_parts.append(
                    ground
                )


            if city:
                venue_parts.append(
                    city
                )


            if country:
                venue_parts.append(
                    country
                )


            venue = ", ".join(
                venue_parts
            )


            # =================================================
            # ADD ROW
            # =================================================

            rows.append(
                {
                    "Match ID":
                        info.get(
                            "matchId"
                        ),

                    "Date":
                        match_datetime,

                    "Time":
                        match_datetime.strftime(
                            "%I:%M %p"
                        ),

                    "Match Type":
                        match_type_name,

                    "Format":
                        info.get(
                            "matchFormat",
                            ""
                        ),

                    "Series":
                        series_name,

                    "Match":
                        info.get(
                            "matchDesc",
                            ""
                        ),

                    "Team 1":
                        team1,

                    "Team 2":
                        team2,

                    "Venue":
                        venue,

                    "Status":
                        info.get(
                            "status",
                            "Scheduled"
                        )
                }
            )


# =========================================================
# CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(
    rows
)


if df.empty:

    st.warning(
        "No upcoming matches available."
    )

    st.stop()


# =========================================================
# PREPARE DATE COLUMN
# =========================================================

df["Date"] = pd.to_datetime(
    df["Date"]
)


df = df.sort_values(
    "Date"
)


# =========================================================
# DATE RANGE
# =========================================================

available_dates = (
    df["Date"]
    .dt.date
    .dropna()
    .unique()
    .tolist()
)


if not available_dates:

    st.warning(
        "No valid match dates available."
    )

    st.stop()


available_dates = sorted(
    available_dates
)


min_date = min(
    available_dates
)

max_date = max(
    available_dates
)


# =========================================================
# DATE PICKER
# =========================================================

st.subheader(
    "🗓️ Select Match Date"
)


selected_date = st.date_input(
    "Select Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY"
)


# =========================================================
# FILTER MATCHES BY SELECTED DATE
# =========================================================

selected_matches = df[
    df["Date"].dt.date
    == selected_date
].copy()


st.divider()


# =========================================================
# MATCH TABLE TITLE
# =========================================================

st.subheader(
    f"🏏 Matches on "
    f"{selected_date.strftime('%d %B %Y')}"
)


# =========================================================
# NO MATCHES
# =========================================================

if selected_matches.empty:

    st.info(
        "No upcoming matches are scheduled "
        "for the selected date."
    )


# =========================================================
# DISPLAY MATCHES
# =========================================================

else:

    display_df = selected_matches[
        [
            "Date",
            "Time",
            "Match Type",
            "Format",
            "Series",
            "Match",
            "Team 1",
            "Team 2",
            "Venue",
            "Status",
            "Match ID"
        ]
    ].copy()


    # -----------------------------------------------------
    # FORMAT DATE
    # -----------------------------------------------------

    display_df[
        "Date"
    ] = display_df[
        "Date"
    ].dt.strftime(
        "%d %b %Y"
    )


    # -----------------------------------------------------
    # DISPLAY TABLE
    # -----------------------------------------------------

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv = display_df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    st.download_button(
        "⬇️ Download Match Schedule",
        data=csv,
        file_name=(
            f"upcoming_matches_"
            f"{selected_date}.csv"
        ),
        mime="text/csv"
    )


# =========================================================
# RAW JSON
# =========================================================

with st.expander(
    "📄 View Raw Upcoming Match JSON"
):

    st.json(
        data
    )
