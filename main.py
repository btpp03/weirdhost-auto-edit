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
                else:
                    print("Cookie 登录成功，已进入服务器页面。")

            # --- 邮箱密码登录 ---
            if not remember_web_cookie:
                if not (pterodactyl_email and pterodactyl_password):
                    print("错误: Cookie 无效，且未提供邮箱或密码，无法登录。")
                    browser.close()
                    return False

                login_url = "https://hub.weirdhost.xyz/auth/login"
                print(f"正在访问登录页面: {login_url}")
                page.goto(login_url, wait_until="domcontentloaded", timeout=90000)

                email_selector = 'input[name="username"]'
                password_selector = 'input[name="password"]'
                login_button_selector = 'button[type="submit"]'

                page.wait_for_selector(email_selector)
                page.wait_for_selector(password_selector)
                page.wait_for_selector(login_button_selector)

                page.fill(email_selector, pterodactyl_email)
                page.fill(password_selector, pterodactyl_password)

                with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
                    page.click(login_button_selector)

                if "login" in page.url or "auth" in page.url:
                    error_text = page.locator('.alert.alert-danger').inner_text().strip() if page.locator('.alert.alert-danger').count() > 0 else "未知错误，URL仍在登录页。"
                    print(f"邮箱密码登录失败: {error_text}")
                    page.screenshot(path="login_fail_error.png")
                    browser.close()
                    return False
                else:
                    print("邮箱密码登录成功。")

            # --- 确保在目标服务器页面 ---
            if page.url != server_url:
                print(f"当前不在目标服务器页面，正在导航至: {server_url}")
                page.goto(server_url, wait_until="domcontentloaded", timeout=90000)
                if "login" in page.url:
                    print("导航失败，会话可能已失效。")
                    page.screenshot(path="server_page_nav_fail.png")
                    browser.close()
                    return False

            # --- 核心操作：查找并点击 "시간 추가" 按钮（兼容前置空格） ---
            print("正在查找并等待 '시간 추가' 按钮（可包含前置空格）...")
            buttons = page.locator("button")
            found = False
            for i in range(buttons.count()):
                text = buttons.nth(i).inner_text().strip()
                if text == "시간 추가":
