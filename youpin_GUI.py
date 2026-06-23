# 强制预导入chrome全套模块，解决打包缺失问题
import selenium.webdriver.chrome
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.chrome.service

from time import sleep
from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys
import os
from selenium.webdriver.chrome.service import Service

# 获取exe同目录下的chromedriver
driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
service = Service(executable_path=driver_path)

# 自定义日志输出类，重定向print到文本框
class LogRedirector:
    def __init__(self, text_widget, root):
        self.text_widget = text_widget
        self.root = root

    def write(self, msg):
        # 使用after主线程更新UI，避免子线程报错
        self.root.after(0, self._insert_log, msg)

    def _insert_log(self, msg):
        if msg.strip() == "":
            return
        # 插入日志并自动滚动到底部
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class Youpin:
    def __init__(self, root):
        self.root = root
        self.root.title("Youpin")
        self.root.geometry("600x400+630+80")
        self.is_running = False

        # 标题
        tk.Label(root, text="游品翻新", font=("微软雅黑", 14, "bold")).pack(pady=10)

        # 开始按钮
        run_btn = tk.Button(
            root,
            text="开始翻新",
            bg="white",
            fg="black",
            font=("微软雅黑", 14, "bold"),
            relief=tk.FLAT,
            command=self.start_task
        )
        run_btn.pack(pady=5)

        # 日志标签
        tk.Label(root, text="运行日志：", font=("微软雅黑", 10)).pack()

        # 滚动日志文本框
        self.log_text = scrolledtext.ScrolledText(root, width=70, height=12, font=("微软雅黑", 9))
        self.log_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # 默认只读

        # 重定向控制台输出到日志框
        self.log_redirect = LogRedirector(self.log_text, self.root)
        sys.stdout = self.log_redirect

    # 按钮点击启动线程
    def start_task(self):
        if self.is_running:
            messagebox.showinfo("提示", "自动化正在运行，请勿重复点击！")
            return
        task_thread = threading.Thread(target=self.allEvents, daemon=True)
        task_thread.start()
        self.is_running = True

    def allEvents(self):
        try:
            print("===== 自动化程序启动，正在打开浏览器 =====")
            # Chrome配置
            option = webdriver.ChromeOptions()
            option.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=option, service=service)
            driver.maximize_window()
            wait = WebDriverWait(driver, 20)

            try:
                print("正在访问系统页面...")
                driver.get('https://www.yplm.com/#/offering/offeringManage')
                # 1.切换标签
                change_xpath = '//div[contains(@class,"arco-tabs-tab") and not(contains(@class,"arco-tabs-tab-active"))]/span'
                change_btn = wait.until(EC.element_to_be_clickable((By.XPATH, change_xpath)))
                change_btn.click()
                print("切换登录标签完成")

                # 账号密码输入
                user_xpath = '//input[@placeholder="请输入登录账号"]'
                user_text = wait.until(EC.element_to_be_clickable((By.XPATH, user_xpath)))
                user_text.clear()
                user_text.send_keys("15382387085")

                pwd_xpath = '//input[@placeholder="请输入密码"]'
                password_text = wait.until(EC.element_to_be_clickable((By.XPATH, pwd_xpath)))
                password_text.clear()
                password_text.send_keys("yc666888")
                print("账号密码输入完成")

                # 勾选协议
                agree_xpath = '//span[contains(@class,"arco-checkbox-icon")]'
                Agreement_btn = wait.until(EC.element_to_be_clickable((By.XPATH, agree_xpath)))
                Agreement_btn.click()
                # 登录
                login_xpath = '//button[contains(@class,"submit-btn") and @type="submit"]'
                login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath)))
                login_btn.click()
                print("点击登录，等待页面加载...")

                # 菜单展开
                first_xpath = "//div[contains(@class,'arco-menu-inline')]//div[contains(@class,'arco-menu-inline-header')]//span[normalize-space()='商品管理' and contains(@class,'arco-menu-title')]"
                first_btn = wait.until(EC.element_to_be_clickable((By.XPATH, first_xpath)))
                first_btn.click()
                second_xpath = "//div[contains(@class,'arco-menu-inline-content')]//div[contains(@class,'arco-menu-item')]//span[normalize-space()='商品管理' and contains(@class,'arco-menu-item-inner')]"
                second_btn = wait.until(EC.element_to_be_clickable((By.XPATH, second_xpath)))
                second_btn.click()
                print("进入商品管理菜单")

                # 筛选已上架
                sale_xpath = "//span[normalize-space()='已上架' and contains(@class,'arco-tag')]"
                sale_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sale_xpath)))
                sale_btn.click()
                sale2_xpath = "//span[contains(@class,'arco-dropdown-option-content')]//div[normalize-space()='已上架']"
                sale2_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sale2_xpath)))
                sale2_btn.click()
                print("筛选【已上架】商品完成")

                outer_table_scroll_loc = (By.XPATH, "//div[contains(@class,'arco-table-body') and not(ancestor::div[contains(@class,'arco-overlay-drawer')])]")
                scroll_ele = wait.until(EC.presence_of_element_located(outer_table_scroll_loc))
                sleep(0.2)
                driver.execute_script("arguments[0].scrollLeft += 200;", scroll_ele)
                sleep(0.3)

                look_xpath = '//a[contains(@class,"arco-link") and normalize-space()="查看"]'
                modal_mask = (By.XPATH, "//div[contains(@class,'arco-modal-wrapper')]")
                drawer_mask = (By.XPATH, "//div[contains(@class,'arco-overlay-drawer')]")
                close_btn1_lic = (By.XPATH, "//div[contains(@class,'arco-overlay-drawer')]//div[contains(@class,'arco-drawer-header')]//div[@aria-label='Close' and contains(@class,'arco-drawer-close-btn')]")

                while True:
                    look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, look_xpath)))
                    print(f"当前页面剩余待处理数据：{len(look_list)}")
                    if len(look_list) == 0:
                        print("当前页无数据，全部处理完成，退出循环")
                        break

                    for idx in range(len(look_list)):
                        print(f"\n===== 开始处理第 {idx + 1}/{len(look_list)} 条 =====")
                        try:
                            temp_look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, look_xpath)))
                            item = temp_look_list[idx]
                            wait.until(EC.invisibility_of_element_located(modal_mask))
                            wait.until(EC.invisibility_of_element_located(drawer_mask))
                            sleep(0.3)
                            driver.execute_script("arguments[0].click();", item)
                            drawer_x = "//div[contains(@class,'arco-overlay-drawer')]"
                            wait.until(EC.visibility_of_element_located((By.XPATH, drawer_x)))
                            sleep(0.4)

                            input_loc = (By.XPATH, "//div[contains(@class,'arco-overlay-drawer')]//tbody/tr[1]//input[contains(@class,'arco-checkbox-target')]")
                            check_input = wait.until(EC.presence_of_element_located(input_loc))
                            js_check = """
                                   const input = arguments[0];
                                   input.checked = true;
                                   input.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                                   input.dispatchEvent(new Event('change', {bubbles:true, cancelable:true}));
                                   input.dispatchEvent(new Event('input', {bubbles:true, cancelable:true}));
                                   """
                            driver.execute_script(js_check, check_input)
                            sleep(0.5)
                            checked_status = driver.execute_script("return arguments[0].checked;", check_input)
                            print("复选框第一次选中状态：", checked_status)
                            if not checked_status:
                                print("-首次勾选失败，二次强制赋值-")
                                driver.execute_script("""
                                           arguments[0].checked = true;
                                           arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                                       """, check_input)
                                sleep(0.3)
                                checked_status = driver.execute_script("return arguments[0].checked;", check_input)
                                print("二次勾选后状态：", checked_status)
                            if not checked_status:
                                print("-勾选失败，关闭抽屉跳过本条-")
                                close_drawer_btn = wait.until(EC.presence_of_element_located(close_btn1_lic))
                                driver.execute_script("arguments[0].click();", close_drawer_btn)
                                sleep(0.6)
                                continue

                            submit_xpath = "//button[normalize-space()='分发翻新']"
                            submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, submit_xpath)))
                            disabled_val = submit_btn.get_attribute("disabled")
                            print("分发按钮禁用状态", disabled_val)
                            if disabled_val == "true":
                                print("-分发按钮禁用，跳过本条-")
                                close_drawer_btn = wait.until(EC.presence_of_element_located(close_btn1_lic))
                                driver.execute_script("arguments[0].click();", close_drawer_btn)
                                sleep(0.6)
                                continue
                            driver.execute_script("arguments[0].click();", submit_btn)

                            modal_title = (By.XPATH, "//div[contains(@class,'arco-modal-title-align-center') and normalize-space()='分发翻新']")
                            title_root = wait.until(EC.visibility_of_element_located(modal_title))
                            sleep(0.6)
                            modal_xpath_str = (By.XPATH, "//div[contains(@class,'arco-modal-container')]//div[contains(@class,'arco-modal-footer')]//button[normalize-space()='确定']")
                            modal_btn = wait.until(EC.element_to_be_clickable(modal_xpath_str))
                            driver.execute_script("arguments[0].click();", modal_btn)
                            sleep(0.8)

                            modal2_title = (By.XPATH, "//div[contains(@class,'arco-modal-title-align-center')  and normalize-space()='确认分发翻新']")
                            print("二次弹窗开始渲染-")
                            title2_root = wait.until(EC.visibility_of_element_located(modal2_title))
                            print("二次弹窗渲染完成-")
                            sleep(0.8)
                            confirm_btn_loc = (By.XPATH, """
                            //div[contains(@class,'arco-modal-container')][.//div[normalize-space()="确认分发翻新"]]
                            //div[contains(@class,'arco-modal-footer')]//button[normalize-space()="确认"]
                            """)
                            confirm_btn = wait.until(EC.element_to_be_clickable(confirm_btn_loc))
                            driver.execute_script("arguments[0].click();", confirm_btn)
                            print("分发翻新成功！-")
                            sleep(0.8)

                            close_drawer_btn = wait.until(EC.presence_of_element_located(close_btn1_lic))
                            driver.execute_script("arguments[0].click();", close_drawer_btn)
                            wait.until(EC.invisibility_of_element_located(modal_mask))
                            wait.until(EC.invisibility_of_element_located(drawer_mask))
                            sleep(0.5)
                        except (TimeoutException, StaleElementReferenceException, ElementClickInterceptedException) as e:
                            print(f"本条数据处理异常：{type(e).__name__} | {e}-")
                            driver.save_screenshot("error_click.png")
                            try:
                                wait.until(EC.invisibility_of_element_located(modal_mask))
                                wait.until(EC.invisibility_of_element_located(drawer_mask))
                            except:
                                pass
                            continue

                    # 分页逻辑
                    print("当前页面所有数据处理完成，检查是否有下一页")
                    sleep(1.5)
                    try:
                        next_page_loc = (By.XPATH, "//span[contains(@class,'arco-pagination-item-next')]")
                        print("让我找一找下一页按钮...")
                        next_btn = wait.until(EC.presence_of_element_located(next_page_loc))
                        print("找到下一页按钮了！-")
                        aria_dis = next_btn.get_attribute("class")
                        print("下一页class值：", aria_dis)
                        if 'arco-pagination-item-disabled' in aria_dis:
                            print("下一页按钮已禁用，无更多数据，全部处理完毕！-")
                            break
                        driver.execute_script("arguments[0].click();", next_btn)
                        print("已点击下一页，等待表格加载新数据-")
                        sleep(2.0)
                        wait.until(EC.presence_of_element_located(outer_table_scroll_loc))
                    except TimeoutException:
                        print("未检测到下一页分页按钮，全部数据处理完毕！-")
                        break

                print("===== 全部商品翻新任务执行完毕 =====")
                # 弹窗提示完成
                self.root.after(0, lambda: messagebox.showinfo("完成", "所有商品处理完成！"))
            except Exception as e:
                print("自动化流程异常：", e)
                driver.save_screenshot("error.png")
        except Exception as e:
            print("程序启动异常：", e)
        finally:
            self.is_running = False
            print("===== 任务结束，可重新点击开始翻新 =====")

if __name__ == '__main__':
    root = tk.Tk()
    app = Youpin(root)
    root.mainloop()