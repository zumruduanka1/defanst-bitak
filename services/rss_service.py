import requests, re, html

def fetch_rss():
    urls = [
        "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr",
        "https://www.trthaber.com/rss/manset.rss",
        "https://www.ntv.com.tr/rss",
        "https://www.sozcu.com.tr/rss.xml"
    ]

    data = []

    for u in urls:
        try:
            r = requests.get(u, timeout=5)
            items = re.findall(r"<item>(.*?)</item>", r.text, re.S)

            for i in items[:6]:
                title = re.search(r"<title>(.*?)</title>", i)
                if title:
                    data.append({"text": html.unescape(title.group(1))})
        except:
            pass

    return data