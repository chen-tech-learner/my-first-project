import json
import requests
import time

# ========== 配置区（小白不用改）==========
JSON_FILE = "lives.json"
TIMEOUT = 8  # 超时8秒判定失效
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
# ========================================

def test_url(url):
    try:
        r = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code < 400:
            return True
        # head失败再试一次get（兼容部分m3u）
        r2 = requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        return r2.status_code <400
    except Exception:
        return False

def main():
    with open(JSON_FILE,"r",encoding="utf-8") as f:
        data = json.load(f)
    
    # 只处理 lives 数组
    old_list = data.get("lives",[])
    new_list = []
    print(f"共载入 {len(old_list)} 条直播源，开始检测...")

    for item in old_list:
        url = item.get("url","")
        if not url:
            continue
        ok = test_url(url)
        if ok:
            new_list.append(item)
            print(f"✅存活：{item['name']}")
        else:
            print(f"❌失效：{item['name']}")
        time.sleep(0.3) # 限速，防止封IP
    
    data["lives"] = new_list
    with open(JSON_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    print(f"\n✅检测完成！存活 {len(new_list)} / {len(old_list)}")

if __name__ == "__main__":
    main()
