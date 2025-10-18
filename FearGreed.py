import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fear_and_greed import get
import requests
import numpy as np

# =============================
# 데이터 불러오기
# =============================
fng = get()
current_score = round(fng.value)
current_rating = fng.description.upper()

url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
data = response.json()
historical = data['fear_and_greed_historical']['data']
df = pd.DataFrame(historical)
df['x'] = pd.to_datetime(df['x'] / 1000, unit='s')
df = df.rename(columns={'x': 'Date', 'y': 'Score'})

# =============================
# CNN 스타일 게이지 생성
# =============================
def cnn_gauge(value):
    # 구간별 색상
    colors = ['#d9534f', '#f0ad4e', '#f7f7f7', '#5bc0de', '#5cb85c']
    labels = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']

    # 게이지 영역을 파이차트로 (반원)
    values = [20, 20, 20, 20, 20, 100]  # 마지막은 투명한 반쪽 (숨김용)
    fig = go.Figure(data=[
        go.Pie(
            values=values,
            rotation=90,
            hole=0.7,
            marker_colors=colors + ['rgba(0,0,0,0)'],
            text=labels + [''],
            textinfo='text',
            textposition='outside',
            direction='clockwise',
            sort=False,
            showlegend=False
        )
    ])

    # 바늘 위치 계산 (값을 0~180도에 매핑)
    theta = 180 * (value / 100)
    r = 0.5
    x_head = 0.5 + r * np.cos(np.radians(180 - theta))
    y_head = 0.5 + r * np.sin(np.radians(180 - theta))

    # 바늘 (검은색 선)
    fig.add_trace(go.Scatter(
        x=[0.5, x_head],
        y=[0.5, y_head],
        mode='lines',
        line=dict(color='black', width=4),
        showlegend=False
    ))

    # 중앙 텍스트 (현재 값)
    fig.add_annotation(
        x=0.5, y=0.35,
        text=f"<b>{value}</b>",
        showarrow=False,
        font=dict(size=36, color="black")
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=400,
        width=700,
        paper_bgcolor='white',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False)
    )
    return fig

# =============================
# Streamlit UI
# =============================
st.set_page_config(page_title="Fear & Greed Index Dashboard", layout="wide")
st.title("🧭 CNN Fear & Greed Index Dashboard")

# CNN 게이지 표시
fig = cnn_gauge(current_score)
st.plotly_chart(fig, use_container_width=True)

# 비교 정보 표시
col1, col2, col3, col4 = st.columns(4)
col1.metric("Previous Close", f"{data['fear_and_greed']['previous_close']}", fng.description)
col2.metric("1 Week Ago", f"{data['fear_and_greed']['previous_1_week']}")
col3.metric("1 Month Ago", f"{data['fear_and_greed']['previous_1_month']}")
col4.metric("1 Year Ago", f"{data['fear_and_greed']['previous_1_year']}")

# 역사 데이터 라인 그래프
st.markdown("### 📈 Historical Fear & Greed Index")
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=df['Date'], y=df['Score'], mode='lines', name='Fear & Greed'))
fig_line.update_layout(
    title='Historical Trend',
    xaxis_title='Date',
    yaxis_title='Score (0-100)',
    yaxis_range=[0, 100],
    paper_bgcolor='white'
)
st.plotly_chart(fig_line, use_container_width=True)
