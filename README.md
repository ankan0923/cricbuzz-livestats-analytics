# 🏏 Cricbuzz LiveStats

### Real-Time Cricket Insights & SQL-Based Analytics

Cricbuzz LiveStats is an interactive cricket analytics application built using Python, Streamlit, SQLite, and the Cricbuzz API through RapidAPI. It combines live cricket information with a relational database to provide match insights, player statistics, SQL-based analysis, and CRUD operations through a user-friendly dashboard.

The project demonstrates an end-to-end workflow: API integration → data processing → SQL storage → analytics → interactive visualization.

## 🌐 Live Interactive Dashboard

Explore the complete Cricbuzz LiveStats application:

👉 [Open Live Streamlit Dashboard](https://homepy-i9qq8g4gqhaj7xutnmu64m.streamlit.app/)

The dashboard allows users to explore live and upcoming matches, view detailed scorecards, analyze player and team performance, execute SQL queries, and manage cricket records.

> **Note:** Live match information depends on the availability of the Cricbuzz API and the configured RapidAPI subscription.

## 🎯 Project Objectives

* Integrate a real-time cricket API using Python.
* Store structured cricket data in a relational SQL database.
* Build an interactive multi-page Streamlit application.
* Analyze player, team, match, and venue performance.
* Implement CRUD operations for managing cricket records.
* Practice beginner, intermediate, and advanced SQL analytics.
* Present meaningful cricket insights through KPIs and visualizations.

## 🛠️ Tech Stack

| Technology   | Purpose                               |
| ------------ | ------------------------------------- |
| Python       | Data processing and application logic |
| Streamlit    | Interactive web application           |
| SQLite       | Relational database                   |
| SQL          | Data retrieval and analytics          |
| Pandas       | Data manipulation and tabular results |
| Requests     | REST API integration                  |
| Cricbuzz API | Live cricket data                     |
| RapidAPI     | API access and authentication         |

## ✨ Application Features

### 🏠 Home Dashboard

The home page provides an overview of the cricket database and current match activity.

* Total players, teams, matches, and venues
* Total runs and wickets
* Highest individual score
* Live match count
* Featured top batter, bowler, and team
* Cricket overview visualizations

### 🔴 Live Matches

View currently available live cricket matches with match status, participating teams, scores, venue details, and other information returned by the API.

### 📅 Recent & Upcoming Matches

Explore recent and scheduled matches through interactive tables, date selection, refresh controls, and CSV downloads.

### 📋 Scorecard

Select a match to view detailed innings information, including batting statistics, bowling figures, extras, and fall of wickets when available from the API.

### 👥 Players

Explore team squads and player information such as player name, playing role, and team. The page also includes role summaries and downloadable data.

### 🗄️ CRUD Operations

Manage cricket records directly through the application using Create, Read, Update, and Delete operations.

Supported data areas include:

* Players
* Matches
* Batting and bowling statistics
* Teams, venues, and series
* Fielding statistics
* Partnerships

The forms use dropdowns, date inputs, and numeric controls to make data entry easier.

### 📊 SQL Analytics

The application includes 25 predefined SQL practice questions organized into three difficulty levels.

| Level        | Questions | Topics                                                                                                   |
| ------------ | --------- | -------------------------------------------------------------------------------------------------------- |
| Beginner     | Q1–Q8     | Players, recent matches, batting records, venues, team wins, and series                                  |
| Intermediate | Q9–Q16    | All-rounders, format comparisons, home/away performance, partnerships, and bowling analysis              |
| Advanced     | Q17–Q25   | Toss advantage, player rankings, consistency, head-to-head analysis, recent form, and time-series trends |

Users can also write and execute their own read-only SQL queries and download results as CSV files.

## 🧠 SQL Analytics Highlights

The project covers practical SQL concepts including:

* JOINs and multi-table relationships
* GROUP BY and HAVING
* Aggregate functions
* Common Table Expressions (CTEs)
* Window functions such as RANK, DENSE_RANK, and LAG
* Conditional aggregation
* Date-based analysis
* Player performance comparisons
* Head-to-head team analysis
* Quarterly performance trends

Some advanced questions require a larger historical dataset. During development, smaller thresholds may be used to demonstrate query logic, while the original project requirements are retained for the final analysis.

## 🗃️ Database Design

The SQLite database is organized into nine related tables:

| Table            | Description                               |
| ---------------- | ----------------------------------------- |
| `players`        | Player profiles and playing roles         |
| `teams`          | Team information                          |
| `matches`        | Match details, teams, venues, and results |
| `venues`         | Stadium and location information          |
| `series`         | Cricket series information                |
| `batting_stats`  | Player batting performances               |
| `bowling_stats`  | Player bowling performances               |
| `fielding_stats` | Catches, stumpings, and run-outs          |
| `partnerships`   | Batting partnership records               |

### Data Flow

```text
Cricbuzz API
     ↓
Python Requests
     ↓
JSON Parsing & Processing
     ↓
SQLite Database
     ↓
SQL Queries & CRUD
     ↓
Streamlit Dashboard
     ↓
Cricket Insights
```

## 📁 Project Structure

```text
Cricbuzz Live Stats API/
│
├── .streamlit/
│   └── secrets.toml
│
├── assets/
│   └── cricket_logo.png
│
├── Pages/
│   ├── CRUD_Operation.py
│   ├── Live_Matches.py
│   ├── Players.py
│   ├── Recent_Matches.py
│   ├── Scorecard.py
│   ├── SQL_Queries.py
│   ├── Upcoming_Matches.py
│   └── Visualizations.py
│
├── Home.py
├── api.py
├── database.py
├── cricket.db
├── requirements.txt
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Create a file named `.streamlit/secrets.toml`:

```toml
API_KEY = "YOUR_RAPIDAPI_KEY"
API_HOST = "cricbuzz-cricket.p.rapidapi.com"
```

Obtain your API key from RapidAPI and subscribe to the appropriate Cricbuzz API plan.

**Never commit your real API key or `secrets.toml` to GitHub.**

### 5. Run the application

```bash
streamlit run Home.py
```

The application will open in your browser at the local Streamlit address.

## 📦 Requirements

A typical `requirements.txt` for this project includes:

```text
streamlit
pandas
requests
plotly
```

SQLite is included with Python through the built-in `sqlite3` module. Add any additional libraries used by your visualization code to the requirements file.

## 📸 Dashboard Screenshots

Provided in Image File.

## 📈 Key Learnings

Through this project, I gained practical experience in integrating REST APIs, processing nested JSON data, designing relational databases, writing analytical SQL queries, implementing CRUD functionality, and developing a multi-page Streamlit application.

The project also strengthened my understanding of data availability, database relationships, query validation, and presenting analytical results through an interactive dashboard.

## ⚠️ Data Limitations

* Live and historical data availability depends on the API response and subscription.
* Some advanced SQL questions require more historical records than the current development database contains.
* Certain fields, such as venue capacity or complete career statistics, may require additional data sources.
* Manually entered sample records should be distinguished from verified API data when presenting analytical findings.

## 🚀 Future Improvements

* Automate historical match and player-statistics ingestion.
* Expand the database with more verified cricket records.
* Add richer player comparison and head-to-head visualizations.
* Improve data validation and database integrity.
* Deploy the application publicly with secure API credential management.

## 👨‍💻 Designed By

**Ankan**

Data Analytics | Python | SQL | Streamlit

---

⭐ If you find this project useful, consider starring the repository.
