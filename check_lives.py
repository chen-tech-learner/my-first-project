import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 8

# 自动分类命名（点播源）
def auto_site_name(uri, old_name):
    txt = (uri + " " + old_name).lower()
    if "cat" in txt:
        return "猫源爬虫"
    elif "drpy" in txt:
        return "DRPY解析"
    elif "4k" in txt or "uhd" in txt:
        return "4K影视"
    else:
        return "点播站点"

# 自动分类命名（直播源）
def auto_live_name(uri, old_name):
    txt = (uri + " " + old_name).lower()
    if "cctv" in txt:
        return "央视频道"
    elif "卫视" in old_name or "weishi" in txt:
        return "卫视频道"
    elif "migu" in txt:
        return "咪咕直播"
    else:
        return old_name

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
            new_name = auto_site_name(api, item.get("name", ""))
            item["name"] = new_name
            out_sites.append(item)

    out_lives = []
    for item in load_lives():
        url = item.get("url", "")
        if test_url(url):
            new_name = auto_live_name(url, item.get("name", ""))
            item["name"] = new_name
            out_lives.append(item)

    final = {
        "sites": out_sites,
        "lives": out_lives
    }
    # ✅重点：ensure_ascii=False 保留原生中文，不再转\u编码！
    with open("live_ok.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    # 导出纯直播m3u
    m3u_text = "#EXTM3U\n"
    for it in out_lives:
        m3u_text += f'#EXTINF:-1,{it["name"]}\n{it["url"]}\n'
    with open("live_ok.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_text)
