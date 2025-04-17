import re

def extract_text(elem):
    return elem.text.strip() if elem is not None and elem.text else ""

def highlight(text, keywords):
    for kw in keywords:
        text = text.replace(kw, f"<span style='color:red;font-weight:bold'>{kw}</span>")
    return text

def parse_law_xml(root, raw_query):
    results = []
    keywords = re.split(r"[,&\-()\s]+", raw_query)
    keywords = [k.strip() for k in keywords if k.strip()]
    for article in root.findall(".//조문단위"):
        article_num = extract_text(article.find("조문번호"))
        article_title = extract_text(article.find("조문제목"))
        article_text = extract_text(article.find("조문내용"))
        base = f"제{article_num}조({article_title})"
        combined = base + " " + article_text
        matches = [kw for kw in keywords if kw in combined]
        if matches:
            content = f"<b>{base}</b> {highlight(article_text, matches)}"
            항들 = article.findall("항")
            for 항 in 항들:
                항번호 = extract_text(항.find("항번호")).replace("①", "1").replace("②", "2").replace("③", "3")
                항내용 = extract_text(항.find("항내용"))
                content += f"<br>&nbsp;&nbsp;({항번호}) {highlight(항내용, matches)}"
            results.append(content)
    return results

def filter_by_logic(results, query, unit):
    return results
