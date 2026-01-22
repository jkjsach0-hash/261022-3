import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="대한민국 인구 현황", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    file_path = '202512_202512.csv'
    # 데이터 로드 (천 단위 콤마 제거)
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    
    # 전처리: 행정구역 분리 (예: '서울특별시 종로구 사직동(1111053000)')
    # 1단계: 괄호 앞의 이름만 추출
    df['full_name'] = df['행정구역'].str.split('(').str[0].strip()
    
    # 2단계: 공백 기준으로 시도, 시군구, 읍면동 분리
    # 주의: 세종특별자치시 등 구조가 다른 경우를 위해 가공
    split_names = df['full_name'].str.split()
    df['시도'] = split_names.str[0]
    df['시군구'] = split_names.str[1].fillna('')
    df['읍면동'] = split_names.str[2].fillna('')
    
    # 컬럼명 정리 (접두사 제거)
    df.columns = [col.replace('2025년12월_계_', '') for col in df.columns]
    
    return df

# 데이터 로드
try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 메인 화면 ---
st.title("🇰🇷 대한민국 인구 현황")
st.info("시/도, 시/군/구, 읍/면/동을 순차적으로 선택하여 상세 인구 현황을 확인하세요.")

# 2. 계층형 필터 영역 (하나의 페이지 상단에 구성)
st.subheader("📍 지역 선택")
c1, c2, c3 = st.columns(3)

with c1:
    sido_list = sorted(df['시도'].unique())
    selected_sido = st.selectbox("시/도", sido_list)

with c2:
    # 선택된 시도에 해당하는 시군구 필터링
    sigungu_list = sorted(df[df['시도'] == selected_sido]['시군구'].unique())
    # '전체' 혹은 비어있는 값 제외 로직 추가 가능
    selected_sigungu = st.selectbox("시/군/구", sigungu_list)

with c3:
    # 선택된 시도+시군구에 해당하는 읍면동 필터링
    cond = (df['시도'] == selected_sido) & (df['시군구'] == selected_sigungu)
    dong_list = sorted(df[cond]['읍면동'].unique())
    selected_dong = st.selectbox("읍/면/동", dong_list)

# 최종 선택된 행 데이터
final_cond = (df['시도'] == selected_sido) & \
             (df['시군구'] == selected_sigungu) & \
             (df['읍면동'] == selected_dong)
selected_row = df[final_cond]

st.markdown("---")

# 3. 데이터 시각화
if not selected_row.empty:
    row = selected_row.iloc[0]
    
    # 지표 출력
    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.metric("총 인구수", f"{int(row['총인구수']):,} 명")
        st.write(f"**현재 위치:** {selected_sido} {selected_sigungu} {selected_dong}")
    
    with col_b:
        # 연령별 차트 데이터 준비
        age_cols = [col for col in df.columns if '세' in col and '구간' not in col]
        chart_df = pd.DataFrame({
            '연령': age_cols,
            '인구수': row[age_cols].values
        })
        
        fig = px.bar(chart_df, x='연령', y='인구수', 
                     title=f"[{selected_dong}] 연령별 인구 분포",
                     color='인구수', color_continuous_scale='GnBu')
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # 4. 상세 데이터 테이블
    with st.expander("데이터 상세보기"):
        st.table(selected_row.drop(columns=['full_name', '시도', '시군구', '읍면동']))
else:
    st.warning("해당 조건에 맞는 데이터가 없습니다. 필터를 다시 확인해주세요.")
