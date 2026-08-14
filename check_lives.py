import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 8

# 自动分类命名（点播源）
def auto_site_name(url, old_name):
    txt = (url + " " + old_name).lower()
    if "cat" in txt:
        return "猫源爬虫"
    elif "drpy" in txt:
        return "DRPY解析"
    elif "4k" in txt or "uhd" in txt:
        return "4K影视"
    else:
        return "点播站点"

# 自动分类命名（直播源）
def auto_live_name(url, old_name):
    txt = (url + " " + old_name).lower()
    if "cctv" in txt:
        return "央视频道"
    elif "卫视" in old_name or "weishi" in txt:
        return "卫视频道"
    elif "4k" in txt or "uhd" in txt:
        return "4K专区"
    elif "migu" in txt or "咪咕" in txt or "huya" in txt or "douyu" in txt:
        return "网络直播"
    elif "少儿" in old_name or "卡通" in old_name:
        return "少儿动画"
    elif "电影" in old_name or "院线" in old_name:
        return "电影频道"
    else:
        return "其他直播"

# 链接存活检测
def check_url(url):
    try:
        r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return 200 <= r.status_code < 400
    except Exception:
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            return 200 <= r.status_code < 400
        except Exception:
            return False

# 读取你的原始源文件列表
src_files = ["lives.json", "cdychj1.json", "cdys620.json"]
good_sites = []
good_lives = []
site_count = 0
live_count = 0

for fname in src_files:
    try:
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"【警告】{fname} 读取失败: {e}")
        continue

    # ---------- 检测点播 sites 影视网站 ----------
    if "sites" in data and isinstance(data["sites"], list):
        for item in data["sites"]:
            api_url = item.get("api")
            if not api_url:
                continue
            if check_url(api_url):
                site_count += 1
                new_name = f"{auto_site_name(api_url, item.get('name',''))}-{site_count}"
                new_item = item.copy()
                new_item["name"] = new_name
                good_sites.append(new_item)
                print(f"✅点播存活: {new_name} | {api_url}")
            else:
                print(f"❌点播失效: {item.get('name')} | {api_url}")

    # ---------- 检测直播 lives ----------
    if "lives" in data and isinstance(data["lives"], list):
        for item in data["lives"]:
            live_url = item.get("url")
            if not live_url:
                continue
            if check_url(live_url):
                live_count += 1
                new_name = f"{auto_live_name(live_url, item.get('name',''))}-{live_count}"
                new_item = item.copy()
                new_item["name"] = new_name
                good_lives.append(new_item)
                print(f"✅直播存活: {new_name} | {live_url}")
            else:
                print(f"❌直播失效: {item.get('name')} | {live_url}")

# ---------- 组装最终成品JSON（影视仓直接加载） ----------
out_json = {
    "sites": good_sites,
    "lives": good_lives
}

# 输出影视仓json
with open("live_ok.json", "w", encoding="utf-8") as f:
    json.dump(out_json, f, ensure_ascii=False, indent=2)

# 输出m3u直播备用
with open("live_ok.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for it in good_lives:
        f.write(f'#EXTINF:-1,{it["name"]}\n{it["url"]}\n')

print(f"\n===== 检测汇总 =====")
print(f"✅存活点播站点：{len(good_sites)} 个")
print(f"✅存活直播源：{len(good_lives)} 条")
print(f"📁已生成 live_ok.json / live_ok.m3u")
