import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 (반드시 최상단에 위치해야 합니다)
st.set_page_config(
    page_title="대한민국 인구 현황", 
    page_icon="📊", 
    layout="wide"
)

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 업로드하신 실제 파일명
    file_path = '202512_202512.csv'
    
    # 데이터 읽기
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    
    # [오류 해결 포인트] .str.strip() 사용을 위해 astype(str) 처리
    df['full_name'] = df['행정구역'].astype(str).str.split('(').str[0].str.strip()
    
    # 행정구역 계층 분리 (시도 / 시군구 / 읍면동)
    split_names = df['full_name'].str.split(n=2, expand=True)
    df['시도'] = split_names[0]
    df['시군구'] = split_names[1].fillna('전체')
    df['읍면동'] = split_names[2].fillna('전체')
    
    # 컬럼명 정리 (접두사 제거)
    df.columns = [col.replace('2025년12월_계_', '') for col in df.columns]
    
    # 연령 컬럼 리스트 (0세 ~ 100세 이상)
    age_cols = [col for col in df.columns if '세' in col and '구간' not in col]
    
    # 숫자 데이터 변환 및 결측치 0 처리
    for col in age_cols + ['총인구수']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df, age_cols

# 데이터 실행
try:
    df, age_cols = load_data()
except Exception as e:
    st.error(f"데이터 로딩 중 오류 발생: {e}")
    st.stop()

# --- 화면 구성 ---
st.title("🇰🇷 대한민국 인구 현황")
st.markdown("지역별 연령 분포를 확인하고 검색할 수 있는 대시보드입니다.")
st.markdown("---")

# 3. 상단 필터 및 검색 영역
st.subheader("📍 지역 선택 및 검색")
c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 2])

with c1:
    sido_list = sorted(df['시도'].unique())
    selected_sido = st.selectbox("시/도", sido_list)

with c2:
    sigungu_list = sorted(df[df['시도'] == selected_sido]['시군구'].unique())
    selected_sigungu = st.selectbox("시/군/구", sigungu_list)

with c3:
    dong_cond = (df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu)
    dong_list = sorted(df[dong_cond]['읍면동'].unique())
    selected_dong = st.selectbox("읍/면/동", dong_list)

with c4:
    search_query = st.text_input("🔍 직접 검색 (예: 강남구, 역삼동)", "")

# 데이터 추출 로직
if search_query:
    search_res = df[df['full_name'].str.contains(search_query, na=False)]
    if not search_res.empty:
        row = search_res.iloc[0]
        st.success(f"검색 결과: **{row['full_name']}**")
    else:
        st.warning("검색 결과가 없어 선택된 필터 값을 표시합니다.")
        row = df[(df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu) & (df['읍면동'] == selected_dong)].iloc[0]
else:
    row = df[(df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu) & (df['읍면동'] == selected_dong)].iloc[0]

# 4. 주요 통계 지표
age_data = row[age_cols].values
total_pop = row['총인구수']

# 연령대 그룹핑 (0-14, 15-64, 65+)
youth_pop = sum(age_data[:15])
work_pop = sum(age_data[15:65])
senior_pop = sum(age_data[65:])

m1, m2, m3, m4 = st.columns(4)
m1.metric("총 인구", f"{total_pop:,.0f}명")
m2.metric("유소년(0~14세)", f"{youth_pop:,.0f}명", f"{youth_pop/total_pop*100:.1f}%")
m3.metric("생산가능(15~64세)", f"{work_pop:,.0f}명", f"{work_pop/total_pop*100:.1f}%")
m4.metric("고령(65세+)", f"{senior_pop:,.0f}명", f"{senior_pop/total_pop*100:.1f}%", delta_color="inverse")

# 5. 시각화
st.markdown("---")
l_col, r_col = st.columns([2, 1])

with l_col:
    # 연령별 곡선 (Area Chart)
    chart_df = pd.DataFrame({'연령': age_cols, '인구수': age_data})
    fig_area = px.area(chart_df, x='연령', y='인구수', 
                       title=f"<b>{row['full_name']}</b> 연령별 인구 분포",
                       color_discrete_sequence=['#4A90E2'])
    fig_area.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_area, use_container_width=True)

with r_col:
    # 비중 파이 차트
    pie_df = pd.DataFrame({'구분': ['유소년', '생산가능', '고령'], '인구수': [youth_pop, work_pop, senior_pop]})
    fig_pie = px.pie(pie_df, values='인구수', names='구분', title="연령대 비중", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. 하단 원본 데이터
with st.expander("📄 선택 지역 상세 데이터 보기"):
    st.dataframe(pd.DataFrame(row[age_cols]).T)
