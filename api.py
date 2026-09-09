import requests
import streamlit as st


# =========================================================
# API CONFIGURATION
# =========================================================

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


def get_headers():

    return {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": st.secrets["API_KEY"],
        "X-RapidAPI-Host": st.secrets["API_HOST"]
    }


# =========================================================
# COMMON REQUEST FUNCTION
# =========================================================

def make_api_request(endpoint):

    url = f"{BASE_URL}{endpoint}"

    try:

        response = requests.get(
            url,
            headers=get_headers(),
            timeout=15
        )

        if response.status_code == 200:

            return response.json()

        if response.status_code == 401:

            st.error(
                "API authentication failed. "
                "Check your API key."
            )

        elif response.status_code == 403:

            st.error(
                "API access denied. Check your "
                "RapidAPI subscription."
            )

        elif response.status_code == 404:

            st.error(
                f"API endpoint not found: {endpoint}"
            )

        elif response.status_code == 429:

            st.error(
                "RapidAPI request limit reached."
            )

        else:

            st.error(
                f"API request failed: "
                f"{response.status_code}"
            )

        st.code(response.text[:500])

        return None

    except requests.exceptions.Timeout:

        st.error(
            "API request timed out."
        )

        return None

    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to the API."
        )

        return None

    except requests.exceptions.RequestException as error:

        st.error(
            f"API request error: {error}"
        )

        return None

    except ValueError:

        st.error(
            "The API returned invalid JSON."
        )

        return None


# =========================================================
# LIVE MATCHES
# =========================================================

def get_live_matches():

    return make_api_request(
        "/matches/v1/live"
    )


# =========================================================
# UPCOMING MATCHES
# =========================================================

def get_upcoming_matches():

    return make_api_request(
        "/matches/v1/upcoming"
    )


# =========================================================
# RECENT MATCHES
# =========================================================

def get_recent_matches():

    return make_api_request(
        "/matches/v1/recent"
    )


# =========================================================
# SCORECARD
# =========================================================

def get_scorecard(match_id):

    return make_api_request(
        f"/mcenter/v1/{match_id}/hscard"
    )


# =========================================================
# TEAM PLAYERS
# =========================================================

def get_match_team(match_id, team_id):

    return make_api_request(
        f"/mcenter/v1/{match_id}/team/{team_id}"
    )
