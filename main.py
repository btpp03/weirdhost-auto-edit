import os
import re
from playwright.sync_api import sync_playwright, TimeoutError

REMEMBER_WEB_COOKIE = os.environ.get("REMEMBER_WEB_COOKIE")

def add_server_time(server_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            # 设置 Cookie 登录
            if REMEMBER_WEB_COOKIE:
                context.add_cookies([{
                    "name": "remember_web",
                    "value": REMEMBER_WEB_COOKIE,
                    "url": "https://hub.weirdhost.xyz"
                }])

            page = context.new_page()
            page.goto(server_url)

            # 匹配 “时间追加” 按钮（有空格 / 没空格都能匹配）
            page.get_by_role("button", name=re.compile("시간 ?추가")).click(timeout=5000)

            print(f"✅ 成功续期: {server_url}")

            browser.close()
    except TimeoutError:
        print(f"⚠️ 找不到按钮或页面加载超时: {server_url}")
    except Exception as e:
        print(f"❌ 续期失败 {server_url}: {e}")

if __name__ == "__main__":
    # 两个实例都跑一次
    servers = [
        "https://hub.weirdhost.xyz/server/ef806adc",
        "https://hub.weirdhost.xyz/server/b52faaa2"
    ]
    for url in servers:
        add_server_time(url)
