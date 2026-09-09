import requests
import streamlit as st


# =========================================================
# API CONFIGURATION
# =========================================================

BASE_URL = "https://crickbuzz-official-apis.p.rapidapi.com"


def get_headers():
    return {
        "X-RapidAPI-Key": st.secrets["API_KEY"],
        "X-RapidAPI-Host": st.secrets["API_HOST"]
    }


# =========================================================
# COMMON API REQUEST
# =========================================================

def make_api_request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.get(
            url,
            headers=get_headers(),
            params=params,
            timeout=15
        )

        if response.status_code == 429:
            st.warning(
                "API request limit reached. Please try again later."
            )
            return None

        if response.status_code != 200:
            st.error(
                f"API request failed. Status: {response.status_code}"
            )
            st.code(response.text[:500])
            return None

        data = response.json()

        # Some providers return an error with HTTP 200.
        if isinstance(data, dict) and "ERROR" in data:
            error_info = data["ERROR"]

            if isinstance(error_info, dict):
                message = error_info.get(
                    "message", "Unknown API error"
                )
            else:
                message = str(error_info)

            st.error(f"API Error: {message}")
            return None

        return data

    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return None

    except requests.exceptions.ConnectionError:
        st.error("Unable to connect to the cricket API.")
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"API request error: {error}")
        return None

    except ValueError:
        st.error("The API returned invalid JSON.")
        return None


# =========================================================
# LIVE MATCHES
# =========================================================

def get_live_matches():
    return make_api_request("/matches/live")


# =========================================================
# UPCOMING MATCHES
# =========================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_upcoming_matches():
    return make_api_request("/matches/upcoming")


# =========================================================
# RECENT MATCHES
# =========================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_recent_matches():
    return make_api_request("/matches/recent")


# =========================================================
# SCORECARD
# =========================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_scorecard(match_id):
    return make_api_request(
        f"/match/{match_id}/scorecard",
        params={"matchID": match_id}
    )


# =========================================================
# MATCH SQUADS / PLAYERS
# =========================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_match_team(match_id, team_id=None):
    # team_id retained for compatibility with existing pages.
    return make_api_request(
        f"/match/{match_id}/squads"
    )
