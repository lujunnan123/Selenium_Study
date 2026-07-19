import os
import re
import sys
import threading
import tkinter as tk
from asyncio.staggered import staggered_race
from time import sleep
import time
import requests
from selenium.common import StaleElementReferenceException

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tkinter import scrolledtext,messagebox

from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from urllib3 import request

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

class Panzhi(tk.Tk):
    def __init__(self,root):
        self.root = root
        self.root.title("Panzhi")
        self.root.geometry("600x400+630+80")
        self.is_running = False

        # 开始按钮
        start_btn = tk.Button(
            text="扫码上号",
            bg="#A151E0",
            fg="white",
            font=("Arial", 12),
            relief=tk.FLAT,
            command=self.start_handle
        )
        start_btn.pack(padx=5,pady=5)

        # 日志标签
        tk.Label(root, text="运行日志：", font=("微软雅黑", 10)).pack()
        # 滚动日志文本框
        self.log_text = scrolledtext.ScrolledText(root, width=70, height=12, font=("微软雅黑", 9))
        self.log_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # 默认只读
        # 重定向控制台输出到日志框
        self.log_redirect = LogRedirector(self.log_text, self.root)
        sys.stdout = self.log_redirect


    def start_task(self):
        if self.is_running:
            messagebox.showinfo("提示", "自动化正在运行，请勿重复点击！")
            return
        task_thread = threading.Thread(target=self.start_handle, daemon=True)
        task_thread.start()
        self.is_running = True

    def start_handle(self):
        try:
            print(f"================= 扫码登录自动化启动，正在打开浏览器 =================\n")
            # chrome配置
            option = webdriver.ChromeOptions()
            option.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=option, service=service)
            driver.maximize_window()
            wait = WebDriverWait(driver, 20)

            driver.get("https://www.pzds.com/login?redirect=%2F")
            # 1.切换登录标签
            change_xpath = "//div[normalize-space()='密码登录']"
            change_btn = wait.until(EC.element_to_be_clickable((By.XPATH, change_xpath)))
            change_btn.click()
            print("切换登录标签完成——")

            # 2.账号密码输入
            user_xpath = '//input[@placeholder="请输入绑定手机号"]'
            user_text = wait.until(EC.element_to_be_clickable((By.XPATH, user_xpath)))
            user_text.clear()
            user_text.send_keys("18058741160")
            pwd_xpath = '//input[@placeholder="请输入6-16位内的登录密码"]'
            password_text = wait.until(EC.element_to_be_clickable((By.XPATH, pwd_xpath)))
            password_text.clear()
            password_text.send_keys("Qwe7899@")
            print("账号密码输入完成——")# 登录
            login_xpath = '//button[contains(@class,"login-btn") and @type="button"]'
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath)))
            login_btn.click()
            print("登录成功——")

            # 3. 页面跳转

            # 获取当前页面句柄
            old_window = driver.current_window_handle
            person_xpath = "//span[normalize-space()='个人中心']"
            person_btn = wait.until(EC.element_to_be_clickable((By.XPATH, person_xpath)))
            person_btn.click()

            start_time = time.time()
            new_handle = None
            while time.time() - start_time < 10:
                handle = driver.window_handles
                if len(handle) > 1:
                    for h in handle:
                        if h!=old_window:
                            new_handle = h
                            break
                    if new_handle:
                        break
                time.sleep(0.1)

            if not new_handle:
                print("等待新标签超时，未检测到新窗口——")
            else:
                driver.switch_to.window(new_handle)
                print("已切换至新打开标签页——")


            wait.until(EC.presence_of_element_located((By.TAG_NAME,"body")))
            sleep(0.8)

            unreleased_xpath = "//div[contains(@class,'item-badge')]"
            unreleased_btn = wait.until(EC.element_to_be_clickable((By.XPATH, unreleased_xpath)))
            unreleased_btn.click()
            print("进入【待发布】——")





            # 获取商品列表
            spDetails_xpath = "//div[contains(@class,'goods-content')]"

            temp_look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, spDetails_xpath)))
            print(temp_look_list)
            print(f"当前页面待处理数据：{len(temp_look_list)}")
            item = temp_look_list[0]
            item.click()
            print("进入【详情页面】——")

            power_xpath = "//button[normalize-space()='授权上号']"
            power_btn = wait.until(EC.element_to_be_clickable((By.XPATH, power_xpath)))
            power_btn.click()
            print("【授权上号】点击 ——")

            # 获取账号
            account_xpath = "//span[contains(@class,'account-info')]"
            account_text = wait.until(EC.visibility_of_element_located((By.XPATH, account_xpath)))
            account_number =''.join(re.findall(r'\d+',account_text.text))
            print("当前账号："+account_number+"——")
            # 获取二维码链接
            QR_xpath = "//img[contains(@class,'qr-content-img')]"
            QR_elem = wait.until(EC.presence_of_element_located((By.XPATH, QR_xpath)))
            QR_url=QR_elem.get_attribute('src')
            print("成功获取QR码链接："+QR_url+"--")
            # 下载二维码
            temp_img_path = "temp_upload_img.png"
            resp = requests.get(QR_url,timeout=10)
            with open(temp_img_path, 'wb') as f:
                f.write(resp.content)
            sleep(5)




            # =============================================  切换页面  =============================================
            # 执行JS，浏览器新建空白标签
            driver.execute_script("window.open('');")
            # 记录当前旧窗口句柄
            penzhi_handle = driver.current_window_handle
            # 获取全部窗口，切换到新标签
            all_handles = driver.window_handles
            new_handle = all_handles[-1]
            driver.switch_to.window(new_handle)
            print(f"\n已切换到新建空白标签——")
            # 新标签加载目标网址
            driver.get("http://kk.onlybaofu.com/login")

            # 运营后台登录
            user_xpath2 = "//input[contains(@class,'n-input__input-el') and contains(@placeholder,'请输入用户名')]"
            user_text2 = wait.until(EC.element_to_be_clickable((By.XPATH, user_xpath2)))
            user_text2.clear()
            user_text2.send_keys("opxx")
            password_xpath2 = "//input[contains(@class,'n-input__input-el') and contains(@placeholder,'请输入密码')]"
            password_text2 = wait.until(EC.element_to_be_clickable((By.XPATH, password_xpath2)))
            password_text2.clear()
            password_text2.send_keys("123456")

            login_xpath2 = "//button[contains(@class,'n-button--medium-type')]//span[normalize-space()='登录']"
            login_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath2)))
            login_btn2.click()

            # 找到搜索框，输入账号
            input_xpath3 = "//input[contains(@placeholder,'搜索 QQ号 / 昵称 / 手机号')]"
            input_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, input_xpath3)))
            input_btn3.clear()
            input_btn3.send_keys(account_number)
            input_btn_xpath = "//span[normalize-space()='搜索']"
            input_btn_btn = wait.until(EC.element_to_be_clickable((By.XPATH, input_btn_xpath)))
            input_btn_btn.click()
            print("搜索完毕--")
            # 等切换搜索完后全部UI加载完毕
            date_xpath = "//td[contains(@class,'n-data-table-td')]"
            wait.until(EC.visibility_of_element_located((By.XPATH,date_xpath)))
            print("数据已加载")
            # 点击扫码登录
            qrlogin_xpath = "//span[normalize-space()='扫码登录']"
            # qrlogin_btn = wait.until(EC.presence_of_element_located((By.XPATH, qrlogin_xpath)))
            # qrlogin_btn.click()
            for  _ in range(2):
                try:
                    qrlogin_btn = wait.until(EC.presence_of_element_located((By.XPATH, qrlogin_xpath)))
                    qrlogin_btn.click()
                    break
                except StaleElementReferenceException:
                    time.sleep(0.3)
            sleep(0.5)
            # 获取上传按钮
            # 转绝对路径
            obs_path = os.path.abspath(temp_img_path)
            file_input_xpath = "//input[@class='n-upload-file-input']"
            file_input = wait.until(EC.presence_of_element_located((By.XPATH,file_input_xpath )))
            file_input.send_keys(obs_path)
            print("图片上传完毕--")
            # 可选：上传后删除临时文件
            # os.remove(obs_path)
            # print("二维码已删除——")
            sleep(1)

            # 点击登录
            login_xpath3 = "//button[contains(@class,'n-button--medium-type')]//span[normalize-space()='登录' and contains(@class,'n-button__content')]"
            login_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath3)))
            login_btn3.click()
            sleep(0.5)
            print(f"\n扫码登录成功！")

            # ============ 处理完单个数据后切换回【盼之页面】，返回待发布列表 ==========
            # 记录当前旧窗口句柄
            yunyin_handle = driver.current_window_handle
            driver.switch_to.window(penzhi_handle)
            sleep(1)
            driver.back()


            # while True:
            #     look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, spDetails_xpath)))
            #     print(f"当前页面待处理数据：{len(look_list)}")
            #     for idx in range(len(look_list)):
            #         print(f"\n========= 开始处理{idx+1}/{len(look_list)}条 =========")
            #         try:
            #
            #             temp_look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, spDetails_xpath)))
            #             item = temp_look_list[idx]
            #             item.click()
            #             print("进入【详情页面】——")
            #
            #         except Exception as e:
            #             print(e)


        except Exception as e:
            print(e)



if __name__ == '__main__':
    root = tk.Tk()
    app = Panzhi(root)
    root.mainloop()
