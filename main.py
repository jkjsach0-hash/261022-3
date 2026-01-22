import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 (가장 먼저 실행되어야 합니다)
st.set_page_config(
    page_title="대한민국 인구 현황", 
    page_icon="📊", 
    layout="wide"
)

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 파일명이 길 경우 업로드한 파일명과 정확히 일치시켜주세요.
    file_path = '202512_202512____________________________.csv'
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    
    # 전처리: '행정구역'에서 지역명만 추출
    df['지역명'] = df['행정구역'].apply(lambda x: x.split('(')[0].strip())
    
    # 컬럼명에서 불필요한 접두사 제거 (데이터 핸들링 편의성)
    df.columns = [col.replace('2025년12월_계_', '') for col in df.columns]
    return df

# 데이터 불러오기
try:
    df = load_data()
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. GitHub 리포지토리에 파일이 있는지 확인해주세요.")
    st.stop()

# 3. 메인 화면 제목
st.title("🇰🇷 대한민국 인구 현황")
st.markdown("---") # 구분선

# 4. 사이드바 설정
st.sidebar.title("📍 지역 설정")
target_city = st.sidebar.selectbox("조회할 지역을 선택하세요", df['지역명'].unique())

# 데이터 필터링
selected_df = df[df['지역명'] == target_city]
total_pop = selected_df['총인구수'].values[0]

# 5. 대시보드 콘텐츠
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📌 지역 요약")
    st.metric(label="총 인구수", value=f"{total_pop:,} 명")
    st.info(f"현재 보고 계신 데이터는 **2025년 12월** 기준 {target_city}의 통계입니다.")

with col2:
    st.subheader("🎂 연령별 인구 분포")
    
    # 연령 컬럼(0세~100세 이상)만 추출하여 차트 데이터 생성
    age_cols = [col for col in df.columns if '세' in col and '구간' not in col]
    age_values = selected_df[age_cols].iloc[0]
    
    chart_data = pd.DataFrame({
        '연령': age_cols,
        '인구수': age_values.values
    })

    fig = px.bar(chart_data, x='연령', y='인구수', 
                 color='인구수', color_continuous_scale='Viridis',
                 labels={'인구수': '명', '연령': '나이'})
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 6. 데이터 하단 테이블
with st.expander("📄 원본 데이터 보기"):
    st.dataframe(selected_df)
