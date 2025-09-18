# --- 核心操作：查找并点击 "시간 추가" 按钮（兼容前置空格） ---
add_button_selector = 'button:has-text(/^\s*시간 추가/)'  # 正则匹配开头可能有空格
print(f"正在查找并等待按钮（可包含前置空格）...")

try:
    add_button = page.locator(add_button_selector)
    add_button.wait_for(state='visible', timeout=30000)
    add_button.click()
    print("成功点击 '시간 추가' 按钮。")
    time.sleep(5)  # 等待5秒，确保操作在服务器端生效
    print("任务完成。")
    browser.close()
    return True
except PlaywrightTimeoutError:
    print(f"错误: 在30秒内未找到或按钮不可见/不可点击。")
    page.screenshot(path="add_6h_button_not_found.png")
    browser.close()
    return False
