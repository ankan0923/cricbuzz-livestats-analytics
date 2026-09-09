import math
import streamlit as st
import pandas as pd
from database import get_connection

st.set_page_config(page_title="Cricket SQL Analytics", page_icon="📊", layout="wide")
st.title("📊 Cricket SQL Analytics")
st.caption("Run the 25 project SQL analytics questions or write your own SELECT query.")

QUESTIONS = {
    "Beginner": {
        "Q1: Indian players": {
            "context": "Find all players who represent India and show their role and playing styles.",
            "sql": """
                SELECT full_name, playing_role, batting_style, bowling_style
                FROM players
                WHERE LOWER(TRIM(country)) = 'india'
                ORDER BY full_name;
            """
        },
        "Q2: Matches played in the last 30 days": {
            "context": "Shows matches played in the last 30 days, newest first.",
            "sql": """
                SELECT match_description, team1_name, team2_name,
                       venue_name, venue_city, match_date
                FROM matches
                WHERE DATE(match_date) >= DATE('now', '-30 day')
                  AND DATE(match_date) <= DATE('now')
                ORDER BY DATETIME(match_date) DESC;
            """
        },
        "Q3: Top 10 ODI run scorers": {
            "context": "Ranks ODI batters by total runs, batting average and centuries.",
            "sql": """
                SELECT p.full_name AS player_name,
                       SUM(b.runs) AS total_runs,
                       ROUND(
                           SUM(b.runs) * 1.0 /
                           NULLIF(SUM(CASE
                               WHEN b.dismissal IS NOT NULL
                                AND TRIM(b.dismissal) != ''
                                AND LOWER(b.dismissal) NOT LIKE '%not out%'
                               THEN 1 ELSE 0 END), 0), 2
                       ) AS batting_average,
                       SUM(CASE WHEN b.runs >= 100 THEN 1 ELSE 0 END) AS centuries
                FROM batting_stats b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE UPPER(m.match_format) = 'ODI'
                GROUP BY p.player_id, p.full_name
                ORDER BY total_runs DESC
                LIMIT 10;
            """
        },
        "Q4: Venues with capacity above 50,000": {
            "context": "Lists venues with seating capacity above 50,000.",
            "sql": """
                SELECT venue_name, city, country, capacity
                FROM venues
                WHERE capacity > 50000
                ORDER BY capacity DESC;
            """
        },
        "Q5: Match wins per team": {
            "context": "Counts how many matches each team has won.",
            "sql": """
                SELECT winner_name AS team_name, COUNT(*) AS total_wins
                FROM matches
                WHERE winner_name IS NOT NULL AND TRIM(winner_name) != ''
                GROUP BY winner_name
                ORDER BY total_wins DESC;
            """
        },
        "Q6: Player count by role": {
            "context": "Counts players in each playing role.",
            "sql": """
                SELECT playing_role, COUNT(*) AS player_count
                FROM players
                WHERE playing_role IS NOT NULL AND TRIM(playing_role) != ''
                GROUP BY playing_role
                ORDER BY player_count DESC;
            """
        },
        "Q7: Highest batting score by format": {
            "context": "Shows the highest individual score in Test, ODI and T20I.",
            "sql": """
                SELECT UPPER(m.match_format) AS format,
                       MAX(b.runs) AS highest_score
                FROM batting_stats b
                JOIN matches m ON m.match_id = b.match_id
                WHERE UPPER(m.match_format) IN ('TEST', 'ODI', 'T20I')
                GROUP BY UPPER(m.match_format)
                ORDER BY CASE UPPER(m.match_format)
                    WHEN 'TEST' THEN 1 WHEN 'ODI' THEN 2 WHEN 'T20I' THEN 3 ELSE 4 END;
            """
        },
        "Q8: Series started in 2024": {
            "context": "Shows series whose start date falls in 2024.",
            "sql": """
                SELECT series_name, host_country, match_type,
                       start_date, total_matches
                FROM series
                WHERE STRFTIME('%Y', start_date) = '2024'
                   OR SUBSTR(start_date, 1, 4) = '2024'
                ORDER BY start_date;
            """
        }
    },

    "Intermediate": {
        "Q9: All-rounders with 1000+ runs and 50+ wickets": {
            "context": "Finds all-rounders crossing both batting and bowling thresholds by format.",
            "sql": """
                WITH batting AS (
                    SELECT b.player_id, UPPER(m.match_format) AS format,
                           SUM(b.runs) AS total_runs
                    FROM batting_stats b
                    JOIN matches m ON m.match_id = b.match_id
                    GROUP BY b.player_id, UPPER(m.match_format)
                ),
                bowling AS (
                    SELECT bw.player_id, UPPER(m.match_format) AS format,
                           SUM(bw.wickets) AS total_wickets
                    FROM bowling_stats bw
                    JOIN matches m ON m.match_id = bw.match_id
                    GROUP BY bw.player_id, UPPER(m.match_format)
                )
                SELECT p.full_name AS player_name,
                       bt.total_runs, bw.total_wickets, bt.format
                FROM batting bt
                JOIN bowling bw ON bw.player_id = bt.player_id AND bw.format = bt.format
                JOIN players p ON p.player_id = bt.player_id
                WHERE LOWER(p.playing_role) LIKE '%allrounder%'
                  AND bt.total_runs > 1000
                  AND bw.total_wickets > 50
                ORDER BY bt.total_runs DESC, bw.total_wickets DESC;
            """
        },
        "Q10: Last 20 completed matches": {
            "context": "Shows the latest 20 completed matches with result details.",
            "sql": """
                SELECT match_description, team1_name, team2_name,
                       winner_name AS winning_team, victory_margin,
                       victory_type, venue_name
                FROM matches
                WHERE LOWER(status) LIKE '%complete%'
                   OR LOWER(status) LIKE '%won%'
                   OR winner_name IS NOT NULL
                ORDER BY DATETIME(match_date) DESC
                LIMIT 20;
            """
        },
        "Q11: Player performance across formats": {
            "context": "Compares Test, ODI and T20I batting for players appearing in at least two formats.",
            "sql": """
                WITH pf AS (
                    SELECT b.player_id, UPPER(m.match_format) AS format,
                           SUM(b.runs) AS runs,
                           SUM(CASE
                               WHEN b.dismissal IS NOT NULL
                                AND TRIM(b.dismissal) != ''
                                AND LOWER(b.dismissal) NOT LIKE '%not out%'
                               THEN 1 ELSE 0 END) AS dismissals
                    FROM batting_stats b
                    JOIN matches m ON m.match_id = b.match_id
                    WHERE UPPER(m.match_format) IN ('TEST','ODI','T20I')
                    GROUP BY b.player_id, UPPER(m.match_format)
                ),
                eligible AS (
                    SELECT player_id
                    FROM pf
                    GROUP BY player_id
                    HAVING COUNT(DISTINCT format) >= 2
                )
                SELECT p.full_name AS player_name,
                       SUM(CASE WHEN pf.format='TEST' THEN pf.runs ELSE 0 END) AS test_runs,
                       SUM(CASE WHEN pf.format='ODI' THEN pf.runs ELSE 0 END) AS odi_runs,
                       SUM(CASE WHEN pf.format='T20I' THEN pf.runs ELSE 0 END) AS t20i_runs,
                       ROUND(SUM(pf.runs) * 1.0 / NULLIF(SUM(pf.dismissals),0), 2)
                           AS overall_batting_average
                FROM pf
                JOIN eligible e ON e.player_id = pf.player_id
                JOIN players p ON p.player_id = pf.player_id
                GROUP BY p.player_id, p.full_name
                ORDER BY overall_batting_average DESC;
            """
        },
        "Q12: Home vs away wins": {
            "context": "Compares team wins at home and away using team country versus venue country.",
            "sql": """
                SELECT t.team_name,
                       SUM(CASE
                           WHEN LOWER(TRIM(m.venue_country)) = LOWER(TRIM(t.country))
                            AND m.winner_name = t.team_name
                           THEN 1 ELSE 0 END) AS home_wins,
                       SUM(CASE
                           WHEN LOWER(TRIM(m.venue_country)) != LOWER(TRIM(t.country))
                            AND m.winner_name = t.team_name
                           THEN 1 ELSE 0 END) AS away_wins
                FROM teams t
                JOIN matches m ON m.team1_name = t.team_name OR m.team2_name = t.team_name
                WHERE t.country IS NOT NULL AND TRIM(t.country) != ''
                  AND m.venue_country IS NOT NULL AND TRIM(m.venue_country) != ''
                GROUP BY t.team_id, t.team_name
                ORDER BY (home_wins + away_wins) DESC;
            """
        },
        "Q13: Consecutive batsmen with 100+ combined runs": {
            "context": "Finds consecutive batting positions in the same innings with at least 100 combined runs.",
            "sql": """
                SELECT p1.full_name AS batsman_1,
                       p2.full_name AS batsman_2,
                       (b1.runs + b2.runs) AS combined_runs,
                       b1.innings_number,
                       b1.match_id
                FROM batting_stats b1
                JOIN batting_stats b2
                  ON b2.match_id = b1.match_id
                 AND b2.innings_number = b1.innings_number
                 AND b2.batting_position = b1.batting_position + 1
                JOIN players p1 ON p1.player_id = b1.player_id
                JOIN players p2 ON p2.player_id = b2.player_id
                WHERE (b1.runs + b2.runs) >= 100
                ORDER BY combined_runs DESC;
            """
        },
        "Q14: Bowling performance by venue": {
            "context": "Evaluates bowlers at venues with at least 3 qualifying matches and 4+ overs each appearance.",
            "sql": """
                SELECT p.full_name AS bowler_name,
                       m.venue_name,
                       ROUND(AVG(b.economy_rate), 2) AS avg_economy,
                       SUM(b.wickets) AS total_wickets,
                       COUNT(DISTINCT b.match_id) AS matches_played
                FROM bowling_stats b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE b.overs >= 4
                GROUP BY b.player_id, p.full_name, m.venue_name
                HAVING COUNT(DISTINCT b.match_id) >= 3
                ORDER BY avg_economy ASC, total_wickets DESC;
            """
        },
        "Q15: Player performance in close matches": {
            "context": "Analyzes batting in matches won by fewer than 50 runs or fewer than 5 wickets.",
            "sql": """
                WITH close_matches AS (
                    SELECT *
                    FROM matches
                    WHERE (LOWER(victory_type)='runs' AND victory_margin < 50)
                       OR (LOWER(victory_type)='wickets' AND victory_margin < 5)
                )
                SELECT p.full_name AS player_name,
                       ROUND(AVG(b.runs), 2) AS average_runs,
                       COUNT(DISTINCT b.match_id) AS close_matches_played,
                       COUNT(DISTINCT CASE
                           WHEN cm.winner_name = p.team_name THEN b.match_id END)
                           AS close_match_wins
                FROM batting_stats b
                JOIN players p ON p.player_id = b.player_id
                JOIN close_matches cm ON cm.match_id = b.match_id
                GROUP BY p.player_id, p.full_name
                ORDER BY average_runs DESC, close_match_wins DESC;
            """
        },
        "Q16: Yearly batting performance since 2020": {
            "context": "Tracks average runs and strike rate by player and year since 2020.",
            "sql": """
                SELECT p.full_name AS player_name,
                       STRFTIME('%Y', m.match_date) AS year,
                       ROUND(AVG(b.runs), 2) AS avg_runs_per_match,
                       ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate,
                       COUNT(DISTINCT b.match_id) AS matches_played
                FROM batting_stats b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE DATE(m.match_date) >= DATE('2020-01-01')
                GROUP BY b.player_id, p.full_name, STRFTIME('%Y', m.match_date)
                HAVING COUNT(DISTINCT b.match_id) >= 5
                ORDER BY p.full_name, year;
            """
        }
    },

    "Advanced": {
        "Q17: Toss advantage": {
            "context": "Measures the percentage of toss-winning teams that also win the match, by toss decision.",
            "sql": """
                SELECT toss_decision,
                       COUNT(*) AS total_matches,
                       SUM(CASE WHEN toss_winner_name = winner_name THEN 1 ELSE 0 END)
                           AS toss_winner_match_wins,
                       ROUND(
                           SUM(CASE WHEN toss_winner_name = winner_name THEN 1 ELSE 0 END)
                           * 100.0 / COUNT(*), 2
                       ) AS toss_win_to_match_win_percentage
                FROM matches
                WHERE toss_winner_name IS NOT NULL
                  AND winner_name IS NOT NULL
                  AND toss_decision IS NOT NULL
                GROUP BY toss_decision
                ORDER BY toss_win_to_match_win_percentage DESC;
            """
        },
        "Q18: Most economical limited-overs bowlers": {
            "context": "Ranks ODI/T20/T20I bowlers with at least 10 matches and 2+ average overs per appearance.",
            "sql": """
                SELECT p.full_name AS bowler_name,
                       ROUND(SUM(b.runs_conceded) * 1.0 / NULLIF(SUM(b.overs),0), 2)
                           AS overall_economy,
                       SUM(b.wickets) AS total_wickets,
                       COUNT(DISTINCT b.match_id) AS matches_played,
                       ROUND(AVG(b.overs), 2) AS avg_overs_per_match
                FROM bowling_stats b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE UPPER(m.match_format) IN ('ODI','T20','T20I')
                GROUP BY b.player_id, p.full_name
                HAVING COUNT(DISTINCT b.match_id) >= 10
                   AND AVG(b.overs) >= 2
                ORDER BY overall_economy ASC, total_wickets DESC;
            """
        },
        "Q19: Most consistent batsmen": {
            "context": "Measures average runs and standard deviation for batting performances since 2022.",
            "sql": """
                SELECT p.full_name AS player_name,
                       ROUND(AVG(b.runs), 2) AS average_runs,
                       ROUND(SQRT(MAX(0,
                           AVG(b.runs * b.runs) - AVG(b.runs) * AVG(b.runs)
                       )), 2) AS runs_stddev,
                       COUNT(*) AS innings_played
                FROM batting_stats b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE DATE(m.match_date) >= DATE('2022-01-01')
                  AND b.balls_faced >= 10
                GROUP BY b.player_id, p.full_name
                ORDER BY runs_stddev ASC, average_runs DESC;
            """
        },
        "Q20: Matches and batting average by format": {
            "context": "Shows Test, ODI and T20 match counts and batting averages for players with 20+ matches overall.",
            "sql": """
                WITH pf AS (
                    SELECT b.player_id,
                           UPPER(m.match_format) AS format,
                           COUNT(DISTINCT b.match_id) AS matches_played,
                           SUM(b.runs) AS runs,
                           SUM(CASE
                               WHEN b.dismissal IS NOT NULL
                                AND TRIM(b.dismissal) != ''
                                AND LOWER(b.dismissal) NOT LIKE '%not out%'
                               THEN 1 ELSE 0 END) AS dismissals
                    FROM batting_stats b
                    JOIN matches m ON m.match_id = b.match_id
                    WHERE UPPER(m.match_format) IN ('TEST','ODI','T20','T20I')
                    GROUP BY b.player_id, UPPER(m.match_format)
                ),
                totals AS (
                    SELECT player_id, SUM(matches_played) AS total_matches
                    FROM pf
                    GROUP BY player_id
                    HAVING SUM(matches_played) >= 20
                )
                SELECT p.full_name AS player_name,
                       SUM(CASE WHEN pf.format='TEST' THEN pf.matches_played ELSE 0 END) AS test_matches,
                       ROUND(SUM(CASE WHEN pf.format='TEST' THEN pf.runs ELSE 0 END) * 1.0 /
                             NULLIF(SUM(CASE WHEN pf.format='TEST' THEN pf.dismissals ELSE 0 END),0), 2)
                             AS test_average,
                       SUM(CASE WHEN pf.format='ODI' THEN pf.matches_played ELSE 0 END) AS odi_matches,
                       ROUND(SUM(CASE WHEN pf.format='ODI' THEN pf.runs ELSE 0 END) * 1.0 /
                             NULLIF(SUM(CASE WHEN pf.format='ODI' THEN pf.dismissals ELSE 0 END),0), 2)
                             AS odi_average,
                       SUM(CASE WHEN pf.format IN ('T20','T20I') THEN pf.matches_played ELSE 0 END)
                             AS t20_matches,
                       ROUND(SUM(CASE WHEN pf.format IN ('T20','T20I') THEN pf.runs ELSE 0 END) * 1.0 /
                             NULLIF(SUM(CASE WHEN pf.format IN ('T20','T20I') THEN pf.dismissals ELSE 0 END),0), 2)
                             AS t20_average,
                       t.total_matches
                FROM pf
                JOIN totals t ON t.player_id = pf.player_id
                JOIN players p ON p.player_id = pf.player_id
                GROUP BY p.player_id, p.full_name, t.total_matches
                ORDER BY t.total_matches DESC;
            """
        },
        "Q21: Comprehensive player ranking": {
            "context": "Combines batting, bowling and fielding points and ranks players within each format.",
            "sql": """
                WITH batting AS (
                    SELECT b.player_id, UPPER(m.match_format) AS format,
                           SUM(b.runs) AS runs_scored,
                           SUM(CASE
                               WHEN b.dismissal IS NOT NULL
                                AND TRIM(b.dismissal) != ''
                                AND LOWER(b.dismissal) NOT LIKE '%not out%'
                               THEN 1 ELSE 0 END) AS dismissals,
                           SUM(b.balls_faced) AS balls_faced
                    FROM batting_stats b
                    JOIN matches m ON m.match_id = b.match_id
                    GROUP BY b.player_id, UPPER(m.match_format)
                ),
                bowling AS (
                    SELECT bw.player_id, UPPER(m.match_format) AS format,
                           SUM(bw.wickets) AS wickets_taken,
                           SUM(bw.runs_conceded) AS runs_conceded,
                           SUM(bw.overs) AS overs_bowled
                    FROM bowling_stats bw
                    JOIN matches m ON m.match_id = bw.match_id
                    GROUP BY bw.player_id, UPPER(m.match_format)
                ),
                fielding AS (
                    SELECT f.player_id, UPPER(m.match_format) AS format,
                           SUM(f.catches) AS catches,
                           SUM(f.stumpings) AS stumpings
                    FROM fielding_stats f
                    JOIN matches m ON m.match_id = f.match_id
                    GROUP BY f.player_id, UPPER(m.match_format)
                ),
                player_formats AS (
                    SELECT player_id, format FROM batting
                    UNION SELECT player_id, format FROM bowling
                    UNION SELECT player_id, format FROM fielding
                ),
                metrics AS (
                    SELECT pf.player_id, pf.format,
                           COALESCE(bt.runs_scored,0) AS runs_scored,
                           COALESCE(bt.runs_scored * 1.0 / NULLIF(bt.dismissals,0),0) AS batting_average,
                           COALESCE(bt.runs_scored * 100.0 / NULLIF(bt.balls_faced,0),0) AS strike_rate,
                           COALESCE(bw.wickets_taken,0) AS wickets_taken,
                           COALESCE(bw.runs_conceded * 1.0 / NULLIF(bw.wickets_taken,0),50) AS bowling_average,
                           COALESCE(bw.runs_conceded * 1.0 / NULLIF(bw.overs_bowled,0),6) AS economy_rate,
                           COALESCE(fd.catches,0) AS catches,
                           COALESCE(fd.stumpings,0) AS stumpings
                    FROM player_formats pf
                    LEFT JOIN batting bt ON bt.player_id=pf.player_id AND bt.format=pf.format
                    LEFT JOIN bowling bw ON bw.player_id=pf.player_id AND bw.format=pf.format
                    LEFT JOIN fielding fd ON fd.player_id=pf.player_id AND fd.format=pf.format
                ),
                scored AS (
                    SELECT *,
                           (runs_scored*0.01) + (batting_average*0.5) + (strike_rate*0.3)
                               AS batting_points,
                           (wickets_taken*2) + ((50-bowling_average)*0.5) + ((6-economy_rate)*2)
                               AS bowling_points,
                           (catches*3) + (stumpings*5) AS fielding_points
                    FROM metrics
                )
                SELECT p.full_name AS player_name, s.format,
                       ROUND(s.batting_points,2) AS batting_points,
                       ROUND(s.bowling_points,2) AS bowling_points,
                       ROUND(s.fielding_points,2) AS fielding_points,
                       ROUND(s.batting_points+s.bowling_points+s.fielding_points,2) AS total_score,
                       RANK() OVER (
                           PARTITION BY s.format
                           ORDER BY (s.batting_points+s.bowling_points+s.fielding_points) DESC
                       ) AS format_rank
                FROM scored s
                JOIN players p ON p.player_id = s.player_id
                ORDER BY s.format, format_rank;
            """
        },
        "Q22: Head-to-head analysis": {
            "context": "Analyzes team pairs with 5+ meetings in the last 3 years, including wins, margins and batting-first/bowling-first results by venue.",
            "sql": """
                WITH recent AS (
                    SELECT *,
                           CASE WHEN team1_name < team2_name THEN team1_name ELSE team2_name END AS team_a,
                           CASE WHEN team1_name < team2_name THEN team2_name ELSE team1_name END AS team_b,
                           CASE
                               WHEN LOWER(toss_decision)='bat' THEN toss_winner_name
                               WHEN LOWER(toss_decision)='bowl' THEN
                                   CASE WHEN toss_winner_name=team1_name THEN team2_name ELSE team1_name END
                           END AS batting_first_team
                    FROM matches
                    WHERE DATE(match_date) >= DATE('now','-3 years')
                      AND team1_name IS NOT NULL
                      AND team2_name IS NOT NULL
                ),
                eligible AS (
                    SELECT team_a, team_b
                    FROM recent
                    GROUP BY team_a, team_b
                    HAVING COUNT(*) >= 5
                )
                SELECT r.team_a, r.team_b, r.venue_name,
                       COUNT(*) AS total_meetings,
                       SUM(CASE WHEN r.winner_name=r.team_a THEN 1 ELSE 0 END) AS team_a_wins,
                       SUM(CASE WHEN r.winner_name=r.team_b THEN 1 ELSE 0 END) AS team_b_wins,
                       ROUND(AVG(CASE WHEN r.winner_name=r.team_a THEN r.victory_margin END),2)
                           AS team_a_avg_victory_margin,
                       ROUND(AVG(CASE WHEN r.winner_name=r.team_b THEN r.victory_margin END),2)
                           AS team_b_avg_victory_margin,
                       SUM(CASE WHEN r.batting_first_team=r.team_a AND r.winner_name=r.team_a THEN 1 ELSE 0 END)
                           AS team_a_wins_batting_first,
                       SUM(CASE WHEN r.batting_first_team!=r.team_a AND r.winner_name=r.team_a THEN 1 ELSE 0 END)
                           AS team_a_wins_bowling_first,
                       SUM(CASE WHEN r.batting_first_team=r.team_b AND r.winner_name=r.team_b THEN 1 ELSE 0 END)
                           AS team_b_wins_batting_first,
                       SUM(CASE WHEN r.batting_first_team!=r.team_b AND r.winner_name=r.team_b THEN 1 ELSE 0 END)
                           AS team_b_wins_bowling_first,
                       ROUND(SUM(CASE WHEN r.winner_name=r.team_a THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
                           AS team_a_win_percentage,
                       ROUND(SUM(CASE WHEN r.winner_name=r.team_b THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
                           AS team_b_win_percentage
                FROM recent r
                JOIN eligible e ON e.team_a=r.team_a AND e.team_b=r.team_b
                GROUP BY r.team_a, r.team_b, r.venue_name
                ORDER BY total_meetings DESC, r.team_a, r.team_b;
            """
        },
        "Q23: Recent player form": {
            "context": "Compares each player's last 5 and last 10 batting performances and assigns a form category.",
            "sql": """
                WITH ranked AS (
                    SELECT b.player_id, b.match_id, b.runs, b.strike_rate, m.match_date,
                           ROW_NUMBER() OVER (
                               PARTITION BY b.player_id
                               ORDER BY DATETIME(m.match_date) DESC, b.match_id DESC, b.innings_number DESC
                           ) AS rn
                    FROM batting_stats b
                    JOIN matches m ON m.match_id = b.match_id
                ),
                last10 AS (
                    SELECT * FROM ranked WHERE rn <= 10
                ),
                form AS (
                    SELECT player_id,
                           ROUND(AVG(CASE WHEN rn<=5 THEN runs END),2) AS avg_runs_last_5,
                           ROUND(AVG(runs),2) AS avg_runs_last_10,
                           ROUND(AVG(CASE WHEN rn<=5 THEN strike_rate END),2) AS avg_sr_last_5,
                           ROUND(AVG(strike_rate),2) AS avg_sr_last_10,
                           SUM(CASE WHEN runs>=50 THEN 1 ELSE 0 END) AS scores_50_plus,
                           ROUND(SQRT(MAX(0, AVG(runs*runs)-AVG(runs)*AVG(runs))),2)
                               AS consistency_stddev,
                           COUNT(*) AS performances_used
                    FROM last10
                    GROUP BY player_id
                    HAVING COUNT(*) >= 5
                )
                SELECT p.full_name AS player_name,
                       f.avg_runs_last_5, f.avg_runs_last_10,
                       f.avg_sr_last_5, f.avg_sr_last_10,
                       f.scores_50_plus, f.consistency_stddev,
                       f.performances_used,
                       CASE
                           WHEN f.avg_runs_last_5 >= 50 AND f.avg_runs_last_5 >= f.avg_runs_last_10
                               THEN 'Excellent Form'
                           WHEN f.avg_runs_last_5 >= 35 THEN 'Good Form'
                           WHEN f.avg_runs_last_5 >= 20 THEN 'Average Form'
                           ELSE 'Poor Form'
                       END AS form_category
                FROM form f
                JOIN players p ON p.player_id = f.player_id
                ORDER BY f.avg_runs_last_5 DESC, f.consistency_stddev ASC;
            """
        },
        "Q24: Best batting partnerships": {
            "context": "Ranks consecutive-position batting pairs with at least five partnerships.",
            "sql": """
                WITH eligible AS (
                    SELECT pt.*,
                           CASE WHEN pt.player1_id < pt.player2_id THEN pt.player1_id ELSE pt.player2_id END
                               AS player_a_id,
                           CASE WHEN pt.player1_id < pt.player2_id THEN pt.player2_id ELSE pt.player1_id END
                               AS player_b_id
                    FROM partnerships pt
                    WHERE ABS(pt.player1_position - pt.player2_position) = 1
                ),
                summary AS (
                    SELECT player_a_id, player_b_id,
                           COUNT(*) AS total_partnerships,
                           ROUND(AVG(partnership_runs),2) AS avg_partnership_runs,
                           SUM(CASE WHEN partnership_runs>=50 THEN 1 ELSE 0 END) AS partnerships_50_plus,
                           MAX(partnership_runs) AS highest_partnership,
                           ROUND(SUM(CASE WHEN partnership_runs>=50 THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
                               AS success_rate
                    FROM eligible
                    GROUP BY player_a_id, player_b_id
                    HAVING COUNT(*) >= 5
                )
                SELECT p1.full_name AS player_1,
                       p2.full_name AS player_2,
                       s.total_partnerships,
                       s.avg_partnership_runs,
                       s.partnerships_50_plus,
                       s.highest_partnership,
                       s.success_rate,
                       RANK() OVER (
                           ORDER BY s.success_rate DESC, s.avg_partnership_runs DESC
                       ) AS partnership_rank
                FROM summary s
                JOIN players p1 ON p1.player_id = s.player_a_id
                JOIN players p2 ON p2.player_id = s.player_b_id
                ORDER BY partnership_rank;
            """
        },
        "Q25: Quarterly player performance evolution": {
            "context": "Tracks quarterly batting averages, quarter-over-quarter trend and career phase.",
            "sql": """
                WITH qb AS (
                    SELECT b.player_id,
                           STRFTIME('%Y', m.match_date) || '-Q' ||
                           CASE
                               WHEN CAST(STRFTIME('%m',m.match_date) AS INTEGER) BETWEEN 1 AND 3 THEN '1'
                               WHEN CAST(STRFTIME('%m',m.match_date) AS INTEGER) BETWEEN 4 AND 6 THEN '2'
                               WHEN CAST(STRFTIME('%m',m.match_date) AS INTEGER) BETWEEN 7 AND 9 THEN '3'
                               ELSE '4'
                           END AS quarter,
                           ROUND(AVG(b.runs),2) AS avg_runs,
                           ROUND(AVG(b.strike_rate),2) AS avg_strike_rate,
                           COUNT(DISTINCT b.match_id) AS matches_played
                    FROM batting_stats b
                    JOIN matches m ON m.match_id = b.match_id
                    WHERE m.match_date IS NOT NULL
                    GROUP BY b.player_id, quarter
                    HAVING COUNT(DISTINCT b.match_id) >= 3
                ),
                eligible AS (
                    SELECT player_id
                    FROM qb
                    GROUP BY player_id
                    HAVING COUNT(*) >= 6
                ),
                q AS (
                    SELECT qb.*,
                           LAG(qb.avg_runs) OVER (
                               PARTITION BY qb.player_id ORDER BY qb.quarter
                           ) AS previous_avg_runs,
                           LAG(qb.avg_strike_rate) OVER (
                               PARTITION BY qb.player_id ORDER BY qb.quarter
                           ) AS previous_avg_strike_rate,
                           FIRST_VALUE(qb.avg_runs) OVER (
                               PARTITION BY qb.player_id ORDER BY qb.quarter
                               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                           ) AS first_quarter_runs,
                           LAST_VALUE(qb.avg_runs) OVER (
                               PARTITION BY qb.player_id ORDER BY qb.quarter
                               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                           ) AS last_quarter_runs
                    FROM qb
                    JOIN eligible e ON e.player_id = qb.player_id
                )
                SELECT p.full_name AS player_name,
                       q.quarter, q.matches_played,
                       q.avg_runs, q.avg_strike_rate,
                       q.previous_avg_runs, q.previous_avg_strike_rate,
                       ROUND(q.avg_runs-q.previous_avg_runs,2) AS runs_change,
                       ROUND(q.avg_strike_rate-q.previous_avg_strike_rate,2) AS strike_rate_change,
                       CASE
                           WHEN q.previous_avg_runs IS NULL THEN 'Starting Quarter'
                           WHEN q.avg_runs > q.previous_avg_runs
                            AND q.avg_strike_rate >= q.previous_avg_strike_rate THEN 'Improving'
                           WHEN q.avg_runs < q.previous_avg_runs
                            AND q.avg_strike_rate <= q.previous_avg_strike_rate THEN 'Declining'
                           ELSE 'Stable'
                       END AS quarterly_trend,
                       CASE
                           WHEN q.last_quarter_runs > q.first_quarter_runs*1.10 THEN 'Career Ascending'
                           WHEN q.last_quarter_runs < q.first_quarter_runs*0.90 THEN 'Career Declining'
                           ELSE 'Career Stable'
                       END AS career_phase
                FROM q
                JOIN players p ON p.player_id = q.player_id
                ORDER BY p.full_name, q.quarter;
            """
        }
    }
}


def prepare_connection():
    conn = get_connection()
    conn.create_function(
        "SQRT",
        1,
        lambda x: math.sqrt(x) if x is not None and x >= 0 else None
    )
    return conn


def run_predefined_query(question, key_name):
    st.markdown(f"**Business Context:** {question['context']}")
    sql = question["sql"]

    with st.expander("🔍 View SQL", expanded=True):
        st.code(sql.strip(), language="sql")

    conn = prepare_connection()
    try:
        df = pd.read_sql_query(sql, conn)
        st.markdown(f"### {len(df)} rows")

        if df.empty:
            st.info(
                "Query executed successfully, but no records were found. "
                "The required table may not have enough data yet."
            )
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download result as CSV",
                data=csv,
                file_name=f"{key_name}_sql_result.csv",
                mime="text/csv",
                key=f"download_{key_name}"
            )
    except Exception as e:
        st.error(f"SQL Error: {e}")
    finally:
        conn.close()


beginner_tab, intermediate_tab, advanced_tab = st.tabs([
    "🌱 Beginner (Q1–Q8)",
    "⚡ Intermediate (Q9–Q16)",
    "🚀 Advanced (Q17–Q25)"
])

with beginner_tab:
    st.header("Beginner Queries")
    q = st.selectbox(
        "Choose a Beginner Question",
        list(QUESTIONS["Beginner"].keys()),
        key="beginner_select"
    )
    run_predefined_query(QUESTIONS["Beginner"][q], "beginner")

with intermediate_tab:
    st.header("Intermediate Queries")
    q = st.selectbox(
        "Choose an Intermediate Question",
        list(QUESTIONS["Intermediate"].keys()),
        key="intermediate_select"
    )
    run_predefined_query(QUESTIONS["Intermediate"][q], "intermediate")

with advanced_tab:
    st.header("Advanced Queries")
    q = st.selectbox(
        "Choose an Advanced Question",
        list(QUESTIONS["Advanced"].keys()),
        key="advanced_select"
    )
    run_predefined_query(QUESTIONS["Advanced"][q], "advanced")


st.divider()
st.header("✍️ Write Your Own SQL Query")
st.caption("Only SELECT and WITH queries are allowed.")

user_query = st.text_area(
    "Enter SQL Query",
    height=180,
    placeholder="SELECT *\nFROM matches\nLIMIT 10;"
)

if st.button("▶ Run Custom Query", type="primary"):
    query = user_query.strip()

    if not query:
        st.warning("Please enter an SQL query.")
    elif not query.lower().startswith(("select", "with")):
        st.error("Only SELECT or WITH queries are allowed.")
    else:
        conn = prepare_connection()
        try:
            df = pd.read_sql_query(query, conn)
            st.success("Custom query executed successfully!")
            st.markdown(f"### {len(df)} rows returned")

            if df.empty:
                st.info("No records returned.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Custom Result",
                    data=csv,
                    file_name="custom_sql_result.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"SQL Error: {e}")
        finally:
            conn.close()
