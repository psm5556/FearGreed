import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fear_and_greed import get  # fear-and-greed 라이브러리
import requests  # 대안으로 직접 API 호출 시

# API 데이터 가져오기 (라이브러리 사용)
fng = get()
current_score = round(fng.value)  # 점수 (0-100)
current_rating = fng.description.upper()  # 등급 (e.g., EXTREME FEAR)

# 역사적 데이터 (직접 API 호출로 가져오기, 라이브러리가 지원 안 할 경우)
url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
data = response.json()
historical = data['fear_and_greed_historical']['data']
df = pd.DataFrame(historical)
df['x'] = pd.to_datetime(df['x'] / 1000, unit='s')  # 타임스탬프 변환
df = df.rename(columns={'x': 'Date', 'y': 'Score'})

# 앱 UI
st.title("CNN Fear & Greed Index Dashboard")

# 현재 값 표시
col1, col2 = st.columns(2)
col1.metric("Current Score", current_score)
col2.metric("Current Rating", current_rating)

# 역사적 차트
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Score'], mode='lines', name='Fear & Greed'))
fig.update_layout(title='Historical Fear & Greed Index', xaxis_title='Date', yaxis_title='Score (0-100)')
st.plotly_chart(fig)

# 추가: 이전 값 비교
st.subheader("Comparisons")
st.write(f"Previous Close: {data['fear_and_greed']['previous_close']}")
st.write(f"1 Week Ago: {data['fear_and_greed']['previous_1_week']}")
st.write(f"1 Month Ago: {data['fear_and_greed']['previous_1_month']}")
st.write(f"1 Year Ago: {data['fear_and_greed']['previous_1_year']}")
