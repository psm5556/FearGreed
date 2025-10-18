import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
#from fear_and_greed import FearAndGreedIndex
from fear_and_greed import get
import datetime as dt

st.set_page_config(page_title="Fear & Greed Index Dashboard", layout="centered")

st.title("📊 Fear & Greed Index Dashboard")
st.caption("Source: CNN Business / fear-and-greed API")

# 데이터 불러오기
fg = FearAndGreedIndex()
data = fg.get()
df = pd.DataFrame(data)

# 데이터 정리
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# 최신 정보
current_value = df.iloc[-1]["value"]
current_label = df.iloc[-1]["label"]
current_date = df.iloc[-1]["timestamp"].strftime("%Y-%m-%d")

st.metric("Current Index", f"{current_value} ({current_label})", help=f"As of {current_date}")

# 그래프
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df["timestamp"], df["value"], color="royalblue", linewidth=2)
ax.fill_between(df["timestamp"], df["value"], color="lightblue", alpha=0.4)
ax.set_title("Fear & Greed Index Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Index (0=Extreme Fear, 100=Extreme Greed)")
ax.grid(True)
st.pyplot(fig)

# 범례 설명
st.markdown("""
| 구간 | 해석 |
|------|------|
| 0~25 | 😱 극단적 공포 (Extreme Fear) |
| 25~45 | 😟 공포 (Fear) |
| 45~55 | 😐 중립 (Neutral) |
| 55~75 | 😌 탐욕 (Greed) |
| 75~100 | 🤩 극단적 탐욕 (Extreme Greed) |
""")

st.markdown("---")
st.caption("🕒 자동으로 최신 지수가 반영됩니다 (CNN Fear & Greed Index API 기준).")

