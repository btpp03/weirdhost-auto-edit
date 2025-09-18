import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def add_server_time(server_url="https://hub.weirdhost.xyz/server/c7206128"):
    """
    尝试登录 hub.weirdhost.xyz 并点击 "시간 추가" 按钮。
    优先使用 REMEMBER_WEB_COOKIE 进行会话登录，如果不存在则回退到邮箱密码登录。
    """
    # 从环境变量获取登录凭据
    remember_web_cookie = os.environ.get('REMEMBER_WEB_COOKIE')
    pterodactyl_email = os.environ.get('PTERODACTYL_EMAIL')
    pterodactyl_password = os.environ.get('PTERODACTYL_PASSWORD')

    if not (remember_web_cookie or (pterodactyl_email and pterodactyl_password)):
        print("错误: 缺少登录凭据。请设置 REMEMBER_WEB_COOKIE 或 PTERODACTYL_EMAIL 和 PTERODACTYL_PASSWORD 环境变量。")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(90000)  # 默认超时时间 90 秒

        try:
            # --- Cookie 登录 ---
            if remember_web_cookie:
                print("检测到 REMEMBER_WEB_COOKIE，尝试使用 Cookie 登录...")
                session_cookie = {
                    'name': 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d',
                    'value': remember_web_cookie,
                    'domain': 'hub.weirdhost.xyz',
                    'path': '/',
                    'expires': int(time.time()) + 3600 * 24 * 365,
                    'httpOnly': True,
                    'secure': True,
                    'sameSite': 'Lax'
                }
                page.context.add_cookies([session_cookie])
                print(f"已设置 Cookie。正在访问目标服务器页面: {server_url}")

                try:
                    page.goto(server_url, wait_until="domcontentloaded", timeout=90000)
                except PlaywrightTimeoutError:
                    print("页面加载超时（90秒）。")
                    page.screenshot(path="goto_timeout_error.png")

                if "login" in page.url or "auth" in page.url:
                    print("Cookie 登录失败或会话已过期，将回退到邮箱密码登录。")
                    page.context.clear_cookies()
                    remember_web_cookie = None
