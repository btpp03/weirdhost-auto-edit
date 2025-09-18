import os
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def add_server_time(server_url: str, cookie_value: str):
    """
    使用指定 Cookie 登录 hub.weirdhost.xyz 并点击 “时间追加” 按钮
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 后台运行
        context = browser.new_context()

        # 设置 Cookie
        context.add_cookies([{
            "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d",
            "value": cookie_value,
            "domain": "hub.weirdhost.xyz",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }])

        page = context.new_page()
        page.goto(server_url)

        try:
            # 点击按钮（兼容 “시간추가” 和 “시간 추가”）
            button = page.get_by_role("button", name=re.compile("시간 ?추가"))
            button.click()
            print(f"✅ {server_url} 成功点击【时间追加】按钮")

        except PlaywrightTimeoutError:
            print(f"❌ {server_url} 没找到【时间追加】按钮，可能是未登录或页面更新")

        browser.close()


if __name__ == "__main__":
    # 账号1
    cookie1 = os.getenv("REMEMBER_WEB_COOKIE1")
    server1 = "https://hub.weirdhost.xyz/server/ef806adc"  # 换成账号1的服务器地址

    # 账号2
    cookie2 = os.getenv("REMEMBER_WEB_COOKIE2")
    server2 = "https://hub.weirdhost.xyz/server/b52faaa2"  # 换成账号2的服务器地址

    if cookie1:
        add_server_time(server1, cookie1)

    if cookie2:
        add_server_time(server2, cookie2)
