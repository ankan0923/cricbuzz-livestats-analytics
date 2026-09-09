import streamlit as st
import pandas as pd
from datetime import date
from database import get_connection

st.title("🗄️ CRUD Operation")
st.caption("Manage the data required for the 25 SQL analytics questions.")

# -------------------- helpers --------------------
def read_sql(sql, params=None):
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params or {})
    finally:
        conn.close()


def run_sql(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or {})
        conn.commit()
        return cur.rowcount, cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def txt(v):
    return "" if pd.isna(v) else str(v)


def match_map():
    df = read_sql("SELECT match_id, team1_name, team2_name FROM matches ORDER BY match_id DESC")
    return {
        f"{txt(r['team1_name'])} vs {txt(r['team2_name'])} (ID: {r['match_id']})": int(r['match_id'])
        for _, r in df.iterrows()
    }


def player_map():
    df = read_sql("SELECT player_id, full_name FROM players ORDER BY full_name")
    return {f"{r['full_name']} (ID: {r['player_id']})": int(r['player_id']) for _, r in df.iterrows()}


def cricket_overs_decimal(value):
    s = f"{float(value):.1f}"
    whole, balls = s.split(".")
    whole, balls = int(whole), int(balls)
    if balls > 5:
        return None
    return whole + balls / 6


ROLES = ["Batsman", "WK-Batsman", "Bowler", "Batting Allrounder", "Bowling Allrounder"]
BATTING_STYLES = ["Right Handed Bat", "Left Handed Bat"]
BOWLING_STYLES = [
    "Does Not Bowl", "Right-arm Fast", "Right-arm Medium", "Left-arm Fast",
    "Left-arm Medium", "Right-arm Offbreak", "Right-arm Legbreak",
    "Left-arm Orthodox", "Left-arm Chinaman"
]
FORMATS = ["ODI", "T20", "T20I", "TEST", "International", "Domestic"]
STATUSES = ["Upcoming", "Live", "Completed", "Abandoned", "No Result"]
VICTORY_TYPES = ["Runs", "Wickets", "Tie", "No Result"]
TOSS_DECISIONS = ["Bat", "Bowl"]

section = st.selectbox(
    "Select Data Type",
    ["Players", "Matches", "Scores", "Fielding", "Partnerships", "Reference Data"]
)

# =========================================================
# PLAYERS
# =========================================================
if section == "Players":
    op = st.selectbox("Select Operation", ["View", "Add", "Update", "Delete"], key="p_op")

    if op == "View":
        df = read_sql("""
            SELECT player_id AS 'Player ID', full_name AS 'Full Name', country AS Country,
                   playing_role AS 'Playing Role', batting_style AS 'Batting Style',
                   bowling_style AS 'Bowling Style', team_name AS Team
            FROM players ORDER BY full_name
        """)
        if df.empty:
            st.info("No players available.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif op == "Add":
        with st.form("add_player"):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Full Name*")
                country = st.text_input("Country*")
                role = st.selectbox("Playing Role*", ROLES)
            with c2:
                batting_style = st.selectbox("Batting Style", BATTING_STYLES)
                bowling_style = st.selectbox("Bowling Style", BOWLING_STYLES)
                team_name = st.text_input("Team")
            submit = st.form_submit_button("Create Player", type="primary", use_container_width=True)

        if submit:
            if not full_name.strip() or not country.strip():
                st.warning("Full Name and Country are required.")
            else:
                try:
                    _, new_id = run_sql("""
                        INSERT INTO players(full_name,country,playing_role,batting_style,bowling_style,team_id,team_name)
                        VALUES(:full_name,:country,:role,:batting,:bowling,NULL,:team)
                    """, {
                        "full_name": full_name.strip(), "country": country.strip(), "role": role,
                        "batting": batting_style, "bowling": bowling_style, "team": team_name.strip() or None
                    })
                    st.success(f"Player created successfully! Player ID: {new_id}")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif op == "Update":
        pm = player_map()
        if not pm:
            st.info("No players available.")
        else:
            selected = st.selectbox("Select Player", list(pm))
            pid = pm[selected]
            r = read_sql("SELECT * FROM players WHERE player_id=:id", {"id": pid}).iloc[0]
            with st.form("update_player"):
                full_name = st.text_input("Full Name", value=txt(r["full_name"]))
                country = st.text_input("Country", value=txt(r["country"]))
                role_opts = ROLES + ([txt(r["playing_role"])] if txt(r["playing_role"]) not in ROLES else [])
                role = st.selectbox("Playing Role", role_opts, index=role_opts.index(txt(r["playing_role"]) or ROLES[0]))
                batting = st.selectbox("Batting Style", BATTING_STYLES, index=0 if txt(r["batting_style"]) not in BATTING_STYLES else BATTING_STYLES.index(txt(r["batting_style"])))
                bowling = st.selectbox("Bowling Style", BOWLING_STYLES, index=0 if txt(r["bowling_style"]) not in BOWLING_STYLES else BOWLING_STYLES.index(txt(r["bowling_style"])))
                team = st.text_input("Team", value=txt(r["team_name"]))
                submit = st.form_submit_button("Update Player", type="primary")
            if submit:
                try:
                    run_sql("""
                        UPDATE players SET full_name=:n,country=:c,playing_role=:r,batting_style=:b,
                        bowling_style=:bo,team_name=:t WHERE player_id=:id
                    """, {"n":full_name.strip(),"c":country.strip(),"r":role,"b":batting,"bo":bowling,"t":team.strip() or None,"id":pid})
                    st.success("Player updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    else:
        pm = player_map()
        if not pm:
            st.info("No players available.")
        else:
            selected = st.selectbox("Select Player", list(pm))
            pid = pm[selected]
            confirm = st.checkbox("Confirm deletion")
            if st.button("Delete Player", type="primary"):
                if not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    try:
                        run_sql("DELETE FROM players WHERE player_id=:id", {"id":pid})
                        st.success("Player deleted successfully!")
                    except Exception as e:
                        st.error(f"Delete failed. Existing stats may reference this player. Error: {e}")

# =========================================================
# MATCHES
# =========================================================
elif section == "Matches":
    op = st.selectbox("Select Operation", ["View", "Add", "Update", "Delete"], key="m_op")

    if op == "View":
        df = read_sql("""
            SELECT match_id AS 'Match ID', series_name AS Series, match_format AS Format,
                   team1_name AS 'Team 1', team2_name AS 'Team 2', venue_name AS Venue,
                   venue_country AS 'Venue Country', match_date AS Date, status AS Status,
                   winner_name AS Winner, victory_margin AS Margin, victory_type AS 'Victory Type',
                   toss_winner_name AS 'Toss Winner', toss_decision AS 'Toss Decision'
            FROM matches ORDER BY match_date DESC, match_id DESC
        """)
        if df.empty:
            st.info("No matches available.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    elif op == "Add":
        with st.form("add_match"):
            match_id = st.number_input("Match ID", min_value=1, step=1)
            series = st.text_input("Series")
            fmt = st.selectbox("Format", FORMATS)
            c1, c2 = st.columns(2)
            with c1: team1 = st.text_input("Team 1")
            with c2: team2 = st.text_input("Team 2")
            venue = st.text_input("Venue")
            venue_country = st.text_input("Venue Country")
            mdate = st.date_input("Date", value=date.today())
            status = st.selectbox("Status", STATUSES)
            st.markdown("#### Result & Toss")
            c3, c4 = st.columns(2)
            with c3:
                winner = st.text_input("Winner")
                margin = st.number_input("Victory Margin", min_value=0, value=0, step=1)
                victory_type = st.selectbox("Victory Type", VICTORY_TYPES)
            with c4:
                toss_winner = st.text_input("Toss Winner")
                toss_decision = st.selectbox("Toss Decision", TOSS_DECISIONS)
            submit = st.form_submit_button("Add Match", type="primary", use_container_width=True)

        if submit:
            if not series.strip() or not team1.strip() or not team2.strip() or not venue.strip():
                st.warning("Series, Team 1, Team 2 and Venue are required.")
            elif team1.strip().lower() == team2.strip().lower():
                st.warning("Team 1 and Team 2 cannot be the same.")
            else:
                try:
                    run_sql("""
                        INSERT INTO matches(
                            match_id,series_id,series_name,match_description,match_format,
                            team1_id,team1_name,team2_id,team2_name,match_date,status,
                            venue_id,venue_name,venue_city,venue_country,
                            winner_id,winner_name,victory_margin,victory_type,
                            toss_winner_id,toss_winner_name,toss_decision
                        ) VALUES(
                            :id,NULL,:series,:desc,:fmt,NULL,:t1,NULL,:t2,:dt,:status,
                            NULL,:venue,NULL,:vcountry,NULL,:winner,:margin,:vtype,
                            NULL,:tosswinner,:tossdecision
                        )
                    """, {
                        "id":int(match_id),"series":series.strip(),"desc":f"{team1.strip()} vs {team2.strip()}",
                        "fmt":fmt,"t1":team1.strip(),"t2":team2.strip(),"dt":mdate.isoformat(),"status":status,
                        "venue":venue.strip(),"vcountry":venue_country.strip() or None,
                        "winner":winner.strip() or None,"margin":int(margin) if winner.strip() else None,
                        "vtype":victory_type if winner.strip() else None,
                        "tosswinner":toss_winner.strip() or None,
                        "tossdecision":toss_decision if toss_winner.strip() else None
                    })
                    st.success("Match added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif op == "Update":
        mm = match_map()
        if not mm:
            st.info("No matches available.")
        else:
            selected = st.selectbox("Select Match", list(mm))
            mid = mm[selected]
            r = read_sql("SELECT * FROM matches WHERE match_id=:id", {"id":mid}).iloc[0]
            with st.form("update_match"):
                series = st.text_input("Series", value=txt(r["series_name"]))
                fmt_opts = FORMATS + ([txt(r["match_format"])] if txt(r["match_format"]) not in FORMATS else [])
                fmt = st.selectbox("Format", fmt_opts, index=fmt_opts.index(txt(r["match_format"]) or FORMATS[0]))
                c1, c2 = st.columns(2)
                with c1: team1 = st.text_input("Team 1", value=txt(r["team1_name"]))
                with c2: team2 = st.text_input("Team 2", value=txt(r["team2_name"]))
                venue = st.text_input("Venue", value=txt(r["venue_name"]))
                venue_country = st.text_input("Venue Country", value=txt(r["venue_country"]))
                mdate = st.text_input("Date (YYYY-MM-DD)", value=txt(r["match_date"])[:10])
                status_opts = STATUSES + ([txt(r["status"])] if txt(r["status"]) not in STATUSES else [])
                status = st.selectbox("Status", status_opts, index=status_opts.index(txt(r["status"]) or STATUSES[0]))
                st.markdown("#### Result & Toss")
                c3, c4 = st.columns(2)
                with c3:
                    winner = st.text_input("Winner", value=txt(r["winner_name"]))
                    margin = st.number_input("Victory Margin", min_value=0, value=int(r["victory_margin"]) if pd.notna(r["victory_margin"]) else 0, step=1)
                    victory_type = st.selectbox("Victory Type", VICTORY_TYPES)
                with c4:
                    toss_winner = st.text_input("Toss Winner", value=txt(r["toss_winner_name"]))
                    toss_decision = st.selectbox("Toss Decision", TOSS_DECISIONS)
                submit = st.form_submit_button("Update Match", type="primary")
            if submit:
                try:
                    run_sql("""
                        UPDATE matches SET series_name=:series,match_description=:desc,match_format=:fmt,
                            team1_name=:t1,team2_name=:t2,match_date=:dt,status=:status,
                            venue_name=:venue,venue_country=:vcountry,winner_name=:winner,
                            victory_margin=:margin,victory_type=:vtype,toss_winner_name=:tosswinner,
                            toss_decision=:tossdecision WHERE match_id=:id
                    """, {
                        "series":series.strip(),"desc":f"{team1.strip()} vs {team2.strip()}","fmt":fmt,
                        "t1":team1.strip(),"t2":team2.strip(),"dt":mdate.strip(),"status":status,
                        "venue":venue.strip(),"vcountry":venue_country.strip() or None,
                        "winner":winner.strip() or None,"margin":int(margin) if winner.strip() else None,
                        "vtype":victory_type if winner.strip() else None,"tosswinner":toss_winner.strip() or None,
                        "tossdecision":toss_decision if toss_winner.strip() else None,"id":mid
                    })
                    st.success("Match updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

    else:
        mm = match_map()
        if not mm:
            st.info("No matches available.")
        else:
            selected = st.selectbox("Select Match", list(mm))
            mid = mm[selected]
            confirm = st.checkbox("Confirm deletion")
            if st.button("Delete Match", type="primary"):
                if not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    try:
                        run_sql("DELETE FROM matches WHERE match_id=:id", {"id":mid})
                        st.success("Match deleted successfully!")
                    except Exception as e:
                        st.error(f"Delete failed. Existing stats may reference this match. Error: {e}")

# =========================================================
# SCORES
# =========================================================
elif section == "Scores":
    score_type = st.selectbox("Score Type", ["Batting", "Bowling"])
    op = st.selectbox("Select Operation", ["View", "Add", "Update", "Delete"], key="s_op")
    mm, pm = match_map(), player_map()

    if score_type == "Batting":
        if op == "View":
            df = read_sql("""
                SELECT b.batting_id AS 'Batting ID', b.match_id AS 'Match ID', p.full_name AS Player,
                       b.innings_number AS Innings, b.batting_position AS Position, b.runs AS Runs,
                       b.balls_faced AS Balls, b.fours AS '4s', b.sixes AS '6s',
                       b.strike_rate AS 'Strike Rate', b.dismissal AS Dismissal
                FROM batting_stats b LEFT JOIN players p ON p.player_id=b.player_id
                ORDER BY b.batting_id DESC
            """)
            if df.empty:
                st.info("No batting scores available.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

        elif op == "Add":
            if not mm: st.warning("Add a match first.")
            elif not pm: st.warning("Add a player first.")
            else:
                with st.form("add_bat"):
                    mlabel = st.selectbox("Match", list(mm))
                    plabel = st.selectbox("Player", list(pm))
                    c1, c2 = st.columns(2)
                    with c1:
                        innings = st.number_input("Innings", 1, 4, 1, 1)
                        position = st.number_input("Batting Position", 1, 11, 1, 1)
                        runs = st.number_input("Runs", min_value=0, value=0, step=1)
                        balls = st.number_input("Balls Faced", min_value=0, value=0, step=1)
                    with c2:
                        fours = st.number_input("Fours", min_value=0, value=0, step=1)
                        sixes = st.number_input("Sixes", min_value=0, value=0, step=1)
                        dismissal = st.text_input("Dismissal")
                    submit = st.form_submit_button("Add Batting Score", type="primary")
                if submit:
                    sr = round(runs*100/balls,2) if balls else 0
                    try:
                        run_sql("""
                            INSERT INTO batting_stats(match_id,player_id,innings_number,batting_position,runs,balls_faced,fours,sixes,strike_rate,dismissal)
                            VALUES(:m,:p,:i,:pos,:r,:b,:f,:s,:sr,:d)
                        """, {"m":mm[mlabel],"p":pm[plabel],"i":int(innings),"pos":int(position),"r":int(runs),"b":int(balls),"f":int(fours),"s":int(sixes),"sr":sr,"d":dismissal.strip() or None})
                        st.success(f"Batting score added! Strike Rate: {sr}")
                    except Exception as e: st.error(f"Error: {e}")

        elif op == "Update":
            df = read_sql("SELECT * FROM batting_stats ORDER BY batting_id DESC")
            if df.empty: st.info("No batting scores available.")
            else:
                opts = {f"Batting ID {r['batting_id']} | Player {r['player_id']} | Match {r['match_id']}": int(r['batting_id']) for _,r in df.iterrows()}
                selected = st.selectbox("Select Batting Record", list(opts))
                bid = opts[selected]; r = df[df["batting_id"]==bid].iloc[0]
                with st.form("upd_bat"):
                    runs = st.number_input("Runs", min_value=0, value=int(r["runs"]), step=1)
                    balls = st.number_input("Balls Faced", min_value=0, value=int(r["balls_faced"]), step=1)
                    fours = st.number_input("Fours", min_value=0, value=int(r["fours"]), step=1)
                    sixes = st.number_input("Sixes", min_value=0, value=int(r["sixes"]), step=1)
                    dismissal = st.text_input("Dismissal", value=txt(r["dismissal"]))
                    submit = st.form_submit_button("Update Batting Score", type="primary")
                if submit:
                    sr = round(runs*100/balls,2) if balls else 0
                    try:
                        run_sql("UPDATE batting_stats SET runs=:r,balls_faced=:b,fours=:f,sixes=:s,strike_rate=:sr,dismissal=:d WHERE batting_id=:id",
                                {"r":int(runs),"b":int(balls),"f":int(fours),"s":int(sixes),"sr":sr,"d":dismissal.strip() or None,"id":bid})
                        st.success("Batting score updated!")
                    except Exception as e: st.error(f"Error: {e}")

        else:
            df = read_sql("SELECT batting_id,match_id,player_id FROM batting_stats ORDER BY batting_id DESC")
            if df.empty: st.info("No batting scores available.")
            else:
                opts = {f"Batting ID {r['batting_id']} | Player {r['player_id']} | Match {r['match_id']}": int(r['batting_id']) for _,r in df.iterrows()}
                selected = st.selectbox("Select Batting Record", list(opts)); bid = opts[selected]
                confirm = st.checkbox("Confirm deletion")
                if st.button("Delete Batting Score", type="primary"):
                    if not confirm: st.warning("Please confirm deletion.")
                    else:
                        try:
                            run_sql("DELETE FROM batting_stats WHERE batting_id=:id", {"id":bid}); st.success("Batting score deleted!")
                        except Exception as e: st.error(f"Error: {e}")

    else:  # Bowling
        if op == "View":
            df = read_sql("""
                SELECT b.bowling_id AS 'Bowling ID', b.match_id AS 'Match ID', p.full_name AS Player,
                       b.innings_number AS Innings, b.overs AS Overs, b.maidens AS Maidens,
                       b.runs_conceded AS 'Runs Conceded', b.wickets AS Wickets,
                       b.economy_rate AS Economy, b.wides AS Wides, b.no_balls AS 'No Balls'
                FROM bowling_stats b LEFT JOIN players p ON p.player_id=b.player_id
                ORDER BY b.bowling_id DESC
            """)
            if df.empty:
                st.info("No bowling scores available.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

        elif op == "Add":
            if not mm: st.warning("Add a match first.")
            elif not pm: st.warning("Add a player first.")
            else:
                with st.form("add_bowl"):
                    mlabel = st.selectbox("Match", list(mm)); plabel = st.selectbox("Player", list(pm))
                    c1,c2 = st.columns(2)
                    with c1:
                        innings = st.number_input("Innings",1,4,1,1)
                        overs = st.number_input("Overs", min_value=0.0, value=0.0, step=0.1, format="%.1f")
                        maidens = st.number_input("Maidens", min_value=0, value=0, step=1)
                        conceded = st.number_input("Runs Conceded", min_value=0, value=0, step=1)
                    with c2:
                        wickets = st.number_input("Wickets",0,10,0,1)
                        wides = st.number_input("Wides", min_value=0, value=0, step=1)
                        no_balls = st.number_input("No Balls", min_value=0, value=0, step=1)
                    submit = st.form_submit_button("Add Bowling Score", type="primary")
                if submit:
                    dec = cricket_overs_decimal(overs)
                    if dec is None: st.warning("Invalid overs. Decimal digit must be 0-5.")
                    else:
                        eco = round(conceded/dec,2) if dec else 0
                        try:
                            run_sql("""
                                INSERT INTO bowling_stats(match_id,player_id,innings_number,overs,maidens,runs_conceded,wickets,economy_rate,wides,no_balls)
                                VALUES(:m,:p,:i,:o,:ma,:r,:w,:e,:wi,:nb)
                            """, {"m":mm[mlabel],"p":pm[plabel],"i":int(innings),"o":float(overs),"ma":int(maidens),"r":int(conceded),"w":int(wickets),"e":eco,"wi":int(wides),"nb":int(no_balls)})
                            st.success(f"Bowling score added! Economy: {eco}")
                        except Exception as e: st.error(f"Error: {e}")

        elif op == "Update":
            df = read_sql("SELECT * FROM bowling_stats ORDER BY bowling_id DESC")
            if df.empty: st.info("No bowling scores available.")
            else:
                opts = {f"Bowling ID {r['bowling_id']} | Player {r['player_id']} | Match {r['match_id']}": int(r['bowling_id']) for _,r in df.iterrows()}
                selected = st.selectbox("Select Bowling Record", list(opts)); bid=opts[selected]; r=df[df["bowling_id"]==bid].iloc[0]
                with st.form("upd_bowl"):
                    overs = st.number_input("Overs", min_value=0.0, value=float(r["overs"]), step=0.1, format="%.1f")
                    maidens = st.number_input("Maidens", min_value=0, value=int(r["maidens"]), step=1)
                    conceded = st.number_input("Runs Conceded", min_value=0, value=int(r["runs_conceded"]), step=1)
                    wickets = st.number_input("Wickets",0,10,int(r["wickets"]),1)
                    wides = st.number_input("Wides", min_value=0, value=int(r["wides"]), step=1)
                    no_balls = st.number_input("No Balls", min_value=0, value=int(r["no_balls"]), step=1)
                    submit = st.form_submit_button("Update Bowling Score", type="primary")
                if submit:
                    dec=cricket_overs_decimal(overs)
                    if dec is None: st.warning("Invalid overs.")
                    else:
                        eco=round(conceded/dec,2) if dec else 0
                        try:
                            run_sql("UPDATE bowling_stats SET overs=:o,maidens=:ma,runs_conceded=:r,wickets=:w,economy_rate=:e,wides=:wi,no_balls=:nb WHERE bowling_id=:id",
                                    {"o":float(overs),"ma":int(maidens),"r":int(conceded),"w":int(wickets),"e":eco,"wi":int(wides),"nb":int(no_balls),"id":bid})
                            st.success("Bowling score updated!")
                        except Exception as e: st.error(f"Error: {e}")

        else:
            df = read_sql("SELECT bowling_id,match_id,player_id FROM bowling_stats ORDER BY bowling_id DESC")
            if df.empty: st.info("No bowling scores available.")
            else:
                opts={f"Bowling ID {r['bowling_id']} | Player {r['player_id']} | Match {r['match_id']}":int(r['bowling_id']) for _,r in df.iterrows()}
                selected=st.selectbox("Select Bowling Record",list(opts)); bid=opts[selected]; confirm=st.checkbox("Confirm deletion")
                if st.button("Delete Bowling Score",type="primary"):
                    if not confirm: st.warning("Please confirm deletion.")
                    else:
                        try: run_sql("DELETE FROM bowling_stats WHERE bowling_id=:id",{"id":bid}); st.success("Bowling score deleted!")
                        except Exception as e: st.error(f"Error: {e}")

# =========================================================
# FIELDING
# =========================================================
elif section == "Fielding":
    op=st.selectbox("Select Operation",["View","Add","Update","Delete"],key="f_op")
    mm,pm=match_map(),player_map()
    if op=="View":
        df=read_sql("""
            SELECT f.fielding_id AS 'Fielding ID',f.match_id AS 'Match ID',p.full_name AS Player,
                   f.innings_number AS Innings,f.catches AS Catches,f.stumpings AS Stumpings,f.run_outs AS 'Run Outs'
            FROM fielding_stats f LEFT JOIN players p ON p.player_id=f.player_id ORDER BY f.fielding_id DESC
        """)
        if df.empty:
            st.info("No fielding data available.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    elif op=="Add":
        if not mm: st.warning("Add a match first.")
        elif not pm: st.warning("Add a player first.")
        else:
            with st.form("add_field"):
                mlabel=st.selectbox("Match",list(mm)); plabel=st.selectbox("Player",list(pm))
                innings=st.number_input("Innings",1,4,1,1)
                catches=st.number_input("Catches",min_value=0,value=0,step=1)
                stumpings=st.number_input("Stumpings",min_value=0,value=0,step=1)
                runouts=st.number_input("Run Outs",min_value=0,value=0,step=1)
                submit=st.form_submit_button("Add Fielding Record",type="primary")
            if submit:
                try:
                    run_sql("INSERT INTO fielding_stats(match_id,player_id,innings_number,catches,stumpings,run_outs) VALUES(:m,:p,:i,:c,:s,:r)",
                            {"m":mm[mlabel],"p":pm[plabel],"i":int(innings),"c":int(catches),"s":int(stumpings),"r":int(runouts)})
                    st.success("Fielding record added!")
                except Exception as e: st.error(f"Error: {e}")
    elif op=="Update":
        df=read_sql("SELECT * FROM fielding_stats ORDER BY fielding_id DESC")
        if df.empty: st.info("No fielding data available.")
        else:
            opts={f"Fielding ID {r['fielding_id']} | Player {r['player_id']} | Match {r['match_id']}":int(r['fielding_id']) for _,r in df.iterrows()}
            selected=st.selectbox("Select Fielding Record",list(opts)); fid=opts[selected]; r=df[df["fielding_id"]==fid].iloc[0]
            with st.form("upd_field"):
                catches=st.number_input("Catches",min_value=0,value=int(r["catches"]),step=1)
                stumpings=st.number_input("Stumpings",min_value=0,value=int(r["stumpings"]),step=1)
                runouts=st.number_input("Run Outs",min_value=0,value=int(r["run_outs"]),step=1)
                submit=st.form_submit_button("Update Fielding Record",type="primary")
            if submit:
                try: run_sql("UPDATE fielding_stats SET catches=:c,stumpings=:s,run_outs=:r WHERE fielding_id=:id",{"c":int(catches),"s":int(stumpings),"r":int(runouts),"id":fid}); st.success("Fielding record updated!")
                except Exception as e: st.error(f"Error: {e}")
    else:
        df=read_sql("SELECT fielding_id,match_id,player_id FROM fielding_stats ORDER BY fielding_id DESC")
        if df.empty: st.info("No fielding data available.")
        else:
            opts={f"Fielding ID {r['fielding_id']} | Player {r['player_id']} | Match {r['match_id']}":int(r['fielding_id']) for _,r in df.iterrows()}
            selected=st.selectbox("Select Fielding Record",list(opts)); fid=opts[selected]; confirm=st.checkbox("Confirm deletion")
            if st.button("Delete Fielding Record",type="primary"):
                if not confirm: st.warning("Please confirm deletion.")
                else:
                    try: run_sql("DELETE FROM fielding_stats WHERE fielding_id=:id",{"id":fid}); st.success("Fielding record deleted!")
                    except Exception as e: st.error(f"Error: {e}")

# =========================================================
# PARTNERSHIPS
# =========================================================
elif section == "Partnerships":
    op=st.selectbox("Select Operation",["View","Add","Update","Delete"],key="pt_op")
    mm,pm=match_map(),player_map()
    if op=="View":
        df=read_sql("SELECT * FROM partnerships ORDER BY partnership_id DESC")
        if df.empty:
            st.info("No partnerships available.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    elif op=="Add":
        if not mm: st.warning("Add a match first.")
        elif len(pm)<2: st.warning("Add at least two players first.")
        else:
            with st.form("add_partnership"):
                mlabel=st.selectbox("Match",list(mm)); innings=st.number_input("Innings",1,4,1,1)
                c1,c2=st.columns(2)
                with c1:
                    p1label=st.selectbox("Player 1",list(pm),key="p1"); p1pos=st.number_input("Player 1 Position",1,11,1,1)
                with c2:
                    p2label=st.selectbox("Player 2",list(pm),key="p2"); p2pos=st.number_input("Player 2 Position",1,11,2,1)
                runs=st.number_input("Partnership Runs",min_value=0,value=0,step=1)
                balls=st.number_input("Partnership Balls",min_value=0,value=0,step=1)
                submit=st.form_submit_button("Add Partnership",type="primary")
            if submit:
                p1,p2=pm[p1label],pm[p2label]
                if p1==p2: st.warning("Player 1 and Player 2 cannot be the same.")
                else:
                    try:
                        run_sql("""
                            INSERT INTO partnerships(match_id,innings_number,player1_id,player2_id,player1_position,player2_position,partnership_runs,partnership_balls)
                            VALUES(:m,:i,:p1,:p2,:p1pos,:p2pos,:r,:b)
                        """,{"m":mm[mlabel],"i":int(innings),"p1":p1,"p2":p2,"p1pos":int(p1pos),"p2pos":int(p2pos),"r":int(runs),"b":int(balls)})
                        st.success("Partnership added!")
                    except Exception as e: st.error(f"Error: {e}")
    elif op=="Update":
        df=read_sql("SELECT * FROM partnerships ORDER BY partnership_id DESC")
        if df.empty: st.info("No partnerships available.")
        else:
            opts={f"Partnership ID {r['partnership_id']} | Match {r['match_id']} | {r['player1_id']} + {r['player2_id']}":int(r['partnership_id']) for _,r in df.iterrows()}
            selected=st.selectbox("Select Partnership",list(opts)); pid=opts[selected]; r=df[df["partnership_id"]==pid].iloc[0]
            with st.form("upd_partner"):
                runs=st.number_input("Partnership Runs",min_value=0,value=int(r["partnership_runs"]),step=1)
                balls=st.number_input("Partnership Balls",min_value=0,value=int(r["partnership_balls"]),step=1)
                submit=st.form_submit_button("Update Partnership",type="primary")
            if submit:
                try: run_sql("UPDATE partnerships SET partnership_runs=:r,partnership_balls=:b WHERE partnership_id=:id",{"r":int(runs),"b":int(balls),"id":pid}); st.success("Partnership updated!")
                except Exception as e: st.error(f"Error: {e}")
    else:
        df=read_sql("SELECT partnership_id,match_id,player1_id,player2_id FROM partnerships ORDER BY partnership_id DESC")
        if df.empty: st.info("No partnerships available.")
        else:
            opts={f"Partnership ID {r['partnership_id']} | Match {r['match_id']} | {r['player1_id']} + {r['player2_id']}":int(r['partnership_id']) for _,r in df.iterrows()}
            selected=st.selectbox("Select Partnership",list(opts)); pid=opts[selected]; confirm=st.checkbox("Confirm deletion")
            if st.button("Delete Partnership",type="primary"):
                if not confirm: st.warning("Please confirm deletion.")
                else:
                    try: run_sql("DELETE FROM partnerships WHERE partnership_id=:id",{"id":pid}); st.success("Partnership deleted!")
                    except Exception as e: st.error(f"Error: {e}")

# =========================================================
# REFERENCE DATA: TEAMS / VENUES / SERIES
# =========================================================
elif section == "Reference Data":
    ref=st.selectbox("Reference Type",["Teams","Venues","Series"])
    op=st.selectbox("Select Operation",["View","Add","Update","Delete"],key="ref_op")

    if ref=="Teams":
        if op=="View":
            df=read_sql("SELECT team_id AS 'Team ID',team_name AS 'Team Name',short_name AS 'Short Name',country AS Country FROM teams ORDER BY team_name")
            if df.empty:
                st.info("No teams available.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        elif op=="Add":
            with st.form("add_team"):
                name=st.text_input("Team Name*"); short=st.text_input("Short Name"); country=st.text_input("Country*")
                submit=st.form_submit_button("Add Team",type="primary")
            if submit:
                if not name.strip() or not country.strip(): st.warning("Team Name and Country are required.")
                else:
                    try:
                        _,nid=run_sql("INSERT INTO teams(team_name,short_name,country) VALUES(:n,:s,:c)",{"n":name.strip(),"s":short.strip() or None,"c":country.strip()}); st.success(f"Team added! Team ID: {nid}")
                    except Exception as e: st.error(f"Error: {e}")
        elif op=="Update":
            df=read_sql("SELECT * FROM teams ORDER BY team_name")
            if df.empty: st.info("No teams available.")
            else:
                opts={f"{r['team_name']} (ID: {r['team_id']})":int(r['team_id']) for _,r in df.iterrows()}; selected=st.selectbox("Select Team",list(opts)); tid=opts[selected]; r=df[df["team_id"]==tid].iloc[0]
                with st.form("upd_team"):
                    name=st.text_input("Team Name",value=txt(r["team_name"])); short=st.text_input("Short Name",value=txt(r["short_name"])); country=st.text_input("Country",value=txt(r["country"])); submit=st.form_submit_button("Update Team",type="primary")
                if submit:
                    try: run_sql("UPDATE teams SET team_name=:n,short_name=:s,country=:c WHERE team_id=:id",{"n":name.strip(),"s":short.strip() or None,"c":country.strip(),"id":tid}); st.success("Team updated!")
                    except Exception as e: st.error(f"Error: {e}")
        else:
            df=read_sql("SELECT team_id,team_name FROM teams ORDER BY team_name")
            if df.empty: st.info("No teams available.")
            else:
                opts={f"{r['team_name']} (ID: {r['team_id']})":int(r['team_id']) for _,r in df.iterrows()}; selected=st.selectbox("Select Team",list(opts)); tid=opts[selected]; confirm=st.checkbox("Confirm deletion")
                if st.button("Delete Team",type="primary"):
                    if not confirm: st.warning("Please confirm deletion.")
                    else:
                        try: run_sql("DELETE FROM teams WHERE team_id=:id",{"id":tid}); st.success("Team deleted!")
                        except Exception as e: st.error(f"Error: {e}")

    elif ref=="Venues":
        if op=="View":
            df=read_sql("SELECT venue_id AS 'Venue ID',venue_name AS 'Venue Name',city AS City,country AS Country,capacity AS Capacity FROM venues ORDER BY venue_name")
            if df.empty:
                st.info("No venues available.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        elif op=="Add":
            with st.form("add_venue"):
                name=st.text_input("Venue Name*"); city=st.text_input("City"); country=st.text_input("Country*"); capacity=st.number_input("Capacity",min_value=0,value=0,step=1000); submit=st.form_submit_button("Add Venue",type="primary")
            if submit:
                if not name.strip() or not country.strip(): st.warning("Venue Name and Country are required.")
                else:
                    try:
                        _,nid=run_sql("INSERT INTO venues(venue_name,city,country,capacity) VALUES(:n,:city,:c,:cap)",{"n":name.strip(),"city":city.strip() or None,"c":country.strip(),"cap":int(capacity)}); st.success(f"Venue added! Venue ID: {nid}")
                    except Exception as e: st.error(f"Error: {e}")
        elif op=="Update":
            df=read_sql("SELECT * FROM venues ORDER BY venue_name")
            if df.empty: st.info("No venues available.")
            else:
                opts={f"{r['venue_name']} (ID: {r['venue_id']})":int(r['venue_id']) for _,r in df.iterrows()}; selected=st.selectbox("Select Venue",list(opts)); vid=opts[selected]; r=df[df["venue_id"]==vid].iloc[0]
                with st.form("upd_venue"):
                    name=st.text_input("Venue Name",value=txt(r["venue_name"])); city=st.text_input("City",value=txt(r["city"])); country=st.text_input("Country",value=txt(r["country"])); capacity=st.number_input("Capacity",min_value=0,value=int(r["capacity"]) if pd.notna(r["capacity"]) else 0,step=1000); submit=st.form_submit_button("Update Venue",type="primary")
                if submit:
                    try: run_sql("UPDATE venues SET venue_name=:n,city=:city,country=:c,capacity=:cap WHERE venue_id=:id",{"n":name.strip(),"city":city.strip() or None,"c":country.strip(),"cap":int(capacity),"id":vid}); st.success("Venue updated!")
                    except Exception as e: st.error(f"Error: {e}")
        else:
            df=read_sql("SELECT venue_id,venue_name FROM venues ORDER BY venue_name")
            if df.empty: st.info("No venues available.")
            else:
                opts={f"{r['venue_name']} (ID: {r['venue_id']})":int(r['venue_id']) for _,r in df.iterrows()}; selected=st.selectbox("Select Venue",list(opts)); vid=opts[selected]; confirm=st.checkbox("Confirm deletion")
                if st.button("Delete Venue",type="primary"):
                    if not confirm: st.warning("Please confirm deletion.")
                    else:
                        try: run_sql("DELETE FROM venues WHERE venue_id=:id",{"id":vid}); st.success("Venue deleted!")
                        except Exception as e: st.error(f"Error: {e}")

    else:  # Series
        if op=="View":
            df=read_sql("SELECT series_id AS 'Series ID',series_name AS 'Series Name',host_country AS 'Host Country',match_type AS 'Match Type',start_date AS 'Start Date',end_date AS 'End Date',total_matches AS 'Total Matches' FROM series ORDER BY start_date DESC")
            if df.empty:
                st.info("No series available.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        elif op=="Add":
            with st.form("add_series"):
                name=st.text_input("Series Name*"); host=st.text_input("Host Country"); mtype=st.selectbox("Match Type",FORMATS); sdate=st.date_input("Start Date",value=date.today()); edate=st.date_input("End Date",value=date.today()); total=st.number_input("Total Matches",min_value=0,value=0,step=1); submit=st.form_submit_button("Add Series",type="primary")
            if submit:
                if not name.strip(): st.warning("Series Name is required.")
                else:
                    try:
                        _,nid=run_sql("INSERT INTO series(series_name,host_country,match_type,start_date,end_date,total_matches) VALUES(:n,:h,:t,:s,:e,:m)",{"n":name.strip(),"h":host.strip() or None,"t":mtype,"s":sdate.isoformat(),"e":edate.isoformat(),"m":int(total)}); st.success(f"Series added! Series ID: {nid}")
                    except Exception as e: st.error(f"Error: {e}")
        elif op=="Update":
            df=read_sql("SELECT * FROM series ORDER BY series_name")
            if df.empty: st.info("No series available.")
            else:
                opts={f"{r['series_name']} (ID: {r['series_id']})":int(r['series_id']) for _,r in df.iterrows()}; selected=st.selectbox("Select Series",list(opts)); sid=opts[selected]; r=df[df["series_id"]==sid].iloc[0]
                with st.form("upd_series"):
                    name=st.text_input("Series Name",value=txt(r["series_name"])); host=st.text_input("Host Country",value=txt(r["host_country"])); mtype=st.selectbox("Match Type",FORMATS); sdate=st.text_input("Start Date (YYYY-MM-DD)",value=txt(r["start_date"])[:10]); edate=st.text_input("End Date (YYYY-MM-DD)",value=txt(r["end_date"])[:10]); total=st.number_input("Total Matches",min_value=0,value=int(r["total_matches"]) if pd.notna(r["total_matches"]) else 0,step=1); submit=st.form_submit_button("Update Series",type="primary")
                if submit:
                    try: run_sql("UPDATE series SET series_name=:n,host_country=:h,match_type=:t,start_date=:s,end_date=:e,total_matches=:m WHERE series_id=:id",{"n":name.strip(),"h":host.strip() or None,"t":mtype,"s":sdate.strip(),"e":edate.strip(),"m":int(total),"id":sid}); st.success("Series updated!")
                    except Exception as e: st.error(f"Error: {e}")
        else:
            df=read_sql("SELECT series_id,series_name FROM series ORDER BY series_name")
            if df.empty: st.info("No series available.")
            else:
                opts={f"{r['series_name']} (ID: {r['series_id']})":int(r['series_id']) for _,r in df.iterrows()}; selected=st.selectbox("Select Series",list(opts)); sid=opts[selected]; confirm=st.checkbox("Confirm deletion")
                if st.button("Delete Series",type="primary"):
                    if not confirm: st.warning("Please confirm deletion.")
                    else:
                        try: run_sql("DELETE FROM series WHERE series_id=:id",{"id":sid}); st.success("Series deleted!")
                        except Exception as e: st.error(f"Error: {e}")
