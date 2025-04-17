import streamlit as st
import os
import requests
import xml.etree.ElementTree as ET
from utils.xml_parser import parse_law_xml, filter_by_logic

st.title("📘 부칙 개정 도우미")
st.markdown("법령 본문 중 검색어를 포함하는 조문을 찾아줍니다.\n\n예시: **A & B , C -D** → A와 B가 모두 포함되거나 C 포함, D는 제외")

query = st.text_input("🔍 찾을 검색어 (다중 검색 지원)", placeholder="예: 지방법원, 지역법원 -지방법원장")
unit = st.radio("검색 단위", options=["조", "항", "선택 없음"], horizontal=True)
if st.button("초기화"):
    st.experimental_rerun()

if st.button("법률 검색") and query:
    with st.spinner(f"🔍 '{query}'을(를) 포함하는 조문을 검색 중입니다..."):
        url = f"http://www.law.go.kr/DRF/lawSearch.do?OC=chetera&target=law&type=XML&display=100&search=2&knd=A0002&query={query}"
        res = requests.get(url)
        res.encoding = 'utf-8'
        law_entries = []
        if res.status_code == 200:
            try:
                root = ET.fromstring(res.content)
                for law in root.findall("law"):
                    name = law.findtext("법령명한글")
                    mst = law.findtext("법령일련번호")
                    detail_url = law.findtext("법령상세링크")
                    law_entries.append((name, mst, detail_url))
            except ET.ParseError:
                st.error("❌ XML 파싱 오류 발생")
        
        for idx, (name, mst, detail_url) in enumerate(law_entries, start=1):
            with st.expander(f"{idx}. {name}"):
                st.markdown(f"[원문 보기]({detail_url})")
                content_url = f"http://www.law.go.kr/DRF/lawService.do?OC=chetera&target=law&type=XML&mst={mst}"
                xml_res = requests.get(content_url)
                xml_res.encoding = 'utf-8'
                if xml_res.status_code == 200:
                    try:
                        law_root = ET.fromstring(xml_res.content)
                        results = parse_law_xml(law_root, query)
                        filtered = filter_by_logic(results, query, unit)
                        if filtered:
                            for line in filtered:
                                st.markdown(line, unsafe_allow_html=True)
                        else:
                            st.info("해당 검색어를 포함한 조문이 없습니다.")
                    except ET.ParseError:
                        st.error("❌ 법령 본문 XML 파싱 오류 발생")
