import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 8

def test_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True, stream=True)
        return r.status_code in (200, 206)
    except Exception:
        return False

def load_sites():
    try:
        with open("cdychj1.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw.get("sites", [])
    except:
        return []

def load_lives():
    try:
        with open("lives.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return raw.get("lives", [])
    except:
        return []

if __name__ == "__main__":
    # 点播：正常检测，剔除死链
    out_sites = []
    for item in load_sites():
        api = item.get("api", "")
        if test_url(api):
            out_sites.append(item)

    # ✅直播：直接原样读取、不做连通性检测，不再误删可用源
    out_lives = load_lives()

    final = {
        "sites": out_sites,
        "lives": out_lives
    }
    # 原生中文输出，不会变成\u编码
    with open("live_ok.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)

    # 同步生成m3u直播清单
    m3u_text = "#EXTM3U\n"
    for it in out_lives:
        m3u_text += f'#EXTINF:-1,{it["name"]}\n{it["url"]}\n'
    with open("live_ok.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_text)
