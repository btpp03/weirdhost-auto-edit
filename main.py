import os
import re
from playwright.sync_api import sync_playwright, TimeoutError

REMEMBER_WEB_COOKIE = os.environ.get("REMEMBER_WEB_COOKIE")

def add_server_time(server_url):
    try:
        with sync_playwright() as p:
            # GitHub Actions 需要 --no-sandbox
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = browser.new_context()

            # 设置 Cookie 登录
            if REMEMBER_WEB_COOKIE:
                context.add_cookies([{
                    "name": "remember_web",
                    "value": REMEMBER_WEB_COOKIE,
                    "url": "https://hub.weirdhost.xyz"
                }])

            page = context.new_page()
            page.goto(server_url, timeout=30000)  # 最多等30秒页面加载

            print(f"当前页面 URL: {page.url}")

            # 等待按钮出现，最多 15 秒
            try:
                page.get_by_role("button", name=re.compile("시간 ?추가")).wait_for(timeout=15000)
                page.get_by_role("button", name=re.compile("시간 ?추가")).click(timeout=5000)
                print(f"✅ 成功续期: {server_url}")
            except TimeoutError:
                print(f"⚠️ 找不到按钮，可能页面未登录或加载慢: {server_url}")
                print("页面前1000字符内容:\n", page.content()[:1000])

            browser.close()
    except Exception as e:
        print(f"❌ 续期失败 {server_url}: {e}")

if __name__ == "__main__":
    servers = [
        "https://hub.weirdhost.xyz/server/ef806adc",
        "https://hub.weirdhost.xyz/server/b52faaa2"
    ]
    for url in servers:
        add_server_time(url)
