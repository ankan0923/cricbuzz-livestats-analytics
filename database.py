import os
import sqlite3
from datetime import datetime


# =========================================================
# DATABASE LOCATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_NAME = os.path.join(
    BASE_DIR,
    "cricket.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return conn


# =========================================================
# DATE CONVERSION
# =========================================================

def convert_epoch_date(value):

    if not value:
        return None

    try:

        value = int(value)

        dt = datetime.fromtimestamp(
            value / 1000
        )

        return dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (
        ValueError,
        TypeError,
        OverflowError
    ):

        return str(value)


# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # =================================================
        # MATCHES
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY,
                series_id INTEGER,
                series_name TEXT,
                match_description TEXT,
                match_format TEXT,
                team1_id INTEGER,
                team1_name TEXT,
                team2_id INTEGER,
                team2_name TEXT,
                match_date TEXT,
                status TEXT,
                venue_id INTEGER,
                venue_name TEXT,
                venue_city TEXT,
                venue_country TEXT,
                winner_id INTEGER,
                winner_name TEXT,
                victory_margin INTEGER,
                victory_type TEXT,
                toss_winner_id INTEGER,
                toss_winner_name TEXT,
                toss_decision TEXT
            )
        """)


        # =================================================
        # PLAYERS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                country TEXT,
                playing_role TEXT,
                batting_style TEXT,
                bowling_style TEXT,
                team_id INTEGER,
                team_name TEXT
            )
        """)


        # =================================================
        # TEAMS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY,
                team_name TEXT NOT NULL,
                short_name TEXT,
                country TEXT
            )
        """)


        # =================================================
        # VENUES
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                venue_id INTEGER PRIMARY KEY,
                venue_name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                capacity INTEGER
            )
        """)


        # =================================================
        # SERIES
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                series_id INTEGER PRIMARY KEY,
                series_name TEXT NOT NULL,
                host_country TEXT,
                match_type TEXT,
                start_date TEXT,
                end_date TEXT,
                total_matches INTEGER
            )
        """)


        # =================================================
        # BATTING STATS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batting_stats (
                batting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                innings_number INTEGER,
                batting_position INTEGER,
                runs INTEGER DEFAULT 0,
                balls_faced INTEGER DEFAULT 0,
                fours INTEGER DEFAULT 0,
                sixes INTEGER DEFAULT 0,
                strike_rate REAL,
                dismissal TEXT,

                FOREIGN KEY (match_id)
                    REFERENCES matches(match_id),

                FOREIGN KEY (player_id)
                    REFERENCES players(player_id)
            )
        """)


        # =================================================
        # BOWLING STATS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bowling_stats (
                bowling_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                innings_number INTEGER,
                overs REAL DEFAULT 0,
                maidens INTEGER DEFAULT 0,
                runs_conceded INTEGER DEFAULT 0,
                wickets INTEGER DEFAULT 0,
                economy_rate REAL,
                wides INTEGER DEFAULT 0,
                no_balls INTEGER DEFAULT 0,

                FOREIGN KEY (match_id)
                    REFERENCES matches(match_id),

                FOREIGN KEY (player_id)
                    REFERENCES players(player_id)
            )
        """)


        # =================================================
        # FIELDING STATS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fielding_stats (
                fielding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                innings_number INTEGER,
                catches INTEGER DEFAULT 0,
                stumpings INTEGER DEFAULT 0,
                run_outs INTEGER DEFAULT 0,

                FOREIGN KEY (match_id)
                    REFERENCES matches(match_id),

                FOREIGN KEY (player_id)
                    REFERENCES players(player_id)
            )
        """)


        # =================================================
        # PARTNERSHIPS
        # =================================================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partnerships (
                partnership_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                innings_number INTEGER NOT NULL,
                player1_id INTEGER NOT NULL,
                player2_id INTEGER NOT NULL,
                player1_position INTEGER,
                player2_position INTEGER,
                partnership_runs INTEGER DEFAULT 0,
                partnership_balls INTEGER DEFAULT 0,

                FOREIGN KEY (match_id)
                    REFERENCES matches(match_id),

                FOREIGN KEY (player1_id)
                    REFERENCES players(player_id),

                FOREIGN KEY (player2_id)
                    REFERENCES players(player_id)
            )
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# SAVE MATCHES
# =========================================================

def save_api_matches(data):

    conn = get_connection()
    cursor = conn.cursor()

    saved_count = 0

    try:

        for match_type in data.get(
            "typeMatches",
            []
        ):

            for series_item in match_type.get(
                "seriesMatches",
                []
            ):

                wrapper = series_item.get(
                    "seriesAdWrapper"
                )

                if not wrapper:
                    continue

                series_id = wrapper.get(
                    "seriesId"
                )

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

                    match_id = info.get(
                        "matchId"
                    )

                    if not match_id:
                        continue


                    team1 = info.get(
                        "team1",
                        {}
                    )

                    team2 = info.get(
                        "team2",
                        {}
                    )

                    venue = info.get(
                        "venueInfo",
                        {}
                    )


                    team1_id = team1.get(
                        "teamId"
                    )

                    team1_name = team1.get(
                        "teamName",
                        ""
                    )

                    team2_id = team2.get(
                        "teamId"
                    )

                    team2_name = team2.get(
                        "teamName",
                        ""
                    )


                    winner_id = info.get(
                        "winnerId"
                    )

                    winner_name = None

                    if winner_id == team1_id:
                        winner_name = team1_name

                    elif winner_id == team2_id:
                        winner_name = team2_name


                    cursor.execute("""
                        INSERT INTO matches (
                            match_id,
                            series_id,
                            series_name,
                            match_description,
                            match_format,
                            team1_id,
                            team1_name,
                            team2_id,
                            team2_name,
                            match_date,
                            status,
                            venue_id,
                            venue_name,
                            venue_city,
                            venue_country,
                            winner_id,
                            winner_name,
                            victory_margin,
                            victory_type,
                            toss_winner_id,
                            toss_winner_name,
                            toss_decision
                        )

                        VALUES (
                            :match_id,
                            :series_id,
                            :series_name,
                            :match_description,
                            :match_format,
                            :team1_id,
                            :team1_name,
                            :team2_id,
                            :team2_name,
                            :match_date,
                            :status,
                            :venue_id,
                            :venue_name,
                            :venue_city,
                            :venue_country,
                            :winner_id,
                            :winner_name,
                            :victory_margin,
                            :victory_type,
                            :toss_winner_id,
                            :toss_winner_name,
                            :toss_decision
                        )

                        ON CONFLICT(match_id)
                        DO UPDATE SET
                            series_id = excluded.series_id,
                            series_name = excluded.series_name,
                            match_description = excluded.match_description,
                            match_format = excluded.match_format,
                            team1_id = excluded.team1_id,
                            team1_name = excluded.team1_name,
                            team2_id = excluded.team2_id,
                            team2_name = excluded.team2_name,
                            match_date = excluded.match_date,
                            status = excluded.status,
                            venue_id = excluded.venue_id,
                            venue_name = excluded.venue_name,
                            venue_city = excluded.venue_city,
                            venue_country = excluded.venue_country,
                            winner_id = excluded.winner_id,
                            winner_name = excluded.winner_name
                    """,
                    {
                        "match_id":
                            match_id,

                        "series_id":
                            series_id,

                        "series_name":
                            series_name,

                        "match_description":
                            info.get(
                                "matchDesc",
                                ""
                            ),

                        "match_format":
                            info.get(
                                "matchFormat",
                                ""
                            ),

                        "team1_id":
                            team1_id,

                        "team1_name":
                            team1_name,

                        "team2_id":
                            team2_id,

                        "team2_name":
                            team2_name,

                        "match_date":
                            convert_epoch_date(
                                info.get(
                                    "startDate"
                                )
                            ),

                        "status":
                            info.get(
                                "status",
                                ""
                            ),

                        "venue_id":
                            venue.get(
                                "id"
                            ),

                        "venue_name":
                            venue.get(
                                "ground",
                                ""
                            ),

                        "venue_city":
                            venue.get(
                                "city",
                                ""
                            ),

                        "venue_country":
                            venue.get(
                                "country",
                                ""
                            ),

                        "winner_id":
                            winner_id,

                        "winner_name":
                            winner_name,

                        "victory_margin":
                            None,

                        "victory_type":
                            None,

                        "toss_winner_id":
                            None,

                        "toss_winner_name":
                            None,

                        "toss_decision":
                            None
                    })

                    saved_count += 1

        conn.commit()

        return saved_count

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# SAVE TEAMS
# =========================================================

def save_api_teams(data):

    conn = get_connection()
    cursor = conn.cursor()

    processed_count = 0

    try:

        for match_type in data.get(
            "typeMatches",
            []
        ):

            for series_item in match_type.get(
                "seriesMatches",
                []
            ):

                wrapper = series_item.get(
                    "seriesAdWrapper"
                )

                if not wrapper:
                    continue


                for match in wrapper.get(
                    "matches",
                    []
                ):

                    info = match.get(
                        "matchInfo",
                        {}
                    )


                    for team_key in [
                        "team1",
                        "team2"
                    ]:

                        team = info.get(
                            team_key,
                            {}
                        )

                        team_id = team.get(
                            "teamId"
                        )

                        team_name = team.get(
                            "teamName"
                        )

                        short_name = team.get(
                            "teamSName"
                        )


                        if (
                            not team_id
                            or not team_name
                        ):
                            continue


                        cursor.execute("""
                            INSERT INTO teams (
                                team_id,
                                team_name,
                                short_name,
                                country
                            )

                            VALUES (?, ?, ?, ?)

                            ON CONFLICT(team_id)
                            DO UPDATE SET
                                team_name = excluded.team_name,
                                short_name = excluded.short_name
                        """,
                        (
                            team_id,
                            team_name,
                            short_name,
                            None
                        ))

                        processed_count += 1

        conn.commit()

        return processed_count

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# SAVE VENUES
# =========================================================

def save_api_venues(data):

    conn = get_connection()
    cursor = conn.cursor()

    processed_count = 0

    try:

        for match_type in data.get(
            "typeMatches",
            []
        ):

            for series_item in match_type.get(
                "seriesMatches",
                []
            ):

                wrapper = series_item.get(
                    "seriesAdWrapper"
                )

                if not wrapper:
                    continue


                for match in wrapper.get(
                    "matches",
                    []
                ):

                    info = match.get(
                        "matchInfo",
                        {}
                    )

                    venue = info.get(
                        "venueInfo",
                        {}
                    )

                    venue_id = venue.get(
                        "id"
                    )

                    venue_name = venue.get(
                        "ground"
                    )

                    city = venue.get(
                        "city"
                    )

                    country = venue.get(
                        "country"
                    )


                    if (
                        not venue_id
                        or not venue_name
                    ):
                        continue


                    cursor.execute("""
                        INSERT INTO venues (
                            venue_id,
                            venue_name,
                            city,
                            country,
                            capacity
                        )

                        VALUES (?, ?, ?, ?, ?)

                        ON CONFLICT(venue_id)
                        DO UPDATE SET
                            venue_name = excluded.venue_name,
                            city = excluded.city,
                            country = excluded.country
                    """,
                    (
                        venue_id,
                        venue_name,
                        city,
                        country,
                        None
                    ))

                    processed_count += 1

        conn.commit()

        return processed_count

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# SAVE SERIES
# =========================================================

def save_api_series(data):

    conn = get_connection()
    cursor = conn.cursor()

    processed_count = 0

    try:

        for match_type in data.get(
            "typeMatches",
            []
        ):

            match_type_name = match_type.get(
                "matchType"
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


                series_id = wrapper.get(
                    "seriesId"
                )

                series_name = wrapper.get(
                    "seriesName"
                )


                if (
                    not series_id
                    or not series_name
                ):
                    continue


                matches = wrapper.get(
                    "matches",
                    []
                )

                match_dates = []
                match_formats = set()


                for match in matches:

                    info = match.get(
                        "matchInfo",
                        {}
                    )

                    start_date = info.get(
                        "startDate"
                    )

                    if start_date:

                        try:

                            match_dates.append(
                                int(start_date)
                            )

                        except (
                            ValueError,
                            TypeError
                        ):
                            pass


                    match_format = info.get(
                        "matchFormat"
                    )

                    if match_format:

                        match_formats.add(
                            match_format
                        )


                # -----------------------------------------
                # START / END DATE
                # -----------------------------------------

                start_date = None
                end_date = None

                if match_dates:

                    start_date = convert_epoch_date(
                        min(match_dates)
                    )

                    end_date = convert_epoch_date(
                        max(match_dates)
                    )


                # -----------------------------------------
                # MATCH TYPE
                # -----------------------------------------

                if len(match_formats) == 1:

                    series_match_type = next(
                        iter(match_formats)
                    )

                elif len(match_formats) > 1:

                    series_match_type = ", ".join(
                        sorted(
                            match_formats
                        )
                    )

                else:

                    series_match_type = (
                        match_type_name
                    )


                # -----------------------------------------
                # INSERT / UPDATE
                # -----------------------------------------

                cursor.execute("""
                    INSERT INTO series (
                        series_id,
                        series_name,
                        host_country,
                        match_type,
                        start_date,
                        end_date,
                        total_matches
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(series_id)
                    DO UPDATE SET
                        series_name = excluded.series_name,
                        match_type = excluded.match_type,
                        start_date = excluded.start_date,
                        end_date = excluded.end_date,
                        total_matches = excluded.total_matches
                """,
                (
                    series_id,
                    series_name,
                    None,
                    series_match_type,
                    start_date,
                    end_date,
                    len(matches)
                ))

                processed_count += 1

        conn.commit()

        return processed_count

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# CREATE INDEXES
# =========================================================

def create_indexes():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_matches_format
            ON matches(match_format)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_matches_date
            ON matches(match_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_matches_team1
            ON matches(team1_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_matches_team2
            ON matches(team2_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_matches_series
            ON matches(series_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_players_country
            ON players(country)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_batting_player
            ON batting_stats(player_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_batting_match
            ON batting_stats(match_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_bowling_player
            ON bowling_stats(player_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_bowling_match
            ON bowling_stats(match_id)
        """)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

create_tables()
create_indexes()