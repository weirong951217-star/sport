# ============================================================
# ⚽🏀 體育版終極融合系統 (補回爬蟲引擎 + 大滿貫全功能絕對完整版)
# ============================================================
import os
import threading
import time
import json
import urllib.parse
import re
import hashlib
import subprocess
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import requests
from scipy.stats import poisson
from flask import Flask, request, jsonify, render_template_string
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from werkzeug.serving import make_server
import warnings
warnings.filterwarnings('ignore')

# 🌟 終極清理指令：強制殺除所有卡住的程序與舊暫存
os.system("fuser -k 5000/tcp >/dev/null 2>&1")
os.system("killall -9 cloudflared-linux-amd64 >/dev/null 2>&1")
os.system("rm -rf /tmp/sports_cf")
time.sleep(2)

# ─────────────────────────────────────────
# 1. 系統常數、字典與【當家球星名單】
# ─────────────────────────────────────────
TEAM_NAME_MAP = {
    "Atlanta Hawks": "亞特蘭大老鷹 (Atlanta Hawks)", "Boston Celtics": "波士頓塞爾蒂克 (Boston Celtics)", "Brooklyn Nets": "布魯克林籃網 (Brooklyn Nets)",
    "Charlotte Hornets": "夏洛特黃蜂 (Charlotte Hornets)", "Chicago Bulls": "芝加哥公牛 (Chicago Bulls)", "Cleveland Cavaliers": "克里夫蘭騎士 (Cleveland Cavaliers)",
    "Dallas Mavericks": "達拉斯獨行俠 (Dallas Mavericks)", "Denver Nuggets": "丹佛金塊 (Denver Nuggets)", "Detroit Pistons": "底特律活塞 (Detroit Pistons)",
    "Golden State Warriors": "金州勇士 (Golden State Warriors)", "Houston Rockets": "休士頓火箭 (Houston Rockets)", "Indiana Pacers": "印第安那溜馬 (Indiana Pacers)",
    "LA Clippers": "洛杉磯快艇 (Los Angeles Clippers)", "Los Angeles Clippers": "洛杉磯快艇 (Los Angeles Clippers)",
    "Los Angeles Lakers": "洛杉磯湖人 (Los Angeles Lakers)", "Memphis Grizzlies": "曼斐斯灰熊 (Memphis Grizzlies)",
    "Miami Heat": "邁阿密熱火 (Miami Heat)", "Milwaukee Bucks": "密爾瓦基公鹿 (Milwaukee Bucks)", "Minnesota Timberwolves": "明尼蘇達灰狼 (Minnesota Timberwolves)",
    "New Orleans Pelicans": "紐奧良鵜鶘 (New Orleans Pelicans)", "New York Knicks": "紐約尼克 (New York Knicks)", "Oklahoma City Thunder": "奧克拉荷馬雷霆 (Oklahoma City Thunder)",
    "Orlando Magic": "奧蘭多魔術 (Orlando Magic)", "Philadelphia 76ers": "費城76人 (Philadelphia 76ers)", "Phoenix Suns": "鳳凰城太陽 (Phoenix Suns)",
    "Portland Trail Blazers": "波特蘭拓荒者 (Portland Trail Blazers)", "Sacramento Kings": "沙加緬度國王 (Sacramento Kings)", "San Antonio Spurs": "聖安東尼奧馬刺 (San Antonio Spurs)",
    "Toronto Raptors": "多倫多暴龍 (Toronto Raptors)", "Utah Jazz": "猶他爵士 (Utah Jazz)", "Washington Wizards": "華盛頓巫師 (Washington Wizards)",
    "LA Lakers": "洛杉磯湖人 (Los Angeles Lakers)", "GS Warriors": "金州勇士 (Golden State Warriors)", "NY Knicks": "紐約尼克 (New York Knicks)",
    "NO Pelicans": "紐奧良鵜鶘 (New Orleans Pelicans)", "SA Spurs": "聖安東尼奧馬刺 (San Antonio Spurs)", "UTAH Jazz": "猶他爵士 (Utah Jazz)",
    "WSH Wizards": "華盛頓巫師 (Washington Wizards)", "BKN Nets": "布魯克林籃網 (Brooklyn Nets)", "CHA Hornets": "夏洛特黃蜂 (Charlotte Hornets)"
}

TEAM_LOGO_MAP = {
    "亞特蘭大老鷹 (Atlanta Hawks)": "atl", "波士頓塞爾蒂克 (Boston Celtics)": "bos", "布魯克林籃網 (Brooklyn Nets)": "bkn",
    "夏洛特黃蜂 (Charlotte Hornets)": "cha", "芝加哥公牛 (Chicago Bulls)": "chi", "克里夫蘭騎士 (Cleveland Cavaliers)": "cle",
    "達拉斯獨行俠 (Dallas Mavericks)": "dal", "丹佛金塊 (Denver Nuggets)": "den", "底特律活塞 (Detroit Pistons)": "det",
    "金州勇士 (Golden State Warriors)": "gs", "休士頓火箭 (Houston Rockets)": "hou", "印第安那溜馬 (Indiana Pacers)": "ind",
    "洛杉磯快艇 (Los Angeles Clippers)": "lac", "洛杉磯湖人 (Los Angeles Lakers)": "lal", "曼斐斯灰熊 (Memphis Grizzlies)": "mem",
    "邁阿密熱火 (Miami Heat)": "mia", "密爾瓦基公鹿 (Milwaukee Bucks)": "mil", "明尼蘇達灰狼 (Minnesota Timberwolves)": "min",
    "紐奧良鵜鶘 (New Orleans Pelicans)": "no", "紐約尼克 (New York Knicks)": "ny", "奧克拉荷馬雷霆 (Oklahoma City Thunder)": "okc",
    "奧蘭多魔術 (Orlando Magic)": "orl", "費城76人 (Philadelphia 76ers)": "phi", "鳳凰城太陽 (Phoenix Suns)": "phx",
    "波特蘭拓荒者 (Portland Trail Blazers)": "por", "沙加緬度國王 (Sacramento Kings)": "sac", "聖安東尼奧馬刺 (San Antonio Spurs)": "sa",
    "多倫多暴龍 (Toronto Raptors)": "tor", "猶他爵士 (Utah Jazz)": "utah", "華盛頓巫師 (Washington Wizards)": "wsh"
}

STAR_PLAYERS = {
    "亞特蘭大老鷹 (Atlanta Hawks)": "Trae Young", "波士頓塞爾蒂克 (Boston Celtics)": "Jayson Tatum", "布魯克林籃網 (Brooklyn Nets)": "Mikal Bridges",
    "夏洛特黃蜂 (Charlotte Hornets)": "LaMelo Ball", "芝加哥公牛 (Chicago Bulls)": "Zach LaVine", "克里夫蘭騎士 (Cleveland Cavaliers)": "D. Mitchell",
    "達拉斯獨行俠 (Dallas Mavericks)": "Luka Doncic", "丹佛金塊 (Denver Nuggets)": "Nikola Jokic", "底特律活塞 (Detroit Pistons)": "Cade Cunningham",
    "金州勇士 (Golden State Warriors)": "Stephen Curry", "休士頓火箭 (Houston Rockets)": "Alperen Sengun", "印第安那溜馬 (Indiana Pacers)": "T. Haliburton",
    "洛杉磯快艇 (Los Angeles Clippers)": "Kawhi Leonard", "洛杉磯湖人 (Los Angeles Lakers)": "LeBron James", "曼斐斯灰熊 (Memphis Grizzlies)": "Ja Morant",
    "邁阿密熱火 (Miami Heat)": "Jimmy Butler", "密爾瓦基公鹿 (Milwaukee Bucks)": "G. Antetokounmpo", "明尼蘇達灰狼 (Minnesota Timberwolves)": "Anthony Edwards",
    "紐奧良鵜鶘 (New Orleans Pelicans)": "Zion Williamson", "紐約尼克 (New York Knicks)": "Jalen Brunson", "奧克拉荷馬雷霆 (Oklahoma City Thunder)": "S. Gilgeous-Alexander",
    "奧蘭多魔術 (Orlando Magic)": "Paolo Banchero", "費城76人 (Philadelphia 76ers)": "Joel Embiid", "鳳凰城太陽 (Phoenix Suns)": "Devin Booker",
    "波特蘭拓荒者 (Portland Trail Blazers)": "A. Simons", "沙加緬度國王 (Sacramento Kings)": "De'Aaron Fox", "聖安東尼奧馬刺 (San Antonio Spurs)": "V. Wembanyama",
    "多倫多暴龍 (Toronto Raptors)": "Scottie Barnes", "猶他爵士 (Utah Jazz)": "Lauri Markkanen", "華盛頓巫師 (Washington Wizards)": "Kyle Kuzma"
}

def get_nba_logo_url(team_name_full):
    abbr = TEAM_LOGO_MAP.get(team_name_full, "nba")
    return f"https://a.espncdn.com/i/teamlogos/nba/500/{abbr}.png"

unique_teams = {v: k for k, v in TEAM_NAME_MAP.items() if '(' in v}
NBA_OPTIONS = [{"name": name, "logo": get_nba_logo_url(name)} for name in sorted(unique_teams.keys())]

# ─────────────────────────────────────────
# 2. 基礎球隊數據生成與 500棵決策樹模型訓練
# ─────────────────────────────────────────
def generate_nba_mock_data():
    np.random.seed(42)
    teams_ranked = list(unique_teams.keys())
    n = len(teams_ranked)
    strength = np.linspace(95, 40, n)
    team_stats = pd.DataFrame({
        'Team': teams_ranked,
        'PPG': np.clip(strength * 0.3 + 85, 105, 122), 'OPP_PPG': np.clip(-strength * 0.25 + 135, 106, 120),
        'FG_pct': np.clip(strength * 0.001 + 0.40, 0.43, 0.50), 'ThreeP_pct': np.clip(strength * 0.001 + 0.30, 0.33, 0.40),
        'DEF_REB_pct': np.clip(strength * 0.002 + 0.60, 0.68, 0.78), 'STL': np.clip(strength * 0.04 + 4, 6.0, 9.0),
        'BLK': np.clip(strength * 0.03 + 3, 4.0, 6.5), 'TOV': np.clip(-strength * 0.05 + 18, 12, 16),
        'Pace': np.random.normal(99, 2.0, n).clip(95, 103), 'TS_pct': np.clip(strength * 0.0015 + 0.48, 0.54, 0.61),
        'W': (strength / 100 * 64).astype(int)
    })
    team_stats['Win_pct'] = team_stats['W'] / 82; team_stats['Net_Rating'] = team_stats['PPG'] - team_stats['OPP_PPG']
    team_stats['Home_W'] = (team_stats['W'] * 0.6).astype(int); team_stats['Home_Win_pct'] = team_stats['Home_W'] / 41
    team_stats['Away_W'] = team_stats['W'] - team_stats['Home_W']; team_stats['Away_Win_pct'] = team_stats['Away_W'] / 41
    return team_stats

def generate_nba_game_log(team_stats, n_games=3000):
    teams = team_stats['Team'].tolist(); records = []
    for _ in range(n_games):
        home_team = np.random.choice(teams); away_team = np.random.choice([t for t in teams if t != home_team])
        ht = team_stats[team_stats['Team'] == home_team].iloc[0]; at = team_stats[team_stats['Team'] == away_team].iloc[0]
        h_rest = np.random.choice([0, 1, 2, 3], p=[0.15, 0.35, 0.35, 0.15]); a_rest = np.random.choice([0, 1, 2, 3], p=[0.15, 0.35, 0.35, 0.15])
        h_strk = int(np.random.normal(0, 2)); a_strk = int(np.random.normal(0, 2))
        h_s_out = np.random.choice([1, 0], p=[0.1, 0.9]); a_s_out = np.random.choice([1, 0], p=[0.1, 0.9])
        h_r_out = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1]); a_r_out = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])
        h_pen = (5.0 if h_s_out else 0) + (1.2 * h_r_out); a_pen = (5.0 if a_s_out else 0) + (1.2 * a_r_out)
        diff = (ht['Net_Rating'] + h_strk*0.5 - (3 if h_rest==0 else 0) - h_pen + 3.0) - (at['Net_Rating'] + a_strk*0.5 - (3 if a_rest==0 else 0) - a_pen)
        records.append({
            'Home_Win': np.random.binomial(1, 1 / (1 + np.exp(-diff / 8.0))), 'H_PPG': ht['PPG'], 'H_OPP_PPG': ht['OPP_PPG'], 'H_FG_pct': ht['FG_pct'],
            'H_Win_pct': ht['Win_pct'], 'H_Last10_W': int(ht['Win_pct']*10), 'H_Streak': h_strk, 'H_Rest_Days': h_rest, 'H_Star_Out': h_s_out, 'H_Role_Out': h_r_out,
            'A_PPG': at['PPG'], 'A_OPP_PPG': at['OPP_PPG'], 'A_FG_pct': at['FG_pct'], 'A_Win_pct': at['Win_pct'], 'A_Last10_W': int(at['Win_pct']*10),
            'A_Streak': a_strk, 'A_Rest_Days': a_rest, 'A_Star_Out': a_s_out, 'A_Role_Out': a_r_out, 'DIFF_Net_Rating': (ht['PPG']-ht['OPP_PPG']) - (at['PPG']-at['OPP_PPG'])
        })
    return pd.DataFrame(records)

print("⚙️ [1/2] 正在訓練 NBA 模型...")
TEAM_STATS = generate_nba_mock_data()
GAME_LOG = generate_nba_game_log(TEAM_STATS, 3000)
FEATURES = [c for c in GAME_LOG.columns if c != 'Home_Win']
SCALER = StandardScaler()
X_scaled = SCALER.fit_transform(GAME_LOG[FEATURES])
MODEL = RandomForestClassifier(n_estimators=500, max_depth=6, min_samples_leaf=10, random_state=42)
MODEL.fit(X_scaled, GAME_LOG['Home_Win'])

# ─────────────────────────────────────────
# 3. 🌟 (補回！) NBA 雙引擎爬蟲與狀態產生器
# ─────────────────────────────────────────
_OFFICIAL_SCHEDULE_CACHE = None
def get_official_schedule():
    global _OFFICIAL_SCHEDULE_CACHE
    if _OFFICIAL_SCHEDULE_CACHE is not None: return _OFFICIAL_SCHEDULE_CACHE
    try:
        resp = requests.get("https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if resp.status_code == 200:
            _OFFICIAL_SCHEDULE_CACHE = resp.json()
            return _OFFICIAL_SCHEDULE_CACHE
    except: pass
    return None

def fetch_games_hybrid(query_type, date_str=None, team_name=None):
    games = []; unique_games = set(); is_future = False
    if query_type == 'date' and date_str:
        if datetime.strptime(date_str, "%Y-%m-%d").date() >= datetime.now().date(): is_future = True

    # 引擎 1：NBA 官網快取 (針對未來賽程)
    if is_future:
        schedule = get_official_schedule()
        if schedule:
            game_dates = schedule.get('leagueSchedule', {}).get('gameDates', [])
            allowed_dates = [(datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
            for d_item in game_dates:
                try:
                    f_date = datetime.strptime(d_item.get('gameDate', '').split(' ')[0].split('T')[0], "%m/%d/%Y").strftime("%Y-%m-%d")
                    if f_date in allowed_dates:
                        for g in d_item.get('games', []):
                            home = f"{g['homeTeam']['teamCity']} {g['homeTeam']['teamName']}"; away = f"{g['awayTeam']['teamCity']} {g['awayTeam']['teamName']}"
                            hm = TEAM_NAME_MAP.get(home, home); am = TEAM_NAME_MAP.get(away, away)
                            if f"{f_date}_{hm}_{am}" not in unique_games:
                                unique_games.add(f"{f_date}_{hm}_{am}")
                                games.append({"date": f_date, "home": hm, "away": am, "source": "NBA 官網"})
                        break
                except: pass

    # 引擎 2：ESPN 備用引擎 (針對歷史賽程或官網無資料)
    if len(games) == 0:
        try:
            if query_type == 'date':
                base_date = datetime.strptime(date_str, "%Y-%m-%d")
                start_str = base_date.strftime("%Y%m%d"); end_str = (base_date + timedelta(days=4)).strftime("%Y%m%d")
                resp = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={start_str}-{end_str}&limit=100", timeout=10)
                if resp.status_code == 200:
                    for e in resp.json().get('events', []):
                        g_date = (datetime.strptime(e['date'], "%Y-%m-%dT%H:%MZ") - timedelta(hours=4)).strftime("%Y-%m-%d")
                        hm = TEAM_NAME_MAP.get(e['competitions'][0]['competitors'][0 if e['competitions'][0]['competitors'][0]['homeAway']=='home' else 1]['team']['displayName'], "")
                        am = TEAM_NAME_MAP.get(e['competitions'][0]['competitors'][1 if e['competitions'][0]['competitors'][0]['homeAway']=='home' else 0]['team']['displayName'], "")
                        if hm and am and f"{g_date}_{hm}_{am}" not in unique_games:
                            unique_games.add(f"{g_date}_{hm}_{am}")
                            games.append({"date": g_date, "home": hm, "away": am, "source": "ESPN"})
            elif query_type == 'team':
                espn_abbr = TEAM_LOGO_MAP.get(team_name, "nba")
                if espn_abbr != "nba":
                    resp = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{espn_abbr}/schedule", timeout=10)
                    if resp.status_code == 200:
                        for e in resp.json().get('events', []):
                            g_date = (datetime.strptime(e['date'], "%Y-%m-%dT%H:%MZ") - timedelta(hours=4)).strftime("%Y-%m-%d")
                            hm = TEAM_NAME_MAP.get(e['competitions'][0]['competitors'][0 if e['competitions'][0]['competitors'][0]['homeAway']=='home' else 1]['team']['displayName'], "")
                            am = TEAM_NAME_MAP.get(e['competitions'][0]['competitors'][1 if e['competitions'][0]['competitors'][0]['homeAway']=='home' else 0]['team']['displayName'], "")
                            if hm and am and f"{g_date}_{hm}_{am}" not in unique_games:
                                unique_games.add(f"{g_date}_{hm}_{am}")
                                games.append({"date": g_date, "home": hm, "away": am, "source": "ESPN"})
            games = sorted(games, key=lambda x: x['date'], reverse=True)
        except: pass
    return games

def get_deterministic_stats(date_str, team_name, base_win_pct, is_historical):
    seed_val = int(hashlib.md5(f"{date_str}_{team_name}".encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_val)
    rest_days = int(np.random.choice([0, 1, 2, 3], p=[0.15, 0.45, 0.30, 0.10]))
    last10_w = max(0, min(10, int(base_win_pct * 10 + np.random.normal(0, 1))))
    streak = max(-8, min(8, int(last10_w - 5 + np.random.normal(0, 1))))
    if is_historical:
        star_injured, role_injured = 0, 0
    else:
        star_injured = 1 if np.random.rand() < 0.12 else 0
        role_injured = int(np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1]))
    return rest_days, last10_w, streak, star_injured, role_injured

# ─────────────────────────────────────────
# 4. ⚽ 歐洲足球五大聯賽資料庫 (修復版)
# ─────────────────────────────────────────
print("⚙️ [2/2] 正在載入足球資料庫...")
LEAGUE_WEIGHTS = {"英超": 1.00, "西甲": 0.95, "義甲": 0.90, "德甲": 0.88, "法甲": 0.82}
TIER_STATS = {"S級": {"attack": 2.5, "defense": 0.5, "x_factor": 0.25}, "A級": {"attack": 1.9, "defense": 0.9, "x_factor": 0.10}, "B級": {"attack": 1.4, "defense": 1.2, "x_factor": 0.05}, "C級": {"attack": 1.0, "defense": 1.6, "x_factor": 0.00}}

FULL_LEAGUES = {
    "英超": {
        "S級": ["Manchester City", "Arsenal", "Liverpool"],
        "A級": ["Chelsea", "Tottenham Hotspur", "Manchester United", "Aston Villa", "Newcastle United"],
        "B級": ["Brighton and Hove Albion", "Brentford", "Crystal Palace", "Everton", "Fulham", "Bournemouth", "Nottingham Forest", "Leeds United"],
        "C級": ["Coventry City", "Hull City", "Ipswich Town", "Sunderland"]
    },
    "西甲": {
        "S級": ["Real Madrid C.F.", "FC Barcelona"],
        "A級": ["Atlético de Madrid", "Villarreal CF", "Real Sociedad", "Athletic Club"],
        "B級": ["Real Betis", "Sevilla FC", "Valencia CF", "Celta de Vigo", "CA Osasuna", "Getafe CF"],
        "C級": ["Rayo Vallecano", "RCD Espanyol", "Deportivo Alaves", "Elche CF", "Levante UD", "Racing de Santander", "Deportivo de La Coruña", "Almería"]
    },
    "義甲": {
        "S級": ["Inter Milan", "Juventus FC"],
        "A級": ["AC Milan", "SSC Napoli", "Atalanta BC", "AS Roma", "S.S. Lazio"],
        "B級": ["Bologna FC 1909", "ACF Fiorentina", "Torino FC", "AC Monza", "Genoa CFC", "U.S. Sassuolo Calcio"],
        "C級": ["Udinese Calcio", "U.S. Lecce", "Cagliari Calcio", "Parma Calcio 1913", "Como 1907", "Venezia FC", "Frosinone Calcio"]
    },
    "德甲": {
        "S級": ["Bayern Munich", "Bayer Leverkusen"],
        "A級": ["Borussia Dortmund", "RB Leipzig", "VfB Stuttgart"],
        "B級": ["Eintracht Frankfurt", "SC Freiburg", "TSG Hoffenheim", "Borussia Monchengladbach", "Union Berlin", "Werder Bremen", "Mainz 05"],
        "C級": ["FC Augsburg", "Hamburger SV", "1. FC Köln", "Schalke 04", "SV Elversberg", "SC Paderborn"]
    },
    "法甲": {
        "S級": ["Paris Saint-Germain"],
        "A級": ["AS Monaco", "Olympique Lyonnais", "Olympique de Marseille", "LOSC Lille", "RC Lens"],
        "B級": ["Stade Rennais F.C.", "OGC Nice", "Stade Brestois 29", "RC Strasbourg Alsace", "Toulouse FC", "FC Lorient"],
        "C級": ["Angers SCO", "Le Havre AC", "AJ Auxerre", "Paris FC", "ES Troyes AC", "Le Mans FC"]
    }
}

SUPERSTARS = {
    # --- 英超 ---
    "Manchester City": "Erling Haaland, Phil Foden, Rodri, Bernardo Silva",
    "Arsenal": "Bukayo Saka, Martin Ødegaard, Declan Rice, William Saliba, Kai Havertz",
    "Liverpool": "Virgil van Dijk, Alisson Becker, Alexis Mac Allister, Luis Díaz",
    "Manchester United": "Bruno Fernandes, Marcus Rashford, Alejandro Garnacho, Kobbie Mainoo",
    "Tottenham Hotspur": "James Maddison, Cristian Romero, Guglielmo Vicario, Xavi Simons",
    "Chelsea": "Cole Palmer, Enzo Fernández, Moisés Caicedo, Christopher Nkunku",
    "Aston Villa": "Ollie Watkins, Emiliano Martínez, Leon Bailey, John McGinn",
    "Newcastle United": "Alexander Isak, Bruno Guimarães, Sven Botman, Kieran Trippier",
    "Brighton and Hove Albion": "Kaoru Mitoma, João Pedro, Evan Ferguson",
    "Crystal Palace": "Eberechi Eze, Jean-Philippe Mateta, Adam Wharton",
    "Bournemouth": "Antoine Semenyo, Marcus Tavernier, Illia Zabarnyi",
    "Brentford": "Bryan Mbeumo, Ivan Toney, Yoane Wissa",
    "Everton": "Jordan Pickford, James Tarkowski, Jarrad Branthwaite",
    "Fulham": "Andreas Pereira, Alex Iwobi, Bernd Leno",
    "Ipswich Town": "Omari Hutchinson, Leif Davis, Conor Chaplin",
    "Nottingham Forest": "Morgan Gibbs-White, Taiwo Awoniyi, Murillo",
    "Coventry City": "Haji Wright, Ben Sheaf",
    "Hull City": "Typehon Noslin, Abdülkadir Ömür",
    "Leeds United": "Illan Meslier, Pascal Struijk, Wilfried Gnonto",
    "Sunderland": "Jobe Bellingham, Anthony Patterson",
    # --- 西甲 ---
    "Real Madrid C.F.": "Kylian Mbappé, Jude Bellingham, Vinícius Júnior",
    "FC Barcelona": "Lamine Yamal, Pedri, Gavi, Raphinha",
    "Atlético de Madrid": "Julián Álvarez, Jan Oblak, Rodrigo De Paul",
    "Real Sociedad": "Takefusa Kubo, Martin Zubimendi",
    "Athletic Club": "Nico Williams, Iñaki Williams",
    "Villarreal CF": "Gerard Moreno, Álex Baena",
    "Real Betis": "Isco, Nabil Fekir",
    "Sevilla FC": "Lucas Ocampos, Loïc Badé",
    "Valencia CF": "Giorgi Mamardashvili, Pepelu",
    "Celta de Vigo": "Iago Aspas, Óscar Mingueza",
    "Getafe CF": "Borja Mayoral, Djené",
    "Rayo Vallecano": "Isi Palazón, Álvaro García",
    "RCD Espanyol": "Javi Puado, Martin Braithwaite",
    "Deportivo Alaves": "Antonio Blanco, Abdel Abqar",
    "Elche CF": "Tete Morente",
    "Levante UD": "Giorgi Kochorashvili",
    "CA Osasuna": "Ante Budimir",
    "Racing de Santander": "Peque Fernández",
    "Deportivo de La Coruña": "Lucas Pérez",
    "Almería": "Sergio Arribas",
    # --- 德甲 ---
    "Bayern Munich": "Harry Kane, Michael Olise, Jamal Musiala",
    "Bayer Leverkusen": "Florian Wirtz, Alejandro Grimaldo",
    "RB Leipzig": "Xavi Simons, Loïs Openda, Dani Olmo",
    "Borussia Dortmund": "Julian Brandt, Gregor Kobel",
    "VfB Stuttgart": "Serhou Guirassy, Chris Führich",
    "Eintracht Frankfurt": "Omar Marmoush, Hugo Ekitiké",
    "TSG Hoffenheim": "Andrej Kramarić",
    "SC Freiburg": "Vincenzo Grifo",
    "FC Augsburg": "Ermedin Demirović",
    "Mainz 05": "Jonathan Burkardt",
    "Union Berlin": "Danilho Doekhi",
    "Borussia Monchengladbach": "Alassane Pléa",
    "Werder Bremen": "Marvin Ducksch",
    "1. FC Köln": "Eric Martel",
    "Hamburger SV": "Robert Glatzel",
    "Schalke 04": "Kenan Karaman",
    "SV Elversberg": "Paul Stock",
    "SC Paderborn": "Adriano Grimaldi",
    # --- 法甲 ---
    "Paris Saint-Germain": "Ousmane Dembélé, Bradley Barcola, Achraf Hakimi, Vitinha, Désiré Doué",
    "AS Monaco": "Aleksandr Golovin, Takumi Minamino",
    "LOSC Lille": "Jonathan David, Edon Zhegrova",
    "Olympique Lyonnais": "Alexandre Lacazette, Rayan Cherki",
    "Olympique de Marseille": "Pierre-Emerick Aubameyang",
    "RC Lens": "Brice Samba",
    "Stade Rennais F.C.": "Amine Gouiri",
    "OGC Nice": "Jean-Clair Todibo",
    "Stade Brestois 29": "Pierre Lees-Melou",
    "RC Strasbourg Alsace": "Emanuel Emegha",
    "Toulouse FC": "Thijs Dallinga",
    "FC Lorient": "Laurent Abergel",
    "Angers SCO": "Loïs Diony",
    "Le Havre AC": "Gautier Lloris",
    "AJ Auxerre": "Gaëtan Perrin",
    "Paris FC": "Ilan Kebbal",
    "ES Troyes AC": "Renaud Ripart",
    "Le Mans FC": "Armindo Rodrigues",
    # --- 義甲 ---
    "Inter Milan": "Lautaro Martínez, Nicolò Barella",
    "AC Milan": "Rafael Leão, Christian Pulisic, Luka Modrić",
    "Juventus FC": "Dušan Vlahović, Federico Chiesa",
    "SSC Napoli": "Khvicha Kvaratskhelia, Victor Osimhen",
    "Atalanta BC": "Ademola Lookman, Charles De Ketelaere",
    "AS Roma": "Paulo Dybala, Romelu Lukaku",
    "S.S. Lazio": "Mattia Zaccagni, Luis Alberto",
    "Bologna FC 1909": "Joshua Zirkzee, Riccardo Calafiori",
    "ACF Fiorentina": "Nicolás González, Lucas Beltrán",
    "Torino FC": "Duván Zapata",
    "Como 1907": "Patrick Cutrone",
    "Genoa CFC": "Albert Guðmundsson",
    "Udinese Calcio": "Florian Thauvin",
    "U.S. Lecce": "Nikola Krstović",
    "Cagliari Calcio": "Nahitan Nández",
    "Parma Calcio 1913": "Dennis Man",
    "U.S. Sassuolo Calcio": "Domenico Berardi",
    "Venezia FC": "Joel Pohjanpalo",
    "Frosinone Calcio": "Matías Soulé",
    "AC Monza": "Matteo Pessina"
}

FB_DB = {}
np.random.seed(42)
for league, tiers in FULL_LEAGUES.items():
    for tier, teams in tiers.items():
        for team in teams:
            base = TIER_STATS[tier]
            star = SUPERSTARS.get(team, f"主力 ({team[:3].upper()})")
            FB_DB[team] = { "league": league, "tier": tier, "attack": base["attack"] + np.random.uniform(-0.1, 0.1), "defense": base["defense"] + np.random.uniform(-0.1, 0.1), "x_factor": base["x_factor"], "star": star }

FB_FRONTEND = {l: sorted([t for tier in tiers.values() for t in tier]) for l, tiers in FULL_LEAGUES.items()}

def get_fb_logo_url(team_name, is_home=True):
    encoded_name = urllib.parse.quote(team_name)
    bg_color = "1e3a8a" if is_home else "b91c1c"
    return f"https://ui-avatars.com/api/?name={encoded_name}&background={bg_color}&color=fff&size=128&bold=true&rounded=true"

def simulate_fb_match(stats_a, stats_b, venue_status, a_inj_count, b_inj_count, team_a_name, team_b_name):
    coef_a, coef_b = LEAGUE_WEIGHTS.get(stats_a["league"], 0.8), LEAGUE_WEIGHTS.get(stats_b["league"], 0.8)
    adj_attack_a = max(0.1, stats_a["attack"] - (a_inj_count * 0.15)) * coef_a
    adj_attack_b = max(0.1, stats_b["attack"] - (b_inj_count * 0.15)) * coef_b
    adj_defense_a, adj_defense_b = stats_a["defense"] + (a_inj_count * 0.15), stats_b["defense"] + (b_inj_count * 0.15)
    xg_a = (adj_attack_a * adj_defense_b) + (0 if a_inj_count > 0 else stats_a["x_factor"])
    xg_b = (adj_attack_b * adj_defense_a) + (0 if b_inj_count > 0 else stats_b["x_factor"])

    # 更新場地敘述以匹配前端名稱
    venue_desc = "📍 場地：中立場地 (盃賽)"
    if venue_status == '1': xg_a += 0.35; venue_desc = f"📍 場地：{team_a_name} 享有主場優勢 (+0.35 xG)"
    elif venue_status == '2': xg_b += 0.35; venue_desc = f"📍 場地：{team_b_name} 享有主場優勢 (+0.35 xG)"

    prob_matrix = np.zeros((6, 6))
    for i in range(6):
        for j in range(6): prob_matrix[i, j] = poisson.pmf(i, xg_a) * poisson.pmf(j, xg_b)

    flat_indices = np.argsort(prob_matrix, axis=None)[::-1]
    top1_idx, top2_idx = np.unravel_index(flat_indices[0], prob_matrix.shape), np.unravel_index(flat_indices[1], prob_matrix.shape)

    return {
        "xg_a": round(xg_a, 2), "xg_b": round(xg_b, 2),
        "win_a": round(np.sum(np.tril(prob_matrix, -1)) * 100, 1), "draw": round(np.sum(np.diag(prob_matrix)) * 100, 1), "win_b": round(np.sum(np.triu(prob_matrix, 1)) * 100, 1),
        "score_1": f"{top1_idx[0]} - {top1_idx[1]}", "prob_1": round(prob_matrix[top1_idx] * 100, 1),
        "score_2": f"{top2_idx[0]} - {top2_idx[1]}", "prob_2": round(prob_matrix[top2_idx] * 100, 1),
        "venue_desc": venue_desc, "adj_attack_a": round(adj_attack_a, 2), "adj_attack_b": round(adj_attack_b, 2), "adj_defense_a": round(adj_defense_a, 2), "adj_defense_b": round(adj_defense_b, 2)
    }

# ─────────────────────────────────────────
# 5. 前端 HTML 模板 (雙系統共用)
# ─────────────────────────────────────────
SPORTS_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YuanZe IEM - Sports Analysis</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Helvetica Neue', 'Inter', 'Noto Sans TC', sans-serif; background-color: #fbfbfb; color: #111; }
        .progress-bar-transition { transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1); }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .sys-hidden { display: none !important; }
        .nba-non-selectable { -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; }
    </style>
</head>
<body class="min-h-screen relative">

    <div id="nba_loading_overlay" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex flex-col items-center justify-center space-y-6 sys-hidden nba-non-selectable">
        <div class="flex space-x-3 items-end h-20">
            <div class="w-4 bg-white rounded-full animate-bounce h-12" style="animation-delay: 0.1s"></div>
            <div class="w-4 bg-white rounded-full animate-bounce h-12" style="animation-delay: 0.2s"></div>
            <div class="w-4 bg-white rounded-full animate-bounce h-12" style="animation-delay: 0.3s"></div>
        </div>
        <p class="text-white font-black text-2xl tracking-[0.2em] animate-pulse uppercase">🤖 AI 執行運算中...</p>
        <p class="text-gray-300 text-sm font-medium">綜合考量過往數據與模型...</p>
    </div>

    <div class="text-center mt-12 mb-8">
        <div class="text-xs text-gray-500 font-bold tracking-[0.3em] mb-3 uppercase">YuanZe IEM // Sports Board</div>
        <h1 class="text-6xl md:text-8xl font-black tracking-tighter text-black">SPORTS®</h1>
    </div>

    <div class="flex justify-center mb-10">
        <div class="bg-white border border-gray-200 rounded-full p-2 inline-flex shadow-sm gap-2">
            <button id="main_tab_nba" onclick="switchMainSystem('nba')" class="px-8 py-3 rounded-full bg-black text-white font-bold text-sm transition shadow-md">🏀 NBA 賽事分析</button>
            <button id="main_tab_fb" onclick="switchMainSystem('fb')" class="px-8 py-3 rounded-full text-gray-500 hover:text-black font-bold text-sm transition bg-transparent">⚽ 歐洲足球預測</button>
        </div>
    </div>

    <div class="container mx-auto px-4 max-w-6xl mb-20 relative">
        <div id="system_nba" class="flex flex-col md:flex-row gap-8">
            <div class="w-full md:w-1/3 bg-white p-8 rounded-[2rem] shadow-sm border border-gray-200">
                <div class="flex border-b border-gray-100 mb-6 pb-2">
                    <button id="nba_tab_date" class="w-1/2 py-2 text-center font-bold text-black border-b-2 border-black" onclick="switchNBATab('date')">📅 日期查詢</button>
                    <button id="nba_tab_team" class="w-1/2 py-2 text-center font-bold text-gray-400 border-b-2 border-transparent" onclick="switchNBATab('team')">👕 球隊查詢</button>
                </div>

                <div id="nba_content_date" class="mb-5">
                    <label class="block text-sm font-bold text-gray-700 mb-3">1. 選擇比賽日期 (美國時間)</label>
                    <input type="date" id="nba_date" class="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none mb-4">
                    <button id="nba_btn_date" onclick="fetchNBAGames('date')" class="w-full bg-black text-white py-4 px-4 font-bold text-sm rounded-full hover:shadow-lg transition">載入賽程</button>
                </div>

                <div id="nba_content_team" class="mb-5 hidden">
                    <label class="block text-sm font-bold text-gray-700 mb-3">1. 選擇喜愛的球隊</label>
                    <div class="relative w-full mb-4">
                        <button id="custom_select_btn" type="button" class="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none flex justify-between items-center text-sm font-bold" onclick="toggleDropdown()">
                            <div id="selected_team_display" class="flex items-center"><span class="text-gray-500">請選擇球隊...</span></div>
                            <svg class="w-4 h-4 ml-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                        </button>
                        <input type="hidden" id="nba_team_select" value="">
                        <div id="custom_dropdown" class="hidden absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto no-scrollbar">
                            <ul id="dropdown_list" class="py-1"></ul>
                        </div>
                    </div>
                    <button id="nba_btn_team" onclick="fetchNBAGames('team')" class="w-full bg-black text-white py-4 px-4 font-bold text-sm rounded-full hover:shadow-lg transition">載入賽程</button>
                </div>

                <div id="nba_selection_area" class="mt-8 hidden pt-6 border-t border-gray-100">
                    <label class="block text-sm font-bold text-gray-700 mb-3">2. 選擇對戰組合</label>
                    <select id="nba_game_select" class="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl mb-6 text-sm font-bold appearance-none"></select>
                    <button id="nba_predict_btn" onclick="predictNBA()" class="w-full bg-black text-white py-4 rounded-full font-bold shadow-lg hover:shadow-xl transition text-lg disabled:opacity-50">⚡ 執行分析預測</button>
                </div>
            </div>

            <div class="w-full md:w-2/3">
                <div id="nba_welcome" class="h-full flex items-center justify-center bg-white p-10 rounded-[2rem] border border-gray-200 min-h-[400px]">
                    <div class="text-center text-gray-300"><div class="text-5xl font-black mb-2">NBA AI</div><p class="text-sm font-bold tracking-wider">請在左側選擇賽事以查看分析</p></div>
                </div>
                <div id="nba_result" class="hidden bg-white p-10 rounded-[2rem] border border-gray-200">
                    <div class="flex items-center justify-between border-b border-gray-100 pb-4 mb-6">
                        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">🏆 勝率預測結果</h2>
                        <span id="nba_data_source" class="bg-gray-50 text-gray-400 text-xs px-3 py-1 rounded-full font-bold border border-gray-200"></span>
                    </div>

                    <div class="flex justify-between items-center mb-10">
                        <div class="text-center w-2/5"><div class="text-xs text-gray-400 font-bold mb-2 uppercase tracking-widest">主場 (Home)</div><img id="nba_home_logo" class="w-28 h-28 mx-auto mb-4 object-contain"><div id="nba_home_name" class="font-black text-lg text-blue-700 leading-tight"></div></div>
                        <div class="text-center w-1/5 text-4xl font-black text-gray-200 italic">VS</div>
                        <div class="text-center w-2/5"><div class="text-xs text-gray-400 font-bold mb-2 uppercase tracking-widest">客場 (Away)</div><img id="nba_away_logo" class="w-28 h-28 mx-auto mb-4 object-contain"><div id="nba_away_name" class="font-black text-lg text-red-600 leading-tight"></div></div>
                    </div>

                    <div class="mb-10 bg-slate-50 p-6 rounded-2xl border border-slate-100 border border-gray-100">
                        <div class="flex justify-between font-black mb-2 text-2xl"><span id="nba_home_prob" class="text-blue-700"></span><span id="nba_away_prob" class="text-red-600"></span></div>
                        <div class="w-full bg-gray-200 rounded-full h-6 flex overflow-hidden mb-4"><div id="nba_home_bar" class="progress-bar-transition bg-blue-600 h-6"></div><div id="nba_away_bar" class="progress-bar-transition bg-red-500 h-6"></div></div>
                        <div id="nba_winner" class="text-center text-sm font-bold py-3 rounded-lg"></div>
                    </div>

                    <div class="mt-8">
                        <h3 class="text-lg font-bold mb-1 text-slate-800 flex items-center gap-2">🔍 模型預測依據 (Features)</h3>
                        <p class="text-xs text-gray-500 mb-4">綜合考量以下構面得出勝率：</p>

                        <div id="nba_injury_section" class="mb-6 bg-white p-5 rounded-2xl border border-gray-200 shadow-sm hidden">
                            <h3 class="text-xs font-bold text-gray-400 mb-4 flex items-center uppercase tracking-widest border-b border-gray-100 pb-2"><span class="mr-2">🚑</span> Injury Report</h3>
                            <div class="flex justify-between text-sm">
                                <div class="w-1/2 pr-4 border-r border-gray-100" id="nba_home_injury_panel"></div>
                                <div class="w-1/2 pl-4" id="nba_away_injury_panel"></div>
                            </div>
                        </div>

                        <div id="nba_stats" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm"></div>
                    </div>
                </div>
            </div>
        </div>

        <div id="system_fb" class="sys-hidden flex flex-col md:flex-row gap-8">
            <div class="w-full md:w-1/3 bg-white p-8 rounded-[2rem] shadow-sm border border-gray-200">
                <h2 class="text-sm font-bold mb-6 text-gray-400 border-b border-gray-100 pb-2 uppercase tracking-widest">Match Settings</h2>
                <div class="mb-4 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                    <label class="block text-sm font-bold text-gray-700 mb-2">主場球隊 (Team A)</label>
                    <select id="fb_league_a" class="w-full p-3 mb-2 bg-white border border-gray-300 rounded-xl text-sm focus:outline-none" onchange="updateFBTeams('a')"></select>
                    <!-- 加上 onchange 呼叫 updateFBVenueOptions() -->
                    <select id="fb_team_a" class="w-full p-3 mb-3 bg-white border border-gray-300 rounded-xl text-sm font-bold focus:outline-none" onchange="updateFBVenueOptions()"></select>
                    <div class="flex justify-between items-center text-xs font-bold text-gray-500"><span>🤕 缺陣人數:</span><input type="number" id="fb_inj_a" min="0" value="0" class="w-12 p-1 border rounded text-center"></div>
                </div>
                <div class="mb-6 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                    <label class="block text-sm font-bold text-gray-700 mb-2">客場球隊 (Team B)</label>
                    <select id="fb_league_b" class="w-full p-2 mb-2 bg-white border border-gray-300 rounded-xl text-sm focus:outline-none" onchange="updateFBTeams('b')"></select>
                    <!-- 加上 onchange 呼叫 updateFBVenueOptions() -->
                    <select id="fb_team_b" class="w-full p-2 mb-3 bg-white border border-gray-300 rounded-xl text-sm font-bold focus:outline-none" onchange="updateFBVenueOptions()"></select>
                    <div class="flex justify-between items-center text-xs font-bold text-gray-500"><span>🤕 缺陣人數:</span><input type="number" id="fb_inj_b" min="0" value="0" class="w-12 p-1 border rounded text-center"></div>
                </div>
                <label class="block text-xs font-bold text-gray-400 mb-2 uppercase">🏟️ 場地優勢</label>
                <!-- 場地選單內容將透過 JS 動態產生以符合選取的球隊名稱 -->
                <select id="fb_venue" class="w-full p-4 bg-white border border-gray-200 rounded-2xl mb-6 text-sm font-bold focus:outline-none"></select>

                <button id="fb_predict_btn" onclick="predictFB()" class="w-full bg-black text-white py-4 rounded-full font-bold shadow-lg hover:shadow-xl transition text-lg disabled:opacity-50">⚡ 執行預測</button>
            </div>

            <div class="w-full md:w-2/3">
                <div id="fb_welcome" class="h-full flex items-center justify-center bg-white p-10 rounded-[2rem] border border-gray-200 min-h-[400px]">
                    <div class="text-center text-gray-300"><div class="text-5xl font-black mb-2">FOOTBALL AI</div><p class="text-sm font-bold tracking-wider">請在左側設定對戰組合與傷兵狀況</p></div>
                </div>
                <div id="fb_result" class="hidden bg-white p-10 rounded-[2rem] border border-gray-200">
                    <div class="flex items-center justify-between border-b border-gray-100 pb-4 mb-6">
                        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">🏆 Poisson Prediction</h2>
                    </div>
                    <div class="flex justify-between items-center mb-8">
                        <div class="text-center w-2/5"><div class="text-xs text-gray-400 font-bold mb-2 uppercase tracking-widest">Home</div><img id="fb_logo_a" class="w-24 h-24 mx-auto mb-3 rounded-full drop-shadow"><div id="fb_name_a" class="font-black text-lg text-black"></div></div>
                        <div class="text-center w-1/5 text-3xl font-black text-gray-200 italic">VS</div>
                        <div class="text-center w-2/5"><div class="text-xs text-gray-400 font-bold mb-2 uppercase tracking-widest">Away</div><img id="fb_logo_b" class="w-24 h-24 mx-auto mb-3 rounded-full drop-shadow"><div id="fb_name_b" class="font-black text-lg text-gray-500"></div></div>
                    </div>
                    <div class="mb-8 bg-gray-50 p-6 rounded-3xl border border-gray-100 order-gray-100">
                        <div class="flex justify-between text-xs font-bold text-gray-500 mb-2 uppercase tracking-widest"><span id="fb_txt_wina"></span><span id="fb_txt_draw"></span><span id="fb_txt_winb"></span></div>
                        <div class="w-full bg-gray-200 rounded-full h-4 flex overflow-hidden"><div id="fb_bar_wina" class="progress-bar-transition bg-black h-4"></div><div id="fb_bar_draw" class="progress-bar-transition bg-gray-400 h-4"></div><div id="fb_bar_winb" class="progress-bar-transition bg-gray-300 h-4"></div></div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <div class="bg-gray-50 p-5 rounded-2xl border border-gray-100">
                            <h3 class="font-bold text-gray-400 mb-3 border-b border-gray-200 pb-2 text-xs uppercase">Score Prediction</h3>
                            <div class="flex justify-between font-bold mb-1">
                                <span class="text-sm text-gray-500">🥇 首選比分:</span>
                                <span id="fb_score1" class="text-lg font-black text-black bg-white px-2 py-0.5 rounded border"></span>
                                <span id="fb_prob1" class="text-xs text-gray-400 font-bold"></span>
                            </div>
                            <div class="flex justify-between font-bold text-gray-500 text-sm mt-2">
                                <span>🥈 次選比分:</span>
                                <span id="fb_score2" class="text-black bg-white px-2 py-0.5 rounded border"></span>
                                <span id="fb_prob2" class="text-xs text-gray-400"></span>
                            </div>
                        </div>
                        <div class="bg-gray-50 p-5 rounded-2xl border border-gray-100">
                            <h3 class="font-bold text-gray-400 mb-3 border-b border-gray-200 pb-2 text-xs uppercase">Expected Goals (xG)</h3>
                            <div class="flex justify-between items-center mb-3">
                                <span id="fb_xga_name" class="text-black font-bold text-sm truncate w-1/2"></span>
                                <span id="fb_xga" class="text-xl font-black text-black"></span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span id="fb_xgb_name" class="text-gray-500 font-bold text-sm truncate w-1/2"></span>
                                <span id="fb_xgb" class="text-xl font-black text-gray-500"></span>
                            </div>
                        </div>
                    </div>

                    <div class="mt-8">
                        <h3 class="text-lg font-bold mb-1 text-slate-800 flex items-center gap-2">🔍 足球模型預測依據 (Key Factors)</h3>
                        <p class="text-xs text-gray-500 mb-4">系統根據雙方攻防能力與泊松分佈計算：</p>
                        <div id="fb_stats" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchMainSystem(sys) {
            document.getElementById('system_nba').classList.add('sys-hidden'); document.getElementById('system_fb').classList.add('sys-hidden');
            document.getElementById('main_tab_nba').className = "px-8 py-3 rounded-full text-gray-500 hover:text-black font-bold text-sm transition bg-transparent";
            document.getElementById('main_tab_fb').className = "px-8 py-3 rounded-full text-gray-500 hover:text-black font-bold text-sm transition bg-transparent";
            document.getElementById('system_' + sys).classList.remove('sys-hidden');
            document.getElementById('main_tab_' + sys).className = "px-8 py-3 rounded-full bg-black text-white font-bold text-sm transition shadow-md";
        }

        const nbaData = {{ NBA_TEAMS_JSON | safe }};
        document.getElementById('nba_date').valueAsDate = new Date();

        function toggleDropdown() { document.getElementById('custom_dropdown').classList.toggle('hidden'); }

        function selectTeam(name, logoUrl) {
            document.getElementById('nba_team_select').value = name;
            const formattedName = name.replace(' (', ' <span class="text-xs text-gray-400">(').replace(')', ')</span>');
            document.getElementById('selected_team_display').innerHTML = `
                <img src="${logoUrl}" class="w-6 h-6 mr-2 object-contain" alt="logo">
                <span class="truncate">${formattedName}</span>
            `;
            toggleDropdown();
        }

        document.addEventListener('click', function(event) {
            const btn = document.getElementById('custom_select_btn');
            const dropdown = document.getElementById('custom_dropdown');
            if (btn && dropdown && !btn.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.classList.add('hidden');
            }
        });

        const list = document.getElementById('dropdown_list');
        nbaData.forEach(team => {
            const li = document.createElement('li');
            const formattedName = team.name.replace(' (', ' <span class="text-xs text-gray-400">(').replace(')', ')</span>');
            li.innerHTML = `
                <div class="flex items-center px-4 py-3 hover:bg-slate-100 cursor-pointer transition-colors border-b border-gray-50" onclick="selectTeam('${team.name}', '${team.logo}')">
                    <img src="${team.logo}" class="w-8 h-8 mr-3 object-contain drop-shadow-sm" alt="logo">
                    <span class="text-sm font-bold text-slate-700">${formattedName}</span>
                </div>
            `;
            list.appendChild(li);
        });
        if (nbaData.length > 0) selectTeam(nbaData[0].name, nbaData[0].logo);

        function switchNBATab(tab) {
            document.getElementById('nba_selection_area').classList.add('hidden');
            if (tab === 'date') {
                document.getElementById('nba_tab_date').className = "w-1/2 py-2 text-center font-bold text-black border-b-2 border-black";
                document.getElementById('nba_tab_team').className = "w-1/2 py-2 text-center font-bold text-gray-400 border-b-2 border-transparent";
                document.getElementById('nba_content_date').classList.remove('hidden'); document.getElementById('nba_content_team').classList.add('hidden');
            } else {
                document.getElementById('nba_tab_team').className = "w-1/2 py-2 text-center font-bold text-black border-b-2 border-black";
                document.getElementById('nba_tab_date').className = "w-1/2 py-2 text-center font-bold text-gray-400 border-b-2 border-transparent";
                document.getElementById('nba_content_team').classList.remove('hidden'); document.getElementById('nba_content_date').classList.add('hidden');
            }
        }

        async function fetchNBAGames(type) {
            let payload = type === 'date' ? { query_type: 'date', date: document.getElementById('nba_date').value } : { query_type: 'team', team_name: document.getElementById('nba_team_select').value };
            try {
                const res = await fetch('/api/nba/games', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
                const data = await res.json();
                const sel = document.getElementById('nba_game_select'); sel.innerHTML = '';
                if(data.games.length === 0) sel.innerHTML = '<option value="">No Games Found</option>';
                else data.games.forEach(g => sel.innerHTML += `<option value='${JSON.stringify(g)}'>${g.date} | ${g.home} vs ${g.away}</option>`);
                document.getElementById('nba_selection_area').classList.remove('hidden');
            } catch(e) { alert("Error fetching NBA schedule."); }
        }

        async function predictNBA() {
            const val = document.getElementById('nba_game_select').value; if(!val) return;
            const game = JSON.parse(val);

            const loadingOverlay = document.getElementById('nba_loading_overlay');
            const predictBtn = document.getElementById('nba_predict_btn');
            loadingOverlay.classList.remove('sys-hidden');
            predictBtn.disabled = true;

            document.getElementById('nba_welcome').classList.add('hidden');
            document.getElementById('nba_result').classList.add('hidden');

            document.getElementById('nba_home_bar').style.width = `50%`;
            document.getElementById('nba_away_bar').style.width = `50%`;

            try {
                await new Promise(resolve => setTimeout(resolve, 1500));

                const res = await fetch('/api/nba/predict', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ game_date: game.date, home_team: game.home, away_team: game.away, source: game.source }) });
                const data = await res.json();

                loadingOverlay.classList.add('sys-hidden');
                predictBtn.disabled = false;
                document.getElementById('nba_result').classList.remove('hidden');

                document.getElementById('nba_data_source').innerText = `Data Source: ${data.source}`;
                const formatName = (name) => name.replace(' (', '<br><span class="text-sm font-medium text-gray-400">').replace(')', '</span>');
                document.getElementById('nba_home_name').innerHTML = formatName(data.home_team); document.getElementById('nba_away_name').innerHTML = formatName(data.away_team);
                document.getElementById('nba_home_logo').src = data.home_logo; document.getElementById('nba_away_logo').src = data.away_logo;

                const homeProb = (data.home_win_prob*100).toFixed(1);
                const awayProb = (data.away_win_prob*100).toFixed(1);
                document.getElementById('nba_home_prob').innerText = homeProb + '%'; document.getElementById('nba_away_prob').innerText = awayProb + '%';
                setTimeout(() => { document.getElementById('nba_home_bar').style.width = homeProb + '%'; document.getElementById('nba_away_bar').style.width = awayProb + '%'; }, 100);

                const homeZh = data.home_team.split(' (')[0];
                const awayZh = data.away_team.split(' (')[0];
                if (data.predicted_winner === 'Home') {
                    document.getElementById('nba_winner').className = "text-center text-sm font-bold text-blue-800 bg-blue-100 border border-blue-200 py-3 rounded-lg";
                    document.getElementById('nba_winner').innerText = `🏀 綜合預測：主場 ${homeZh} 勝出機率較高`;
                } else {
                    document.getElementById('nba_winner').className = "text-center text-sm font-bold text-red-800 bg-red-100 border border-red-200 py-3 rounded-lg";
                    document.getElementById('nba_winner').innerText = `🏀 綜合預測：客場 ${awayZh} 勝出機率較高`;
                }

                const isHistorical = data.is_historical;
                const injurySection = document.getElementById('nba_injury_section');
                if (isHistorical) {
                    injurySection.classList.add('hidden');
                } else {
                    injurySection.classList.remove('hidden');
                    const renderInjury = (inj, teamName) => {
                        let html = `<p class="font-black text-black mb-2">${teamName.split(' ')[0]}</p>`;
                        if (inj.star_out) html += `<p class="text-rose-600 font-bold text-xs mb-1">❌ 當家球星 (${inj.star_name}) 缺陣</p>`;
                        else html += `<p class="text-emerald-600 font-bold text-xs mb-1">✅ 當家球星 (${inj.star_name}) 健康</p>`;
                        if (inj.role_out > 0) html += `<p class="text-amber-600 text-xs">⚠️ ${inj.role_out} 名輪替球員缺陣</p>`;
                        else html += `<p class="text-gray-500 text-xs">✓ 輪替陣容完整</p>`;
                        return html;
                    };
                    document.getElementById('nba_home_injury_panel').innerHTML = renderInjury(data.injury.home, data.home_team);
                    document.getElementById('nba_away_injury_panel').innerHTML = renderInjury(data.injury.away, data.away_team);
                }

                const sH = data.stats.home; const sA = data.stats.away;
                let statsHtml = '';

                const renderCategory = (title) => {
                    statsHtml += `<div class="bg-slate-200 px-4 py-2 text-sm font-bold text-slate-700">${title}</div>`;
                };

                const renderRow = (label, vH, vA, isLowerBetter=false, isPercentage=false) => {
                    let winH = false; let winA = false;
                    if(vH !== vA){ if(isLowerBetter){winH = vH<vA; winA = vH>vA;} else {winH = vH>vA; winA = vH<vA;} }
                    let cH = winH ? 'text-green-600' : 'text-slate-600'; let cA = winA ? 'text-green-600' : 'text-slate-600';
                    const formatVal = (v) => {
                        if (isPercentage) return (v * 100).toFixed(1) + '%';
                        if (Number.isInteger(v)) return v;
                        return v.toFixed(1);
                    };
                    statsHtml += `<div class="flex justify-between p-3 border-b border-gray-100 text-sm bg-white hover:bg-slate-50"><div class="w-1/3 text-center font-bold ${cH}">${formatVal(vH)}</div><div class="w-1/3 text-center text-slate-600 font-medium text-xs">${label}</div><div class="w-1/3 text-center font-bold ${cA}">${formatVal(vA)}</div></div>`;
                };

                renderCategory("⚔️ 基本攻防數據 (Team Stats)");
                renderRow("場均得分 (PPG)", sH.PPG, sA.PPG, false);
                renderRow("場均失分 (OPP PPG)", sH.OPP_PPG, sA.OPP_PPG, true);
                renderRow("投籃命中率 (FG%)", sH.FG_pct, sA.FG_pct, false, true);
                renderRow("三分命中率 (3P%)", sH.ThreeP_pct, sA.ThreeP_pct, false, true);
                renderRow("防守籃板率 (DEF REB%)", sH.DEF_REB_pct, sA.DEF_REB_pct, false, true);
                renderRow("抄截數 (STL)", sH.STL, sA.STL, false);
                renderRow("阻攻數 (BLK)", sH.BLK, sA.BLK, false);

                renderCategory("🔥 近期狀態 (Recent Form)");
                renderRow("近 10 場勝仗 (Last 10)", sH.Last10_W, sA.Last10_W, false);
                renderRow("連勝/連敗 (Streak)", sH.Streak, sA.Streak, false);

                renderCategory("🏟️ 環境與體力因素 (Contextual)");
                renderRow("主/客場勝率 (Home/Away Win%)", sH.Home_Win_pct, sA.Away_Win_pct, false, true);
                renderRow("賽前休息天數 (0=背靠背)", data.rest.home_rest, data.rest.away_rest, false);

                renderCategory("📈 進階數據 (Advanced Stats)");
                renderRow("真實命中率 (TS%)", sH.TS_pct, sA.TS_pct, false, true);
                renderRow("比賽節奏 (Pace)", sH.Pace, sA.Pace, false);

                document.getElementById('nba_stats').innerHTML = statsHtml;

            } catch(e) {
                console.error(e);
                loadingOverlay.classList.add('sys-hidden');
                predictBtn.disabled = false;
                document.getElementById('nba_welcome').classList.remove('hidden');
            }
        }

        const fbLeagues = {{ FB_LEAGUES_JSON | safe }};
        function initFBSelect(id, opts) { const el = document.getElementById(id); el.innerHTML=''; opts.forEach(o => el.innerHTML+=`<option value="${o}">${o}</option>`); }

        // 🌟 新增：動態更新場地優勢選項的文字
        function updateFBVenueOptions() {
            const ta = document.getElementById('fb_team_a').value;
            const tb = document.getElementById('fb_team_b').value;
            const venueEl = document.getElementById('fb_venue');

            if (!ta || !tb) return;

            // 記住原本選的選項（1=主場, 2=客場, 3=中立）
            const currentVal = venueEl.value || "1";

            venueEl.innerHTML = `
                <option value="1">${ta} 坐鎮主場</option>
                <option value="2">${tb} 坐鎮主場</option>
                <option value="3">中立場地 (盃賽)</option>
            `;

            // 重新選定原本選的索引
            if (["1", "2", "3"].includes(currentVal)) {
                venueEl.value = currentVal;
            } else {
                venueEl.value = "1";
            }
        }

        function updateFBTeams(side) {
            initFBSelect('fb_team_'+side, fbLeagues[document.getElementById('fb_league_'+side).value]);
            updateFBVenueOptions(); // 在聯賽與隊伍更新時，同步更新場地文字
        }

        initFBSelect('fb_league_a', Object.keys(fbLeagues)); initFBSelect('fb_league_b', Object.keys(fbLeagues));
        updateFBTeams('a'); updateFBTeams('b');

        const renderFBRow = (label, valA, valB, lowerIsBetter=false, isText=false) => {
            let winA = false; let winB = false;
            if (!isText && valA !== valB) { if (lowerIsBetter) { winA = valA < valB; winB = valA > valB; } else { winA = valA > valB; winB = valA < valB; } }
            const colorA = isText ? 'text-slate-700' : (winA ? 'text-green-600' : 'text-slate-500');
            const colorB = isText ? 'text-slate-700' : (winB ? 'text-green-600' : 'text-slate-500');
            const wrapClass = isText ? 'break-words whitespace-normal text-xs md:text-sm' : 'truncate';
            return `<div class="flex items-center justify-between p-3 border-b border-gray-100 text-sm hover:bg-slate-50 bg-white"><div class="w-2/5 text-center font-bold ${colorA} ${wrapClass} px-2">${valA}</div><div class="w-1/5 text-center font-semibold text-slate-600 text-xs">${label}</div><div class="w-2/5 text-center font-bold ${colorB} ${wrapClass} px-2">${valB}</div></div>`;
        };

        async function predictFB() {
            const ta = document.getElementById('fb_team_a').value, tb = document.getElementById('fb_team_b').value;
            const inj_a = parseInt(document.getElementById('fb_inj_a').value);
            const inj_b = parseInt(document.getElementById('fb_inj_b').value);

            if(ta === tb) { alert("請選擇不同的兩支球隊！"); return; }

            const loadingOverlay = document.getElementById('nba_loading_overlay');
            const predictBtn = document.getElementById('fb_predict_btn');
            loadingOverlay.classList.remove('sys-hidden');
            predictBtn.disabled = true;

            document.getElementById('fb_welcome').classList.add('hidden');
            document.getElementById('fb_result').classList.add('hidden');

            document.getElementById('fb_bar_wina').style.width = `33%`;
            document.getElementById('fb_bar_draw').style.width = `33%`;
            document.getElementById('fb_bar_winb').style.width = `33%`;

            const payload = { team_a: ta, team_b: tb, inj_a: inj_a, inj_b: inj_b, venue: document.getElementById('fb_venue').value };
            try {
                await new Promise(resolve => setTimeout(resolve, 1000));

                const res = await fetch('/api/fb/predict', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
                const data = await res.json();

                loadingOverlay.classList.add('sys-hidden');
                predictBtn.disabled = false;
                document.getElementById('fb_result').classList.remove('hidden');

                document.getElementById('fb_name_a').innerText = data.team_a; document.getElementById('fb_name_b').innerText = data.team_b;
                document.getElementById('fb_logo_a').src = data.logo_a; document.getElementById('fb_logo_b').src = data.logo_b;
                document.getElementById('fb_txt_wina').innerText = `Home ${data.res.win_a}%`;
                document.getElementById('fb_txt_draw').innerText = `Draw ${data.res.draw}%`;
                document.getElementById('fb_txt_winb').innerText = `Away ${data.res.win_b}%`;
                setTimeout(() => { document.getElementById('fb_bar_wina').style.width=data.res.win_a+'%'; document.getElementById('fb_bar_draw').style.width=data.res.draw+'%'; document.getElementById('fb_bar_winb').style.width=data.res.win_b+'%'; }, 100);
                document.getElementById('fb_score1').innerText = data.res.score_1; document.getElementById('fb_prob1').innerText = `Prob ${data.res.prob_1}%`;
                document.getElementById('fb_score2').innerText = data.res.score_2; document.getElementById('fb_prob2').innerText = `Prob ${data.res.prob_2}%`;
                document.getElementById('fb_xga_name').innerText = data.team_a; document.getElementById('fb_xgb_name').innerText = data.team_b;
                document.getElementById('fb_xga').innerText = `${data.res.xg_a}`; document.getElementById('fb_xgb').innerText = `${data.res.xg_b}`;

                let fbStatsHtml = `<div class="bg-slate-200 px-4 py-2 text-sm font-bold text-slate-700">⚔️ 核心攻防指標 (Core Metrics)</div>`;
                fbStatsHtml += renderFBRow("X Factor (關鍵球星)", data.stats_a.star, data.stats_b.star, false, true);
                fbStatsHtml += renderFBRow("進攻火力 (Attack)", data.res.adj_attack_a, data.res.adj_attack_b);
                fbStatsHtml += renderFBRow("防守破綻 (Defense)", data.res.adj_defense_a, data.res.adj_defense_b, true);

                const injA_text = inj_a > 0 ? `❌ 缺陣 ${inj_a} 人` : "✅ 健康";
                const injB_text = inj_b > 0 ? `❌ 缺陣 ${inj_b} 人` : "✅ 健康";
                fbStatsHtml += renderFBRow("傷兵影響 (Injuries)", injA_text, injB_text, false, true);

                fbStatsHtml += `<div class="bg-slate-50 p-4 text-center text-sm text-slate-600 font-bold uppercase tracking-widest border-t">${data.res.venue_desc}</div>`;
                document.getElementById('fb_stats').innerHTML = fbStatsHtml;

            } catch(e) {
                console.error(e);
                loadingOverlay.classList.add('sys-hidden');
                predictBtn.disabled = false;
                document.getElementById('fb_welcome').classList.remove('hidden');
            }
        }
    </script>
</body>
</html>
"""
SPORTS_HTML_TEMPLATE = SPORTS_HTML_TEMPLATE.replace('{{ NBA_TEAMS_JSON | safe }}', json.dumps(NBA_OPTIONS)).replace('{{ FB_LEAGUES_JSON | safe }}', json.dumps(FB_FRONTEND))

# ─────────────────────────────────────────
# 6. Flask 路由 (sports_app)
# ─────────────────────────────────────────
sports_app = Flask(__name__)

@sports_app.route('/')
def home():
    return render_template_string(SPORTS_HTML_TEMPLATE)

@sports_app.route('/api/nba/games', methods=['POST'])
def nba_games():
    data = request.json
    games = fetch_games_hybrid(data.get('query_type', 'date'), data.get('date', ''), data.get('team_name', ''))
    return jsonify({"games": games})

@sports_app.route('/api/nba/predict', methods=['POST'])
def nba_predict():
    data = request.json
    try:
        ht = TEAM_STATS[TEAM_STATS['Team'] == data.get('home_team')].iloc[0]
        at = TEAM_STATS[TEAM_STATS['Team'] == data.get('away_team')].iloc[0]
    except IndexError:
        return jsonify({"error": "系統內無法匹配雙方球隊特徵"}), 400

    is_historical = datetime.strptime(data.get('game_date'), "%Y-%m-%d").date() < datetime.now().date()
    h_rest, h_l10, h_streak, h_star_out, h_role_out = get_deterministic_stats(data.get('game_date'), data.get('home_team'), ht['Win_pct'], is_historical)
    a_rest, a_l10, a_streak, a_star_out, a_role_out = get_deterministic_stats(data.get('game_date'), data.get('away_team'), at['Win_pct'], is_historical)
    features_dict = {
        'H_PPG': ht['PPG'], 'H_OPP_PPG': ht['OPP_PPG'], 'H_FG_pct': ht['FG_pct'], 'H_3P_pct': ht['ThreeP_pct'], 'H_DEF_REB_pct': ht['DEF_REB_pct'], 'H_STL': ht['STL'], 'H_BLK': ht['BLK'], 'H_Win_pct': ht['Win_pct'], 'H_Home_Win_pct': ht['Home_Win_pct'], 'H_Last10_W': h_l10, 'H_Streak': h_streak, 'H_Rest_Days': h_rest, 'H_Star_Out': h_star_out, 'H_Role_Out': h_role_out, 'H_Pace': ht['Pace'], 'H_TS_pct': ht['TS_pct'],
        'A_PPG': at['PPG'], 'A_OPP_PPG': at['OPP_PPG'], 'A_FG_pct': at['FG_pct'], 'A_3P_pct': at['ThreeP_pct'], 'A_DEF_REB_pct': at['DEF_REB_pct'], 'A_STL': at['STL'], 'A_BLK': at['BLK'], 'A_Win_pct': at['Win_pct'], 'A_Away_Win_pct': at['Away_Win_pct'], 'A_Last10_W': a_l10, 'A_Streak': a_streak, 'A_Rest_Days': a_rest, 'A_Star_Out': a_star_out, 'A_Role_Out': a_role_out, 'A_Pace': at['Pace'], 'A_TS_pct': at['TS_pct'], 'DIFF_Net_Rating': (ht['PPG']-ht['OPP_PPG']) - (at['PPG']-at['OPP_PPG'])
    }
    X_scaled_input = SCALER.transform(pd.DataFrame([features_dict])[FEATURES])
    proba = MODEL.predict_proba(X_scaled_input)[0]

    response = {
        "home_team": data.get('home_team'), "away_team": data.get('away_team'), "home_logo": get_nba_logo_url(data.get('home_team')), "away_logo": get_nba_logo_url(data.get('away_team')), "home_win_prob": float(proba[1]), "away_win_prob": float(proba[0]), "predicted_winner": "Home" if proba[1] > 0.5 else "Away", "is_historical": is_historical, "source": data.get('source', 'ESPN'),
        "stats": { "home": {k: float(v) for k, v in ht.items() if isinstance(v, (int, float, np.floating))}, "away": {k: float(v) for k, v in at.items() if isinstance(v, (int, float, np.floating))} },
        "rest": {"home_rest": h_rest, "away_rest": a_rest},
        "injury": { "home": {"star_out": bool(h_star_out), "role_out": h_role_out, "star_name": STAR_PLAYERS.get(data.get('home_team'), "當家主力")}, "away": {"star_out": bool(a_star_out), "role_out": a_role_out, "star_name": STAR_PLAYERS.get(data.get('away_team'), "當家主力")} }
    }
    response["stats"]["home"]["Last10_W"] = h_l10; response["stats"]["home"]["Streak"] = h_streak; response["stats"]["away"]["Last10_W"] = a_l10; response["stats"]["away"]["Streak"] = a_streak
    time.sleep(1.2)
    return jsonify(response)

@sports_app.route('/api/fb/predict', methods=['POST'])
def fb_predict():
    data = request.json
    sa = FB_DB.get(data['team_a'], {"league": "Unknown", "tier": "C級", "attack": 1.0, "defense": 1.6, "x_factor": 0.0, "star":"無"})
    sb = FB_DB.get(data['team_b'], {"league": "Unknown", "tier": "C級", "attack": 1.0, "defense": 1.6, "x_factor": 0.0, "star":"無"})
    # 傳入雙方球隊名稱以供場地敘述使用
    res = simulate_fb_match(sa, sb, data['venue'], data['inj_a'], data['inj_b'], data['team_a'], data['team_b'])
    return jsonify({ "team_a": data['team_a'], "team_b": data['team_b'], "logo_a": get_fb_logo_url(data['team_a'], True), "logo_b": get_fb_logo_url(data['team_b'], False), "stats_a": sa, "stats_b": sb, "res": res })

# ─────────────────────────────────────────
# 7. 啟動伺服器與 Cloudflare (5000埠，15秒防禦機制)
# ─────────────────────────────────────────
class SportsServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()
    def run(self): self.server.serve_forever()
    def shutdown(self): self.server.shutdown()

def start_sports_server():
    global sports_server
    if 'sports_server' in globals(): sports_server.shutdown(); time.sleep(1)
    sports_server = SportsServerThread(sports_app)
    sports_server.start()

    print("\n" + "="*60)
    print("🚀 體育版終極融合系統已啟動！(大滿貫全功能絕對完整版)")
    print("🌍 正在啟動【體育版】專屬通道 (預計 15 秒內完成)...")

    subprocess.run(["wget", "-q", "-nc", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"])
    subprocess.run(["chmod", "+x", "cloudflared-linux-amd64"])

    os.system("mkdir -p /tmp/sports_cf")
    subprocess.Popen(['./cloudflared-linux-amd64', 'tunnel', '--url', 'http://127.0.0.1:5000', '--logfile', '/tmp/sports_cf/sports.log', '--metrics', '127.0.0.1:40001'], stdout=open('sports_cf.log', 'w'), stderr=subprocess.STDOUT)

    url_match = None
    for _ in range(15):
        time.sleep(1)
        try:
            with open('sports_cf.log', 'r') as f:
                log_content = f.read()
                url_match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", log_content)
                if url_match:
                    break
        except:
            pass

    if url_match:
        print("✅ 成功！這是你的體育版公開網址：")
        print(f"👉 {url_match.group(0)}")
    else:
        print("❌ 網址獲取失敗。詳細日誌內容：")
        os.system("cat sports_cf.log")
    print("="*60 + "\n")

if __name__ == '__main__':
    get_official_schedule()
    start_sports_server()