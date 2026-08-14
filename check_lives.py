import json
import requests

# 要检测的json列表（在这里增减）
scan_files = [
    "lives.json",
    "cdychj1.json",
    "cdys620.json"
]

timeout = 10
headers = {"User-Agent": "Mozilla/5.0"}

def test_url(name, url):
    try:
        r = requests.head(url, timeout=timeout, headers=headers)
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
        print(f"共载入 {len(lives)} 条直播源，开始检测…")
        for item in lives:
            n = item.get("name", "无名")
            u = item.get("url", "")
            if not u:
                continue
            total_all +=1
            if test_url(n, u):
                print(f"✅存活: {n}")
                live_all +=1
            else:
                print(f"❌失效: {n}")
    except Exception as e:
        print(f"⚠️读取失败 {fname}：{str(e)}")

print(f"\n===== 全部检测完成 =====")
print(f"总计扫描：{total_all} 条 | 存活：{live_all} 条")
