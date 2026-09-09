import requests
import streamlit as st


BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


def get_headers():
    return {
        "X-RapidAPI-Key": st.secrets["API_KEY"],
        "X-RapidAPI-Host": st.secrets["API_HOST"]
    }


def get_live_matches():
    url = f"{BASE_URL}/matches/v1/live"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_upcoming_matches():
    url = f"{BASE_URL}/matches/v1/upcoming"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_recent_matches():
    url = f"{BASE_URL}/matches/v1/recent"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None


# SCORECARD
def get_scorecard(match_id):

    url = f"{BASE_URL}/mcenter/v1/{match_id}/hscard"

    try:

        response = requests.get(
            url,
            headers=get_headers(),
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(f"Scorecard API Error: {e}")

        return None


# PLAYERS
def get_match_team(match_id, team_id):

    url = f"{BASE_URL}/mcenter/v1/{match_id}/team/{team_id}"

    response = requests.get(
        url,
        headers=get_headers(),
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None
