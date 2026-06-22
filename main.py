from selenium import webdriver

# 不自动关闭浏览器
option = webdriver.ChromeOptions()
option.add_experimental_option("detach", True)

# 注意此处添加了chrome_options参数
driver = webdriver.Chrome(options=option)
driver.get('https://www.yplm.com/#/offering/offeringManage')
