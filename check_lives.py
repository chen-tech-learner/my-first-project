import json
import requests
import re

# 需要扫描的影视仓配置
scan_files = [
    "lives.json",
    "cdychj1.json",
    "cdys620.json"
]
out_m3u = "live_ok.m3u"
out_json = "live_ok.json"
timeout = 10
headers = {"User-Agent": "Mozilla/5.0"}

# 关键词自动识别频道名
def auto_name(url, old_name):
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

def extract_m3u_urls(raw_text):
    pat = re.compile(r'http[s]?://[^\s,#\n]+')
    return pat.findall(raw_text)

def test_url(url):
    try:
        r = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        return r.status_code in (200,301,302)
    except Exception:
        return False

good_items = []
count = 0

for fname in scan_files:
    print(f"\n===== 检测文件：{fname} =====")
    with open(fname, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    lives = cfg.get("lives", [])
    print(f"载入 {len(lives)} 个直播分组")

    for item in lives:
        g_name = item.get("name","无名频道")
        g_url = item.get("url","")
        if not g_url:
            continue
        print(f"\n👉分组【{g_name}】")
        if g_url.endswith((".m3u",".m3u8")):
            try:
                r = requests.get(g_url, timeout=timeout, headers=headers)
                subs = extract_m3u_urls(r.text)
                print(f"解析出 {len(subs)} 条子频道")
                for u in subs:
                    if test_url(u):
                        count += 1
                        cate_name = auto_name(u, g_name)
                        full_name = f"{cate_name}-{count}"
                        good_items.append({
                            "name": full_name,
                            "type": 0,
                            "url": u,
                            "timeout":15
                        })
                        print(f"✅存活 {full_name} | {u}")
                    else:
                        print(f"❌失效 {u}")
            except Exception as e:
                print(f"⚠️拉取m3u失败:{e}")
        else:
            if test_url(g_url):
                cate_name = auto_name(g_url, g_name)
                good_items.append({
                    "name": f"{cate_name}-{g_name}",
                    "type": 0,
                    "url": g_url,
                    "timeout":15
                })
                print(f"✅存活 {g_name} | {g_url}")
            else:
                print(f"❌失效 {g_name} | {g_url}")

# 1. 输出m3u
with open(out_m3u,"w",encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for it in good_items:
        f.write(f"#EXTINF:-1,{it['name']}\n{it['url']}\n")

# 2. 输出影视仓专用json（直接复制替换lives部分）
result_json = {
    "sites": [],
    "lives": good_items
}
with open(out_json,"w",encoding="utf-8") as f:
    json.dump(result_json, f, ensure_ascii=False, indent=2)

print(f"\n===== 检测完成！存活频道总数：{len(good_items)} =====")
print(f"✅已生成 {out_m3u} 和 {out_json}")
print(f"✅live_ok.json 可以直接给影视仓加载使用")
