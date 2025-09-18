import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SERVER_URLS = [
    "https://hub.weirdhost.xyz/server/ef806adc",
    "https://hub.weirdhost.xyz/server/b52faaa2"
]

def click_add_time_button(page):
    """
    查找并点击按钮，其文本可能有前置空格/换行。
    """
    buttons = page.locator("button").all()
    for btn in buttons:
        text = btn.inner_text().strip()
        if text == "시간 추가":
            btn.click()
            return True
    return False

def add_server_time(server_url):
    """
    登录并点击 '시간 추가' 按钮。
    """
    remember_web_cookie = os.environ.get('REMEMBER_WEB_COOKIE')
    pterodactyl_email = os.environ.get('PTERODACTYL_EMAIL')
    pterodactyl_password = os.environ.get('PTERODACTYL_PASSWORD')

    if not (remember_web_cookie or (pterodactyl_email and pterodactyl_password)):
        print("错误: 缺少登录凭据。")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(90000)

        try:
            if remember_web_cookie:
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
                page.goto(server_url, wait_until="domcontentloaded", timeout=90000)
                if "login" in page.url or "auth" in page.url:
                    print("Cookie 登录失败，将回退到邮箱密码登录。")
                    page.context.clear_cookies()
                    remember_web_cookie = None
                else:
                    print(f"Cookie 登录成功: {server_url}")

            if not remember_web_cookie:
                if not (pterodactyl_email and pterodactyl_password):
                    print("无法登录，没有邮箱密码。")
                    browser.close()
                    return False

                login_url = "https://hub.weirdhost.xyz/auth/login"
                page.goto(login_url, wait_until="domcontentloaded", timeout=90000)
                page.fill('input[name="username"]', pterodactyl_email)
                page.fill('input[name="password"]', pterodactyl_password)
                with page.expect_navigation(wait_until="domcontentloaded", timeout=60000):
                    page.click('button[type="submit"]')

                if "login" in page.url or "auth" in page.url:
                    print("邮箱密码登录失败。")
                    page.screenshot(path=f"login_fail_{server_url.split('/')[-1]}.png")
                    browser.close()
                    return False
                else:
                    print(f"邮箱密码登录成功: {server_url}")

            if page.url != server_url:
                page.goto(server_url, wait_until="domcontentloaded", timeout=90000)

            print(f"查找并点击 '시간 추가' 按钮: {server_url}")
            if click_add_time_button(page):
                print(f"成功点击按钮: {server_url}")
                time.sleep(5)
                browser.close()
                return True
            else:
                print(f"未找到 '시간 추가' 按钮: {server_url}")
                page.screenshot(path=f"add_button_not_found_{server_url.split('/')[-1]}.png")
                browser.close()
                return False

        except Exception as e:
            print(f"执行过程中发生未知错误: {e}")
            page.screenshot(path=f"general_error_{server_url.split('/')[-1]}.png")
            browser.close()
            return False

if __name__ == "__main__":
    for url in SERVER_URLS:
        print(f"开始处理服务器: {url}")
        success = add_server_time(url)
        if success:
            print(f"{url} 任务执行成功。")
        else:
            print(f"{url} 任务执行失败。")
