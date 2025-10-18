import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import datetime as dt

st.set_page_config(page_title="Fear & Greed Index Dashboard", layout="centered")
st.title("📊 Fear & Greed Index Dashboard")
st.caption("Source: CNN Business (Fear & Greed Index API)")

# CNN 데이터 요청
url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
r = requests.get(url)
data = r.json()

df = pd.DataFrame(data["fear_and_greed_historical"]["data"])
df["x"] = pd.to_datetime(df["x"], unit="s")
df.rename(columns={"x": "timestamp", "y": "value"}, inplace=True)
df = df.sort_values("timestamp")

current_value = data["fear_and_greed"]["score"]
current_label = data["fear_and_greed"]["rating"]
current_date = dt.datetime.fromtimestamp(data["fear_and_greed"]["timestamp"]).strftime("%Y-%m-%d")

st.metric("Current Index", f"{current_value} ({current_label})", help=f"As of {current_date}")

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df["timestamp"], df["value"], color="royalblue", linewidth=2)
ax.fill_between(df["timestamp"], df["value"], color="lightblue", alpha=0.4)
ax.set_title("Fear & Greed Index Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Index (0 = Extreme Fear, 100 = Extreme Greed)")
ax.grid(True)
st.pyplot(fig)

st.markdown("""
| 구간 | 해석 |
|------|------|
| 0~25 | 😱 극단적 공포 |
| 25~45 | 😟 공포 |
| 45~55 | 😐 중립 |
| 55~75 | 😌 탐욕 |
| 75~100 | 🤩 극단적 탐욕 |
""")
st.caption("🕒 자동으로 CNN의 최신 Fear & Greed 지수를 반영합니다.")
