@st.cache_data
def load_data():
    file_path = '202512_202512____________________________.csv'
    # 데이터 로드
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    
    # [수정] .str을 사용하여 문자열 처리를 명시합니다.
    # 1. 괄호 앞부분만 가져오기
    df['full_name'] = df['행정구역'].astype(str).str.split('(').str[0].str.strip()
    
    # 2. 계층 구조 생성 (공백 기준 분리)
    split_names = df['full_name'].str.split(expand=True)
    
    # 데이터 구조에 따라 컬럼 할당 (예외 처리 포함)
    df['시도'] = split_names[0] if 0 in split_names.columns else '정보없음'
    df['시군구'] = split_names[1] if 1 in split_names.columns else '전체'
    df['읍면동'] = split_names[2] if 2 in split_names.columns else '전체'
    
    # 3. '전체' 및 None 값 채우기
    df['시군구'] = df['시군구'].fillna('전체')
    df['읍면동'] = df['읍면동'].fillna('전체')
    
    # 컬럼명 간소화
    df.columns = [col.replace('2025년12월_계_', '') for col in df.columns]
    
    # 숫자형 변환 (강제 변환 후 결측치 0 처리)
    age_cols = [col for col in df.columns if '세' in col and '구간' not in col]
    for col in age_cols + ['총인구수']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df, age_cols
