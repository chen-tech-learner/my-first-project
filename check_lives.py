import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
# 超时拉长到12秒，给国内源更多连接时间
TIMEOUT = 12

def test_url(url):
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
            stream=True
        )
        # 放宽判断：200/206都算存活（很多m3u8分片返回206）
        return r.status_code in (200, 206)
    except Exception:
        return False

# 读取点播
def load_sites():
    try:
        with open("cdychj1.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw.get("sites", [])
    except:
        return []

# 读取直播
def load_lives():
    try:
        with open("lives.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw.get("lives", [])
    except:
        return []

if __name__ == "__main__":
    out_sites = []
    for item in load_sites():
        api = item.get("api", "")
        if test_url(api):
            out_sites.append(item)

    out_lives = []
    for item in load_lives():
        url = item.get("url", "")
        if test_url(url):
            out_lives.append(item)

    final = {
        "sites": out_sites,
        "lives": out_lives
    }
    # 中文原生输出，不转\u编码
    with open("live_ok.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    # 导出m3u
    m3u_text = "#EXTM3U\n"
    for it in out_lives:
        m3u_text += f'#EXTINF:-1,{it["name"]}\n{it["url"]}\n'
    with open("live_ok.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_text)
