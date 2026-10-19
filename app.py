import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="India vs West Indies T20I Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. PROJECT PATHS
# ============================================================

# Project paths — works locally and on Streamlit Cloud
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "Data"

CLEAN_DIR = DATA_DIR / "Clean"
PROCESSED_DIR = DATA_DIR / "Processed"

CLEAN_FILE = CLEAN_DIR / "t20i_ball_by_ball_clean.csv"


# ============================================================
# 3. COLOUR PALETTE
# ============================================================

NAVY = "#0B1F3A"
BLUE = "#3B8CFF"       # India / primary
MAROON = "#E0476B"     # West Indies
GOLD = "#F2A900"       # accent
TEAL = "#14A38B"
CORAL = "#E4572E"
SLATE = "#9FB0C8"
BG = "#0A1424"
HEAD = "#FFFFFF"
CARD = "#12233D"
BORDER = "#26456F"
TEXT = "#E6EDF7"

COLORWAY = [BLUE, MAROON, GOLD, TEAL, CORAL, "#7C5CFC", SLATE, "#2BB3E0"]


def team_color_map(teams):
    """India -> blue, West Indies -> maroon, anything else from the palette."""
    mapping, spare = {}, [GOLD, TEAL, CORAL, SLATE]
    for t in teams:
        name = str(t).lower()
        if "india" in name:
            mapping[t] = BLUE
        elif "west" in name or "windies" in name or name == "wi":
            mapping[t] = MAROON
        else:
            mapping[t] = spare.pop(0) if spare else SLATE
    return mapping


# ============================================================
# 4. STYLING
# ============================================================

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    [data-testid="stHeader"] {{ background-color: transparent; }}
    .main .block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }}

    h1, h2, h3, h4 {{ color: {HEAD} !important; }}
    .stApp p, .stApp label, .stApp span, .stApp li {{ color: {TEXT}; }}
    [data-testid="stCaptionContainer"], .stApp small {{ color: {SLATE} !important; }}
    [data-baseweb="select"] > div {{ background-color: {CARD}; color: {TEXT}; border-color: {BORDER}; }}
    [data-baseweb="select"] span {{ color: {TEXT} !important; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #050C18 0%, #0F2A4F 100%);
    }}
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{ color: #E8EEF8 !important; }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.15); }}
    [data-testid="stSidebar"] [role="radiogroup"] label {{
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 4px;
        transition: all .15s ease;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
        background: rgba(242,169,0,0.22);
        transform: translateX(3px);
    }}

    /* Hero banner */
    .hero {{
        background: linear-gradient(115deg, {NAVY} 0%, {BLUE} 55%, {MAROON} 100%);
        padding: 32px 36px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(11,31,58,0.18);
    }}
    .hero h1 {{ color: #fff !important; font-size: 2.3rem; margin: 0 0 6px 0; }}
    .hero p {{ color: #DCE8FA !important; margin: 2px 0; font-size: 1.02rem; }}
    .hero .tag {{
        display: inline-block; background: {GOLD}; color: {NAVY};
        padding: 3px 12px; border-radius: 20px; font-weight: 700;
        font-size: .8rem; margin-bottom: 10px;
    }}

    .page-title {{
        border-left: 6px solid {GOLD};
        padding-left: 14px; margin-bottom: 6px;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-top: 4px solid {BLUE};
        padding: 14px 16px;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }}
    [data-testid="stMetricLabel"] {{ color: {SLATE} !important; }}
    [data-testid="stMetricValue"] {{ color: {HEAD} !important; font-weight: 700; }}

    /* Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {CARD};
        border-radius: 14px;
        border-color: {BORDER};
    }}

    /* Buttons */
    .stButton button, .stDownloadButton button {{
        background: linear-gradient(135deg, {BLUE}, #174FA3);
        color: #fff; border: none; border-radius: 10px;
        font-weight: 600; padding: 0.55rem 1rem;
        transition: all .15s ease;
    }}
    .stButton button:hover, .stDownloadButton button:hover {{
        background: linear-gradient(135deg, {GOLD}, #E08E00);
        color: {NAVY}; transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(242,169,0,0.35);
    }}
    .stButton button:active {{ transform: translateY(0); }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        background: {CARD}; border: 1px solid {BORDER};
        border-radius: 10px 10px 0 0; padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {BLUE} !important; color: #fff !important;
    }}
    .stTabs [aria-selected="true"] p {{ color: #fff !important; }}

    .score-line {{
        display:flex; justify-content:space-between; align-items:center;
        padding: 6px 0; border-bottom: 1px dashed {BORDER}; font-size: 1rem;
    }}
    .score-line b {{ color: {HEAD}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 5. DATA LOADING
# ============================================================


@st.cache_data
def load_csv(file_path, modified_time):
    return pd.read_csv(file_path)


def get_csv(file_path):
    if not file_path.exists():
        return pd.DataFrame()
    try:
        return load_csv(str(file_path), file_path.stat().st_mtime)
    except Exception as exc:
        st.warning(f"Could not load {file_path.name}: {exc}")
        return pd.DataFrame()


BALL_BY_BALL = get_csv(CLEAN_FILE)
BATTING_LEADERBOARD = get_csv(PROCESSED_DIR / "final_batting_leaderboard.csv")
BOWLING_LEADERBOARD = get_csv(PROCESSED_DIR / "final_bowling_leaderboard.csv")

# Fallback: let the user upload the clean CSV if the path is unavailable
if BALL_BY_BALL.empty:
    uploaded = st.sidebar.file_uploader(
        "Upload ball-by-ball CSV", type="csv",
        help="Used when the project folder can't be found."
    )
    if uploaded is not None:
        BALL_BY_BALL = pd.read_csv(uploaded)

# ============================================================
# 6. PREPARE BALL-BY-BALL DATA
# ============================================================

df = pd.DataFrame()

if not BALL_BY_BALL.empty:
    df = BALL_BY_BALL.copy()

    numeric_columns = [
        "Runs Off The Bat", "Team Runs", "Extra", "Wide", "No Ball",
        "Leg Bye", "Bye", "Wicket", "4's", "6's", "Legal_Ball",
        "Bowler_Runs_Conceded",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["Wide", "No Ball", "Leg Bye", "Bye", "Extra", "Runs Off The Bat", "Wicket"]:
        if col not in df.columns:
            df[col] = 0

    if "Team Runs" not in df.columns:
        df["Team Runs"] = df["Runs Off The Bat"] + df["Extra"]

    if "Legal_Ball" not in df.columns:
        df["Legal_Ball"] = ((df["Wide"] == 0) & (df["No Ball"] == 0)).astype(int)

    if "Bowler_Runs_Conceded" not in df.columns:
        df["Bowler_Runs_Conceded"] = df["Runs Off The Bat"] + df["Wide"] + df["No Ball"]

    for col in ["MatchDay", "Innings"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Zero-based over notation: 0.1 = first delivery of over 1
    if "Ball Number" in df.columns:
        ball_text = df["Ball Number"].astype(str).str.strip()
        df["Over_Number"] = pd.to_numeric(
            ball_text.str.split(".").str[0], errors="coerce"
        ) + 1
        df["Phase"] = np.select(
            [
                df["Over_Number"].between(1, 6),
                df["Over_Number"].between(7, 15),
                df["Over_Number"].between(16, 20),
            ],
            ["Powerplay", "Middle Overs", "Death Overs"],
            default="Unknown",
        )

    df["Balls_Faced"] = (df["Wide"] == 0).astype(int)
    df["Dot_Ball"] = (
        (df["Runs Off The Bat"] == 0) & (df["Extra"] == 0) & (df["Wide"] == 0)
    ).astype(int)
    df["Bowler_Dot"] = (
        (df["Legal_Ball"] == 1) & (df["Bowler_Runs_Conceded"] == 0)
    ).astype(int)

PHASE_ORDER = ["Powerplay", "Middle Overs", "Death Overs"]
TEAMS = (
    sorted(df["Batting Team"].dropna().unique().tolist())
    if not df.empty and "Batting Team" in df.columns else []
)
TEAM_COLORS = team_color_map(TEAMS)

# ============================================================
# 7. HELPER FUNCTIONS
# ============================================================


def style_fig(fig, height=420, legend=True):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        colorway=COLORWAY,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=13),
        title=dict(font=dict(size=17, color=HEAD)),
        margin=dict(l=20, r=20, t=55, b=30),
        showlegend=legend,
        hoverlabel=dict(bgcolor=NAVY, font_color="white"),
    )
    axis_style = dict(
        gridcolor="#223B5E",
        zeroline=False,
        linecolor="#4A6285",
        tickfont=dict(color=TEXT, size=12),
        title_font=dict(color=TEXT, size=13),
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=TEXT, size=12),
            title_font=dict(color=TEXT),
            bgcolor="rgba(255,255,255,0)",
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color=TEXT), title_font=dict(color=TEXT)
        ),
    )
    return fig


def show(fig, key=None):
    st.plotly_chart(fig, use_container_width=True, key=key, theme=None)


def page_header(title, subtitle=""):
    st.markdown(f"<div class='page-title'><h1>{title}</h1></div>", unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


def show_table(data, columns=None, height=380):
    if data.empty:
        st.info("No data is available for this section yet.")
        return
    if columns:
        data = data[[c for c in columns if c in data.columns]]
    st.dataframe(data, use_container_width=True, hide_index=True, height=height)


def overs_text(legal_balls):
    return f"{int(legal_balls) // 6}.{int(legal_balls) % 6}"


def calculate_batter_table(data):
    if data.empty or "Striker" not in data.columns:
        return pd.DataFrame()
    r = data.groupby("Striker", as_index=False).agg(
        Runs=("Runs Off The Bat", "sum"),
        Balls=("Balls_Faced", "sum"),
        Fours=("4's", "sum"),
        Sixes=("6's", "sum"),
        Dot_Balls=("Dot_Ball", "sum"),
    )
    r["Strike_Rate"] = np.where(r["Balls"] > 0, (r["Runs"] * 100 / r["Balls"]).round(2), np.nan)
    r["Boundary_Runs"] = r["Fours"] * 4 + r["Sixes"] * 6
    r["Boundary_Pct"] = np.where(r["Runs"] > 0, (r["Boundary_Runs"] * 100 / r["Runs"]).round(2), 0)
    r["Dot_Ball_Pct"] = np.where(r["Balls"] > 0, (r["Dot_Balls"] * 100 / r["Balls"]).round(2), 0)
    return r.sort_values("Runs", ascending=False).reset_index(drop=True)


def calculate_bowler_table(data):
    if data.empty or "Bowler" not in data.columns:
        return pd.DataFrame()
    r = data.groupby("Bowler", as_index=False).agg(
        Legal_Balls=("Legal_Ball", "sum"),
        Runs_Conceded=("Bowler_Runs_Conceded", "sum"),
        Wicket_Events=("Wicket", "sum"),
        Dot_Balls=("Bowler_Dot", "sum"),
    )
    r["Overs"] = r["Legal_Balls"].apply(overs_text)
    r["Economy"] = (r["Runs_Conceded"] * 6 / r["Legal_Balls"].replace(0, np.nan)).round(2)
    r["Dot_Ball_Pct"] = (r["Dot_Balls"] * 100 / r["Legal_Balls"].replace(0, np.nan)).round(2)
    return r.sort_values(["Wicket_Events", "Economy"], ascending=[False, True]).reset_index(drop=True)


def innings_scores(data):
    if data.empty:
        return pd.DataFrame()
    g = data.groupby(["MatchDay", "Innings", "Batting Team"], as_index=False).agg(
        Runs=("Team Runs", "sum"),
        Wickets=("Wicket", "sum"),
        Legal_Balls=("Legal_Ball", "sum"),
    )
    g["Overs"] = g["Legal_Balls"].apply(overs_text)
    g["Score"] = g["Runs"].astype(int).astype(str) + "/" + g["Wickets"].astype(int).astype(str)
    g["Run_Rate"] = (g["Runs"] * 6 / g["Legal_Balls"].replace(0, np.nan)).round(2)
    return g


def go_to(page_name):
    st.session_state["page"] = page_name


def hbar(data, names, values, title, color=BLUE, top=10, ascending=True, fmt=None):
    d = data[[names, values]].dropna().sort_values(values, ascending=False).head(top)
    d = d.sort_values(values, ascending=True)
    fig = px.bar(d, x=values, y=names, orientation="h", title=title,
                 text=values, color_discrete_sequence=[color])
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_yaxes(title=None)
    return style_fig(fig, height=max(320, 34 * len(d) + 120), legend=False)


# ============================================================
# 8. SIDEBAR NAVIGATION
# ============================================================

PAGES = [
    "Home",
    "Match Centre",
    "Batter Analysis",
    "Bowler Analysis",
    "Phase Analysis",
    "Team Performance",
    "Player Comparison",
    "Leaderboards",
    "Data Explorer",
]
PAGE_ICONS = {
    "Home": "🏠", "Match Centre": "🏟️", "Batter Analysis": "🏏",
    "Bowler Analysis": "🎯", "Phase Analysis": "⏱️", "Team Performance": "📊",
    "Player Comparison": "⚔️", "Leaderboards": "🏆", "Data Explorer": "🗂️",
}

st.session_state.setdefault("page", "Home")
st.session_state.setdefault("match_selector", 1)

st.sidebar.title("🏏 T20I Analytics")
st.sidebar.caption("India vs West Indies Series")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate", PAGES, key="page",
    format_func=lambda p: f"{PAGE_ICONS[p]}  {p}",
)

st.sidebar.divider()
st.sidebar.caption(f"Ball-by-ball records: {len(df):,}")
if df.empty:
    st.sidebar.error("Clean data file not loaded.")
else:
    st.sidebar.success("Clean data loaded.")

# Global guard
if df.empty and page != "Home":
    page_header("Data unavailable")
    st.error("Ball-by-ball data could not be loaded. Check the path or upload the CSV in the sidebar.")
    st.stop()

# ============================================================
# 9. HOME
# ============================================================

if page == "Home":
    st.markdown(
        """
        <div class="hero">
            <span class="tag">T20I SERIES</span>
            <h1>🏏 India vs West Indies</h1>
            <p>Interactive cricket analytics dashboard</p>
            <p>Explore matches, batters, bowlers, phases and team performance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.error("Ball-by-ball data could not be loaded.")
        with st.expander("Data loading diagnostics"):
            st.write("Project directory:", str(PROJECT_DIR), "| exists:", PROJECT_DIR.exists())
            st.write("Clean directory:", str(CLEAN_DIR), "| exists:", CLEAN_DIR.exists())
            st.write("Clean CSV:", str(CLEAN_FILE), "| exists:", CLEAN_FILE.exists())
    else:
        scores = innings_scores(df)
        matches = df["MatchDay"].nunique()
        total_runs = int(df["Team Runs"].sum())
        sixes = int(df["6's"].sum()) if "6's" in df.columns else 0
        fours = int(df["4's"].sum()) if "4's" in df.columns else 0
        wkts = int(df["Wicket"].sum())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Matches", matches)
        c2.metric("Total Runs", f"{total_runs:,}")
        c3.metric("Fours", fours)
        c4.metric("Sixes", sixes)
        c5.metric("Wicket Events", wkts)

        st.subheader("Match Centre")
        cols = st.columns(4)
        for i, m in enumerate(sorted(df["MatchDay"].dropna().unique())):
            m = int(m)
            ms = scores[scores["MatchDay"] == m].sort_values("Innings")
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"#### Matchday {m}")
                    for _, r in ms.iterrows():
                        st.markdown(
                            f"<div class='score-line'><span>{r['Batting Team']}</span>"
                            f"<b>{r['Score']}</b></div>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"{r['Overs']} overs · RR {r['Run_Rate']}")
                    st.button(
                        f"Open Matchday {m}", key=f"home_match_{m}",
                        use_container_width=True,
                        on_click=lambda mm=m: (
                            st.session_state.update(match_selector=mm),
                            go_to("Match Centre"),
                        ),
                    )

        st.divider()
        left, right = st.columns([3, 2])

        with left:
            by_match = scores.groupby(["MatchDay", "Batting Team"], as_index=False).agg(Runs=("Runs", "sum"))
            fig = px.bar(
                by_match, x="MatchDay", y="Runs", color="Batting Team", barmode="group",
                title="Runs by Match and Team", text="Runs", color_discrete_map=TEAM_COLORS,
            )
            fig.update_traces(textposition="outside")
            fig.update_xaxes(dtick=1, title="Matchday")
            show(style_fig(fig), "home_bar")

        with right:
            dist = df[df["Legal_Ball"] == 1]["Runs Off The Bat"].value_counts().sort_index().reset_index()
            dist.columns = ["Runs", "Balls"]
            dist["Runs"] = dist["Runs"].astype(int).astype(str) + " run(s)"
            dist.loc[dist["Runs"] == "0 run(s)", "Runs"] = "Dot"
            fig = px.pie(dist, names="Runs", values="Balls", hole=0.55,
                         title="Where Runs Come From (Ball Outcomes)",
                         color_discrete_sequence=COLORWAY)
            fig.update_traces(textinfo="percent+label")
            show(style_fig(fig, legend=False), "home_donut")

        # Run rate trend
        fig = px.line(
            scores.sort_values("MatchDay"), x="MatchDay", y="Run_Rate",
            color="Batting Team", markers=True, title="Run Rate Trend Across the Series",
            color_discrete_map=TEAM_COLORS,
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        fig.update_xaxes(dtick=1, title="Matchday")
        fig.update_yaxes(title="Runs per over")
        show(style_fig(fig, 380), "home_line")

# ============================================================
# 10. MATCH CENTRE
# ============================================================

elif page == "Match Centre":
    page_header("🏟️ Match Centre", "Scorecards, worm charts and over-by-over progress.")

    match_ids = sorted(int(m) for m in df["MatchDay"].dropna().unique())
    if st.session_state["match_selector"] not in match_ids:
        st.session_state["match_selector"] = match_ids[0]

    match_day = st.radio(
        "Select match", match_ids, key="match_selector", horizontal=True,
        format_func=lambda m: f"Matchday {m}",
    )
    md = df[df["MatchDay"] == match_day].copy()
    scores = innings_scores(md).sort_values("Innings")

    cols = st.columns(len(scores) + 2)
    for i, (_, r) in enumerate(scores.iterrows()):
        cols[i].metric(f"{r['Batting Team']} (Inns {int(r['Innings'])})", r["Score"], f"{r['Overs']} ov · RR {r['Run_Rate']}", delta_color="off")
    cols[-2].metric("Fours", int(md["4's"].sum()))
    cols[-1].metric("Sixes", int(md["6's"].sum()))

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Progression", "🏏 Batting", "🎯 Bowling", "📋 Innings Summary"])

    with tab1:
        over_runs = md.groupby(["Innings", "Batting Team", "Over_Number"], as_index=False).agg(
            Runs=("Team Runs", "sum"), Wickets=("Wicket", "sum")
        )
        over_runs["Cumulative"] = over_runs.groupby(["Innings", "Batting Team"])["Runs"].cumsum()

        c1, c2 = st.columns(2)
        with c1:
            fig = px.line(over_runs, x="Over_Number", y="Cumulative", color="Batting Team",
                          markers=True, title="Worm Chart (Cumulative Runs)",
                          color_discrete_map=TEAM_COLORS)
            wk = over_runs[over_runs["Wickets"] > 0]
            for team, g in wk.groupby("Batting Team"):
                fig.add_trace(go.Scatter(
                    x=g["Over_Number"], y=g["Cumulative"], mode="markers",
                    marker=dict(symbol="x", size=13, color=CORAL, line=dict(width=2)),
                    name=f"{team} wicket(s)", showlegend=False,
                    hovertext=[f"{int(w)} wicket(s)" for w in g["Wickets"]],
                ))
            fig.update_xaxes(title="Over", dtick=1)
            fig.update_yaxes(title="Runs")
            show(style_fig(fig), f"worm_{match_day}")
        with c2:
            fig = px.bar(over_runs, x="Over_Number", y="Runs", color="Batting Team",
                         barmode="group", title="Runs Per Over", color_discrete_map=TEAM_COLORS)
            fig.update_xaxes(title="Over", dtick=1)
            show(style_fig(fig), f"rpo_{match_day}")

    with tab2:
        inns_opts = sorted(md["Innings"].dropna().unique())
        inns = st.selectbox("Select innings", inns_opts, key=f"inns_{match_day}")
        idata = md[md["Innings"] == inns]
        bt = calculate_batter_table(idata)
        show_table(bt, ["Striker", "Runs", "Balls", "Fours", "Sixes", "Strike_Rate", "Boundary_Pct", "Dot_Ball_Pct"])
        c1, c2 = st.columns(2)
        with c1:
            show(hbar(bt, "Striker", "Runs", "Runs by Batter", BLUE), f"mbat_{match_day}")
        with c2:
            fig = px.scatter(bt, x="Balls", y="Runs", size="Boundary_Runs", color="Strike_Rate",
                             hover_name="Striker", color_continuous_scale="YlOrRd",
                             title="Balls Faced vs Runs (size = boundary runs)")
            show(style_fig(fig, legend=False), f"mscat_{match_day}")

    with tab3:
        inns_b = st.selectbox("Select innings", inns_opts, key=f"binns_{match_day}")
        bdata = md[md["Innings"] == inns_b]
        bw = calculate_bowler_table(bdata)
        show_table(bw, ["Bowler", "Overs", "Runs_Conceded", "Wicket_Events", "Economy", "Dot_Ball_Pct"])
        c1, c2 = st.columns(2)
        with c1:
            d = bw.sort_values("Economy")
            fig = px.bar(d, x="Bowler", y="Economy", title="Bowler Economy", text="Economy",
                         color="Economy", color_continuous_scale="RdYlGn_r")
            fig.update_traces(textposition="outside")
            show(style_fig(fig, legend=False), f"meco_{match_day}")
        with c2:
            fig = px.bar(bw, x="Bowler", y=["Runs_Conceded", "Wicket_Events"], barmode="group",
                         title="Runs Conceded vs Wicket Events",
                         color_discrete_sequence=[CORAL, TEAL])
            show(style_fig(fig), f"mrw_{match_day}")

    with tab4:
        show_table(scores[["Innings", "Batting Team", "Score", "Overs", "Run_Rate"]])

# ============================================================
# 11. BATTER ANALYSIS
# ============================================================

elif page == "Batter Analysis":
    page_header("🏏 Batter Analysis", "Runs, strike rates, boundaries and dot balls.")

    f1, f2, f3 = st.columns(3)
    team = f1.selectbox("Batting team", ["All Teams"] + TEAMS)
    match_opts = ["All Matches"] + sorted(int(m) for m in df["MatchDay"].dropna().unique())
    match = f2.selectbox("Match", match_opts)
    phase = f3.selectbox("Phase", ["All Phases"] + PHASE_ORDER)

    bd = df.copy()
    if team != "All Teams":
        bd = bd[bd["Batting Team"] == team]
    if match != "All Matches":
        bd = bd[bd["MatchDay"] == match]
    if phase != "All Phases":
        bd = bd[bd["Phase"] == phase]

    bt = calculate_batter_table(bd)
    if bt.empty:
        st.warning("No data for the selected filters.")
        st.stop()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Batters", len(bt))
    c2.metric("Runs", int(bt["Runs"].sum()))
    c3.metric("Fours", int(bt["Fours"].sum()))
    c4.metric("Sixes", int(bt["Sixes"].sum()))
    c5.metric("Avg Strike Rate", f"{bt['Runs'].sum() * 100 / max(bt['Balls'].sum(), 1):.1f}")

    t1, t2, t3, t4 = st.tabs(["Overview", "Scatter & Distribution", "Boundaries", "Individual Batter"])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            show(hbar(bt, "Striker", "Runs", "Top 10 Run Scorers", BLUE), "bat_runs")
        with c2:
            q = bt[bt["Balls"] >= 6]
            show(hbar(q, "Striker", "Strike_Rate", "Top 10 Strike Rates (min 6 balls)", TEAL), "bat_sr")
        show_table(bt)

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter(bt, x="Runs", y="Strike_Rate", size="Balls", color="Boundary_Pct",
                             hover_name="Striker", color_continuous_scale="Viridis",
                             title="Runs vs Strike Rate (size = balls faced)")
            show(style_fig(fig, legend=False), "bat_scatter")
        with c2:
            fig = px.histogram(bt, x="Strike_Rate", nbins=12, title="Strike Rate Distribution",
                               color_discrete_sequence=[MAROON])
            fig.update_traces(marker_line_color="white", marker_line_width=1)
            show(style_fig(fig, legend=False), "bat_hist")
        fig = px.scatter(bt, x="Dot_Ball_Pct", y="Boundary_Pct", size="Runs", hover_name="Striker",
                         color="Strike_Rate", color_continuous_scale="Turbo",
                         title="Dot Ball % vs Boundary Run %")
        show(style_fig(fig, legend=False), "bat_scatter2")

    with t3:
        top = bt.sort_values("Runs", ascending=False).head(10)
        fig = px.bar(top, x="Striker", y=["Fours", "Sixes"], barmode="stack",
                     title="Fours and Sixes (Top 10 Run Scorers)",
                     color_discrete_sequence=[BLUE, GOLD])
        show(style_fig(fig), "bat_stack")
        c1, c2 = st.columns(2)
        with c1:
            show(hbar(bt, "Striker", "Boundary_Runs", "Boundary Runs", MAROON), "bat_bound")
        with c2:
            fig = px.treemap(bt[bt["Runs"] > 0], path=["Striker"], values="Runs",
                             color="Strike_Rate", color_continuous_scale="Blues",
                             title="Share of Runs (treemap)")
            show(style_fig(fig, legend=False), "bat_tree")

    with t4:
        who = st.selectbox("Choose a batter", sorted(bt["Striker"].dropna().unique()))
        pd_ = bd[bd["Striker"] == who]
        row = calculate_batter_table(pd_).iloc[0]
        a, b, c, d = st.columns(4)
        a.metric("Runs", int(row["Runs"]))
        b.metric("Balls", int(row["Balls"]))
        c.metric("Strike Rate", f"{row['Strike_Rate']:.2f}")
        d.metric("Boundary Runs", int(row["Boundary_Runs"]))

        c1, c2 = st.columns(2)
        with c1:
            pm = pd_.groupby("MatchDay", as_index=False).agg(Runs=("Runs Off The Bat", "sum"),
                                                              Balls=("Balls_Faced", "sum"))
            pm["SR"] = (pm["Runs"] * 100 / pm["Balls"].replace(0, np.nan)).round(1)
            fig = go.Figure()
            fig.add_bar(x=pm["MatchDay"], y=pm["Runs"], name="Runs", marker_color=BLUE)
            fig.add_scatter(x=pm["MatchDay"], y=pm["SR"], name="Strike Rate", yaxis="y2",
                            mode="lines+markers", line=dict(color=GOLD, width=3))
            fig.update_layout(title=f"{who}: Runs & Strike Rate by Match",
                              yaxis2=dict(overlaying="y", side="right", showgrid=False, title="SR"))
            fig.update_xaxes(dtick=1, title="Matchday")
            show(style_fig(fig), "bat_player_combo")
        with c2:
            pp = pd_.groupby("Phase", as_index=False).agg(Runs=("Runs Off The Bat", "sum"))
            pp["Phase"] = pd.Categorical(pp["Phase"], PHASE_ORDER, ordered=True)
            fig = px.pie(pp.sort_values("Phase"), names="Phase", values="Runs", hole=0.5,
                         title=f"{who}: Runs by Phase", color_discrete_sequence=[BLUE, TEAL, GOLD])
            show(style_fig(fig), "bat_player_pie")

# ============================================================
# 12. BOWLER ANALYSIS
# ============================================================

elif page == "Bowler Analysis":
    page_header("🎯 Bowler Analysis", "Economy, workload and recorded wicket events.")

    bw_data = df.copy()
    team = st.selectbox("Bowling team", ["All Teams"] + sorted(df["Bowling Team"].dropna().unique().tolist()))
    if team != "All Teams":
        bw_data = bw_data[bw_data["Bowling Team"] == team]

    bt = calculate_bowler_table(bw_data)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bowlers", len(bt))
    c2.metric("Runs Conceded", int(bt["Runs_Conceded"].sum()))
    c3.metric("Wicket Events", int(bt["Wicket_Events"].sum()))
    c4.metric("Overall Economy", f"{bt['Runs_Conceded'].sum() * 6 / max(bt['Legal_Balls'].sum(), 1):.2f}")

    t1, t2, t3 = st.tabs(["Overview", "Economy & Wickets", "Workload"])

    with t1:
        show_table(bt, ["Bowler", "Overs", "Runs_Conceded", "Wicket_Events", "Economy", "Dot_Ball_Pct"])
        c1, c2 = st.columns(2)
        with c1:
            q = bt[bt["Legal_Balls"] >= 6]
            d = q.sort_values("Economy").head(10).sort_values("Economy", ascending=False)
            fig = px.bar(d, x="Economy", y="Bowler", orientation="h", text="Economy",
                         title="Most Economical (min 1 over)", color="Economy",
                         color_continuous_scale="RdYlGn_r")
            fig.update_traces(textposition="outside")
            show(style_fig(fig, legend=False), "bowl_eco")
        with c2:
            show(hbar(bt, "Bowler", "Wicket_Events", "Wicket Events", MAROON), "bowl_wkt")

    with t2:
        fig = px.scatter(bt, x="Economy", y="Wicket_Events", size="Legal_Balls", color="Dot_Ball_Pct",
                         hover_name="Bowler", color_continuous_scale="Tealgrn",
                         title="Economy vs Wicket Events (size = balls bowled)")
        show(style_fig(fig, legend=False), "bowl_scatter")
        fig = px.box(bw_data[bw_data["Legal_Ball"] == 1], x="Bowling Team", y="Bowler_Runs_Conceded",
                     color="Bowling Team", color_discrete_map=TEAM_COLORS, points="outliers",
                     title="Distribution of Runs Conceded per Legal Ball")
        show(style_fig(fig, legend=False, height=360), "bowl_box")

    with t3:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(bt.sort_values("Legal_Balls", ascending=False).head(12),
                         x="Bowler", y="Legal_Balls", title="Legal Balls Bowled",
                         color_discrete_sequence=[BLUE])
            show(style_fig(fig, legend=False), "bowl_work")
        with c2:
            fig = px.bar(bt.sort_values("Dot_Ball_Pct", ascending=False).head(12),
                         x="Bowler", y="Dot_Ball_Pct", title="Dot Ball % (top 12)",
                         color_discrete_sequence=[TEAL])
            show(style_fig(fig, legend=False), "bowl_dot")

# ============================================================
# 13. PHASE ANALYSIS
# ============================================================

elif page == "Phase Analysis":
    page_header("⏱️ Phase Analysis", "Powerplay (1–6), Middle (7–15) and Death (16–20) overs.")

    if "Phase" not in df.columns:
        st.error("Phase information is unavailable (missing 'Ball Number').")
        st.stop()

    pdat = df[df["Phase"].isin(PHASE_ORDER)]

    bat_ph = pdat.groupby(["Batting Team", "Phase"], as_index=False).agg(
        Runs=("Team Runs", "sum"), Balls=("Legal_Ball", "sum"), Wickets=("Wicket", "sum"))
    bat_ph["Run_Rate"] = (bat_ph["Runs"] * 6 / bat_ph["Balls"].replace(0, np.nan)).round(2)

    bowl_ph = pdat.groupby(["Bowling Team", "Phase"], as_index=False).agg(
        Runs=("Bowler_Runs_Conceded", "sum"), Balls=("Legal_Ball", "sum"), Wickets=("Wicket", "sum"))
    bowl_ph["Economy"] = (bowl_ph["Runs"] * 6 / bowl_ph["Balls"].replace(0, np.nan)).round(2)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(bat_ph, x="Phase", y="Run_Rate", color="Batting Team", barmode="group",
                     category_orders={"Phase": PHASE_ORDER}, text="Run_Rate",
                     title="Batting Run Rate by Phase", color_discrete_map=TEAM_COLORS)
        fig.update_traces(textposition="outside")
        show(style_fig(fig), "ph_bat")
    with c2:
        fig = px.bar(bowl_ph, x="Phase", y="Economy", color="Bowling Team", barmode="group",
                     category_orders={"Phase": PHASE_ORDER}, text="Economy",
                     title="Bowling Economy by Phase", color_discrete_map=TEAM_COLORS)
        fig.update_traces(textposition="outside")
        show(style_fig(fig), "ph_bowl")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(bat_ph, x="Batting Team", y="Runs", color="Phase", barmode="stack",
                     category_orders={"Phase": PHASE_ORDER}, title="Runs Scored by Phase (stacked)",
                     color_discrete_sequence=[BLUE, TEAL, GOLD])
        show(style_fig(fig), "ph_stack")
    with c2:
        fig = px.line_polar(bat_ph, r="Run_Rate", theta="Phase", color="Batting Team",
                            line_close=True, color_discrete_map=TEAM_COLORS,
                            category_orders={"Phase": PHASE_ORDER},
                            title="Phase Run-Rate Profile")
        fig.update_traces(fill="toself", opacity=0.55)
        show(style_fig(fig), "ph_radar")

    st.subheader("Over-by-Over Heatmap")
    heat = pdat.pivot_table(index="Over_Number", columns="MatchDay", values="Team Runs", aggfunc="sum")
    fig = px.imshow(heat, aspect="auto", color_continuous_scale="YlOrRd",
                    labels=dict(x="Matchday", y="Over", color="Runs"),
                    title="Total Runs by Over and Matchday")
    show(style_fig(fig, height=520, legend=False), "ph_heat")

    st.subheader("Wickets by Phase")
    fig = px.bar(bowl_ph, x="Phase", y="Wickets", color="Bowling Team", barmode="group",
                 category_orders={"Phase": PHASE_ORDER}, color_discrete_map=TEAM_COLORS,
                 title="Wicket Events by Phase")
    show(style_fig(fig, height=360), "ph_wkts")

# ============================================================
# 14. TEAM PERFORMANCE
# ============================================================

elif page == "Team Performance":
    page_header("📊 Team Performance")

    scores = innings_scores(df)
    team_sum = df.groupby("Batting Team", as_index=False).agg(
        Runs=("Team Runs", "sum"),
        Runs_Off_Bat=("Runs Off The Bat", "sum"),
        Extras=("Extra", "sum"),
        Fours=("4's", "sum"),
        Sixes=("6's", "sum"),
        Wicket_Events=("Wicket", "sum"),
        Legal_Balls=("Legal_Ball", "sum"),
    )
    team_sum["Run_Rate"] = (team_sum["Runs"] * 6 / team_sum["Legal_Balls"].replace(0, np.nan)).round(2)

    bowl_sum = df.groupby("Bowling Team", as_index=False).agg(
        Legal_Balls=("Legal_Ball", "sum"),
        Runs_Conceded=("Bowler_Runs_Conceded", "sum"),
        Wicket_Events=("Wicket", "sum"),
    )
    bowl_sum["Economy"] = (bowl_sum["Runs_Conceded"] * 6 / bowl_sum["Legal_Balls"].replace(0, np.nan)).round(2)

    cols = st.columns(len(team_sum))
    for col, (_, r) in zip(cols, team_sum.iterrows()):
        col.metric(r["Batting Team"], f"{int(r['Runs'])} runs", f"RR {r['Run_Rate']}", delta_color="off")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(team_sum, x="Batting Team", y=["Runs_Off_Bat", "Extras"], barmode="stack",
                     title="Runs: Off the Bat vs Extras", color_discrete_sequence=[BLUE, GOLD])
        show(style_fig(fig), "team_stack")
    with c2:
        fig = px.bar(team_sum, x="Batting Team", y=["Fours", "Sixes"], barmode="group",
                     title="Boundaries Hit", color_discrete_sequence=[TEAL, MAROON])
        show(style_fig(fig), "team_bound")

    st.subheader("Match-by-Match Comparison")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(scores.sort_values("MatchDay"), x="MatchDay", y="Runs", color="Batting Team",
                      markers=True, title="Runs per Match", color_discrete_map=TEAM_COLORS)
        fig.update_traces(line=dict(width=3), marker=dict(size=10))
        fig.update_xaxes(dtick=1, title="Matchday")
        show(style_fig(fig), "team_line")
    with c2:
        fig = px.scatter(scores, x="Run_Rate", y="Wickets", color="Batting Team", size="Runs",
                         hover_data=["MatchDay", "Score"], color_discrete_map=TEAM_COLORS,
                         title="Run Rate vs Wickets Lost (size = runs)")
        show(style_fig(fig), "team_scatter")

    st.subheader("Bowling Comparison")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(bowl_sum, x="Bowling Team", y="Economy", color="Bowling Team", text="Economy",
                     color_discrete_map=TEAM_COLORS, title="Team Bowling Economy")
        fig.update_traces(textposition="outside")
        show(style_fig(fig, legend=False), "team_eco")
    with c2:
        fig = px.bar(bowl_sum, x="Bowling Team", y="Wicket_Events", color="Bowling Team", text="Wicket_Events",
                     color_discrete_map=TEAM_COLORS, title="Wicket Events Taken")
        fig.update_traces(textposition="outside")
        show(style_fig(fig, legend=False), "team_wkts")

    show_table(team_sum)
    st.caption("Wicket events are recorded events, not necessarily wickets credited to the bowler. "
               "Bowler runs conceded exclude byes and leg-byes.")

# ============================================================
# 15. PLAYER COMPARISON
# ============================================================

elif page == "Player Comparison":
    page_header("⚔️ Player Comparison", "Compare two batters or two bowlers head to head.")

    mode = st.radio("Compare", ["Batters", "Bowlers"], horizontal=True)

    if mode == "Batters":
        tbl = calculate_batter_table(df)
        names = tbl["Striker"].tolist()
        metrics = {"Runs": "Runs", "Strike Rate": "Strike_Rate", "Boundary %": "Boundary_Pct",
                   "Sixes": "Sixes", "Fours": "Fours", "Dot Ball % (inverse)": "Dot_Ball_Pct"}
        key_col = "Striker"
    else:
        tbl = calculate_bowler_table(df)
        names = tbl["Bowler"].tolist()
        tbl["Wickets"] = tbl["Wicket_Events"]
        tbl["Balls Bowled"] = tbl["Legal_Balls"]
        tbl["Economy (inverse)"] = tbl["Economy"]
        metrics = {"Wickets": "Wicket_Events", "Dot Ball %": "Dot_Ball_Pct",
                   "Balls Bowled": "Legal_Balls", "Economy (inverse)": "Economy",
                   "Runs Conceded (inverse)": "Runs_Conceded"}
        key_col = "Bowler"

    if len(names) < 2:
        st.warning("Not enough players to compare.")
        st.stop()

    c1, c2 = st.columns(2)
    p1 = c1.selectbox("Player 1", names, index=0)
    p2 = c2.selectbox("Player 2", names, index=1)

    inverse = [k for k in metrics if "inverse" in k]
    norm = {}
    for label, col in metrics.items():
        mx = tbl[col].max() or 1
        for p in (p1, p2):
            v = float(tbl.loc[tbl[key_col] == p, col].iloc[0])
            score = v / mx * 100
            if label in inverse:
                score = 100 - score
            norm.setdefault(p, []).append(round(score, 1))

    labels = list(metrics.keys())
    fig = go.Figure()
    for p, color in ((p1, BLUE), (p2, MAROON)):
        fig.add_trace(go.Scatterpolar(r=norm[p] + [norm[p][0]], theta=labels + [labels[0]],
                                      fill="toself", name=p, line=dict(color=color, width=3),
                                      opacity=0.6))
    fig.update_layout(title="Relative Strength Radar (0–100, higher is better)",
                      polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    show(style_fig(fig, height=480), "cmp_radar")

    cmp_tbl = tbl[tbl[key_col].isin([p1, p2])].set_index(key_col)[list(metrics.values())].T
    cmp_tbl.index = labels
    st.dataframe(cmp_tbl, use_container_width=True)

# ============================================================
# 16. LEADERBOARDS
# ============================================================

elif page == "Leaderboards":
    page_header("🏆 Series Leaderboards")

    live_bat = calculate_batter_table(df)
    live_bowl = calculate_bowler_table(df)
    bat_lb = BATTING_LEADERBOARD if not BATTING_LEADERBOARD.empty else live_bat
    bowl_lb = BOWLING_LEADERBOARD if not BOWLING_LEADERBOARD.empty else live_bowl

    tab1, tab2 = st.tabs(["🏏 Top Batters", "🎯 Top Bowlers"])

    with tab1:
        if "Runs" in bat_lb.columns:
            show_table(bat_lb.sort_values("Runs", ascending=False),
                       ["Striker", "Runs", "Balls_Faced", "Balls", "Strike_Rate", "Fours", "Sixes",
                        "Boundary_Runs", "Dot_Balls", "Dot_Ball_Percentage", "Dot_Ball_Pct"])
            if "Striker" in bat_lb.columns:
                show(hbar(bat_lb, "Striker", "Runs", "Top 10 Run Scorers", BLUE), "lb_bat")
        else:
            st.info("Batting leaderboard unavailable.")

    with tab2:
        if "Economy" in bowl_lb.columns:
            show_table(bowl_lb.sort_values("Wicket_Events", ascending=False),
                       ["Bowler", "Bowling Team", "Legal_Balls", "Overs", "Runs_Conceded",
                        "Wicket_Events", "Economy"])
            c1, c2 = st.columns(2)
            with c1:
                show(hbar(bowl_lb, "Bowler", "Wicket_Events", "Top Wicket Events", MAROON), "lb_bowl_w")
            with c2:
                d = bowl_lb.dropna(subset=["Economy"]).sort_values("Economy").head(10)
                fig = px.bar(d.sort_values("Economy", ascending=False), x="Economy", y="Bowler",
                             orientation="h", text="Economy", title="Most Economical Bowlers",
                             color_discrete_sequence=[TEAL])
                fig.update_traces(textposition="outside")
                show(style_fig(fig, legend=False, height=max(320, 34 * len(d) + 120)), "lb_bowl_e")
        else:
            st.info("Bowling leaderboard unavailable.")

# ============================================================
# 17. DATA EXPLORER
# ============================================================

elif page == "Data Explorer":
    page_header("🗂️ Data Explorer", "Filter the cleaned ball-by-ball data and download it.")

    d = df.copy()
    c1, c2, c3 = st.columns(3)
    sel_match = c1.multiselect("Matchday", sorted(int(m) for m in d["MatchDay"].dropna().unique()))
    sel_team = c2.multiselect("Batting team", TEAMS)
    sel_phase = c3.multiselect("Phase", PHASE_ORDER)

    if sel_match:
        d = d[d["MatchDay"].isin(sel_match)]
    if sel_team:
        d = d[d["Batting Team"].isin(sel_team)]
    if sel_phase:
        d = d[d["Phase"].isin(sel_phase)]

    st.caption(f"{len(d):,} rows")
    st.dataframe(d, use_container_width=True, hide_index=True, height=480)
    st.download_button("⬇️ Download filtered CSV", d.to_csv(index=False).encode("utf-8"),
                       file_name="t20i_filtered.csv", mime="text/csv")

# ============================================================
# 18. FOOTER
# ============================================================

st.divider()
st.caption("India vs West Indies T20I Analytics | Python • Pandas • Streamlit • Plotly")
