import json
import re
from collections import defaultdict

# 업종 코드표 정의 (탭 구분 그대로 사용)
sector_code_text = """
시장\t업종구분\t업종코드
K\t\t001
K\t종합(KOSPI)\t001
K\t대형주\t002
K\t중형주\t003
K\t소형주\t004
K\t음식료/담배\t005
K\t섬유/의류\t006
K\t종이/목재\t007
K\t화학\t008
K\t제약\t009
K\t비금속\t010
K\t금속\t011
K\t기계/장비\t012
K\t전기/전자\t013
K\t의료/정밀기기\t014
K\t운송장비/부품\t015
K\t유통\t016
K\t전기/가스\t017
K\t건설\t018
K\t운송/창고\t019
K\t통신\t020
K\t금융\t021
K\t증권\t024
K\t보험\t025
K\t일반서비스\t026
K\t제조\t027
K\t부동산\t028
K\tIT 서비스\t029
K\t오락/문화\t030
Q\t\t101
Q\t종합(KOSDAQ)\t101
Q\t일반서비스\t103
Q\t제조\t106
Q\t건설\t107
Q\t유통\t108
Q\t운송/창고\t110
Q\t금융\t111
Q\t음식료/담배\t115
Q\t섬유/의류\t116
Q\t종이/목재\t117
Q\t출판/매체복제\t118
Q\t화학\t119
Q\t제약\t120
Q\t비금속\t121
Q\t금속\t122
Q\t기계/장비\t123
Q\t전기/전자\t124
Q\t의료/정밀기기\t125
Q\t운송장비/부품\t126
Q\t기타제조\t127
Q\t통신\t128
Q\tIT 서비스\t129
Q\tKOSDAQ 100\t138
Q\tKOSDAQ MID 300\t139
Q\tKOSDAQ SMALL\t140
Q\t오락/문화\t141
Q\t코스닥 우량기업\t142
Q\t코스닥 벤처기업\t143
Q\t코스닥 중견기업\t144
Q\t코스닥 신성장기업\t145
Q\tKOSDAQ 150\t150
Q\t코스닥글로벌지수\t151
Q\tF-KOSDAQ150\t160
Q\tF-KOSDAQ150인버스\t165
"""

# ✅ 업종 코드 맵핑 (빈 업종명도 정확히 등록)
sector_code_table = {}
for line in sector_code_text.strip().splitlines()[1:]:  # 첫 줄 제외
    market, sector, code = line.strip().split('\t')
    sector_code_table[(market, sector)] = code  # strip 하지 않고 그대로 등록

# 📄 데이터 파일 경로 설정
input_file_path = "input.txt"
# output_file_path = "output.json"

# 📥 파일 읽기
with open(input_file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

records = []

# 🔤 특수문자 제거용 정규식
clean_regex = re.compile(r"[^\w\sㄱ-힣\t./]")
# 이 정규식은 다음을 제외한 모든 문자 제거입니다:
# \w: 영문자 + 숫자 + 밑줄 (_)
# \s: 공백 문자 (스페이스, 탭 등)
# ㄱ-힣: 한글 전체
# \t: 탭
# .: 마침표

# 📊 입력 데이터 처리
for line in lines:
    if line.startswith("시장") or not line.strip():
        continue

    # 특수문자 제거
    line = clean_regex.sub('', line)

    def clean_field(field):
        field = field.strip().strip("'").strip('"')  # 앞뒤 따옴표 제거
        field = field.replace(",", "")               # 쉼표 제거
        return field
    parts = [clean_field(p) for p in line.strip().split('\t')]

    if len(parts) != 6:
        continue

    market, sector, name, code, cap, float_ratio = parts

    try:
        cap = int(cap)
    except ValueError:
        continue

    try:
        float_ratio = round(float(float_ratio) / 100, 4)
    except ValueError:
        float_ratio = 0.0

    # 업종코드 처리
    if sector == "은행":
        sector = "금융"  # 예외 처리 추가
        
    # ✅ 업종코드 매핑
    if sector:
        sector_code = sector_code_table.get((market, sector), "000")
    else:
        sector_code = sector_code_table.get((market, ""), "000")

    floating_market_cap = int(cap * float_ratio)

    records.append({
        "업종코드": sector_code,
        "종목명": name,
        "종목코드": code,
        "시가총액": cap,
        "유통비율": float_ratio,
        "유통시총": floating_market_cap
    })

# 📈 업종별 시가총액 합계
sector_sum = defaultdict(int)
for r in records:
    sector_sum[r["업종코드"]] += r["시가총액"]

# 🧮 업종 내 비율 계산
for r in records:
    total = sector_sum[r["업종코드"]]
    ratio = r["시가총액"] / total if total > 0 else 0
    r["업종내비율"] = round(ratio, 6)

# # 💾 JSON 저장
# with open(output_file_path, "w", encoding="utf-8") as f:
#     json.dump(records, f, ensure_ascii=False, indent=2)

# print(f"변환 완료: {output_file_path}")

# ✅ HTML 자동 갱신도 같이 처리 (추가)
html_path = r"index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# stockInfoList 교체
pattern = r"(const\s+stockInfoList\s*=\s*)(\[.*?\])"
replacement = r"\1" + json.dumps(records, ensure_ascii=False, indent=2)
new_html = re.sub(pattern, replacement, html, flags=re.DOTALL)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("✅ HTML 자동 갱신 완료")

