"""
╔══════════════════════════════════════════════════════════════════════╗
║   INDIA SDG INTELLIGENCE DASHBOARD                                   ║
║   SDG 1: No Poverty  |  SDG 2: Zero Hunger                          ║
║   TISS Mumbai — MSc Analytics 1st Year 2025                         ║
║   Student : G Chaitanya Venkatesh  |  M2025ANL013                   ║
║   Country : India                                                    ║
╚══════════════════════════════════════════════════════════════════════╝

HOW TO RUN
----------
1.  Install dependencies (one-time):
        pip install dash dash-bootstrap-components plotly pandas numpy reportlab

2.  Run from VS Code terminal:
        python india_sdg_dashboard.py

3.  Open browser at  http://127.0.0.1:8050
"""

# ── Imports ───────────────────────────────────────────────────────────
import os, re, datetime, threading, webbrowser
from io import BytesIO

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from xml.sax.saxutils import escape as xml_escape

# ══════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE  (Indian Tricolour — saffron, white, green + navy)
# ══════════════════════════════════════════════════════════════════════
C = dict(
    saffron   = "#FF6B00",
    saffronL  = "#FFE0C0",
    saffronD  = "#C24E00",
    green     = "#138808",
    greenL    = "#D4F0D4",
    greenD    = "#0A5C05",
    navy      = "#000080",
    navyL     = "#D0D4F0",
    gold      = "#DAA520",
    goldL     = "#FFF3CD",
    red       = "#C0392B",
    redL      = "#FADBD8",
    teal      = "#1A7F7A",
    tealL     = "#D1F2F0",
    purple    = "#7D3C98",
    purpleL   = "#E8DAEF",
    card      = "#FFFFFF",
    bg        = "#FDF9F5",
    bg2       = "#FFF5EA",
    muted     = "#6B6B6B",
    border    = "rgba(0,0,0,0.08)",
    glass     = "rgba(255,107,0,0.08)",
    red_t     = "rgba(192,57,43,0.12)",
    saffron_t = "rgba(255,107,0,0.12)",
    green_t   = "rgba(19,136,8,0.12)",
    navy_t    = "rgba(0,0,128,0.10)",
    gridline  = "rgba(0,0,128,0.06)",
)

# ── Shared Plotly layout ───────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor = "rgba(255,255,255,0.95)",
    plot_bgcolor  = "rgba(255,255,255,0.95)",
    font          = dict(family="Georgia, serif", color=C["navy"], size=12),
    title_font    = dict(family="Georgia, serif", size=15, color=C["navy"]),
    legend        = dict(bgcolor="rgba(255,255,255,0.85)", bordercolor=C["border"],
                         borderwidth=1, font=dict(size=11)),
    xaxis         = dict(gridcolor=C["gridline"], zerolinecolor=C["gridline"],
                         tickfont=dict(size=10), title_font=dict(size=11)),
    yaxis         = dict(gridcolor=C["gridline"], zerolinecolor=C["gridline"],
                         tickfont=dict(size=10), title_font=dict(size=11)),
    margin        = dict(l=55, r=25, t=65, b=55),
    hovermode     = "x unified",
)

# ══════════════════════════════════════════════════════════════════════
#  ALL DATA  (embedded — no external Excel files needed)
# ══════════════════════════════════════════════════════════════════════

# ── SDG 1: Poverty ────────────────────────────────────────────────────
poverty_headcount = pd.DataFrame([
    dict(year=1993, national=45.3, rural=50.1, urban=31.8),
    dict(year=2004, national=37.2, rural=41.8, urban=25.7),
    dict(year=2009, national=29.8, rural=33.8, urban=20.9),
    dict(year=2011, national=21.9, rural=25.7, urban=13.7),
    dict(year=2015, national=16.4, rural=19.2, urban=10.0),
    dict(year=2018, national=13.1, rural=15.8, urban=8.3),
    dict(year=2021, national=10.2, rural=12.5, urban=6.2),
    dict(year=2023, national=8.5,  rural=10.6, urban=5.2),
])

mpi_states = pd.DataFrame([
    dict(state="Bihar",       mpi=0.252, poor=51.9),
    dict(state="Jharkhand",   mpi=0.241, poor=42.2),
    dict(state="Uttar Pradesh",mpi=0.195,poor=37.7),
    dict(state="Madhya Pradesh",mpi=0.175,poor=36.6),
    dict(state="Meghalaya",   mpi=0.161, poor=32.7),
    dict(state="Odisha",      mpi=0.119, poor=29.4),
    dict(state="Rajasthan",   mpi=0.119, poor=25.1),
    dict(state="Chhattisgarh",mpi=0.107, poor=22.5),
    dict(state="Assam",       mpi=0.108, poor=21.4),
    dict(state="Karnataka",   mpi=0.060, poor=11.6),
    dict(state="Kerala",      mpi=0.011, poor=2.0),
    dict(state="Goa",         mpi=0.006, poor=1.0),
])

pmjdy = pd.DataFrame([
    dict(year=2015, accounts=147, balance=8000),
    dict(year=2017, accounts=287, balance=63500),
    dict(year=2019, accounts=363, balance=103000),
    dict(year=2021, accounts=417, balance=146000),
    dict(year=2023, accounts=500, balance=210000),
])

mgnregs = pd.DataFrame([
    dict(year=2014, person_days=166, hh_employed=4.78),
    dict(year=2016, person_days=235, hh_employed=5.07),
    dict(year=2018, person_days=268, hh_employed=5.11),
    dict(year=2020, person_days=389, hh_employed=7.55),
    dict(year=2022, person_days=264, hh_employed=5.72),
    dict(year=2024, person_days=256, hh_employed=5.49),
])

# ── SDG 2: Hunger & Nutrition ─────────────────────────────────────────
hunger_trends = pd.DataFrame([
    dict(year=2000, stunting=54.2, wasting=19.7, underweight=47.0, anemia=74.3),
    dict(year=2005, stunting=48.0, wasting=20.0, underweight=42.5, anemia=69.5),
    dict(year=2015, stunting=38.4, wasting=21.0, underweight=35.7, anemia=58.4),
    dict(year=2019, stunting=35.5, wasting=17.3, underweight=32.1, anemia=59.1),
    dict(year=2021, stunting=35.5, wasting=19.3, underweight=32.1, anemia=67.1),
    dict(year=2023, stunting=33.1, wasting=17.0, underweight=30.0, anemia=65.0),
])

nfhs_nutrition = pd.DataFrame([
    dict(indicator="Stunting (children <5)",   nfhs4=38.4, nfhs5=35.5, target2030=25.0),
    dict(indicator="Wasting (<5)",             nfhs4=21.0, nfhs5=19.3, target2030=5.0),
    dict(indicator="Underweight (<5)",         nfhs4=35.8, nfhs5=32.1, target2030=20.0),
    dict(indicator="Anaemia (women 15-49)",    nfhs4=53.1, nfhs5=57.0, target2030=30.0),
    dict(indicator="Anaemia (children 6-59m)", nfhs4=58.6, nfhs5=67.1, target2030=25.0),
    dict(indicator="Low birth weight",         nfhs4=18.2, nfhs5=16.0, target2030=10.0),
])

food_insecurity = pd.DataFrame([
    dict(year=2014, severe=15.2, moderate=24.8),
    dict(year=2016, severe=14.8, moderate=24.5),
    dict(year=2018, severe=14.5, moderate=24.1),
    dict(year=2020, severe=16.3, moderate=26.4),
    dict(year=2022, severe=15.1, moderate=25.6),
    dict(year=2023, severe=14.0, moderate=24.0),
])

ghi_global = pd.DataFrame([
    dict(country="India",     score=28.7, rank=111, category="Serious"),
    dict(country="Pakistan",  score=26.6, rank=102, category="Serious"),
    dict(country="Nepal",     score=23.1, rank=93,  category="Serious"),
    dict(country="Bangladesh",score=19.1, rank=84,  category="Moderate"),
    dict(country="World Avg", score=18.3, rank=None, category="Moderate"),
    dict(country="Sri Lanka", score=13.7, rank=56,  category="Moderate"),
    dict(country="Brazil",    score=5.3,  rank=11,  category="Low"),
    dict(country="China",     score=5.0,  rank=9,   category="Low"),
])

# ── Comparator table ──────────────────────────────────────────────────
comparator_table = pd.DataFrame([
    dict(country="India 🇮🇳",       ext_poverty=2.3,  stunting=35.5, ghi=28.7, category="Serious",  highlight=True),
    dict(country="China 🇨🇳",       ext_poverty=0.1,  stunting=4.8,  ghi=5.0,  category="Low",       highlight=False),
    dict(country="Brazil 🇧🇷",      ext_poverty=4.6,  stunting=6.7,  ghi=5.3,  category="Low",       highlight=False),
    dict(country="Bangladesh 🇧🇩",  ext_poverty=5.0,  stunting=28.9, ghi=19.1, category="Moderate",  highlight=False),
    dict(country="Nepal 🇳🇵",       ext_poverty=3.6,  stunting=31.4, ghi=23.1, category="Serious",   highlight=False),
    dict(country="Pakistan 🇵🇰",    ext_poverty=4.4,  stunting=40.2, ghi=26.6, category="Serious",   highlight=False),
    dict(country="Sri Lanka 🇱🇰",   ext_poverty=0.7,  stunting=17.3, ghi=13.7, category="Moderate",  highlight=False),
])

# ── SDG Progress trackers ─────────────────────────────────────────────
sdg1_progress = [
    dict(label="Eliminate extreme poverty (<$2.15)", current=2.3,  target=0,   pct=88),
    dict(label="Halve national poverty rate",        current=8.5,  target=5.5, pct=72),
    dict(label="Universal social protection",        current=24.4, target=100, pct=24),
    dict(label="PMAY housing target",               current=2.95, target=4.0, pct=74),
    dict(label="MGNREGS person-days target",         current=256,  target=300, pct=85),
]

sdg2_progress = [
    dict(label="End stunting in children",           current=35.5, target=25,  pct=45),
    dict(label="End wasting in children",            current=19.3, target=5,   pct=22),
    dict(label="Eliminate anaemia (women)",          current=57.0, target=30,  pct=35),
    dict(label="Universal PDS coverage",             current=80,   target=100, pct=80),
    dict(label="Women land rights (farmers)",        current=12.8, target=50,  pct=26),
    dict(label="Agri R&D spending (% GDP)",          current=0.36, target=1.0, pct=36),
]

# ── Radar / readiness data ────────────────────────────────────────────
radar_categories  = ["Education", "Healthcare", "Infrastructure",
                     "Social Protection", "Food Access", "Digital Access"]
radar_sdg1_scores = [72, 60, 58, 45, 68, 55]
radar_sdg2_scores = [65, 55, 62, 50, 48, 58]

# ── Govt schemes ──────────────────────────────────────────────────────
govt_schemes = [
    dict(scheme="PM Garib Kalyan Anna Yojana", beneficiaries="80 Cr people",
         budget="₹2,00,000 Cr/yr", sdg="SDG 2", impact="High"),
    dict(scheme="MGNREGS", beneficiaries="15 Cr households",
         budget="₹73,000 Cr/yr",   sdg="SDG 1", impact="High"),
    dict(scheme="PM-KISAN", beneficiaries="11 Cr farmers",
         budget="₹60,000 Cr/yr",   sdg="SDG 1+2", impact="High"),
    dict(scheme="PM Jan Dhan Yojana", beneficiaries="50 Cr accounts",
         budget="Financial Inclusion", sdg="SDG 1", impact="High"),
    dict(scheme="Ayushman Bharat", beneficiaries="50 Cr people",
         budget="₹6,400 Cr/yr",    sdg="SDG 1+2", impact="High"),
    dict(scheme="PMAY (Urban + Rural)", beneficiaries="2.95 Cr houses built",
         budget="₹79,000 Cr/yr",   sdg="SDG 1", impact="Medium"),
    dict(scheme="Poshan Abhiyaan", beneficiaries="10 Cr children + women",
         budget="₹3,700 Cr/yr",    sdg="SDG 2", impact="Medium"),
    dict(scheme="National Food Security Act", beneficiaries="81.35 Cr people",
         budget="Legal entitlement", sdg="SDG 2", impact="High"),
]

# ══════════════════════════════════════════════════════════════════════
#  REUSABLE UI HELPERS
# ══════════════════════════════════════════════════════════════════════

def kpi_card(icon, label, value, sub="", color=None):
    color = color or C["saffron"]
    return html.Div([
        html.Div(icon, style={"fontSize": "32px", "marginBottom": "8px"}),
        html.Div(value, style={"fontSize": "22px", "fontWeight": "900",
                               "fontFamily": "Georgia, serif", "color": color}),
        html.Div(label, style={"fontSize": "11px", "color": "#2C3E50",
                               "textTransform": "uppercase", "letterSpacing": "1.2px",
                               "marginTop": "5px", "fontWeight": "700"}),
        html.Div(sub, style={"fontSize": "11px", "color": C["muted"],
                             "marginTop": "4px", "fontStyle": "italic"}) if sub else None,
    ], style={
        "background": f"linear-gradient(135deg,{C['card']},{C['bg2']})",
        "borderRadius": "16px", "padding": "20px 14px",
        "borderTop": f"4px solid {color}",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.08)",
        "textAlign": "center", "flex": "1", "minWidth": "145px",
        "border": f"1px solid {C['border']}",
    }, className="kpi-hover dashboard-panel")


def section_title(text, sub="", color=None):
    color = color or C["saffron"]
    return html.Div([
        html.Div(style={
            "width": "5px", "height": "42px",
            "background": f"linear-gradient(180deg,{color},{C['navy']})",
            "borderRadius": "3px", "marginRight": "14px", "flexShrink": "0",
        }),
        html.Div([
            html.Div(text, style={
                "fontSize": "22px", "fontWeight": "900",
                "fontFamily": "Georgia, serif", "color": C["navy"],
            }),
            html.Div(sub, style={"fontSize": "12px", "color": C["muted"],
                                 "marginTop": "5px", "fontStyle": "italic"}) if sub else None,
        ]),
    ], style={"display": "flex", "alignItems": "center",
              "marginBottom": "22px", "marginTop": "30px"})


def graph_card(graph_id, title="", height=380, footer=""):
    return html.Div([
        html.Div(title, style={
            "fontSize": "12px", "fontWeight": "800", "color": C["navy"],
            "textTransform": "uppercase", "letterSpacing": "1.8px",
            "marginBottom": "14px", "fontFamily": "Georgia,serif",
            "borderBottom": f"2px solid {C['saffron']}", "paddingBottom": "8px",
        }) if title else None,
        dcc.Graph(id=graph_id, style={"height": f"{height}px"},
                  config={"displayModeBar": True,
                          "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                          "displaylogo": False}),
        html.Div(footer, style={"fontSize": "10px", "color": C["muted"],
                                "marginTop": "8px", "textAlign": "right",
                                "fontStyle": "italic"}) if footer else None,
    ], style={
        "background": f"linear-gradient(135deg,{C['card']},{C['bg2']})",
        "borderRadius": "16px", "padding": "22px",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.08)",
        "marginBottom": "22px", "border": f"1px solid {C['border']}",
    }, className="graph-card dashboard-panel")


def status_badge(status):
    cfg = {
        "on-track":  (C["greenL"],  C["green"]),
        "progress":  (C["goldL"],   C["gold"]),
        "lagging":   (C["redL"],    C["red"]),
    }
    bg, fg = cfg.get(status, (C["navyL"], C["navy"]))
    label  = {"on-track": "On Track", "progress": "In Progress", "lagging": "Lagging"}.get(status, status)
    return html.Span(label, style={
        "background": bg, "color": fg,
        "padding": "2px 10px", "borderRadius": "12px",
        "fontSize": "11px", "fontWeight": "700",
    })


def progress_row(label, current, target, pct, color=None):
    color = color or (C["green"] if pct >= 70 else C["saffron"] if pct >= 40 else C["red"])
    return html.Div([
        html.Div([
            html.Span(label, style={"color": C["navy"], "fontWeight": "600", "fontSize": "12px"}),
            html.Span(f"{current} → {target} (target)",
                      style={"color": C["muted"], "fontSize": "11px", "float": "right"}),
        ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "5px"}),
        html.Div(html.Div(style={
            "width": f"{pct}%", "height": "100%",
            "background": color, "borderRadius": "4px",
        }), style={"background": C["bg"], "borderRadius": "4px",
                   "height": "8px", "overflow": "hidden"}),
        html.Div(f"{pct}% progress toward 2030 target",
                 style={"fontSize": "10px", "color": C["muted"], "marginTop": "3px"}),
    ], style={"marginBottom": "14px"})


def info_box(title, body, color=None):
    color = color or C["saffron"]
    return html.Div([
        html.Div(title, style={"fontFamily": "Georgia,serif", "fontSize": "13px",
                               "color": color, "marginBottom": "10px", "fontWeight": "700",
                               "borderBottom": f"1px solid {C['border']}", "paddingBottom": "7px"}),
        html.P(body, style={"color": C["navy"], "fontFamily": "Georgia,serif",
                            "fontSize": "13px", "lineHeight": "1.85", "margin": 0}),
    ], style={
        "background": C["card"], "borderRadius": "14px", "padding": "20px",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.07)", "marginTop": "20px",
        "borderLeft": f"4px solid {color}", "border": f"1px solid {C['border']}",
    }, className="dashboard-panel")


# ══════════════════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ══════════════════════════════════════════════════════════════════════
splash = html.Div(id="splash-screen", children=[
    html.Div(id="splash-inner", children=[
        html.Div("🇮🇳", style={"fontSize": "72px", "marginBottom": "10px", "textAlign": "center"}),
        html.H1("INDIA SDG", style={
            "fontFamily": "Georgia, serif",
            "fontSize": "clamp(40px,7vw,80px)", "fontWeight": "900",
            "background": f"linear-gradient(135deg,{C['saffron']},#FFD700,{C['green']})",
            "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent",
            "letterSpacing": "0.15em", "margin": "0", "lineHeight": "1",
            "textAlign": "center",
        }),
        html.Div("POVERTY & HUNGER DASHBOARD", style={
            "fontFamily": "Georgia, serif", "fontSize": "clamp(9px,1.5vw,15px)",
            "letterSpacing": "0.3em", "color": "rgba(255,255,255,0.65)",
            "textAlign": "center", "marginTop": "8px", "textTransform": "uppercase",
        }),
        html.Hr(style={"borderColor": C["saffron"], "width": "55%",
                        "margin": "18px auto", "opacity": "0.6"}),
        html.Div("SDG 1: NO POVERTY  ·  SDG 2: ZERO HUNGER", style={
            "color": "rgba(255,255,255,0.45)", "fontSize": "11px",
            "letterSpacing": "2px", "textAlign": "center", "marginBottom": "28px",
        }),
        html.Button([html.Span("✦ EXPLORE DASHBOARD ✦")],
                    id="enter-btn", style={
            "background": f"linear-gradient(135deg,{C['saffron']},{C['saffronD']})",
            "border": "none", "borderRadius": "50px", "color": "white",
            "fontFamily": "Georgia, serif", "fontSize": "13px", "letterSpacing": "3px",
            "padding": "15px 44px", "cursor": "pointer",
            "fontWeight": "700", "textTransform": "uppercase",
            "display": "block", "margin": "0 auto",
        }),
        html.Div("G Chaitanya Venkatesh  |  M2025ANL013  |  MSc Analytics  |  TISS Mumbai",
                 style={"color": "rgba(255,255,255,0.3)", "fontSize": "10px",
                        "letterSpacing": "1.5px", "textAlign": "center", "marginTop": "24px"}),
    ], style={"position": "relative", "zIndex": "10",
              "maxWidth": "600px", "width": "90%", "padding": "20px"}),
], style={
    "position": "fixed", "top": "0", "left": "0",
    "width": "100vw", "height": "100vh",
    "background": f"linear-gradient(135deg,{C['navy']} 0%,#000040 45%,#1a0800 100%)",
    "display": "flex", "flexDirection": "column",
    "alignItems": "center", "justifyContent": "center",
    "zIndex": "9999", "overflow": "hidden",
    "transition": "opacity .8s, transform .8s",
})

# ══════════════════════════════════════════════════════════════════════
#  NAVIGATION BAR
# ══════════════════════════════════════════════════════════════════════
TABS_CONFIG = [
    ("🇮🇳", "Overview",         "tab-overview"),
    ("💰",  "SDG 1: Poverty",   "tab-sdg1"),
    ("🌾",  "SDG 2: Hunger",    "tab-sdg2"),
    ("🌍",  "Global Compare",   "tab-compare"),
    ("⚠️",  "Challenges",       "tab-challenges"),
    ("📋",  "Govt. Schemes",    "tab-schemes"),
    ("📄",  "Report",           "tab-report"),
    ("🔬",  "Methodology",      "tab-methodology"),
    ("👤",  "About",            "tab-about"),
]

navbar = html.Div([
    # Top strip
    html.Div([
        html.Div([
            html.Span("🇮🇳", style={"fontSize": "20px"}),
            html.Div([
                html.Span("INDIA ", style={"color": C["saffron"], "fontWeight": "900"}),
                html.Span("SDG DASHBOARD", style={"color": C["navy"]}),
            ], style={"fontFamily": "Georgia,serif", "fontSize": "14px",
                      "letterSpacing": "2px", "marginLeft": "10px"}),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div("G Chaitanya Venkatesh  |  M2025ANL013  |  MSc Analytics  |  TISS Mumbai",
                 style={"fontSize": "9px", "color": C["muted"], "letterSpacing": "1.2px"}),
    ], style={
        "padding": "9px 22px", "borderBottom": f"1px solid {C['border']}",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "background": f"linear-gradient(90deg,{C['bg2']},{C['card']})",
    }),
    # Tab strip
    html.Div([
        html.Div([
            html.Button([
                html.Span(icon, style={"fontSize": "15px", "display": "block"}),
                html.Span(label, style={"fontSize": "9px", "letterSpacing": "0.8px",
                                        "marginTop": "2px", "display": "block"}),
            ], id=f"nav-{tab_id}", className="nav-tab",
               **{"data-tab": tab_id},
               style={
                "background": "transparent", "border": "none", "color": C["muted"],
                "padding": "9px 14px", "cursor": "pointer", "borderRadius": "8px",
                "fontFamily": "Georgia, serif", "textTransform": "uppercase",
                "transition": "all .2s", "whiteSpace": "nowrap",
               })
            for icon, label, tab_id in TABS_CONFIG
        ], style={"display": "flex", "gap": "4px", "flexWrap": "wrap",
                  "justifyContent": "center", "padding": "7px 14px"}),
    ], style={"background": C["bg2"], "borderBottom": f"2px solid {C['saffron']}"}),
], style={
    "position": "sticky", "top": "0", "zIndex": "1000",
    "boxShadow": "0 4px 24px rgba(0,0,0,0.12)",
})

# ══════════════════════════════════════════════════════════════════════
#  TAB CONTENT BUILDERS
# ══════════════════════════════════════════════════════════════════════

# ── TAB 0: OVERVIEW ──────────────────────────────────────────────────
def build_overview():
    kpis = html.Div([
        kpi_card("📉", "Extreme Poor (<$2.15/day)", "2.3%", "Down from 22.5% (2011)", C["green"]),
        kpi_card("🏠", "National Poverty Line",     "8.5%", "~115 Million people",    C["saffron"]),
        kpi_card("🌾", "GHI Score 2023",            "28.7", "Rank 111 / 125 — Serious", C["red"]),
        kpi_card("👶", "Children Stunted",          "35.5%","Under-5 · NFHS-5 (2021)", C["red"]),
        kpi_card("🍚", "Food Insecure",             "~74 Cr","Moderate or severe (FAO 2023)", C["saffron"]),
        kpi_card("💰", "PM-KISAN Beneficiaries",    "11 Cr", "Farmers getting ₹6,000/yr", C["navy"]),
    ], style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"})

    # Country profile card
    profile = html.Div([
        section_title("🇮🇳 Country Profile",
                      "India — World's most populous nation | 1.44 Bn people | 5th largest economy"),
        html.Div([
            html.Div([
                html.P("""India is home to 1.44 billion people and is simultaneously the world's 5th largest 
                economy and a country confronting deep structural poverty and hunger. Despite remarkable 
                economic growth averaging 6–7% annually over two decades, the benefits have not reached 
                all citizens equally. India accounts for the largest share of the world's poor and hungry 
                in absolute numbers, making SDG 1 and SDG 2 its most critical sustainability challenges.""",
                       style={"color": C["navy"], "lineHeight": "1.8",
                              "fontFamily": "Georgia,serif", "fontSize": "13px"}),
                html.P("""The country has made extraordinary progress: lifting 415 million people out of 
                multidimensional poverty between 2005 and 2021 (UNDP/OPHI 2023) — the fastest reduction 
                ever recorded globally. Yet India ranks 111th out of 125 countries on the Global Hunger 
                Index 2023 with a 'Serious' rating — a stark paradox for a net food exporter that feeds 
                the world while millions of its own children go to bed malnourished.""",
                       style={"color": C["navy"], "lineHeight": "1.8",
                              "fontFamily": "Georgia,serif", "fontSize": "13px", "marginTop": "10px"}),
                html.Div([
                    *[html.Div([
                        html.Span(f"{k}: ", style={"color": C["muted"], "fontWeight": "600"}),
                        html.Span(v, style={"color": C["navy"]}),
                    ], style={"marginBottom": "5px", "fontSize": "13px"})
                    for k, v in [
                        ("Capital", "New Delhi"),
                        ("Population", "1.44 Billion (2024)"),
                        ("GDP (nominal)", "$3.73 Trillion (5th globally)"),
                        ("HDI Score", "0.644 — Medium Human Development (2022)"),
                        ("Official poverty line", "₹1,059.42/month rural · ₹1,286.05/month urban"),
                        ("Major languages", "Hindi, English + 21 other scheduled languages"),
                    ]],
                ], style={"background": C["bg2"], "borderRadius": "10px",
                          "padding": "14px 18px", "marginTop": "14px"}),
            ], style={"flex": "1", "minWidth": "280px"}),
            html.Div([
                html.Div("⚡", style={"fontSize": "60px", "textAlign": "center", "marginBottom": "6px"}),
                html.Div("Quick Facts", style={"fontFamily": "Georgia,serif", "fontSize": "11px",
                                              "color": C["muted"], "textAlign": "center",
                                              "letterSpacing": "2px", "marginBottom": "12px"}),
                *[html.Div([
                    html.Span(icon + " ", style={"fontSize": "15px"}),
                    html.Span(fact, style={"color": C["navy"], "fontSize": "12px",
                                          "fontFamily": "Georgia,serif"}),
                ], style={"marginBottom": "9px", "display": "flex", "alignItems": "flex-start"})
                  for icon, fact in [
                      ("🌾", "2nd largest agricultural producer globally"),
                      ("🚜", "58% of workforce employed in agriculture"),
                      ("👶", "26.7 million babies born every year — highest globally"),
                      ("🍽️", "Net food exporter — yet 200 Mn undernourished"),
                      ("☀️", "2nd largest solar power capacity in Asia (2024)"),
                      ("📱", "750 Mn+ internet users — digital divide persists"),
                      ("🏗️", "Largest public works programme (MGNREGS) globally"),
                      ("🩺", "Only 2.1% of GDP on public healthcare (WHO: 5%)"),
                  ]],
            ], style={"background": C["bg2"], "borderRadius": "14px", "padding": "18px",
                      "minWidth": "240px", "flex": "0 0 auto"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "20px"},
       className="dashboard-panel")

    # Data sources table
    sources = html.Div([
        section_title("📚 Data Sources & Variables",
                      "All datasets used in this dashboard — APA 7th edition citations"),
        dash_table.DataTable(
            data=[
                {"Variable": "National Poverty Headcount (%)", "Source": "World Bank PIP / NSSO HCES 2022-23",
                 "Coverage": "India 1993–2023", "Format": "CSV"},
                {"Variable": "Multidimensional Poverty Index", "Source": "NITI Aayog National MPI 2023",
                 "Coverage": "36 States & UTs", "Format": "PDF/Excel"},
                {"Variable": "Child Malnutrition (Stunting/Wasting)", "Source": "NFHS-5 (2019-21), NFHS-4",
                 "Coverage": "India — all states", "Format": "PDF/Excel"},
                {"Variable": "Global Hunger Index Score", "Source": "GHI 2023 (Welthungerhilfe)",
                 "Coverage": "125 countries", "Format": "Excel"},
                {"Variable": "Food Insecurity (FIES)", "Source": "FAO — SOFI 2023",
                 "Coverage": "India 2014–2023", "Format": "CSV/Excel"},
                {"Variable": "PM Jan Dhan Yojana Data", "Source": "Ministry of Finance PMJDY Portal",
                 "Coverage": "India 2015–2023", "Format": "Portal/PDF"},
                {"Variable": "MGNREGS Employment Data", "Source": "Ministry of Rural Development MIS",
                 "Coverage": "India FY2014–2024", "Format": "Portal"},
                {"Variable": "SDG India Index Scores", "Source": "NITI Aayog SDG India Index 2023-24",
                 "Coverage": "All 17 SDGs × 36 States", "Format": "PDF/Excel"},
                {"Variable": "SDG Indicator Database", "Source": "UN Statistics Division SDG Portal",
                 "Coverage": "Global SDG indicators", "Format": "API/CSV"},
            ],
            columns=[{"name": c, "id": c} for c in ["Variable", "Source", "Coverage", "Format"]],
            style_table={"overflowX": "auto", "borderRadius": "10px", "overflow": "hidden"},
            style_header={"backgroundColor": C["saffron"], "color": "white",
                          "fontWeight": "700", "fontFamily": "Georgia,serif",
                          "fontSize": "11px", "letterSpacing": "1.5px",
                          "padding": "11px 14px", "textTransform": "uppercase"},
            style_cell={"backgroundColor": "white", "color": C["navy"],
                        "fontFamily": "Georgia,serif", "fontSize": "12px",
                        "border": f"1px solid {C['border']}", "padding": "10px 14px",
                        "whiteSpace": "normal", "textAlign": "left"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": C["bg"]},
            ],
        ),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}"},
       className="dashboard-panel")

    return html.Div([kpis, profile, sources])


# ── TAB 1: SDG 1 — NO POVERTY ─────────────────────────────────────────
def build_sdg1():
    kpis = html.Div([
        kpi_card("📉", "Extreme Poor",          "2.3%",    "<$2.15/day (2023)", C["green"]),
        kpi_card("🏠", "National Poverty Line", "8.5%",    "~115 Mn people", C["saffron"]),
        kpi_card("🔵", "MPI Poor (2021)",       "16.4%",   "Down from 55.1% (2005-06)", C["navy"]),
        kpi_card("🌱", "Social Protection",     "24.4%",   "Coverage gap is critical", C["red"]),
        kpi_card("🏗️", "PMAY Houses",           "2.95 Cr", "Completed under rural scheme", C["teal"]),
        kpi_card("💳", "Jan Dhan Accounts",     "50 Cr",   "₹2.1 Lakh Cr deposits", C["navy"]),
    ], style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"})

    # Indicator table
    indicator_table = html.Div([
        section_title("📊 SDG 1 — Key Indicator Progress (2023)",
                      "Source: UN SDG Portal, World Bank, NITI Aayog MPI 2023", C["saffron"]),
        dash_table.DataTable(
            data=[
                {"Indicator": "Extreme poverty (<$2.15/day)", "Current": "2.3%", "Target (2030)": "0%", "Status": "On Track"},
                {"Indicator": "Below national poverty line",  "Current": "8.5%", "Target (2030)": "0%", "Status": "In Progress"},
                {"Indicator": "Social protection coverage",   "Current": "24.4%","Target (2030)": "100%","Status": "Lagging"},
                {"Indicator": "PM-KISAN beneficiaries",      "Current": "11 Cr", "Target (2030)": "14 Cr","Status": "In Progress"},
                {"Indicator": "MGNREGS person-days (FY24)",  "Current": "256 Cr","Target": "300 Cr",      "Status": "In Progress"},
                {"Indicator": "PMAY houses completed",       "Current": "2.95 Cr","Target": "4.0 Cr",    "Status": "Lagging"},
            ],
            columns=[{"name": c, "id": c} for c in ["Indicator", "Current", "Target (2030)", "Status"]],
            style_table={"overflowX": "auto", "borderRadius": "10px", "overflow": "hidden"},
            style_header={"backgroundColor": C["navyL"], "color": C["navy"],
                          "fontWeight": "700", "fontFamily": "Georgia,serif",
                          "fontSize": "11px", "padding": "11px 14px"},
            style_cell={"backgroundColor": "white", "color": C["navy"],
                        "fontFamily": "Georgia,serif", "fontSize": "12px",
                        "border": f"1px solid {C['border']}", "padding": "10px 14px"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": C["bg"]},
                {"if": {"filter_query": '{Status} = "On Track"',  "column_id": "Status"},
                 "backgroundColor": C["greenL"], "color": C["green"], "fontWeight": "700"},
                {"if": {"filter_query": '{Status} = "Lagging"',   "column_id": "Status"},
                 "backgroundColor": C["redL"],   "color": C["red"],   "fontWeight": "700"},
                {"if": {"filter_query": '{Status} = "In Progress"',"column_id": "Status"},
                 "backgroundColor": C["goldL"],  "color": C["gold"],  "fontWeight": "700"},
            ],
        ),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "22px"},
       className="dashboard-panel")

    # 2030 progress bars
    prog_bars = html.Div([
        section_title("📅 2030 Gap Analysis — SDG 1", color=C["saffron"]),
        *[progress_row(**r) for r in sdg1_progress],
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "22px"},
       className="dashboard-panel")

    # Challenge cards
    challenges = html.Div([
        section_title("⚠️ Key Barriers to Eliminating Poverty", color=C["red"]),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(emoji, style={"fontSize": "24px", "marginBottom": "6px"}),
                    html.Div(title, style={"fontWeight": "700", "color": C["navy"],
                                          "fontSize": "13px", "marginBottom": "6px",
                                          "fontFamily": "Georgia,serif"}),
                    html.Div(body, style={"fontSize": "12px", "color": C["muted"],
                                         "lineHeight": "1.75"}),
                ], style={"background": C["bg"], "borderRadius": "10px", "padding": "14px",
                          "borderLeft": f"3px solid {color}"}),
            ])
            for emoji, title, body, color in [
                ("🌾", "Agricultural Distress",
                 "58% of workforce in agriculture earns <₹8,000/month. Land fragmentation reduces productivity. 86% of farmers are smallholders (<2 ha).",
                 C["saffron"]),
                ("🏙️", "Urban Informal Labour",
                 "90% of urban workforce lacks social security. Irregular wages, no housing rights, poor working conditions. Platform economy obscures precarity.",
                 C["red"]),
                ("📊", "Social Protection Gaps",
                 "Only 24.4% covered — far below 45%+ global average. Exclusion errors plague Aadhaar-linked DBT: millions miss entitlements due to tech failures.",
                 C["navy"]),
                ("⚡", "Energy & Infrastructure",
                 "Lack of reliable electricity, roads, and clean water limits livelihood opportunities in 40%+ of rural India. Last-mile connectivity remains the bottleneck.",
                 C["purple"]),
                ("📚", "Education-Poverty Trap",
                 "Learning poverty (inability to read by age 10) at 70%+ in low-income states. Poor schooling quality perpetuates intergenerational poverty cycles.",
                 C["teal"]),
                ("🌡️", "Climate Vulnerability",
                 "3.4 Mn people displaced by extreme weather in 2022. Agricultural distress from erratic monsoons pushes 20 Mn farmers toward poverty each drought year.",
                 C["gold"]),
            ]
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(auto-fit,minmax(240px,1fr))",
                  "gap": "14px"}),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}"},
       className="dashboard-panel")

    return html.Div([
        section_title("💰 SDG 1: No Poverty — India's Status",
                      "Target: End poverty in all its forms everywhere by 2030 · "
                      "Source: World Bank, NITI Aayog MPI 2023, UN SDG Portal",
                      C["saffron"]),
        kpis,
        html.Div([
            html.Label("Year Range for Poverty Charts",
                       style={"color": C["muted"], "fontSize": "11px",
                              "letterSpacing": "1.5px", "textTransform": "uppercase"}),
            dcc.RangeSlider(id="sdg1-year-range", min=1993, max=2023, step=1,
                            value=[1993, 2023],
                            marks={y: {"label": str(y),
                                       "style": {"color": C["muted"], "fontSize": "9px"}}
                                   for y in [1993, 2000, 2005, 2010, 2015, 2020, 2023]},
                            tooltip={"placement": "bottom"}),
        ], style={"background": C["card"], "borderRadius": "14px", "padding": "18px",
                  "marginBottom": "20px",
                  "boxShadow": "0 4px 20px rgba(0,0,0,0.07)"},
           className="dashboard-panel"),
        html.Div([
            html.Div(graph_card("fig-poverty-trend", "", 380,
                                "Source: World Bank PovcalNet / HCES 2022-23 / CPHS"),
                     style={"flex": "1", "minWidth": "300px"}),
            html.Div(graph_card("fig-mpi-states", "", 380,
                                "Source: NITI Aayog National MPI 2023"),
                     style={"flex": "1", "minWidth": "300px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
        html.Div([
            html.Div(graph_card("fig-pmjdy", "", 340,
                                "Source: Ministry of Finance / PMJDY Portal (2024)"),
                     style={"flex": "1", "minWidth": "300px"}),
            html.Div(graph_card("fig-mgnregs", "", 340,
                                "Source: Ministry of Rural Development MIS (2024)"),
                     style={"flex": "1", "minWidth": "300px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
        indicator_table,
        prog_bars,
        challenges,
    ])


# ── TAB 2: SDG 2 — ZERO HUNGER ───────────────────────────────────────
def build_sdg2():
    kpis = html.Div([
        kpi_card("🌍", "GHI Score 2023",  "28.7",  "Rank 111/125 countries", C["red"]),
        kpi_card("👶", "Stunting (<5 yrs)","35.5%", "NFHS-5 · ~53 Mn children", C["red"]),
        kpi_card("⚡", "Wasting (<5 yrs)", "19.3%", "Acute malnutrition — worsened", C["saffron"]),
        kpi_card("🩸", "Anaemia (Women)",  "57.0%", "15–49 age group · NFHS-5", C["purple"]),
        kpi_card("🍚", "PDS Coverage",     "80 Cr", "Free grain under PMGKAY", C["green"]),
        kpi_card("🌱", "Undernourished",   "200 Mn","FAO 2023 · 14% of population", C["saffron"]),
    ], style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"})

    indicator_table = html.Div([
        section_title("📊 SDG 2 — Key Indicator Progress (2023)",
                      "Source: FAO, NFHS-5, GHI 2023, UN SDG Portal", C["green"]),
        dash_table.DataTable(
            data=[
                {"Indicator": "GHI Score (2023)",           "Current": "28.7",    "Target (2030)": "<10",  "Status": "Lagging"},
                {"Indicator": "Under-5 stunting",           "Current": "35.5%",   "Target (2030)": "25%",  "Status": "In Progress"},
                {"Indicator": "Under-5 wasting",            "Current": "19.3%",   "Target (2030)": "5%",   "Status": "Lagging"},
                {"Indicator": "PDS food grain coverage",    "Current": "80 Cr",   "Target (2030)": "100%", "Status": "In Progress"},
                {"Indicator": "Women land rights (farmers)","Current": "12.8%",   "Target (2030)": "50%",  "Status": "Lagging"},
                {"Indicator": "Agri R&D spending (% GDP)", "Current": "0.36%",   "Target (2030)": "1.0%", "Status": "Lagging"},
                {"Indicator": "Anaemia prevalence (women)", "Current": "57.0%",   "Target (2030)": "30%",  "Status": "Lagging"},
            ],
            columns=[{"name": c, "id": c} for c in ["Indicator", "Current", "Target (2030)", "Status"]],
            style_table={"overflowX": "auto", "borderRadius": "10px", "overflow": "hidden"},
            style_header={"backgroundColor": C["greenL"], "color": C["greenD"],
                          "fontWeight": "700", "fontFamily": "Georgia,serif",
                          "fontSize": "11px", "padding": "11px 14px"},
            style_cell={"backgroundColor": "white", "color": C["navy"],
                        "fontFamily": "Georgia,serif", "fontSize": "12px",
                        "border": f"1px solid {C['border']}", "padding": "10px 14px"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": C["bg"]},
                {"if": {"filter_query": '{Status} = "Lagging"',    "column_id": "Status"},
                 "backgroundColor": C["redL"],  "color": C["red"],  "fontWeight": "700"},
                {"if": {"filter_query": '{Status} = "In Progress"',"column_id": "Status"},
                 "backgroundColor": C["goldL"], "color": C["gold"], "fontWeight": "700"},
            ],
        ),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "22px"},
       className="dashboard-panel")

    prog_bars = html.Div([
        section_title("📅 2030 Gap Analysis — SDG 2", color=C["green"]),
        *[progress_row(**r) for r in sdg2_progress],
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "22px"},
       className="dashboard-panel")

    root_causes = html.Div([
        section_title("🌾 Root Causes of Hunger in India", color=C["greenD"]),
        html.Div([
            html.Div([
                html.Div(emoji, style={"fontSize": "22px", "marginBottom": "6px"}),
                html.Div(title, style={"fontWeight": "700", "color": C["greenD"],
                                      "fontSize": "12px", "marginBottom": "5px"}),
                html.Div(body, style={"fontSize": "11px", "color": "#2d5a27",
                                     "lineHeight": "1.75"}),
            ], style={"background": C["greenL"], "borderRadius": "10px", "padding": "14px"})
            for emoji, title, body in [
                ("💧", "Water Stress",
                 "700+ Mn face high water stress. 85% of water goes to agriculture — depleting aquifers. Groundwater depletion threatens food production in Punjab, Haryana, UP."),
                ("🌡️", "Climate Shocks",
                 "Rising temperatures cut crop yields 2–6% per decade. Erratic monsoon destroys 10–15% of crops. Climate change disproportionately hits smallholder farmers."),
                ("🏭", "Post-Harvest Losses",
                 "15–20% of produce lost due to poor cold chain and storage infrastructure. Only 4% of perishable produce needs are met by existing cold storage capacity."),
                ("📚", "Nutritional Illiteracy",
                 "Rice-wheat monoculture dominates diets. Poor dietary diversity limits protein, iron, and micronutrient intake — causing 'hidden hunger' in 700 Mn+ people."),
                ("♀️", "Gender Gap",
                 "Women own <12.8% of agri land despite being 42% of farm labour. Low female autonomy directly drives child malnutrition — mother's education is the strongest predictor."),
                ("🏥", "Healthcare Deficits",
                 "Low healthcare access means infections rob children of nutrients. Anaemia worsened from 58.6% to 67.1% in children — a systemic failure of nutrition-health integration."),
            ]
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(auto-fit,minmax(220px,1fr))",
                  "gap": "12px"}),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}"},
       className="dashboard-panel")

    return html.Div([
        section_title("🌾 SDG 2: Zero Hunger — India's Status",
                      "Target: End hunger, achieve food security, improve nutrition by 2030 · "
                      "Source: FAO, NFHS-5, GHI 2023, UN SDG Portal",
                      C["green"]),
        kpis,
        html.Div([
            html.Div(graph_card("fig-hunger-trends", "", 380,
                                "Source: NFHS Rounds 3,4,5 (2005–2021) · FAO 2023"),
                     style={"flex": "1", "minWidth": "300px"}),
            html.Div(graph_card("fig-nfhs-compare", "", 380,
                                "Source: NFHS-4 (2015-16), NFHS-5 (2019-21), SDG Target 2030"),
                     style={"flex": "1", "minWidth": "300px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
        html.Div([
            html.Div(graph_card("fig-food-insecurity", "", 340,
                                "Source: FAO FIES Survey Module · SOFI 2023"),
                     style={"flex": "1", "minWidth": "300px"}),
            html.Div(graph_card("fig-ghi-gauge", "", 340,
                                "Source: Global Hunger Index 2023 (Welthungerhilfe / Concern Worldwide)"),
                     style={"flex": "1", "minWidth": "300px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
        indicator_table,
        prog_bars,
        root_causes,
    ])


# ── TAB 3: GLOBAL COMPARE ─────────────────────────────────────────────
def build_compare():
    comp_table = html.Div([
        section_title("🌍 Regional Nutrition & Poverty Profile — 2023",
                      "Source: GHI 2023, World Bank PIP, FAO, NFHS-5"),
        dash_table.DataTable(
            data=comparator_table.rename(columns={
                "country": "Country", "ext_poverty": "Ext. Poverty %",
                "stunting": "Stunting %", "ghi": "GHI Score",
                "category": "GHI Category",
            })[["Country","Ext. Poverty %","Stunting %","GHI Score","GHI Category"]].to_dict("records"),
            columns=[{"name": c, "id": c} for c in
                     ["Country","Ext. Poverty %","Stunting %","GHI Score","GHI Category"]],
            style_table={"overflowX": "auto", "borderRadius": "10px", "overflow": "hidden"},
            style_header={"backgroundColor": C["navyL"], "color": C["navy"],
                          "fontWeight": "700", "fontFamily": "Georgia,serif",
                          "fontSize": "11px", "padding": "11px 14px"},
            style_cell={"backgroundColor": "white", "color": C["navy"],
                        "fontFamily": "Georgia,serif", "fontSize": "12px",
                        "border": f"1px solid {C['border']}", "padding": "10px 14px"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": C["bg"]},
                {"if": {"filter_query": '{Country} contains "India"'},
                 "backgroundColor": C["redL"], "fontWeight": "700"},
                {"if": {"filter_query": '{GHI Category} = "Serious"', "column_id": "GHI Category"},
                 "backgroundColor": C["redL"], "color": C["red"], "fontWeight": "700"},
                {"if": {"filter_query": '{GHI Category} = "Low"', "column_id": "GHI Category"},
                 "backgroundColor": C["greenL"], "color": C["green"], "fontWeight": "700"},
            ],
        ),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "22px"},
       className="dashboard-panel")

    paradox = info_box(
        "⚠️ India's Hunger Paradox",
        """India is the world's 5th largest economy and a net food exporter — yet ranks 111/125 on the 
Global Hunger Index 2023 with a 'Serious' rating. This paradox arises because food availability ≠ food access. 
India exports $50+ billion in food annually while 200 million citizens remain undernourished. 
The problem is distribution, affordability, dietary diversity, and systemic inequality — not production alone. 
COVID-19 reversed a decade of progress, pushing 56 million back into poverty in 2020–21 alone. 
India's wasting (19.3%) is among the highest in the world — higher than Sub-Saharan Africa's average — 
making child acute malnutrition India's single most urgent public health crisis.""",
        C["red"]
    )

    return html.Div([
        section_title("🌍 Global Comparison — Hunger & Poverty Indicators",
                      "How India compares with South Asian peers and global benchmarks · "
                      "Source: GHI 2023, FAO, World Bank, UN SDG Portal"),
        html.Div([
            kpi_card("🌏", "GHI Rank",          "#111",    "Out of 125 countries", C["red"]),
            kpi_card("📊", "GHI Category",       "Serious",  "Score 28.7 — urgent action needed", C["red"]),
            kpi_card("📈", "South Asia Rank",     "Worst",   "Lower than Pak, BD, Nepal", C["saffron"]),
            kpi_card("💡", "Extreme Poverty",     "2.3%",    "Better than regional avg (4.2%)", C["green"]),
            kpi_card("🌾", "Undernourished",      "200 Mn",  "FAO 2023 estimate", C["saffron"]),
        ], style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"}),
        html.Div([
            html.Div(graph_card("fig-ghi-compare", "", 380,
                                "Source: Global Hunger Index 2023 (Welthungerhilfe / Concern Worldwide)"),
                     style={"flex": "1", "minWidth": "300px"}),
            html.Div(graph_card("fig-stunting-compare", "", 380,
                                "Source: World Bank, UNICEF, WHO Joint Child Malnutrition Estimates 2023"),
                     style={"flex": "1", "minWidth": "300px"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
        comp_table,
        paradox,
    ])


# ── TAB 4: CHALLENGES ─────────────────────────────────────────────────
def build_challenges():
    challenge_cards = html.Div([
        html.Div([
            html.Div(emoji, style={"fontSize": "28px", "marginBottom": "8px"}),
            html.Div(title, style={"fontWeight": "700", "color": C["navy"], "fontSize": "14px",
                                  "marginBottom": "10px", "fontFamily": "Georgia,serif"}),
            html.Ul([html.Li(pt, style={"fontSize": "12px", "color": C["muted"],
                                       "marginBottom": "7px", "lineHeight": "1.75"})
                    for pt in points],
                   style={"paddingLeft": "16px", "margin": "0"}),
        ], style={"background": C["card"], "borderRadius": "14px", "padding": "20px",
                  "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                  "border": f"1px solid {C['border']}", "borderTop": f"4px solid {color}"})
        for emoji, title, points, color in [
            ("🌡️", "Climate Change & Agricultural Vulnerability", [
                "Rising temperatures cut crop yields by 4–9% per decade in key states",
                "800 Mn+ dependent on rain-fed agriculture face monsoon unpredictability",
                "Extreme events (floods, droughts) displaced 3.4 Mn people in 2022",
                "Glacial melt threatens Himalayan rivers feeding 40% of farmland",
            ], C["saffron"]),
            ("💼", "Unemployment & Informal Economy", [
                "Youth unemployment: 23.2% (ILO 2023) — highest in South Asia",
                "90% of workers in informal sector with no social security",
                "Platform/gig economy growth masks structural job quality decline",
                "Rural-urban migration increasing urban slum populations by 6% annually",
            ], C["red"]),
            ("♀️", "Gender Inequality & Malnutrition", [
                "Women own <13% of agricultural land despite being 42% of farm labour",
                "57% of women of reproductive age are anaemic (NFHS-5)",
                "Low FLFP (22.3%) limits household income and child nutrition",
                "Child marriage (23.3%) perpetuates intergenerational poverty cycles",
            ], C["purple"]),
            ("🏥", "Healthcare & Nutrition System Gaps", [
                "India spends only 2.1% of GDP on public health (WHO norm: 5%)",
                "1 doctor per 1,445 people in rural India (WHO: 1:1,000)",
                "Anaemia in children INCREASED 58.6% → 67.1% (NFHS-4 to NFHS-5)",
                "Micronutrient deficiency ('hidden hunger') affects 700 Mn+ people",
            ], C["navy"]),
            ("📡", "Digital & Infrastructure Divide", [
                "Only 31% of rural households have internet access",
                "40% of PMGKAY beneficiaries face Aadhaar/ration card linking issues",
                "Cold chain infrastructure covers only 4% of perishable needs",
                "11% of villages lack all-weather road connectivity",
            ], C["teal"]),
            ("📊", "Data Gaps & Policy Blind Spots", [
                "No comprehensive national poverty survey since NSSO 2011-12 (until 2022-23 HCES)",
                "GHI methodology disputed — highlights measurement & political challenges",
                "Caste-disaggregated hunger data absent from official reports",
                "Lack of real-time nutrition surveillance in 650,000+ villages",
            ], C["gold"]),
        ]
    ], style={"display": "grid",
              "gridTemplateColumns": "repeat(auto-fit,minmax(280px,1fr))",
              "gap": "16px", "marginBottom": "22px"})

    return html.Div([
        section_title("⚠️ Key Challenges — SDG 1 & SDG 2",
                      "Structural barriers impeding India's progress toward zero poverty and zero hunger by 2030",
                      C["red"]),
        challenge_cards,
        html.Div([
            html.Div(graph_card("fig-radar-challenge", "", 420,
                                "Note: Illustrative composite scores — NITI Aayog SDG India Index 2023-24 dimensions"),
                     style={"flex": "1", "minWidth": "300px"}),
            html.Div([
                section_title("📅 2030 Gap Summary — All Key Indicators", color=C["navy"]),
                *[progress_row(**r) for r in sdg1_progress[:3]],
                html.Hr(style={"borderColor": C["border"]}),
                *[progress_row(**r) for r in sdg2_progress[:4]],
            ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
                      "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                      "border": f"1px solid {C['border']}", "flex": "1", "minWidth": "300px"},
               className="dashboard-panel"),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
    ])


# ── TAB 5: GOVT SCHEMES ───────────────────────────────────────────────
def build_schemes():
    kpis = html.Div([
        kpi_card("📜", "Active Major Schemes",  "8",         "Combined: 140+ Cr beneficiaries", C["navy"]),
        kpi_card("💸", "Annual Budget",         "~₹5.2 L Cr","Combined FY2023-24 allocation",   C["saffron"]),
        kpi_card("🌾", "PMGKAY (Free Grain)",   "₹2 L Cr/yr","World's largest food security pgm", C["green"]),
        kpi_card("🏗️", "MGNREGS (FY24)",        "256 Cr days","Rural wage employment generated", C["teal"]),
    ], style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"})

    schemes_table = html.Div([
        section_title("📋 Major Government Programmes — SDG 1 & 2 Alignment",
                      "Source: Ministry of Finance, NITI Aayog, PIB 2024"),
        dash_table.DataTable(
            data=govt_schemes,
            columns=[{"name": c, "id": c}
                     for c in ["scheme", "beneficiaries", "budget", "sdg", "impact"]],
            style_table={"overflowX": "auto", "borderRadius": "10px", "overflow": "hidden"},
            style_header={"backgroundColor": C["navy"], "color": "white",
                          "fontWeight": "700", "fontFamily": "Georgia,serif",
                          "fontSize": "11px", "padding": "11px 14px",
                          "textTransform": "uppercase"},
            style_cell={"backgroundColor": "white", "color": C["navy"],
                        "fontFamily": "Georgia,serif", "fontSize": "12px",
                        "border": f"1px solid {C['border']}", "padding": "10px 14px"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": C["bg"]},
                {"if": {"filter_query": '{impact} = "High"', "column_id": "impact"},
                 "backgroundColor": C["greenL"], "color": C["green"], "fontWeight": "700"},
            ],
            column_selectable=False,
        ),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}", "marginBottom": "22px"},
       className="dashboard-panel")

    # Scheme deep-dives
    deep_dives = html.Div([
        section_title("🔍 Scheme Deep-Dives", color=C["navy"]),
        html.Div([
            html.Div([
                html.Div([
                    html.Span(icon, style={"fontSize": "28px"}),
                    html.Div([
                        html.Div(name, style={"fontWeight": "700", "color": C["navy"],
                                             "fontSize": "13px", "fontFamily": "Georgia,serif"}),
                        html.Span(tag, style={"background": bg, "color": fg,
                                             "padding": "1px 8px", "borderRadius": "8px",
                                             "fontSize": "10px", "fontWeight": "700"}),
                    ]),
                ], style={"display": "flex", "gap": "10px", "alignItems": "flex-start",
                          "marginBottom": "10px"}),
                html.P(summary, style={"fontSize": "12px", "color": C["muted"],
                                      "lineHeight": "1.75", "margin": "8px 0"}),
                html.Div(impact, style={"background": C["bg"], "borderRadius": "8px",
                                       "padding": "10px 12px", "fontSize": "11px",
                                       "color": C["navy"], "lineHeight": "1.7",
                                       "borderLeft": f"3px solid {border}"}),
            ], style={"background": C["card"], "borderRadius": "14px", "padding": "20px",
                      "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                      "border": f"1px solid {C['border']}", "borderLeft": f"5px solid {border}"})
            for icon, name, tag, bg, fg, summary, impact, border in [
                ("🍚", "PM Garib Kalyan Anna Yojana", "SDG 2 · 80 Cr people",
                 C["greenL"], C["greenD"],
                 "World's largest food security programme — provides 5 kg free grain/month to 80 Cr beneficiaries. Launched during COVID-19 in 2020, made permanent in Jan 2023. Annual cost: ₹2,00,000 Cr — India's single largest welfare expenditure.",
                 "✅ Impact: Prevented mass starvation during COVID-19. Reduced severe food insecurity. ⚠️ Gap: Dietary diversity and protein/micronutrient access remain completely unaddressed — grain alone cannot end malnutrition.",
                 C["green"]),
                ("🌾", "PM-KISAN + MGNREGS", "SDG 1+2 · 11 Cr + 15 Cr",
                 C["saffronL"], C["saffronD"],
                 "PM-KISAN provides ₹6,000/year direct cash transfer to 11 Cr farmers. MGNREGS guarantees 100 days of wage work to rural households — 256 Cr person-days generated in FY2024. Together they form India's rural income floor.",
                 "✅ Impact: Income floor for rural poor. MGNREGS reduces distress migration. ⚠️ Gap: PM-KISAN amount (₹6,000/yr = ₹500/month) is grossly insufficient — average farmer needs ₹50,000+/yr to break even on input costs.",
                 C["saffron"]),
                ("👶", "Poshan Abhiyaan (National Nutrition Mission)", "SDG 2 · 10 Cr children + women",
                 C["purpleL"], C["purple"],
                 "National Nutrition Mission (2018) targeting 2% per year reduction in stunting, wasting, and underweight. Integrates 40+ nutrition-linked schemes via ICDS, ASHA workers, and 13.9 lakh Anganwadi centres across the country.",
                 "✅ Impact: Stunting declined from 38.4% → 35.5%. ⚠️ Gap: Anaemia WORSENED — reveals critical failures in micronutrient supplementation delivery and programme monitoring. Beneficiary reach vs. quality of service remains a major gap.",
                 C["purple"]),
                ("🏠", "PM Awas Yojana (PMAY)", "SDG 1 · 2.95 Cr houses",
                 C["navyL"], C["navy"],
                 "Housing for All mission targeting 4 Cr rural + urban households. Provides ₹1.2–1.5 lakh subsidy per rural house and ₹2.67 lakh home loan interest subsidy for EWS urban beneficiaries. 2.95 Cr rural houses completed as of 2024.",
                 "✅ Impact: Shelter for millions of homeless. Reduces climate vulnerability. ⚠️ Gap: 1.05 Cr rural houses pending. Urban phase significantly behind — waiting lists in metros exceed 10 years. Quality of construction widely criticised.",
                 C["navy"]),
            ]
        ], style={"display": "grid",
                  "gridTemplateColumns": "repeat(auto-fit,minmax(280px,1fr))",
                  "gap": "16px"}),
    ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
              "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
              "border": f"1px solid {C['border']}"},
       className="dashboard-panel")

    return html.Div([
        section_title("📋 Government Schemes — Anti-Poverty & Food Security",
                      "Major Central Government programmes targeting SDG 1 & 2 · "
                      "Source: MoF, NITI Aayog, PIB 2024"),
        kpis, schemes_table, deep_dives,
    ])


# ── TAB 6: REPORT GENERATOR ──────────────────────────────────────────
def build_report():
    return html.Div([
        section_title("📄 Report Generator",
                      "Generate and download a professional PDF report on India's SDG 1 & 2 status"),
        html.Div([
            html.Div([
                html.Label("Select Sections to Include",
                           style={"color": C["muted"], "fontSize": "11px",
                                  "letterSpacing": "1.5px", "textTransform": "uppercase",
                                  "display": "block", "marginBottom": "8px"}),
                dcc.Checklist(
                    id="rep-sections",
                    options=[
                        {"label": " Country Overview & Profile",         "value": "overview"},
                        {"label": " SDG 1: Poverty Analysis",            "value": "sdg1"},
                        {"label": " SDG 2: Hunger & Nutrition Analysis", "value": "sdg2"},
                        {"label": " Global Comparison (GHI, stunting)",  "value": "compare"},
                        {"label": " Challenges & Structural Barriers",   "value": "challenges"},
                        {"label": " Government Schemes Assessment",      "value": "schemes"},
                        {"label": " 2030 Gap Analysis",                  "value": "gap"},
                        {"label": " Climate Justice Reflection",         "value": "justice"},
                    ],
                    value=["overview", "sdg1", "sdg2", "compare", "gap", "justice"],
                    labelStyle={"display": "block", "color": C["navy"],
                                "fontFamily": "Georgia,serif", "fontSize": "13px",
                                "marginBottom": "8px", "cursor": "pointer"},
                    inputStyle={"marginRight": "8px", "accentColor": C["saffron"]},
                ),
            ], style={"marginBottom": "16px"}),
            html.Div([
                html.Label("Student Name",
                           style={"color": C["muted"], "fontSize": "11px",
                                  "display": "block", "marginBottom": "5px"}),
                dcc.Input(id="rep-name", value="G Chaitanya Venkatesh", type="text",
                          style={"width": "100%", "border": f"1px solid {C['border']}",
                                 "borderRadius": "8px", "padding": "10px 14px",
                                 "fontFamily": "Georgia,serif", "fontSize": "13px"}),
            ], style={"marginBottom": "12px"}),
            html.Div([
                html.Label("Enrolment Number",
                           style={"color": C["muted"], "fontSize": "11px",
                                  "display": "block", "marginBottom": "5px"}),
                dcc.Input(id="rep-enrol", value="M2025ANL013", type="text",
                          style={"width": "100%", "border": f"1px solid {C['border']}",
                                 "borderRadius": "8px", "padding": "10px 14px",
                                 "fontFamily": "Georgia,serif", "fontSize": "13px"}),
            ], style={"marginBottom": "20px"}),
            html.Button("📋 Preview Report",
                        id="preview-report-btn",
                        style={"background": f"linear-gradient(135deg,{C['saffron']},{C['saffronD']})",
                               "border": "none", "borderRadius": "10px", "color": "white",
                               "fontFamily": "Georgia,serif", "fontSize": "13px",
                               "letterSpacing": "2px", "padding": "13px 28px",
                               "cursor": "pointer", "width": "100%",
                               "fontWeight": "700", "marginBottom": "10px"}),
            html.Button("⬇ Download PDF",
                        id="download-report-btn",
                        style={"background": f"linear-gradient(135deg,{C['navy']},{C['navyL']})",
                               "border": "none", "borderRadius": "10px", "color": "white",
                               "fontFamily": "Georgia,serif", "fontSize": "12px",
                               "letterSpacing": "2px", "padding": "12px 28px",
                               "cursor": "pointer", "width": "100%", "fontWeight": "600"}),
            dcc.Download(id="download-report"),
        ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
                  "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                  "border": f"1px solid {C['border']}", "maxWidth": "600px",
                  "marginBottom": "20px"}),
        html.Div([
            html.Div("Report Preview", style={"fontFamily": "Georgia,serif", "fontSize": "11px",
                                             "color": C["muted"], "letterSpacing": "2px",
                                             "marginBottom": "10px"}),
            html.Pre(id="report-preview",
                     style={"color": C["navy"], "fontFamily": "'Courier New',monospace",
                            "fontSize": "11px", "lineHeight": "1.65",
                            "overflow": "auto", "maxHeight": "500px",
                            "background": C["bg"], "borderRadius": "8px", "padding": "16px",
                            "border": f"1px solid {C['border']}"}),
        ], style={"background": C["card"], "borderRadius": "14px", "padding": "24px",
                  "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                  "border": f"1px solid {C['border']}"}),
    ])


# ── TAB 7: METHODOLOGY ────────────────────────────────────────────────
def build_methodology():
    steps = [
        ("1. Data Sources", "data-sources",
         """All datasets sourced from open, peer-reviewed global repositories. Primary sources:
• UN Statistics Division SDG Global Database (SDG Indicators 1.1, 1.2, 2.1, 2.2)
• World Bank Poverty and Inequality Platform (PIP) — national headcount ratios 1993–2023
• NITI Aayog National MPI 2023 — state-level multidimensional poverty
• NFHS-5 (2019-21) and NFHS-4 (2015-16) — child malnutrition, anaemia
• Global Hunger Index 2023 — Welthungerhilfe & Concern Worldwide
• FAO State of Food Security and Nutrition (SOFI 2023) — food insecurity prevalence
• Ministry of Finance / PMJDY Portal — Jan Dhan account data 2015-2023
• Ministry of Rural Development MGNREGS MIS — person-days FY2014-2024
• NITI Aayog SDG India Index 2023-24 — state SDG readiness scores"""),

        ("2. Data Handling & Embedding", "data-handling",
         """All data is embedded directly in the Python script as pandas DataFrames — 
no external Excel or CSV files are required to run this dashboard. 
Data was cleaned, validated, and cross-referenced across multiple sources before embedding.
Where 2023 data was unavailable, the most recent authoritative estimate is used 
with appropriate notation. World Bank modelled estimates supplement gaps in official surveys."""),

        ("3. Metric Definitions", "definitions",
         """• Extreme Poverty: Living on <$2.15/day (2017 PPP) — World Bank international poverty line
• National Poverty Line: India's Tendulkar Committee line (₹1,059/month rural, ₹1,286/month urban)  
• MPI (Multidimensional Poverty Index): OPHI methodology — 10 indicators across Health, Education, Living Standards
• Stunting: Height-for-age <-2 SD from WHO median — chronic malnutrition
• Wasting: Weight-for-height <-2 SD — acute malnutrition (more dangerous, short-term)
• Underweight: Weight-for-age <-2 SD — composite of stunting + wasting
• Anaemia: Haemoglobin <12 g/dL (women), <11 g/dL (children)
• GHI Score: Composite of undernourishment %, child stunting %, child wasting %, child mortality
• FIES (Food Insecurity Experience Scale): WHO/FAO self-reported food access deprivation"""),

        ("4. Visualisation", "visualisation",
         """Dashboard built with Plotly Dash (Python), using Plotly graph_objects for chart-level control.
Colour palette derived from the Indian national flag: Saffron (#FF6B00), White/Cream (#FDF9F5), 
Green (#138808), supplemented by Navy Blue (#000080) for authority/government data.
Typography: Georgia serif throughout — balancing academic gravitas with readability.
All charts include source citations in footer. All data tables use conditional formatting 
to highlight progress status (On Track / In Progress / Lagging) using semantic colours."""),

        ("5. Progress Assessment", "progress",
         """'On Track' = current trajectory will meet 2030 target at observed rate of change.
'In Progress' = improvement recorded but pace insufficient to meet 2030 target.  
'Lagging' = no significant improvement, regression, or gap so large current pace cannot close it.
Assessment based on linear extrapolation of observed trends plus NITI Aayog SDG India Index ratings."""),

        ("6. Limitations", "limitations",
         """• India has not had a comprehensive consumption survey between 2011-12 and 2022-23 (HCES released Feb 2024).
• GHI methodology is disputed by the Indian government — see Ministry of Women & Child Development (2022) rebuttal.
• NFHS-5 is a sample survey — state-level estimates have wider confidence intervals for small states.
• Consumption-based poverty estimates for 2015-2021 use World Bank modelled estimates.
• 2023 figures for some indicators are preliminary or extrapolated from 2021 base data.
• Radar/readiness scores are illustrative composite indices — not directly comparable across sectors."""),

        ("7. Software Stack", "software",
         """Python 3.9+ | pandas | numpy | plotly 5.x | dash 2.x | dash-bootstrap-components | reportlab
All open-source. No proprietary software. No external data files required.
Run with: python india_sdg_dashboard.py"""),
    ]

    return html.Div([
        section_title("🔬 Methodology",
                      "Transparent, reproducible pipeline — full documentation"),
        *[html.Div([
            html.Div(title, style={"fontFamily": "Georgia,serif", "fontSize": "14px",
                                  "color": C["saffron"], "marginBottom": "8px",
                                  "fontWeight": "700"}),
            html.P(body, style={"color": C["navy"], "fontFamily": "Georgia,serif",
                                "fontSize": "13px", "lineHeight": "1.9",
                                "whiteSpace": "pre-line"}),
        ], style={"background": C["card"], "borderRadius": "14px", "padding": "22px",
                  "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                  "marginBottom": "16px", "border": f"1px solid {C['border']}",
                  "borderLeft": f"3px solid {C['navy']}"})
          for title, _, body in steps],
    ])


# ── TAB 8: ABOUT ─────────────────────────────────────────────────────
def build_about():
    refs = [
        "United Nations Statistics Division. (2024). SDG Global Database. https://unstats.un.org/sdgs/dataportal",
        "World Bank. (2024). Poverty and Inequality Platform (PIP). https://pip.worldbank.org",
        "NITI Aayog. (2023). National Multidimensional Poverty Index: A Progress Review 2023. Government of India.",
        "International Institute for Population Sciences (IIPS). (2022). National Family Health Survey (NFHS-5), 2019-21: India. Mumbai: IIPS.",
        "Welthungerhilfe & Concern Worldwide. (2023). Global Hunger Index 2023: Confronting the Crises of Hunger and Inequality. https://www.globalhungerindex.org",
        "FAO, IFAD, UNICEF, WFP, WHO. (2023). The State of Food Security and Nutrition in the World 2023. Rome: FAO.",
        "NITI Aayog. (2024). SDG India Index & Dashboard 2023-24. Government of India. https://sdgindiaindex.niti.gov.in",
        "Ministry of Finance. (2024). PM Jan Dhan Yojana — Progress Report 2024. Government of India. https://pmjdy.gov.in",
        "Ministry of Agriculture & Farmers Welfare. (2024). PM-KISAN Progress Dashboard. https://pmkisan.gov.in",
        "Ministry of Rural Development. (2024). MGNREGS MIS Annual Report 2023-24. Government of India.",
    ]

    return html.Div([
        section_title("👤 About This Dashboard",
                      "Purpose, author, acknowledgements and full references"),
        html.Div([
            # Author card
            html.Div([
                html.Div("🇮🇳", style={"fontSize": "36px", "marginBottom": "12px"}),
                html.Div("INDIA SDG 1 & 2 DASHBOARD",
                         style={"fontFamily": "Georgia,serif", "fontSize": "16px",
                                "fontWeight": "900", "color": C["navy"],
                                "letterSpacing": "1px", "marginBottom": "4px"}),
                html.Div("Version 1.0  ·  December 2024",
                         style={"color": C["muted"], "fontSize": "11px",
                                "letterSpacing": "1.5px", "marginBottom": "18px"}),
                html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),
                html.Div("PREPARED BY",
                         style={"color": C["muted"], "fontSize": "10px",
                                "letterSpacing": "2px", "marginBottom": "6px"}),
                html.Div("G Chaitanya Venkatesh",
                         style={"fontFamily": "Georgia,serif", "fontSize": "20px",
                                "color": C["saffron"], "fontWeight": "700"}),
                html.Div("Enrolment: M2025ANL013",
                         style={"color": C["navy"], "fontSize": "13px", "marginTop": "4px"}),
                html.Div("MSc Analytics — 1st Year",
                         style={"color": C["muted"], "fontSize": "13px", "marginTop": "3px"}),
                html.Div("Tata Institute of Social Sciences, Mumbai",
                         style={"color": C["muted"], "fontSize": "13px", "marginTop": "3px"}),
                html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),
                html.Div("COURSE / ASSIGNMENT",
                         style={"color": C["muted"], "fontSize": "10px",
                                "letterSpacing": "2px", "marginBottom": "6px"}),
                html.Div("Sustainability Science & Analytics",
                         style={"color": C["navy"], "fontSize": "13px", "fontWeight": "600"}),
                html.Div("Dashboard / Storyboard on SDG 1 & 2 for India",
                         style={"color": C["muted"], "fontSize": "12px", "marginTop": "3px"}),
                html.Hr(style={"borderColor": C["border"], "margin": "14px 0"}),
                html.Div("TECH STACK",
                         style={"color": C["muted"], "fontSize": "10px",
                                "letterSpacing": "2px", "marginBottom": "8px"}),
                html.Div([
                    html.Span(t, style={"background": C["bg2"], "borderRadius": "6px",
                                       "padding": "3px 9px", "color": C["navy"],
                                       "fontSize": "11px", "margin": "3px",
                                       "border": f"1px solid {C['border']}",
                                       "display": "inline-block"})
                    for t in ["Python 3.9+", "Plotly 5.x", "Dash 2.x",
                              "pandas", "numpy", "dash-bootstrap-components",
                              "reportlab", "Georgia Font"]
                ]),
            ], style={"background": C["card"], "borderRadius": "14px", "padding": "26px",
                      "flex": "1", "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                      "border": f"1px solid {C['border']}"}),

            # Purpose + references
            html.Div([
                html.Div("DASHBOARD PURPOSE",
                         style={"color": C["muted"], "fontSize": "10px",
                                "letterSpacing": "2px", "marginBottom": "10px"}),
                html.P("""This dashboard was developed as a comprehensive analytical storyboard 
for understanding India's progress and challenges in achieving SDG Goal 1 (No Poverty) and 
SDG Goal 2 (Zero Hunger) — the two most critical and interlinked sustainability concerns 
for the world's most populous country.""",
                       style={"color": C["navy"], "fontFamily": "Georgia,serif",
                              "fontSize": "13px", "lineHeight": "1.85", "marginBottom": "10px"}),
                html.P("""It integrates nine datasets from the UN SDG Portal, World Bank, NITI Aayog, 
NFHS, FAO, and GHI 2023 to provide multi-dimensional insights across poverty headcount, 
multidimensional poverty, child malnutrition, food insecurity, government programme reach, 
and 2030 gap analysis — structured for academic submission, policy communication, 
and public education.""",
                       style={"color": C["navy"], "fontFamily": "Georgia,serif",
                              "fontSize": "13px", "lineHeight": "1.85"}),
                html.Hr(style={"borderColor": C["border"], "margin": "16px 0"}),
                html.Div("REFERENCES (APA 7th EDITION)",
                         style={"color": C["muted"], "fontSize": "10px",
                                "letterSpacing": "2px", "marginBottom": "10px"}),
                *[html.P(ref, style={"color": C["navy"], "fontFamily": "Georgia,serif",
                                    "fontSize": "11px", "lineHeight": "1.75",
                                    "marginBottom": "8px", "fontStyle": "italic",
                                    "paddingLeft": "12px",
                                    "borderLeft": f"2px solid {C['border']}"})
                  for ref in refs],
            ], style={"background": C["card"], "borderRadius": "14px", "padding": "26px",
                      "flex": "2", "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
                      "border": f"1px solid {C['border']}"}),
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
    ])


# ══════════════════════════════════════════════════════════════════════
#  FIGURE BUILDERS (called by callbacks)
# ══════════════════════════════════════════════════════════════════════

def make_poverty_trend(y0=1993, y1=2023):
    df = poverty_headcount[(poverty_headcount["year"] >= y0) &
                           (poverty_headcount["year"] <= y1)]
    fig = go.Figure()
    for col, name, color, dash in [
        ("national", "National",  C["saffron"], "solid"),
        ("rural",    "Rural",     C["navy"],    "dot"),
        ("urban",    "Urban",     C["green"],   "dash"),
    ]:
        fig.add_trace(go.Scatter(
            x=df["year"], y=df[col], name=name, mode="lines+markers",
            line=dict(color=color, width=2.5 if col == "national" else 2, dash=dash),
            marker=dict(size=7 if col == "national" else 5, color=color),
            fill="tozeroy" if col == "national" else None,
            fillcolor=C["saffron_t"] if col == "national" else None,
            hovertemplate=f"<b>{name}</b> %{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": f"Poverty Headcount Ratio — India ({y0}–{y1})",
                         "yaxis_title": "Population below poverty line (%)",
                         "xaxis_title": "Year"})
    return fig


def make_mpi_states():
    df = mpi_states.sort_values("poor", ascending=True)
    colors = [C["red"] if p > 35 else C["saffron"] if p > 20 else C["green"]
              for p in df["poor"]]
    fig = go.Figure(go.Bar(
        x=df["poor"], y=df["state"], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.1)", width=0.5)),
        text=[f"{v:.1f}%" for v in df["poor"]],
        textposition="outside", textfont=dict(size=9, color=C["navy"]),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% MPI Poor<extra></extra>",
    ))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "Multidimensional Poverty (MPI) — % Poor by State (2021)",
                         "xaxis_title": "% MPI Poor",
                         "margin": dict(l=130, r=60, t=65, b=40)})
    return fig


def make_pmjdy():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=pmjdy["year"], y=pmjdy["accounts"],
                         name="Accounts (Crore)",
                         marker=dict(color=C["navyL"],
                                     line=dict(color=C["navy"], width=1.5)),
                         hovertemplate="Accounts: %{y} Cr<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=pmjdy["year"], y=pmjdy["balance"],
                             name="Balance (Cr ₹)",
                             line=dict(color=C["saffron"], width=3),
                             marker=dict(size=7, color=C["saffron"]),
                             hovertemplate="Balance: ₹%{y:,.0f} Cr<extra></extra>"),
                  secondary_y=True)
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "PM Jan Dhan Yojana — Financial Inclusion (2015–2023)"})
    fig.update_yaxes(title_text="Accounts (Crore)", secondary_y=False,
                     gridcolor=C["gridline"], tickfont=dict(size=9))
    fig.update_yaxes(title_text="Deposits (₹ Crore)", secondary_y=True,
                     gridcolor="rgba(0,0,0,0)", tickfont=dict(size=9))
    return fig


def make_mgnregs():
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mgnregs["year"], y=mgnregs["person_days"],
        name="Person-days (Crore)",
        marker=dict(color=C["green_t"],
                    line=dict(color=C["green"], width=1.5)),
        hovertemplate="Person-days: %{y} Cr<extra></extra>",
    ))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "MGNREGS — Employment Person-Days Generated (Crore)",
                         "yaxis_title": "Crore Person-Days",
                         "xaxis_title": "Financial Year"})
    return fig


def make_hunger_trends():
    fig = go.Figure()
    for col, name, color, dash in [
        ("stunting",    "Stunting",    C["red"],    "solid"),
        ("wasting",     "Wasting",     C["saffron"],"solid"),
        ("underweight", "Underweight", C["navy"],   "dot"),
        ("anemia",      "Anaemia",     C["purple"], "dash"),
    ]:
        fig.add_trace(go.Scatter(
            x=hunger_trends["year"], y=hunger_trends[col],
            name=name, mode="lines+markers",
            line=dict(color=color, width=2.5 if col in ("stunting", "anemia") else 2, dash=dash),
            marker=dict(size=7, color=color),
            hovertemplate=f"<b>{name}</b> %{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "Child Malnutrition Trends — India (2000–2023)",
                         "yaxis_title": "% of Children Under 5",
                         "xaxis_title": "Year"})
    return fig


def make_nfhs_compare():
    df = nfhs_nutrition
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["indicator"], y=df["nfhs4"], name="NFHS-4 (2016)",
                         marker=dict(color=C["navyL"],
                                     line=dict(color=C["navy"], width=1)),
                         hovertemplate="%{x}<br>NFHS-4: %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Bar(x=df["indicator"], y=df["nfhs5"], name="NFHS-5 (2021)",
                         marker=dict(color=C["saffronL"],
                                     line=dict(color=C["saffron"], width=1)),
                         hovertemplate="%{x}<br>NFHS-5: %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=df["indicator"], y=df["target2030"], name="2030 Target",
                             mode="markers", marker=dict(symbol="diamond", size=10,
                                                         color=C["green"]),
                             hovertemplate="%{x}<br>Target: %{y:.1f}%<extra></extra>"))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "NFHS-4 vs NFHS-5 Nutrition Indicators vs 2030 Target",
                         "yaxis_title": "Percentage (%)",
                         "barmode": "group",
                         "xaxis": {**PLOT_LAYOUT["xaxis"],
                                   "tickangle": -30, "tickfont": dict(size=9)}})
    return fig


def make_food_insecurity():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=food_insecurity["year"],
        y=food_insecurity["severe"] + food_insecurity["moderate"],
        name="Moderate + Severe",
        fill="tozeroy", fillcolor=C["saffron_t"],
        line=dict(color=C["saffron"], width=2),
        hovertemplate="Total: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=food_insecurity["year"], y=food_insecurity["severe"],
        name="Severe only",
        fill="tozeroy", fillcolor=C["red_t"],
        line=dict(color=C["red"], width=2),
        hovertemplate="Severe: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "Food Insecurity Prevalence — India (% Population)",
                         "yaxis_title": "% of Population",
                         "xaxis_title": "Year"})
    return fig


def make_ghi_gauge():
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=28.7,
        delta={"reference": 18.3, "valueformat": ".1f",
               "increasing": {"color": C["red"]},
               "decreasing": {"color": C["green"]}},
        title={"text": "India GHI Score 2023<br><span style='font-size:12px'>vs World Avg (18.3)</span>",
               "font": {"color": C["muted"], "size": 13}},
        number={"font": {"color": C["navy"], "size": 32, "family": "Georgia, serif"}},
        gauge={
            "axis": {"range": [0, 50], "tickcolor": C["muted"],
                     "tickfont": {"size": 9}},
            "bar": {"color": C["red"], "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 10],  "color": "rgba(19,136,8,0.18)"},
                {"range": [10, 20], "color": "rgba(255,107,0,0.18)"},
                {"range": [20, 35], "color": "rgba(192,57,43,0.22)"},
                {"range": [35, 50], "color": "rgba(128,0,0,0.28)"},
            ],
            "threshold": {"line": {"color": C["saffron"], "width": 2},
                          "thickness": 0.75, "value": 18.3},
        }
    ))
    pl = {k: v for k, v in PLOT_LAYOUT.items() if k != "margin"}
    fig.update_layout(**pl, height=300, margin=dict(l=30, r=30, t=60, b=20))
    return fig


def make_ghi_compare():
    df = ghi_global.sort_values("score", ascending=False)
    colors = [C["red"] if c == "India" else
              C["saffron"] if s > 20 else
              C["gold"] if s > 10 else C["green"]
              for c, s in zip(df["country"], df["score"])]
    fig = go.Figure(go.Bar(
        x=df["country"], y=df["score"],
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.1)", width=0.5)),
        text=[f"{v:.1f}" for v in df["score"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{x}</b><br>GHI Score: %{y:.1f}<extra></extra>",
    ))
    fig.add_hline(y=10, line=dict(color=C["green"], dash="dash", width=1.5),
                  annotation_text="Target: <10 (Low hunger)",
                  annotation_font=dict(color=C["green"], size=9))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "Global Hunger Index 2023 — Country Comparison",
                         "yaxis_title": "GHI Score (lower = better)"})
    return fig


def make_stunting_compare():
    df = comparator_table.sort_values("stunting", ascending=True)
    colors = [C["red"] if "India" in c else
              C["saffron"] if v > 25 else C["green"]
              for c, v in zip(df["country"], df["stunting"])]
    fig = go.Figure(go.Bar(
        x=df["stunting"], y=df["country"], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.1)", width=0.5)),
        text=[f"{v:.1f}%" for v in df["stunting"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Stunting: %{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=25, line=dict(color=C["green"], dash="dash", width=1.5),
                  annotation_text="2030 Target (25%)",
                  annotation_font=dict(color=C["green"], size=9))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "Under-5 Stunting — Country Comparison (2023)",
                         "xaxis_title": "% Children Stunted",
                         "margin": dict(l=140, r=60, t=65, b=40)})
    return fig


def make_radar_challenge():
    cats = radar_categories + [radar_categories[0]]   # close the polygon
    s1   = radar_sdg1_scores + [radar_sdg1_scores[0]]
    s2   = radar_sdg2_scores + [radar_sdg2_scores[0]]

    fig = go.Figure()
    for name, scores, color in [
        ("SDG 1 Readiness", s1, C["saffron"]),
        ("SDG 2 Readiness", s2, C["green"]),
    ]:
        fig.add_trace(go.Scatterpolar(
            r=scores, theta=cats, fill="toself", name=name,
            line=dict(color=color, width=2),
            fillcolor=color.replace("FF6B00", "FF6B00").replace("138808", "138808") + "30",
        ))
    fig.update_layout(**{**PLOT_LAYOUT,
                         "title": "SDG Achievement Readiness — Sector Scores (0–100)",
                         "polar": dict(
                             bgcolor=C["bg"],
                             radialaxis=dict(visible=True, range=[0, 100],
                                            gridcolor=C["border"],
                                            tickfont=dict(size=8)),
                             angularaxis=dict(gridcolor=C["border"],
                                             tickfont=dict(size=10, color=C["navy"]))),
                         "showlegend": True})
    return fig


# ══════════════════════════════════════════════════════════════════════
#  REPORT CONTENT BUILDER
# ══════════════════════════════════════════════════════════════════════

def build_report_sections(sections, name, enrol):
    today = datetime.date.today().strftime("%B %d, %Y")
    out = []

    out.append(("Title Page",
                 f"India — SDG 1 (No Poverty) & SDG 2 (Zero Hunger)\n"
                 f"Sustainability Dashboard Report\n\n"
                 f"Author     : {name}\n"
                 f"Enrolment  : {enrol}\n"
                 f"Course     : Sustainability Science & Analytics\n"
                 f"Institute  : Tata Institute of Social Sciences, Mumbai\n"
                 f"Date       : {today}"))

    if "overview" in sections:
        out.append(("1. Country Overview", """
India is home to 1.44 billion people and is simultaneously the world's 5th largest economy and a country 
confronting deep structural poverty and hunger. Despite remarkable economic growth averaging 6–7% annually, 
benefits have not reached all citizens equally. India accounts for the largest share of the world's poor 
and hungry in absolute numbers, making SDG 1 and SDG 2 its most critical sustainability challenges.

Key indicators (2023):
• Extreme poor (<$2.15/day): 2.3% of population
• National poverty line: 8.5% (~115 million people)
• GHI Score: 28.7 (Rank 111/125) — "Serious" category
• Under-5 stunting: 35.5% (~53 million children)
• Under-5 wasting: 19.3% (worsened from 17.3% in 2019)
• Food insecure: ~74 Crore people (moderate or severe, FAO 2023)
""".strip()))

    if "sdg1" in sections:
        out.append(("2. SDG 1: No Poverty — Analysis", """
India's poverty reduction has been significant but uneven. Extreme poverty (<$2.15/day) has fallen 
from 22.5% in 2011 to 2.3% in 2023 — one of the fastest reductions globally. However, the national 
poverty line headcount (8.5%) and multidimensional poverty (16.4% MPI, 2021) remain high in absolute terms.

State-level disparities are extreme: Bihar (51.9% MPI poor) and Jharkhand (42.2%) lag far behind 
Kerala (2.0%) and Goa (1.0%), revealing a deeply uneven federal development landscape.

Social protection coverage at 24.4% is critically below the global average of 45%+. Financial inclusion 
has improved dramatically through PMJDY (50 Crore accounts, ₹2.1 Lakh Crore deposits by 2023).

Key barriers: agricultural distress, urban informal labour, social protection gaps, infrastructure deficits.

2030 Gap: Halving national poverty to 5.5% is achievable; universal social protection (target: 100%) 
is severely lagging at 24.4% — India's largest SDG 1 structural challenge.
""".strip()))

    if "sdg2" in sections:
        out.append(("3. SDG 2: Zero Hunger — Analysis", """
India's hunger situation is characterised by a devastating paradox: the world's largest food producer 
and exporter has 200 million undernourished citizens (FAO 2023) and ranks 111th globally on the GHI.

Child malnutrition data from NFHS-5 (2019-21) reveals:
• Stunting: 35.5% (improved from 38.4% in NFHS-4 but still catastrophically high)
• Wasting: 19.3% (WORSENED from 17.3% — a COVID-era regression)
• Anaemia (women 15-49): 57.0% (WORSENED from 53.1%)
• Anaemia (children 6-59m): 67.1% (WORSENED from 58.6%)

The worsening of multiple indicators between NFHS-4 and NFHS-5 despite massive government spending 
reveals systemic failures in last-mile delivery, programme quality, and nutritional diversity.

Root causes: water stress, climate shocks, post-harvest losses (15-20%), nutritional illiteracy, 
gender gap in land rights (women own only 12.8% of agricultural land), and healthcare deficits.
""".strip()))

    if "compare" in sections:
        out.append(("4. Global Comparison", """
India's GHI score of 28.7 is classified as 'Serious' — worse than Pakistan (26.6), Nepal (23.1), 
Bangladesh (19.1), and Sri Lanka (13.7). This makes India the worst performer in South Asia 
on the Global Hunger Index 2023, despite having the region's largest and most diversified economy.

On extreme poverty, India (2.3%) performs better than Bangladesh (5.0%) and Pakistan (4.4%), 
reflecting successful cash transfer and food security programmes. However, child wasting at 19.3% 
is higher than the Sub-Saharan Africa average — an extraordinary public health failure.

China demonstrates what is achievable: GHI score of 5.0 (Low) from a comparable starting point 
three decades ago, through sustained agricultural investment, nutrition integration, and social protection.
""".strip()))

    if "challenges" in sections:
        out.append(("5. Structural Challenges", """
1. Climate Change: India loses 4-9% of crop yields per decade from rising temperatures. 
   3.4 million people were displaced by extreme weather events in 2022 alone.

2. Informal Economy: 90% of workers lack formal social security. Youth unemployment at 23.2% 
   (ILO 2023) is the highest in South Asia.

3. Gender Inequality: Women's low land ownership (12.8%), high anaemia rates (57%), and 
   limited FLFP (22.3%) create an intergenerational nutrition-poverty trap.

4. Healthcare Deficits: Public health spending at 2.1% of GDP (vs WHO norm of 5%) means 
   infections deplete nutritional status of children who are already malnourished.

5. Data Gaps: No comprehensive consumption survey between 2011-12 and 2022-23 means 
   policy has operated on outdated poverty maps for over a decade.
""".strip()))

    if "schemes" in sections:
        out.append(("6. Government Schemes Assessment", """
India has the world's most extensive portfolio of anti-poverty and food security schemes:

• PM Garib Kalyan Anna Yojana (₹2,00,000 Cr/yr): Free grain to 80 Crore people — 
  effective at preventing starvation but does not address dietary diversity.

• MGNREGS (₹73,000 Cr/yr): 100 days of wage employment to rural households. 
  256 Crore person-days generated in FY2024. Critical income floor for rural poor.

• PM-KISAN (₹60,000 Cr/yr): ₹6,000/year to 11 Crore farmers — insufficient 
  for agricultural viability but provides cash flow support.

• Poshan Abhiyaan (₹3,700 Cr/yr): Nutrition mission covering 10 Crore children. 
  Stunting improved but anaemia worsened — revealing implementation quality gaps.

• Ayushman Bharat (₹6,400 Cr/yr): Health insurance for 50 Crore people — 
  addresses healthcare access barrier to nutrition outcomes.

Key gap: Schemes are well-funded but suffer from last-mile delivery failures, exclusion errors, 
and lack of integration between nutrition, healthcare, education, and livelihood programmes.
""".strip()))

    if "gap" in sections:
        out.append(("7. 2030 Gap Analysis", """
SDG 1 Progress:
• Extreme poverty (→0%): 88% progress — likely achievable ✅
• National poverty rate (→5.5%): 72% — achievable with sustained effort ⚠️
• Social protection (→100%): Only 24% — severely lagging ❌
• PMAY housing (→4 Cr): 74% — achievable ⚠️

SDG 2 Progress:
• Stunting (→25%): 45% progress — needs acceleration ⚠️
• Wasting (→5%): Only 22% — severely lagging ❌
• Anaemia women (→30%): 35% — lagging and regressing ❌
• Universal PDS: 80% — near achievable ⚠️
• Women land rights (→50%): 26% — severely lagging ❌

Overall Assessment: India is on track for extreme poverty elimination but severely lagging on 
hunger, malnutrition, and social protection — the harder half of its SDG 1 & 2 commitments.
""".strip()))

    if "justice" in sections:
        out.append(("8. Sustainability & Justice Reflection", """
India's SDG challenge is not one of resources — it is one of distribution, governance, and equity. 
India is simultaneously among the world's fastest-growing economies and home to the world's largest 
concentration of malnourished children. This paradox is a fundamental sustainability failure.

From a climate justice perspective, India's food insecurity is increasingly climate-driven: 
erratic monsoons, extreme heat, and groundwater depletion threaten the food systems that 
800 million people depend upon — yet India has contributed only 3% of cumulative historical CO₂ emissions.

The path forward requires: (1) Transforming food systems away from rice-wheat monoculture 
toward diverse, climate-resilient crops; (2) Investing in women's empowerment as the single 
strongest predictor of child nutrition outcomes; (3) Fixing last-mile delivery through 
technology, community accountability, and convergence across health, nutrition, and livelihood schemes; 
(4) Demanding adaptation finance from high-emitting nations whose decisions have destabilised 
the climate systems India's smallholder farmers depend upon.

Data conclusion: India has the capacity to achieve SDG 1 and SDG 2 by 2030. 
What it requires is not more money — it requires better policy quality, political will, 
and an unflinching commitment to reaching the most excluded citizens first.
""".strip()))

    out.append(("References (APA 7th Edition)", """
United Nations Statistics Division. (2024). SDG Global Database. https://unstats.un.org/sdgs/dataportal
World Bank. (2024). Poverty and Inequality Platform (PIP). https://pip.worldbank.org
NITI Aayog. (2023). National Multidimensional Poverty Index: A Progress Review 2023. Government of India.
IIPS. (2022). National Family Health Survey (NFHS-5), 2019-21: India. Mumbai: IIPS.
Welthungerhilfe & Concern Worldwide. (2023). Global Hunger Index 2023. https://www.globalhungerindex.org
FAO, IFAD, UNICEF, WFP, WHO. (2023). The State of Food Security and Nutrition in the World 2023. Rome: FAO.
NITI Aayog. (2024). SDG India Index & Dashboard 2023-24. https://sdgindiaindex.niti.gov.in
Ministry of Finance. (2024). PM Jan Dhan Yojana Progress Report 2024. https://pmjdy.gov.in
Ministry of Agriculture. (2024). PM-KISAN Dashboard. https://pmkisan.gov.in
Ministry of Rural Development. (2024). MGNREGS MIS Annual Report 2023-24. Government of India.
""".strip()))

    return out


def build_pdf_bytes(sections_list, name, enrol):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             leftMargin=54, rightMargin=54,
                             topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("T", parent=styles["Title"],
                               fontSize=16, leading=22, alignment=1,
                               textColor="#000080", spaceAfter=12)
    h_st = ParagraphStyle("H", parent=styles["Heading1"],
                           fontSize=12, leading=16, textColor="#000080",
                           spaceAfter=6, spaceBefore=10)
    n_st = ParagraphStyle("N", parent=styles["Normal"],
                           fontSize=10, leading=15, textColor="#1a1a1a")

    story = []
    story.append(Paragraph("India — SDG 1 &amp; SDG 2 Dashboard Report", title_st))
    story.append(Paragraph(f"<b>Author:</b> {xml_escape(name)}<br/>"
                            f"<b>Enrolment:</b> {xml_escape(enrol)}<br/>"
                            f"<b>Institute:</b> Tata Institute of Social Sciences, Mumbai<br/>"
                            f"<b>Programme:</b> MSc Analytics — 1st Year<br/>"
                            f"<b>Date:</b> {datetime.date.today().strftime('%B %d, %Y')}",
                            n_st))
    story.append(Spacer(1, 16))

    for sec_title, content in sections_list[1:]:  # skip title page (already above)
        story.append(Paragraph(f"<b>{xml_escape(sec_title)}</b>", h_st))
        for block in content.split("\n\n"):
            b = block.strip()
            if not b:
                continue
            inner = "<br/>".join(xml_escape(line) for line in b.split("\n"))
            story.append(Paragraph(inner, n_st))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 8))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# ══════════════════════════════════════════════════════════════════════
#  CSS INJECTION  (inline — no external assets folder needed)
# ══════════════════════════════════════════════════════════════════════
INLINE_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&display=swap');

body {{ background:{C['bg']} !important; }}

.kpi-hover:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(255,107,0,0.18) !important;
    transition: all 0.25s ease;
}}

.graph-card:hover {{
    box-shadow: 0 8px 32px rgba(0,0,128,0.12) !important;
    transition: all 0.25s ease;
}}

.nav-tab:hover {{
    background: {C['saffron_t']} !important;
    color: {C['saffron']} !important;
}}

.nav-tab.active {{
    background: linear-gradient(135deg,{C['saffron']},{C['saffronD']}) !important;
    color: white !important;
    font-weight: 700 !important;
}}

.dashboard-panel {{ transition: all 0.2s ease; }}

/* Custom scrollbar */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {C['bg']}; }}
::-webkit-scrollbar-thumb {{ background: {C['saffron']}; border-radius: 3px; }}
"""

# ══════════════════════════════════════════════════════════════════════
#  APP LAYOUT
# ══════════════════════════════════════════════════════════════════════
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&"
        "family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap"],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width,initial-scale=1"}],
)
app.title = "India SDG Dashboard — G Chaitanya Venkatesh"
server = app.server

# Inject CSS via a server-side asset
app.index_string = f"""
<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    <style>{INLINE_CSS}</style>
</head>
<body>
    {{%app_entry%}}
    <footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer>
</body>
</html>
"""

app.layout = html.Div([
    splash,
    dcc.Store(id="active-tab", data="tab-overview"),
    # Main content (shown after splash)
    html.Div([
        navbar,
        html.Div(id="tab-content", style={
            "padding": "24px 28px", "maxWidth": "1380px",
            "margin": "0 auto", "minHeight": "calc(100vh - 130px)",
        }),
        # Footer
        html.Div([
            html.Hr(style={"borderColor": C["border"], "margin": "0"}),
            html.Div(
                "India SDG 1 & 2 Dashboard  ·  G Chaitanya Venkatesh  ·  M2025ANL013  ·  "
                "MSc Analytics  ·  TISS Mumbai  ·  "
                "Data: UN SDG Portal, NFHS-5, World Bank, FAO, GHI 2023, NITI Aayog",
                style={"padding": "14px 28px", "textAlign": "center",
                       "color": C["muted"], "fontSize": "10px", "letterSpacing": "1px"},
            ),
        ], style={"background": C["bg2"], "marginTop": "40px"}),
    ], id="main-content", style={"display": "none"}),
], style={"background": C["bg"], "minHeight": "100vh"})


# ══════════════════════════════════════════════════════════════════════
#  CALLBACKS
# ══════════════════════════════════════════════════════════════════════

# Splash dismiss
app.clientside_callback(
    """
    function(n) {
        if (n && n > 0) {
            var splash = document.getElementById('splash-screen');
            var main   = document.getElementById('main-content');
            if (!splash || !main) return window.dash_clientside.no_update;
            splash.style.opacity  = '0';
            splash.style.pointerEvents = 'none';
            main.style.display = 'block';
            main.style.opacity = '0';
            setTimeout(function() {
                main.style.transition = 'opacity 0.6s';
                main.style.opacity = '1';
                setTimeout(function() { splash.style.display = 'none'; }, 800);
            }, 100);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("splash-screen", "className"),
    Input("enter-btn", "n_clicks"),
    prevent_initial_call=True,
)

# Tab navigation — set active tab
@callback(
    Output("active-tab", "data"),
    [Input(f"nav-{tid}", "n_clicks") for _, _, tid in TABS_CONFIG],
    prevent_initial_call=True,
)
def update_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return btn_id.replace("nav-", "")

# Nav button highlighting
for _, _, tid in TABS_CONFIG:
    app.clientside_callback(
        f"""
        function(activeTab) {{
            return activeTab === '{tid}' ? 'nav-tab active' : 'nav-tab';
        }}
        """,
        Output(f"nav-{tid}", "className"),
        Input("active-tab", "data"),
    )

# Render tab content
@callback(Output("tab-content", "children"), Input("active-tab", "data"))
def render_tab(tab):
    if tab == "tab-overview":    return build_overview()
    if tab == "tab-sdg1":       return build_sdg1()
    if tab == "tab-sdg2":       return build_sdg2()
    if tab == "tab-compare":    return build_compare()
    if tab == "tab-challenges": return build_challenges()
    if tab == "tab-schemes":    return build_schemes()
    if tab == "tab-report":     return build_report()
    if tab == "tab-methodology":return build_methodology()
    if tab == "tab-about":      return build_about()
    return build_overview()


# ── SDG1 charts ───────────────────────────────────────────────────────
@callback(
    [Output("fig-poverty-trend", "figure"),
     Output("fig-mpi-states",    "figure"),
     Output("fig-pmjdy",         "figure"),
     Output("fig-mgnregs",       "figure")],
    [Input("active-tab", "data"),
     Input("sdg1-year-range", "value")],
)
def update_sdg1_figs(tab, yr):
    if tab != "tab-sdg1":
        return [dash.no_update] * 4
    y0, y1 = (yr[0], yr[1]) if yr else (1993, 2023)
    return make_poverty_trend(y0, y1), make_mpi_states(), make_pmjdy(), make_mgnregs()


# ── SDG2 charts ───────────────────────────────────────────────────────
@callback(
    [Output("fig-hunger-trends",    "figure"),
     Output("fig-nfhs-compare",     "figure"),
     Output("fig-food-insecurity",  "figure"),
     Output("fig-ghi-gauge",        "figure")],
    Input("active-tab", "data"),
)
def update_sdg2_figs(tab):
    if tab != "tab-sdg2":
        return [dash.no_update] * 4
    return (make_hunger_trends(), make_nfhs_compare(),
            make_food_insecurity(), make_ghi_gauge())


# ── Compare charts ────────────────────────────────────────────────────
@callback(
    [Output("fig-ghi-compare",      "figure"),
     Output("fig-stunting-compare", "figure")],
    Input("active-tab", "data"),
)
def update_compare_figs(tab):
    if tab != "tab-compare":
        return [dash.no_update] * 2
    return make_ghi_compare(), make_stunting_compare()


# ── Challenge radar ───────────────────────────────────────────────────
@callback(
    Output("fig-radar-challenge", "figure"),
    Input("active-tab", "data"),
)
def update_challenge_figs(tab):
    if tab != "tab-challenges":
        return dash.no_update
    return make_radar_challenge()


# ── Overview poverty trend (on Overview tab) ──────────────────────────
# (overview uses static figures embedded in the layout;
#  no callbacks needed since build_overview() is called fresh each time)


# ── Report: preview ───────────────────────────────────────────────────
@callback(
    Output("report-preview", "children"),
    Input("preview-report-btn", "n_clicks"),
    [State("rep-sections", "value"),
     State("rep-name",     "value"),
     State("rep-enrol",    "value")],
    prevent_initial_call=True,
)
def preview_report(n, sections, name, enrol):
    if not n:
        return dash.no_update
    sects = build_report_sections(sections or [], name or "—", enrol or "—")
    return "\n\n".join(
        f"{t}\n{'─' * min(len(t), 72)}\n{b}" for t, b in sects
    )


# ── Report: PDF download ──────────────────────────────────────────────
@callback(
    Output("download-report", "data"),
    Input("download-report-btn", "n_clicks"),
    [State("rep-sections", "value"),
     State("rep-name",     "value"),
     State("rep-enrol",    "value")],
    prevent_initial_call=True,
)
def download_report(n, sections, name, enrol):
    if not n:
        return dash.no_update
    sects    = build_report_sections(sections or [], name or "Student", enrol or "")
    pdf_data = build_pdf_bytes(sects, name or "Student", enrol or "")
    safe     = re.sub(r"[^\w\-]", "_", (name or "Student").strip())[:40]
    return dcc.send_bytes(pdf_data, filename=f"{safe}_India_SDG_Report.pdf")


# ══════════════════════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════════════════════
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == "__main__":
    print("=" * 60)
    print("  INDIA SDG INTELLIGENCE DASHBOARD")
    print("  G Chaitanya Venkatesh  |  M2025ANL013")
    print("  MSc Analytics — TISS Mumbai")
    print("=" * 60)
    print("  Starting server at http://127.0.0.1:8050")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    threading.Timer(2, open_browser).start()
    app.run(debug=False, host="127.0.0.1", port=8050, use_reloader=False)
