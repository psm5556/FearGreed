import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fear_and_greed import get
import requests
import math

st.set_page_config(page_title="Fear & Greed - CNN style gauge", layout="wide")

# -------------------------
# 데이터 (예: 실제 호출)
# -------------------------
try:
    fng = get()
    current_score = int(round(fng.value))
    current_rating = fng.description.title()
except Exception:
    # 로컬 테스트용 fallback
    current_score = 27
    current_rating = "Fear"

# CNN 데이터 (history + comparisons)
try:
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = requests.get(url, headers=headers).json()
except Exception:
    # fallback 더미
    data = {
        "fear_and_greed": {
            "previous_close": 23.35,
            "previous_1_week": 31.73,
            "previous_1_month": 58.46,
            "previous_1_year": 68.57
        },
        "fear_and_greed_historical": {"data": []}
    }

# -------------------------
# CNN 스타일 반원 게이지 함수
# -------------------------
def cnn_semi_gauge(value, size=(700, 420)):
    # segments: Extreme Fear, Fear, Neutral, Greed, Extreme Greed
    seg_colors = ["#d9534f", "#f0ad4e", "#f2f2f2", "#5bc0de", "#5cb85c"]
    seg_labels = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    seg_values = [20, 20, 20, 20, 20]  # equal segments (0-100)

    # We add an invisible half to hide bottom semicircle
    invisible = [0.0001]  # tiny slice to complete circle (or use larger to ensure hide)
    pie_vals = seg_values + invisible
    pie_colors = seg_colors + ["rgba(0,0,0,0)"]

    fig = go.Figure()

    fig.add_trace(go.Pie(
        values=pie_vals,
        marker_colors=pie_colors,
        hole=0.62,
        rotation=180,        # start from left, sweep clockwise
        direction="clockwise",
        sort=False,
        textinfo="none",
        hoverinfo="none",
        showlegend=False,
        domain=dict(x=[0, 1], y=[0, 1])
    ))

    # --- Needle 계산 ---
    # Map value 0..100 -> angle 0..180 degrees (0 at left, 180 at right)
    theta = (value / 100.0) * 180.0
    # convert to plot coordinates: angle measured from left (180 deg) clockwise -> we want trig angle
    # We'll compute angle from x-axis: trig_angle = math.radians(180 - theta)
    trig_angle = math.radians(180 - theta)
    cx, cy = 0.5, 0.5  # center in pie domain coords
    needle_len = 0.38
    x_head = cx + needle_len * math.cos(trig_angle)
    y_head = cy + needle_len * math.sin(trig_angle)

    # base of needle slightly shorter for thickness illusion
    x_base = cx + 0.02 * math.cos(trig_angle + math.pi)
    y_base = cy + 0.02 * math.sin(trig_angle + math.pi)

    # draw needle (thick black line) and a small center circle
    fig.add_trace(go.Scatter(
        x=[x_base, x_head],
        y=[y_base, y_head],
        mode="lines",
        line=dict(color="black", width=9),
        hoverinfo="none",
        showlegend=False
    ))
    # needle tip (thin)
    fig.add_trace(go.Scatter(
        x=[x_base, x_head],
        y=[y_base, y_head],
        mode="lines",
        line=dict(color="black", width=2),
        hoverinfo="none",
        showlegend=False
    ))

    # center white circle to mimic gauge hole
    fig.add_shape(type="circle",
                  xref="paper", yref="paper",
                  x0=0.48, y0=0.36, x1=0.52, y1=0.40,
                  fillcolor="white", line_color="rgba(0,0,0,0)")
    # center score annotation (below center a bit)
    fig.add_annotation(x=0.5, y=0.34, text=f"<b style='font-size:36px'>{value}</b>",
                       showarrow=False, font=dict(size=36, color="black"))

    # ticks 0,25,50,75,100
    tick_vals = [0, 25, 50, 75, 100]
    tick_radius = 0.515
    for t in tick_vals:
        t_theta = math.radians(180 - (t / 100.0) * 180.0)
        tx = cx + tick_radius * math.cos(t_theta)
        ty = cy + tick_radius * math.sin(t_theta)
        fig.add_annotation(x=tx, y=ty, text=str(t), showarrow=False,
                           font=dict(size=12, color="gray"), yshift=-5)

    # segment labels (place outside arcs)
    seg_mid_angles = [10, 45, 90, 135, 170]  # approximate mid positions (deg from left->right)
    label_radius = 0.78
    for lab, ang in zip(seg_labels, seg_mid_angles):
        a = math.radians(180 - ang)
        lx = cx + label_radius * math.cos(a)
        ly = cy + label_radius * math.sin(a)
        fig.add_annotation(x=lx, y=ly, text=f"<b>{lab}</b>", showarrow=False,
                           font=dict(size=13, color="#6b6b6b"))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        width=size[0],
        height=size[1],
        paper_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, visible=False, range=[0, 1])
    )

    # ensure pie appears as perfect semicircle: make plot square-ish and hide axes
    fig.update_traces(hoverinfo="none", textfont_size=12)
    return fig

# -------------------------
# Streamlit 레이아웃
# -------------------------
st.title("CNN Fear & Greed — Semi-circle Gauge (Improved)")

left, right = st.columns([2, 1])

with left:
    fig = cnn_semi_gauge(current_score, size=(820, 460))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    st.markdown("### Current")
    st.markdown(f"**{current_score}**  —  {current_rating}")
    st.write("")
    st.markdown("### Comparisons")
    prev = data["fear_and_greed"]["previous_close"]
    onew = data["fear_and_greed"]["previous_1_week"]
    onem = data["fear_and_greed"]["previous_1_month"]
    oney = data["fear_and_greed"]["previous_1_year"]

    def small_badge(val):
        color = "#5cb85c" if val >= 60 else ("#f0ad4e" if val >= 45 else "#d9534f")
        return f"<div style='display:inline-block;padding:6px 10px;border-radius:20px;background:{color};color:white;font-weight:600'>{val:.0f}</div>"

    st.markdown(f"**Previous Close**  {small_badge(prev)}", unsafe_allow_html=True)
    st.markdown(f"**1 Week Ago**  {small_badge(onew)}", unsafe_allow_html=True)
    st.markdown(f"**1 Month Ago**  {small_badge(onem)}", unsafe_allow_html=True)
    st.markdown(f"**1 Year Ago**  {small_badge(oney)}", unsafe_allow_html=True)

# optional: show history line if available
if data.get("fear_and_greed_historical", {}).get("data"):
    hist = pd.DataFrame(data["fear_and_greed_historical"]["data"])
    hist["x"] = pd.to_datetime(hist["x"] / 1000, unit="s")
    hist = hist.rename(columns={"x": "Date", "y": "Score"})
    st.markdown("### Historical trend")
    fig_line = go.Figure(go.Scatter(x=hist["Date"], y=hist["Score"], mode="lines"))
    fig_line.update_layout(yaxis_range=[0, 100], margin=dict(l=0, r=0, t=20, b=0), height=240)
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
