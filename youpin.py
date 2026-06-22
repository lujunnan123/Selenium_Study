from time import sleep
from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome配置
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=option)
driver.maximize_window()
# 全局等待器，统一20秒超时
wait = WebDriverWait(driver, 20)

try:
    # 访问页面
    driver.get('https://www.yplm.com/#/offering/offeringManage')

    # 1. 切换标签按钮（去除XPath多余空格，用等待可点击）
    change_xpath = '//div[contains(@class,"arco-tabs-tab") and not(contains(@class,"arco-tabs-tab-active"))]/span'
    change_btn = wait.until(EC.element_to_be_clickable((By.XPATH, change_xpath)))
    change_btn.click()

    # 2. 账号输入框
    user_xpath = '//input[@placeholder="请输入登录账号"]'
    user_text = wait.until(EC.element_to_be_clickable((By.XPATH, user_xpath)))
    user_text.clear()
    user_text.send_keys("15382387085")

    # 3. 密码输入框
    pwd_xpath = '//input[@placeholder="请输入密码"]'
    password_text = wait.until(EC.element_to_be_clickable((By.XPATH, pwd_xpath)))
    password_text.clear()
    password_text.send_keys("yc666888")

    # 4. 勾选协议复选框
    agree_xpath = '//span[contains(@class,"arco-checkbox-icon")]'
    Agreement_btn = wait.until(EC.element_to_be_clickable((By.XPATH, agree_xpath)))
    Agreement_btn.click()

    # 5. 登录按钮
    login_xpath = '//button[contains(@class,"submit-btn") and @type="submit"]'
    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath)))
    login_btn.click()

    # 6. 一级分类列表按钮（核心报错点，加等待）
    first_xpath = "//div[contains(@class,'arco-menu-inline')]//div[contains(@class,'arco-menu-inline-header')]//span[normalize-space()='商品管理' and contains(@class,'arco-menu-title')]"
    first_btn = wait.until(EC.element_to_be_clickable((By.XPATH, first_xpath)))
    first_btn.click()

    # 7. 二级分类列表按钮（核心报错点，加等待）
    second_xpath = "//div[contains(@class,'arco-menu-inline-content')]//div[contains(@class,'arco-menu-item')]//span[normalize-space()='商品管理' and contains(@class,'arco-menu-item-inner')]"
    second_btn = wait.until(EC.element_to_be_clickable((By.XPATH, second_xpath)))
    second_btn.click()

    # 进入已上架页面
    # 8. 点击一级已上架
    sale_xpath = "//span[normalize-space()='已上架' and contains(@class,'arco-tag')]"
    sale_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sale_xpath)))
    sale_btn.click()
    # 9. 点击二级已上架
    sale2_xpath = "//span[contains(@class,'arco-dropdown-option-content')]//div[normalize-space()='已上架']"
    sale2_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sale2_xpath)))
    sale2_btn.click()

    # ========== * 滚动外层主表格，露出查看按钮 ==========
    outer_table_scroll_loc = (By.XPATH,
                              "//div[contains(@class,'arco-table-body') and not(ancestor::div[contains(@class,'arco-overlay-drawer')])]")
    scroll_ele = wait.until(EC.presence_of_element_located(outer_table_scroll_loc))
    sleep(0.2)
    # 水平向右滚动，把操作列（查看）滚到可视区
    driver.execute_script("arguments[0].scrollLeft += 200;", scroll_ele)
    sleep(0.3)

    # 分发翻新
    # 10. 点击查看
    look_xpath = '//a[contains(@class,"arco-link") and normalize-space()="查看"]'
    # ====================== 遍历全部查看按钮 核心改造 ======================
    # 遮罩定位器（全局复用）
    modal_mask = (By.XPATH, "//div[contains(@class,'arco-modal-wrapper')]")
    drawer_mask = (By.XPATH, "//div[contains(@class,'arco-overlay-drawer')]")
    close_btn1_lic=(By.XPATH,"//div[contains(@class,'arco-overlay-drawer')]//div[contains(@class,'arco-drawer-header')]//div[@aria-label='Close' and contains(@class,'arco-drawer-close-btn')]")

    while True:

        # 【关键】每次循环重新查询列表，规避Stale元素
        look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, look_xpath)))
        print(f"当前页面剩余待处理数据：{len(look_list)}")
        if len(look_list) == 0:
            print("所有数据遍历完成，退出循环")
            break
        # ========= 遍历当前页每一条 =========
        for idx in range(len(look_list)):
            print(f"\n===== 开始处理第 {idx + 1}/{len(look_list)} 条 =====")
            try:
                # 每次循环重新获取列表
                temp_look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, look_xpath)))
                item = temp_look_list[idx]
                # 前置等待所有遮罩完全消失
                wait.until(EC.invisibility_of_element_located(modal_mask))
                wait.until(EC.invisibility_of_element_located(drawer_mask))
                sleep(0.3)

                # JS点击查看，规避遮挡拦截
                driver.execute_script("arguments[0].click();", item)

                # 等待抽屉完全渲染
                drawer_x = "//div[contains(@class,'arco-overlay-drawer')]"
                wait.until(EC.visibility_of_element_located((By.XPATH, drawer_x)))
                sleep(0.4)

                # 【重点】移除tr[1]限制，匹配抽屉内任意复选框input
                input_loc = (
                    By.XPATH,
                    "//div[contains(@class,'arco-drawer-body')]//input[contains(@class,'arco-checkbox-target')]"
                )
                check_input = wait.until(EC.presence_of_element_located(input_loc))

                # 完整事件链，保证前端识别勾选
                js_check = """
                       const input = arguments[0];
                       input.checked = true;
                       input.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                       input.dispatchEvent(new Event('change', {bubbles:true, cancelable:true}));
                       input.dispatchEvent(new Event('input', {bubbles:true, cancelable:true}));
                       """
                driver.execute_script(js_check, check_input)
                sleep(0.5)

                # 第一次校验
                checked_status = driver.execute_script("return arguments[0].checked;", check_input)
                print("复选框第一次选中状态：", checked_status)

                # 二次兜底强制勾选
                if not checked_status:
                    print("首次勾选失败，二次强制赋值")
                    driver.execute_script("""
                               arguments[0].checked = true;
                               arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                           """, check_input)
                    sleep(0.3)
                    checked_status = driver.execute_script("return arguments[0].checked;", check_input)
                    print("二次勾选后状态：", checked_status)

                # 勾选失败，关闭抽屉并加长等待，防止下轮超时
                if not checked_status:
                    print("关闭图标渲染c")
                    close_drawer_btn = wait.until(EC.presence_of_element_located(close_btn1_lic))
                    driver.execute_script("arguments[0].click();", close_drawer_btn)
                    print("关闭按钮点击完成")
                    sleep(0.6)  # 加长缓冲，解决TimeoutException
                    continue

                # JS点击分发翻新，避免原生click拦截
                submit_xpath = "//button[normalize-space()='分发翻新']"
                submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, submit_xpath)))
                    # 先判断【分发翻新】是否被禁用，即账号暂未上架
                disabled_val = submit_btn.get_attribute("disabled")
                print("分发按钮禁用状态",disabled_val)
                if disabled_val == "true":
                    print("关闭图标渲染")
                    close_drawer_btn = wait.until(EC.presence_of_element_located(close_btn1_lic))
                    driver.execute_script("arguments[0].click();", close_drawer_btn)
                    print("关闭按钮点击完成")
                    sleep(0.6)  # 加长缓冲，解决TimeoutException
                    continue
                driver.execute_script("arguments[0].click();", submit_btn)

                # 等待首次确认弹窗
                modal_title = (By.XPATH,
                               "//div[contains(@class,'arco-modal-title-align-center') and normalize-space()='分发翻新']")
                title_root = wait.until(EC.visibility_of_element_located(modal_title))
                sleep(0.6)
                # 点击弹窗口中确定按钮
                modal_xpath_str = (
                    By.XPATH,
                    "//div[contains(@class,'arco-modal-container')]//div[contains(@class,'arco-modal-footer')]//button[normalize-space()='确定']"
                )
                modal_btn = wait.until(EC.element_to_be_clickable(modal_xpath_str))
                driver.execute_script("arguments[0].click();", modal_btn)
                sleep(1.2)


                # 点击二次弹窗口中确定按钮
                modal2_title = (By.XPATH,
                               "//div[contains(@class,'arco-modal-title-align-center')  and normalize-space()='确认分发翻新']")
                print("二次弹窗开始渲染")
                title2_root = wait.until(EC.visibility_of_element_located(modal2_title))
                print("二次弹窗渲染完成")
                sleep(1.2)

                # 5-1 点击二次弹窗口中确定按钮

                # 精准XPath：仅标题=确认分发翻新的弹窗内【确认】按钮
                confirm_btn_loc = (By.XPATH, """
                //div[contains(@class,'arco-modal-container')][.//div[normalize-space()="确认分发翻新"]]
                //div[contains(@class,'arco-modal-footer')]//button[normalize-space()="确认"]
                """)
                # 显式等待按钮可点击
                confirm_btn = wait.until(EC.element_to_be_clickable(confirm_btn_loc))
                # JS点击防遮罩拦截
                driver.execute_script("arguments[0].click();", confirm_btn)
                print("二级弹窗确认按钮点击完成")
                sleep(1.2)

                # 6-1 关闭所有弹窗print("查找关闭按钮")
                print("关闭图标渲染c")
                close_drawer_btn = wait.until(EC.presence_of_element_located(close_btn1_lic))
                print("关闭按钮点击完成")
                driver.execute_script("arguments[0].click();", close_drawer_btn)

                # 等待弹窗+抽屉全部消失
                wait.until(EC.invisibility_of_element_located(modal_mask))
                wait.until(EC.invisibility_of_element_located(drawer_mask))
                sleep(0.5)
            except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException) as e:
                print(f"本条数据处理异常：{type(e).__name__} | {e}")
                # 报错瞬间截图，直观查看页面遮罩
                driver.save_screenshot("error_click.png")
                # 兜底强制清除所有弹窗遮罩
                try:
                    modal_mask = (By.XPATH, "//div[contains(@class,'arco-modal-wrapper')]")
                    drawer_mask = (By.XPATH, "//div[contains(@class,'arco-overlay-drawer')]")
                    wait.until(EC.invisibility_of_element_located(modal_mask))
                    wait.until(EC.invisibility_of_element_located(drawer_mask))
                except:
                    pass
                continue

        # ===================== 当前页全部处理完毕，处理分页翻页逻辑 =====================
        print("当前页面所有数据处理完成，检查是否有下一页")
        sleep(1.5)

        try:
            # 等待分页按钮出现
            next_page_loc = (By.XPATH, "//span[contains(@class,'arco-pagination-item-next')]")
            # 等待分页按钮出现
            print("让我找一找下一页按钮...")
            next_btn = wait.until(EC.presence_of_element_located(next_page_loc))
            print("找到下一页按钮了！")
            # 判断是否禁用（arco分页禁用会带aria-disabled="true"）
            aria_dis = next_btn.get_attribute("class")
            print("下一页class值：",aria_dis)
            if 'arco-pagination-item-disabled' in aria_dis:
                print("下一页按钮已禁用，无更多数据，全部处理完毕！")
                break
            # 可点击，执行翻页
            driver.execute_script("arguments[0].click();", next_btn)
            print("已点击下一页，等待表格加载新数据")
            sleep(2.0)
            # 等待表格body重新渲染完成
            wait.until(EC.presence_of_element_located(outer_table_scroll_loc))
        except TimeoutException:
            # 找不到下一页按钮，无分页
            print("未检测到下一页分页按钮，全部数据处理完毕！")
            break


except Exception as e:
    print("执行出错：", e)
    # 出错截图方便定位
    driver.save_screenshot("error.png")
finally:
    # 如需自动关闭取消下面注释
    # sleep(5)
    # driver.quit()
    pass