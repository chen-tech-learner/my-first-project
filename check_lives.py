import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 8

# 测试链接是否存活
def test_url(url):
    try:
        r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False

# 读取原始点播sites
def load_sites():
    try:
        with open("cdychj1.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw.get("sites", [])
    except:
        return []

# 读取原始直播lives
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
            # ✅直接保留原名，不自动改名
            out_sites.append(item)

    out_lives = []
    for item in load_lives():
        url = item.get("url", "")
        if test_url(url):
            # ✅直接保留原名，不自动改名
            out_lives.append(item)

    final = {
        "sites": out_sites,
        "lives": out_lives
    }
    # ✅ensure_ascii=False → 中文正常，不会变成\u编码
    with open("live_ok.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    # 导出纯直播m3u
    m3u_text = "#EXTM3U\n"
    for it in out_lives:
        m3u_text += f'#EXTINF:-1,{it["name"]}\n{it["url"]}\n'
    with open("live_ok.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_text)
