import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="대한민국 인구 현황", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    file_path = '202512_202512.csv'
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    
    # 전처리: 행정구역 분리
    df['full_name'] = df['행정구역'].str.split('(').str[0].strip()
    
    # 계층 구조 생성
    split_names = df['full_name'].str.split()
    df['시도'] = split_names.str[0]
    df['시군구'] = split_names.str[1].fillna('전체')
    df['읍면동'] = split_names.str[2].fillna('전체')
    
    # 컬럼명 간소화
    df.columns = [col.replace('2025년12월_계_', '') for col in df.columns]
    
    # 숫자형 변환 (혹시 모를 에러 방지)
    age_cols = [col for col in df.columns if '세' in col and '구간' not in col]
    for col in age_cols + ['총인구수']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df, age_cols

# 데이터 로드
try:
    df, age_cols = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 메인 화면 ---
st.title("🇰🇷 대한민국 인구 현황")
st.markdown("전국 행정구역별 연령 구조를 분석하고 검색할 수 있는 대시보드입니다.")

# 2. 계층형 필터 및 검색 영역
st.subheader("📍 지역 선택 및 검색")
c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 2])

with c1:
    sido_list = sorted(df['시도'].unique())
    selected_sido = st.selectbox("시/도 선택", sido_list)

with c2:
    sigungu_list = sorted(df[df['시도'] == selected_sido]['시군구'].unique())
    selected_sigungu = st.selectbox("시/군/구 선택", sigungu_list)

with c3:
    cond = (df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu)
    dong_list = sorted(df[cond]['읍면동'].unique())
    selected_dong = st.selectbox("읍/면/동 선택", dong_list)

with c4:
    search_query = st.text_input("🔍 지역명으로 직접 검색 (예: 역삼동)", "")

# 필터링 로직 (검색어 우선)
if search_query:
    selected_row = df[df['full_name'].str.contains(search_query)]
    if not selected_row.empty:
        # 검색 결과가 여러 개일 경우 첫 번째 선택
        row = selected_row.iloc[0]
        st.success(f"'{search_query}' 검색 결과: **{row['full_name']}** 데이터가 표시됩니다.")
    else:
        st.warning("검색 결과가 없습니다. 필터를 이용해 주세요.")
        row = df[(df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu) & (df['읍면동'] == selected_dong)].iloc[0]
else:
    row = df[(df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu) & (df['읍면동'] == selected_dong)].iloc[0]
