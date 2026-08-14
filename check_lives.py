import json
import requests
import re

# 要检测的影视仓JSON列表（在这里增减）
scan_files = [
    "lives.json",
    "cdychj1.json",
    "cdys620.json"
]

timeout = 10
headers = {"User-Agent": "Mozilla/5.0"}

# 提取m3u里面所有直播url
def extract_m3u_urls(raw_text):
    pattern = re.compile(r'http[s]?://[^\s,#\n]+')
    return pattern.findall(raw_text)

def test_url(name, url):
    try:
        r = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        if r.status_code in [200, 301, 302]:
            return True
    except Exception:
        pass
    return False

total_all = 0
live_all = 0

for fname in scan_files:
    print(f"\n===== 检测文件：{fname} =====")
    try:
        with open(fname, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        lives = cfg.get("lives", [])
        print(f"载入 {len(lives)} 个直播分组，开始检测…")

        for item in lives:
            group_name = item.get("name", "无名分组")
            group_url = item.get("url", "")
            if not group_url:
                continue

            print(f"\n👉分组【{group_name}】{group_url}")
            # 判断是不是m3u/m3u8远程清单
            if group_url.endswith((".m3u", ".m3u8")):
                try:
                    resp = requests.get(group_url, timeout=timeout, headers=headers)
                    sub_urls = extract_m3u_urls(resp.text)
                    print(f"✅解析出M3U内 {len(sub_urls)} 条子频道")
                    for sub_u in sub_urls:
                        total_all += 1
                        if test_url("子频道", sub_u):
                            print(f"  ✅存活: {sub_u}")
                            live_all += 1
                        else:
                            print(f"  ❌失效: {sub_u}")
                except Exception as e:
                    print(f"  ⚠️拉取M3U失败：{str(e)}")
            else:
                # 普通单条直播链接
                total_all += 1
                if test_url(group_name, group_url):
                    print(f"✅存活: {group_name}")
                    live_all += 1
                else:
                    print(f"❌失效: {group_name}")
    except Exception as e:
        print(f"⚠️读取失败 {fname}：{str(e)}")

print(f"\n===== 全部检测完成 =====")
print(f"✅总计扫描：{total_all} 条频道 | ✅存活：{live_all} 条")
