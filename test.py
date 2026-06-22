from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium import webdriver

# Chrome配置
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=option)
driver.maximize_window()
# 全局等待器，统一20秒超时
wait = WebDriverWait(driver, 20)

wait = WebDriverWait(driver, 20)
look_xpath = '//a[contains(@class,"arco-link") and normalize-space()="查看"]'
modal_mask = (By.XPATH, "//div[contains(@class,'arco-modal-wrapper')]")
drawer_mask = (By.XPATH, "//div[contains(@class,'arco-overlay-drawer')]")

# 外层主表格滚动容器定位（页面底部滚动条）
outer_table_scroll_loc = (By.XPATH, "//div[contains(@class,'arco-table-body') and not(ancestor::div[contains(@class,'arco-drawer-body')])]")

while True:
    # 第一步：滚动外层主表格，露出【查看】按钮
    scroll_outer = wait.until(EC.presence_of_element_located(outer_table_scroll_loc))
    driver.execute_script("arguments[0].scrollLeft += 120;", scroll_outer)
    sleep(0.2)

    # 获取所有查看按钮
    look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, look_xpath)))
    print(f"当前页面剩余待处理数据：{len(look_list)}")
    if len(look_list) == 0:
        print("所有数据遍历完成，退出循环")
        break
    item = look_list[0]

    try:
        # 前置等待所有遮罩消失
        wait.until(EC.invisibility_of_element_located(modal_mask))
        wait.until(EC.invisibility_of_element_located(drawer_mask))

        # JS点击查看a标签，规避表格单元格拦截
        driver.execute_script("arguments[0].click();", item)

        # 等待抽屉渲染完成
        drawer_x = "//div[contains(@class,'arco-overlay-drawer')]"
        wait.until(EC.visibility_of_element_located((By.XPATH, drawer_x)))

        # ========== 抽屉内表格滚动，避开表头遮挡复选框 ==========
        inner_table_scroll_loc = (By.XPATH, "//div[contains(@class,'arco-drawer-body')]//div[contains(@class,'arco-table-body')]")
        scroll_inner = wait.until(EC.presence_of_element_located(inner_table_scroll_loc))
        driver.execute_script("arguments[0].scrollTop += 70;", scroll_inner)
        sleep(0.2)

        # ========== 直接操作原生input勾选，彻底放弃点击label ==========
        input_loc = (
            By.XPATH,
            "//div[contains(@class,'arco-drawer-body')]//tr[contains(@class,'arco-table-tr')][1]//input[contains(@class,'arco-checkbox-target')]"
        )
        check_input = wait.until(EC.presence_of_element_located(input_loc))
        # 滚动input到可视区居中
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", check_input)
        sleep(0.3)

        # 增强JS勾选，派发完整事件链，前端表单识别选中
        js_check = """
        const input = arguments[0];
        const clickEv = new MouseEvent('click', {bubbles:true,cancelable:true});
        input.dispatchEvent(clickEv);
        input.checked = true;
        const changeEv = new Event('change', {bubbles:true,cancelable:true});
        input.dispatchEvent(changeEv);
        input.dispatchEvent(new Event('input', {bubbles:true}));
        """
        driver.execute_script(js_check, check_input)
        sleep(0.5)

        # 校验勾选状态，失败直接跳过本条
        checked_status = driver.execute_script("return arguments[0].checked;", check_input)
        print("复选框最终选中状态：", checked_status)
        if not checked_status:
            print("勾选失败，关闭抽屉跳过本条")
            close_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='关闭']")))
            driver.execute_script("arguments[0].click();", close_btn)
            wait.until(EC.invisibility_of_element_located((By.XPATH, drawer_x)))
            continue

        # 点击抽屉内【分发翻新】按钮
        submit_xpath = "//button[normalize-space()='分发翻新']"
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, submit_xpath)))
        driver.execute_script("arguments[0].click();", submit_btn)

        # 等待弹窗DOM生成（仅presence，不卡死在visibility动画）
        modal_title_loc = (By.XPATH, "//div[contains(@class,'arco-modal-title-align-center') and normalize-space()='分发翻新']")
        wait.until(EC.presence_of_element_located(modal_title_loc))
        sleep(0.8)

        # JS筛选页面最高层级弹窗（解决4个残留modal干扰），自动点击确认
        confirm_js = """
        const allModals = Array.from(document.querySelectorAll('.arco-modal-container'));
        let activeModal = null;
        let maxZ = -1;
        for(let m of allModals){
            const st = window.getComputedStyle(m);
            const z = Number(st.zIndex);
            if(m.offsetParent !== null && Number(st.opacity) > 0 && z > maxZ){
                maxZ = z;
                activeModal = m;
            }
        }
        if(!activeModal) return false;
        const btns = activeModal.querySelectorAll('.arco-btn');
        let confirmBtn = null;
        for(let b of btns){
            const t = b.textContent.trim();
            if(t === "确认"){
                confirmBtn = b;
                break;
            }
        }
        if(!confirmBtn) return false;
        confirmBtn.scrollIntoView({block:"center"});
        confirmBtn.dispatchEvent(new MouseEvent('pointerdown'));
        confirmBtn.click();
        confirmBtn.dispatchEvent(new MouseEvent('pointerup'));
        return true;
        """
        res = driver.execute_script(confirm_js)
        print("确认按钮点击执行结果：", res)
        sleep(0.5)

        # 等待弹窗、抽屉全部关闭消失
        wait.until(EC.invisibility_of_element_located(modal_mask))
        wait.until(EC.invisibility_of_element_located(drawer_mask))

        # 清理页面残留隐藏旧弹窗DOM，避免堆积多个modal
        driver.execute_script("document.querySelectorAll('.arco-modal-container').forEach(m=>{if(m.offsetParent===null)m.remove()})")
        print("本条数据处理完成\n")

    except Exception as e:
        print(f"本条处理异常：{type(e).__name__} | {e}")
        driver.save_screenshot("error_screenshot.png")
        # 异常兜底清除所有遮罩
        try:
            wait.until(EC.invisibility_of_element_located(modal_mask))
            wait.until(EC.invisibility_of_element_located(drawer_mask))
        except:
            pass
        continue