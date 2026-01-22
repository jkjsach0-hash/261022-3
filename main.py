import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정 (가장 상단에 위치)
st.set_page_config(page_title="인구 통계 대시보드", layout="wide")

@st.cache_data
def load_data():
    # 실제 파일명으로 수정하세요. 파일이 main.py와 같은 폴더에 있어야 합니다.
    file_path = '202512_202512.csv'
    
    # GitHub 환경에서는 경로 인식이 중요합니다.
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    
    # 전처리: 컬럼명 정리
    df['지역명'] = df['행정구역'].apply(lambda x: x.split('(')[0].strip())
    return df

# 데이터 로드
df = load_data()

# --- 사이드바 ---
st.sidebar.title("🔍 필터")
target_city = st.sidebar.selectbox("지역을 선택하세요", df['지역명'].unique())

# 선택된 데이터 추출
selected_df = df[df['지역명'] == target_city]

# --- 메인 화면 ---
st.title(f"📊 {target_city} 인구 분석 리포트")

# 1. 핵심 지표 (Metric)
col1, col2 = st.columns(2)
total_pop = selected_df['2025년12월_계_총인구수'].values[0]
col1.metric("총 인구수", f"{total_pop:,} 명")

# 2. 연령별 분포 그래프 (Plotly 사용)
st.subheader("🎂 연령별 인구 분포")

# 연령 컬럼만 추출 (0세 ~ 100세 이상)
age_columns = [col for col in df.columns if '세' in col and '연령구간' not in col]
age_values = selected_df[age_columns].iloc[0]

# 그래프용 데이터프레임 변환
chart_data = pd.DataFrame({
    '연령': [col.replace('2025년12월_계_', '') for col in age_columns],
    '인구수': age_values.values
})

fig = px.bar(chart_data, x='연령', y='인구수', 
             title=f"{target_city} 연령별 인구수",
             color='인구수', color_continuous_scale='Blues')

st.plotly_chart(fig, use_container_width=True)
