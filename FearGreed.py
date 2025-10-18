import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from fear_and_greed import get
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    """Fear & Greed Index를 위한 클래스 (다른 기능 제거)"""
    
    def __init__(self):
        """초기화"""
        self.fear_greed_current = None
        self.fear_greed_label = None
        self.fear_greed_history = None
        self.current_period = '6mo'  # 기본값
        
        # 기간별 라벨 매핑
        self.period_labels = {
            '1mo': '1개월',
            '3mo': '3개월', 
            '6mo': '6개월',
            '1y': '1년',
            '2y': '2년',
            '5y': '5년'
        }
        
        # 기간별 일수 매핑
        self.period_days = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825
        }
    
    def get_period_days(self, period):
        """기간을 일수로 변환"""
        return self.period_days.get(period, 180)
        
    def get_fear_greed_index(self, period='6mo'):
        """CNN Fear & Greed Index 가져오기"""
        try:
            self.current_period = period  # 현재 기간 저장
            
            # 현재 공포 & 탐욕 지수
            fear_greed_data = get()
            self.fear_greed_current = fear_greed_data.value
            self.fear_greed_label = fear_greed_data.description
            
            print(f"[DEBUG] 공포탐욕지수 수신 성공: {self.fear_greed_current}")
            
        except Exception as e:
            print(f"Fear & Greed Index 가져오기 실패: {e}")
            self.fear_greed_current = 50.0
            self.fear_greed_label = "Neutral"
        
        try:
            # CNN에서 실제 과거 데이터 가져오기
            self.fear_greed_history = self._get_real_fear_greed_history(period)
            if self.fear_greed_history is not None:
                print(f"[DEBUG] 공포탐욕지수 히스토리 생성 완료: {len(self.fear_greed_history)}개 데이터")
            else:
                print("[WARNING] CNN 히스토리 데이터 가져오기 실패")
                
        except Exception as e:
            print(f"공포탐욕지수 히스토리 생성 실패: {e}")
            self.fear_greed_history = None
                
        return self.fear_greed_current
    
    def _get_real_fear_greed_history(self, period='6mo'):
        """실제 CNN Fear & Greed Index 과거 데이터 가져오기"""
        try:
            # CNN Fear & Greed Index API 엔드포인트
            days = self.get_period_days(period)
            url = f"https://production.dataviz.cnn.io/index/fearandgreed/graphdata?start=0&end={days}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'fear_and_greed_historical' in data:
                scores = data['fear_and_greed_historical']
                
                # 데이터프레임으로 변환
                df = pd.DataFrame(scores['data'])
                df['x'] = pd.to_datetime(df['x'], unit='ms')
                df = df.rename(columns={'x': 'Date', 'y': 'Value'})
                df = df[['Date', 'Value']]
                
                return df
                
        except Exception as e:
            print(f"[WARNING] CNN API 데이터 가져오기 실패: {e}")
            return None
    
    def get_fear_greed_chart(self):
        """공포 & 탐욕 지수 차트 생성"""
        period = getattr(self, 'current_period', '6mo')  # 현재 설정된 기간 사용
        
        if self.fear_greed_history is None:
            return go.Figure()
        
        fig = go.Figure()
        
        # 공포 & 탐욕 지수 라인
        fig.add_trace(go.Scatter(
            x=self.fear_greed_history['Date'],
            y=self.fear_greed_history['Value'],
            mode='lines',
            name='Fear & Greed Index',
            line=dict(color='purple', width=2),
            fill='tonexty'
        ))
        
        # 구간별 색상 영역 추가
        fig.add_hline(y=75, line=dict(color="red", width=1, dash="dash"), 
                      annotation_text="극도의 탐욕")
        fig.add_hline(y=55, line=dict(color="orange", width=1, dash="dash"), 
                      annotation_text="탐욕")
        fig.add_hline(y=45, line=dict(color="gray", width=1, dash="dash"), 
                      annotation_text="중립")
        fig.add_hline(y=25, line=dict(color="blue", width=1, dash="dash"), 
                      annotation_text="공포")
        
        # 현재값 포인트 추가
        if self.fear_greed_current and self.fear_greed_history is not None and not self.fear_greed_history.empty:
            fig.add_trace(go.Scatter(
                x=[self.fear_greed_history['Date'].iloc[-1]],
                y=[self.fear_greed_current],
                mode='markers',
                marker=dict(color='red', size=10),
                name=f'현재: {self.fear_greed_current:.1f}'
            ))
        
        period_label = self.period_labels.get(period, period)
        
        fig.update_layout(
            title=f"공포 & 탐욕 지수 ({period_label})",
            xaxis_title="날짜",
            yaxis_title="지수",
            height=300,
            showlegend=True,
            # plot_bgcolor='white',
            # paper_bgcolor='white',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(range=[0, 100], gridcolor='lightgray'),
            margin=dict(t=40, b=40, l=50, r=50)
        )
        
        return fig

# Streamlit 앱 메인 함수
def main():
    st.set_page_config(
        page_title="😨 공포 & 탐욕 지수 앱",
        page_icon="😨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("😨 공포 & 탐욕 지수 앱")
    
    # 사이드바 설정
    st.sidebar.header("🔍 설정")
    
    period = st.sidebar.selectbox(
        "📅 조회 기간 설정",
        options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        index=2,  # 기본값: 6mo
        format_func=lambda x: {
            '1mo': '1개월',
            '3mo': '3개월',
            '6mo': '6개월',
            '1y': '1년',
            '2y': '2년',
            '5y': '5년'
        }[x]
    )
    
    # 분석 시작 버튼
    analyze_button = st.sidebar.button("🚀 데이터 로드", type="primary")
    
    # StockAnalyzer 인스턴스 생성
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = StockAnalyzer()
    
    analyzer = st.session_state.analyzer
    
    # 공포 탐욕 지수 (full width)
    st.subheader("😨 공포 탐욕 지수")
    
    if analyze_button or 'fear_greed_current' in st.session_state:
        try:
            if analyze_button:
                with st.spinner("공포 탐욕 지수 로딩 중..."):
                    fear_greed = analyzer.get_fear_greed_index(period)
                    st.session_state.fear_greed_current = fear_greed
                    st.session_state.fear_greed_label = analyzer.fear_greed_label
                    st.session_state.fear_greed_chart = analyzer.get_fear_greed_chart()
            
            # 현재 지수 표시
            fear_greed = st.session_state.get('fear_greed_current', 50.0)
            fear_greed_label = st.session_state.get('fear_greed_label', 'Neutral')
            
            # 감정 상태 및 색상 결정
            if fear_greed >= 75:
                color = 'red'
                emotion = '극도의 탐욕'
            elif fear_greed >= 55:
                color = 'orange'
                emotion = '탐욕'
            elif fear_greed >= 45:
                color = 'gray'
                emotion = '중립'
            elif fear_greed >= 25:
                color = 'blue'
                emotion = '공포'
            else:
                color = 'darkblue'
                emotion = '극도의 공포'
            
            # 지수와 차트를 나란히 배치
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # 지수 표시
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; border: 2px solid {color}; border-radius: 10px; margin: 10px 0;">
                    <h1 style="color: {color}; margin: 0;">{fear_greed:.1f}</h1>
                    <h3 style="color: {color}; margin: 0;">{emotion}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # 차트 표시
                if 'fear_greed_chart' in st.session_state:
                    st.plotly_chart(st.session_state.fear_greed_chart, use_container_width=True)
                    
        except Exception as e:
            st.error(f"공포 탐욕 지수 로딩 실패: {e}")
            st.markdown("""
            <div style="text-align: center; padding: 20px; border: 2px solid gray; border-radius: 10px; margin: 10px 0;">
                <h1 style="color: gray; margin: 0;">50.0</h1>
                <h3 style="color: gray; margin: 0;">중립 (오류)</h3>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("왼쪽에서 기간을 선택하고 '데이터 로드' 버튼을 클릭하세요.")
    
    # 사이드바에 사용법 설명
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 사용법")
    st.sidebar.markdown("""
    1. **기간 설정**: 조회 기간을 선택하세요  
    2. **데이터 로드**: 버튼을 클릭하여 Fear & Greed Index를 로드하세요
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ 정보")
    st.sidebar.markdown("""
    - 실시간 CNN Fear & Greed Index 기반
    - 과거 히스토리 차트 표시
    - 감정 상태 자동 분류
    """)
    
    # 하단 정보
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    😨 공포 & 탐욕 지수 앱 | 데이터 출처: CNN Money
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
