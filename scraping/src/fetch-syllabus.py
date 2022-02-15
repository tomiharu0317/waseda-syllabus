import os

from selenium import webdriver


driver = webdriver.Remote(
    command_executor=os.environ["SELENIUM_URL"],
    options=webdriver.FirefoxOptions()
)
driver.implicitly_wait(5)

driver.get("https://www.time-j.net/worldtime/country/jp")

print(driver.find_element_by_xpath("/html/body/div/div[6]/div[1]/div/p[5]").text)
driver.quit()

