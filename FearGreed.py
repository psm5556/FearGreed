import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# CNN API 데이터 가져오기
url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
data = response.json()
current = data['fear_and_greed']
current_score = round(current['score'])
current_rating = current['rating'].upper()

# 역사적 데이터
historical = data['fear_and_greed_historical']['data']
df = pd.DataFrame(historical)
df['x'] = pd.to_datetime(df['x'] / 1000, unit='s')  # 타임스탬프 변환
df = df.rename(columns={'x': 'Date', 'y': 'Score'})

# 앱 UI
st.title("CNN Fear & Greed Index Dashboard")

# 게이지 형태로 현재 값 표시
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=current_score,
    title={'text': f"Fear & Greed Index<br><span style='font-size:0.8em;color:gray'>{current_rating}</span>"},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "black"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 25], 'color': "red"},
            {'range': [25, 45], 'color': "orange"},
            {'range': [45, 55], 'color': "yellow"},
            {'range': [55, 75], 'color': "lightgreen"},
            {'range': [75, 100], 'color': "green"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': current_score
        }
    }
))
fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
st.plotly_chart(fig_gauge)

# 역사적 차트
st.subheader("Historical Fear & Greed Index")
fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(x=df['Date'], y=df['Score'], mode='lines', name='Fear & Greed'))
fig_hist.update_layout(xaxis_title='Date', yaxis_title='Score (0-100)')
st.plotly_chart(fig_hist)

# 추가: 이전 값 비교
st.subheader("Comparisons")
st.write(f"Previous Close: {current['previous_close']}")
st.write(f"1 Week Ago: {current['previous_1_week']}")
st.write(f"1 Month Ago: {current['previous_1_month']}")
st.write(f"1 Year Ago: {current['previous_1_year']}")
