import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re

def add_server_time(server_url="https://hub.weirdhost.xyz/server/c7206128"):
    remember_web_cookie = os.environ.get('REMEMBER_WEB_COOKIE')
    if not remember_web_cookie:
        print("缺少 REMEMBER_WEB_COOKIE")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies([{
            "name": "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d",
            "value": remember_web_cookie,
            "url": "https://hub.weirdhost.xyz"
        }])
        page = context.new_page()
        page.set_default_timeout(60000)

        try:
            page.goto(server_url, wait_until="domcontentloaded")

            # 直接用正则匹配按钮文本，允许前后空格或换行
            regex = re.compile(r"^\s*시간\s*추가\s*$")
            add_button = page.get_by_role("button")
            found = False
            for i in range(add_button.count()):
                text = add_button.nth(i).text_content()
                if text and regex.match(text):
                    add_button.nth(i).click()
                    print("✅ 成功点击按钮！")
                    time.sleep(3)
                    found = True
                    break

            if not found:
                print("⚠️ 未找到 '시간 추가' 按钮。")
                page.screenshot(path="button_not_found.png")
                return False

            return True

        except PlaywrightTimeoutError:
            print("页面加载或操作超时")
            page.screenshot(path="timeout.png")
            return False
        except Exception as e:
            print("执行错误:", e)
            page.screenshot(path="error.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    print("开始执行添加服务器时间任务...")
    success = add_server_time()
    if success:
        print("任务执行成功。")
        exit(0)
    else:
        print("任务执行失败。")
        exit(1)
