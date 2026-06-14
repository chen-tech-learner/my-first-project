import requests

# 你的直播源文件
m3u_file = "cd4wb8.m3u"

# 读取原有M3U内容
with open(m3u_file, "r", encoding="utf-8") as f:
    content = f.readlines()

valid = []
i = 0
while i < len(content):
    line = content[i].strip()
    if line.startswith("#EXTINF:-1,"):
        name = line.replace("#EXTINF:-1,", "")
        url = content[i+1].strip()
        # 校验链接
        try:
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                valid.append((name, url))
        except:
            pass
        i += 2
    else:
        i += 1

# 重写文件，只保留有效源
with open(m3u_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for name, url in valid:
        f.write(f"#EXTINF:-1,{name}\n{url}\n")
