# 强制预导入chrome全套模块，解决打包缺失问题
import base64
from asyncio import tasks
from unittest import result

import cv2
import numpy as np
import ddddocr
import selenium.webdriver.chrome
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.chrome.service

import os
import re
import sys
import time
import requests
import threading
import tkinter as tk
from time import sleep

from easyocr import easyocr
from selenium.common import StaleElementReferenceException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tkinter import scrolledtext,messagebox

from selenium.webdriver.support.wait import WebDriverWait

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# 获取exe同目录下的chromedriver
driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
service = Service(executable_path=driver_path)

# 初始化识别器，只识别英文数字符号，关闭GPU（本地CPU运行）
# 只初始化一次，不要循环内反复创建，提升速度
reader = easyocr.Reader(['en'], gpu=False)
ocr_engine = ddddocr.DdddOcr(show_ad=False)

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

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)


        # 号商通同步按钮
        sync_btn = tk.Button(
            btn_frame,
            text="号商通同步",
            font=("Arial", 10),
            bg="#0065FF",
            fg="white",
            relief=tk.FLAT,
            command=self.sync_task
        )
        sync_btn.pack(side=tk.LEFT,padx=10)

        # 开始按钮
        start_btn = tk.Button(
            btn_frame,
            text="扫码上号",
            bg="#A151E0",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            command=self.start_task
        )
        start_btn.pack(side=tk.LEFT,padx=10)

        # 日志标签
        tk.Label(root, text="运行日志：", font=("微软雅黑", 10)).pack()
        # 滚动日志文本框
        self.log_text = scrolledtext.ScrolledText(root, width=70, height=12, font=("微软雅黑", 9))
        self.log_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # 默认只读
        # 重定向控制台输出到日志框
        self.log_redirect = LogRedirector(self.log_text, self.root)
        sys.stdout = self.log_redirect

    def sync_task(self):
        if self.is_running:
            messagebox.showinfo("提示","同步自动化正在运行，请勿重复点击！")
            return
        task_thread = threading.Thread(target=self.sync_goods, daemon=True)
        task_thread.start()
        self.is_running = True

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
            wait = WebDriverWait(driver, 8)

            # ====================  新建运营主端页面  ====================
            # 新标签加载目标网址
            print(f"运营主端初始化\n")
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
            print(f"运营页面初始化成功！\n")
            sleep(1)


            # ====================  新建盼之个人中心页面  ====================

            # 执行JS，浏览器新建空白标签
            driver.execute_script("window.open('');")
            # 记录当前旧窗口句柄
            yunyin_handle = driver.current_window_handle
            # 获取全部窗口，切换到新标签
            all_handles = driver.window_handles
            new_handle = all_handles[-1]
            driver.switch_to.window(new_handle)
            print(f"盼之主页初始化\n")
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
            user_text.send_keys("17581687962")
            pwd_xpath = '//input[@placeholder="请输入6-16位内的登录密码"]'
            password_text = wait.until(EC.element_to_be_clickable((By.XPATH, pwd_xpath)))
            password_text.clear()
            password_text.send_keys("Aa123456")
            print("账号密码输入完成——")  # 登录
            login_xpath = '//button[contains(@class,"login-btn") and @type="button"]'
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath)))
            login_btn.click()
            print("登录成功——")

            # 3. 页面跳转
            # 获取当前页面句柄
            person_xpath = "//span[normalize-space()='个人中心']"
            person_btn = wait.until(EC.element_to_be_clickable((By.XPATH, person_xpath)))
            person_btn.click()

            start_time = time.time()
            new_handle = None
            while time.time() - start_time < 10:
                handles = driver.window_handles
                if len(handles) > 1:
                    # 直接取最后一个，不用循环遍历匹配
                    new_handle = handles[-1]
                    break
                time.sleep(0.1)
            if not new_handle:
                print("等待新标签超时，未检测到新窗口——")
            else:
                driver.switch_to.window(new_handle)
                print("已切换至新打开标签页——")

            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            sleep(0.8)
            # 记录当前旧窗口句柄
            panzhi_handle = driver.current_window_handle

            unreleased_xpath = "//div[contains(@class,'item-badge')]"
            unreleased_btn = wait.until(EC.element_to_be_clickable((By.XPATH, unreleased_xpath)))
            unreleased_btn.click()
            print("进入【待发布】")
            print(f"\n盼之页面初始化成功！\n")
            sleep(1)
            print(f"———————————————————————————————————————————")

            # ------------------- 遍历操作 -------------------

            countnum = 0
            errorNum = 0
            while True:
                try:
                    # 获取商品总数
                    goodscount_xpath = "//sup[contains(@class,'el-badge__content')]"
                    try:
                        goods_elem = wait.until(EC.presence_of_element_located((By.XPATH, goodscount_xpath)))
                    except TimeoutException:
                        print("未找到商品总数，可能数量为0")
                    print(goods_elem)
                    if goods_elem:
                        goods_num = int(goods_elem.text)
                        print(f"当前数据总数：{goods_num}")
                    else:
                        print("当前数据总数：0")

                    if goods_num == errorNum and goods_num!= 0:
                        # 当前数据和错误数据一致，新增数据未加入，刷新等待
                        print(f"\n当前数据：{goods_num}，错误数据：{errorNum},无新增数据，等待刷新...")
                        sleep(5)
                        driver.refresh()
                    else:

                        # 获取当前商品列表
                        spdetails_xpath = "//div[contains(@class,'goods-content')]"
                        temp_look_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, spdetails_xpath)))
                        # 永久循环
                        # if len(temp_look_list) == errorNum:
                        #     print(f"\n全部数据处理完毕！")
                        #     break

                        print(f"\n========= 已处理：{countnum}条，异常数据：{errorNum}条  =========\n")
                        temp_look_list[0].click()
                        print("进入【详情页面】——")
                        auth_ok = True
                        try:
                            power_xpath = "//button[normalize-space()='授权上号']"
                            # power_btn = wait.until(EC.element_to_be_clickable((By.XPATH, power_xpath)))
                            power_btn = WebDriverWait(driver,1).until((EC.presence_of_element_located((By.XPATH, power_xpath))))
                            power_btn.click()
                            print("【授权上号】点击 ——")
                        except TimeoutException:
                            errorNum += 1
                            auth_ok = False
                            print("请求超时，跳过此行数据——当前异常数据："+str(errorNum)+f"条\n")
                        except ElementClickInterceptedException:
                            # 按钮被遮挡、无法点击单独捕获
                            errorNum += 1
                            auth_ok = False
                            print("授权按钮被弹窗/遮罩挡住，无法点击")
                        except Exception as e:
                            errorNum += 1
                            auth_ok = False
                            # 兜底所有未知异常，防止程序直接崩停
                            print(f"授权按钮未知异常：{e}")

                        # 授权失败执行
                        if not auth_ok:
                            print('执行失败'+str(auth_ok))
                            driver.back()
                            continue
                        # 获取账号
                        account_xpath = "//span[contains(@class,'account-info')]"
                        account_text = wait.until(EC.visibility_of_element_located((By.XPATH, account_xpath)))
                        account_number =''.join(re.findall(r'\d+',account_text.text))
                        print("当前账号："+account_number+"——")
                        # 获取二维码链接
                        qr_xpath = "//img[contains(@class,'qr-content-img')]"
                        # qr_elem = wait.until(EC.presence_of_element_located((By.XPATH, qr_xpath)))
                        # qr_elem = wait.until(EC.visibility_of_element_located((By.XPATH, qr_xpath)))
                        qr_elem = WebDriverWait(driver,60).until(EC.visibility_of_element_located((By.XPATH, qr_xpath)))
                        qr_url=qr_elem.get_attribute('src')
                        print("成功获取QR码链接："+qr_url+"--")
                        # 下载二维码
                        temp_img_path = "temp_upload_img.png"
                        resp = requests.get(qr_url,timeout=10)
                        with open(temp_img_path, 'wb') as f:
                            f.write(resp.content)

                        # =============================================  运营主端页面  =============================================

                        driver.switch_to.window(yunyin_handle)
                        driver.refresh()
                        try:
                            # 找到搜索框，输入账号
                            # input_xpath3 = "//input[contains(@placeholder,'搜索 QQ号 / 昵称 / 手机号')]"
                            input_xpath3 = "//input[contains(@class,'n-input__input-el')]"
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
                        except StaleElementReferenceException:
                            print("元素陈旧，请刷新")
                            break
                        except TimeoutException:
                            print("获取超时：账号不存在、不在线、已熔断...")
                            # ============ 处理完单个数据后切换回【盼之页面】，返回待发布列表 ==========
                            errorNum += 1
                            driver.switch_to.window(panzhi_handle)
                            driver.back()
                            driver.refresh()
                            continue

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
                        try:
                            obs_path = os.path.abspath(temp_img_path)
                            file_input_xpath ="//input[@class='n-upload-file-input']"
                            file_input = wait.until(EC.presence_of_element_located((By.XPATH,file_input_xpath )))
                            file_input.send_keys(obs_path)
                            print("图片上传完毕--")
                            # 可选：上传后删除临时文件
                            os.remove(obs_path)
                            print("二维码已删除——")
                            sleep(1)
                        except TimeoutException:
                            errorNum += 1
                            print("扫码登录失败,跳过此行")
                            driver.refresh()
                            continue

                        # 点击登录.
                        auth_ok2 = True
                        try:
                            # file_input_xpath = "//div[contains(@class,'n-card-header__main') and contains(normalize-space(),'登录')]"
                            login_xpath3 = "//button[contains(@class,'n-button--medium-type')]//span[normalize-space()='登录' and contains(@class,'n-button__content')]"
                            login_btn3 = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath3)))
                            login_btn3.click()
                            drawer2_xpath = "//div[contains(@class,'n-modal')]"
                            WebDriverWait(driver,60).until(EC.invisibility_of_element_located((By.XPATH,drawer2_xpath)))
                            # sleep(5)
                            countnum +=1
                            print(f"\n扫码登录成功！")

                        except TimeoutException:
                            errorNum += 1
                            auth_ok2 = False
                            print("请求超时，跳过此行数据——当前异常数据："+str(errorNum)+f"条\n")
                        except ElementClickInterceptedException:
                            # 按钮被遮挡、无法点击单独捕获
                            errorNum += 1
                            auth_ok2 = False
                            print("授权按钮被弹窗/遮罩挡住，无法点击")
                        except Exception as e:
                            errorNum += 1
                            auth_ok2 = False
                            # 兜底所有未知异常，防止程序直接崩停
                            print(f"授权按钮未知异常：{e}")

                        # 运营主端，登录时出错
                        if not auth_ok2:
                            print("##登录超时##")
                            driver.refresh()
                            sleep(1)
                            driver.switch_to.window(panzhi_handle)
                            sleep(1)
                            driver.back()
                            sleep(1)
                            driver.refresh()
                            sleep(1)
                            continue


                        # ============ 处理完单个数据后切换回【盼之页面】，返回待发布列表 ==========
                        driver.switch_to.window(panzhi_handle)
                        # sleep(5)
                        # 等扫码弹窗执行完后自动关闭
                        # drawer_xpath = "//div[contains(@class,'third-party-auth-dialog')]"
                        # WebDriverWait(driver,180).until(
                        #     EC.invisibility_of_element_located((By.XPATH,qr_xpath))
                        # )

                        driver.back()
                        sleep(8)
                        driver.refresh()
                except Exception as e:
                    print(e)
                    driver.refresh()
                    continue

        except Exception as e:
            print(e)
        except TimeoutException:
            print("！超时！")

    # easyocr 处理
    # def recognize(self,vfcode_url):
    #     # 分割并清洗base64
    #     if "," in vfcode_url:
    #         b64_part = vfcode_url.split(",")[1]
    #     else:
    #         b64_part = vfcode_url
    #     # 清除空白字符
    #     b64_part = b64_part.translate(str.maketrans("", "", " \n\r\t"))
    #
    #     try:
    #         img_bytes = base64.b64decode(b64_part, validate=True)
    #         print(f"base64解码成功，字节大小：{len(img_bytes)}")
    #         # 临时导出原始数据用于排查
    #         with open("debug_raw.bin", "wb") as f:
    #             f.write(img_bytes)
    #     except Exception as e:
    #         print(f"❌ base64解码异常: {e}")
    #         return None
    #
    #     nparr = np.frombuffer(img_bytes, np.uint8)
    #     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #
    #     if img is None:
    #         print("❌ cv2.imdecode 图像解码失败，二进制数据不是合法图片！")
    #         return None
    #
    #     print(f"✅ 图像加载成功，尺寸：{img.shape}")
    #     scale = 2
    #     img_big = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    #     blue = img_big[:, :, 0]
    #     _, thresh = cv2.threshold(blue, 90, 255, cv2.THRESH_BINARY_INV)
    #     result = reader.readtext(thresh,
    #         detail=0,
    #         allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    #         text_threshold=0.35,    # 降低文本置信阈值，默认0.7
    #         contrast_ths=0.25       # 降低对比度过滤，适配模糊图片)  # # 调试：保存预处理图片，看文字清不清晰
    #     )
    #     text = "".join(result).strip()
    #     print(f"识别结果：[{text}]")
    #     return text
    #
    #     # # 1. 放大 2倍，使用高质量插值
    #     # scale = 2
    #     # img_big = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    #     # # 2.转灰度（不再强行只用蓝色通道，先通用方案）
    #     # gray = cv2.cvtColor(img_big, cv2.COLOR_BGR2GRAY)
    #     # # 3.高斯轻微降噪
    #     # gray = cv2.GaussianBlur(gray, (3, 3), 0)
    #     # # 4.OTSU自动二值化，自动选择阈值
    #     # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    #     # # 可选形态学，修补文字断裂、去除细小噪点
    #     # kernel = np.ones((1, 1), np.uint8)
    #     # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    #     # # 调试：保存预处理图片，看文字清不清晰
    #     # cv2.imwrite("debug_thresh.png", thresh)
    #     # # 5.识别增加关键参数 allowlist，只识别数字+字母，大幅提升检测
    #     # result = self.reader.readtext(
    #     #     thresh,
    #     #     detail=0,
    #     #     allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    #     # )
    #     # print(f"📝原始识别列表：{result}")
    #     # text = "".join(result).strip()
    #     # print(f"✅识别文本：[{text}]")

    # ddddocr处理
    def recognize_captcha(vfcode_url: str) -> str:
        """
        识别蓝色字体数学验证码（适配 8+2=? 这类图片）
        :param vfcode_url: base64字符串，形如 data:image/png;base64,xxxx
        :return: 识别文本 例如 "8+2=?"
        """
        # 清洗base64
        if "," in vfcode_url:
            b64_part = vfcode_url.split(",")[1]
        else:
            b64_part = vfcode_url
        b64_part = b64_part.translate(str.maketrans("", "", " \n\r\t"))

        # base64解码
        try:
            img_bytes = base64.b64decode(b64_part, validate=True)
        except Exception as e:
            print("base64解码失败:", e)
            return ""

        # 转opencv图像
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            print("图像解码失败")
            return ""

        # ==========针对性预处理（适配蓝色文字验证码核心代码）==========
        scale = 2.5
        img_big = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # 提取蓝色通道（BGR顺序，第0通道=蓝色）
        blue_channel = img_big[:, :, 0]

        # 二值化：蓝色区域变白，背景变黑
        _, thresh = cv2.threshold(blue_channel, 80, 255, cv2.THRESH_BINARY_INV)

        # 形态学降噪，消除阴影杂点
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # 调试：保存预处理图片
        # cv2.imwrite("debug_result.png", thresh)

        # 将处理后的图片编码为bytes送入ocr
        _, encode_img = cv2.imencode(".png", thresh)
        result = ocr_engine.classification(encode_img.tobytes())
        text = result.strip()
        print(f"识别结果：[{text}]")
        return text

    def sync_goods(self):


        try:
            print(f"================= 号商通同步功能启动，正在打开浏览器 =================\n")
            # chrome配置
            option = webdriver.ChromeOptions()
            option.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=option, service=service)
            driver.maximize_window()
            wait = WebDriverWait(driver, 8)
            driver.get("https://hst.hswlkj.com/login?redirect=%2Findex")
            # 号商通登录
            user_xpath2 = "//input[contains(@class,'el-input__inner') and contains(@placeholder,'请输入手机号')]"
            user_text2 = wait.until(EC.element_to_be_clickable((By.XPATH, user_xpath2)))
            user_text2.clear()
            user_text2.send_keys("15888809526")
            password_xpath2 = "//input[contains(@class,'el-input__inner') and contains(@placeholder,'请输入密码')]"
            password_text2 = wait.until(EC.element_to_be_clickable((By.XPATH, password_xpath2)))
            password_text2.clear()
            password_text2.send_keys("809526")
            #获取验证码
            vfcode_xpath = "//img[contains(@class,'login-code-img')]"
            vfcode_elem = wait.until(EC.visibility_of_element_located((By.XPATH, vfcode_xpath)))
            vfcode_url=vfcode_elem.get_attribute('src')
            print("验证码地址："+vfcode_url)
            self.recognize_captcha(vfcode_url)

            login_xpath2 = "//button[contains(@class,'form-item-btn')]//span//span[normalize-space()='密码登录']"
            login_btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, login_xpath2)))
            login_btn2.click()
            print(f"号上通登录成功！\n")
            sleep(1)
        except TimeoutException:
            print("超时...")



if __name__ == '__main__':
    root = tk.Tk()
    root.attributes('-topmost', True)
    app = Panzhi(root)
    root.mainloop()
