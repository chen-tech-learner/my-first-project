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
    except Exception as e:
        print(f"❌读取cdychj1.json异常: {e}")
        return []

def load_lives():
    try:
        with open("lives.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        # 自动判断：顶层是数组直接用；是对象就取lives
        if isinstance(raw, list):
            arr = raw
        else:
            arr = raw.get("lives", [])
        print(f"✅【调试】lives.json读取成功，直播数量={len(arr)}")
        print(json.dumps(arr, indent=2, ensure_ascii=False))
        return arr
    except Exception as e:
        print(f"❌读取lives.json异常: {e}")
        return []

if __name__ == "__main__":
    # 点播去死链
    out_sites = []
    for item in load_sites():
        api = item.get("api", "")
        if test_url(api):
            out_sites.append(item)

    # 直播原样保留，不检测
    out_lives = load_lives()
    print(f"\n✅【最终汇总】直播总数={len(out_lives)}")

    final = {
        "sites": out_sites,
        "lives": out_lives
    }
    # 写入文件：原生中文
    with open("live_ok.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print("✅live_ok.json 写入完成")

    # m3u清单
    m3u_text = "#EXTM3U\n"
    for it in out_lives:
        m3u_text += f'#EXTINF:-1,{it["name"]}\n{it["url"]}\n'
    with open("live_ok.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_text)
    print("✅live_ok.m3u 写入完成")
