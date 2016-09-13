from selenium import webdriver
from selenium.webdriver.common.by import By
driver = webdriver.Chrome("C:\Python27\Scripts\chromedriver.exe")

# Request Fidelity Research page
driver.get("https://eresearch.fidelity.com/eresearch/landing.jhtml")

# Search by Ticker
ticker = driver.find_element_by_id("symbol")
ticker.send_keys("TSLA")
ticker.submit()

# Click to log in
driver.find_element(By.XPATH, "html/body/table/tbody/tr/td[4]/div[4]/div/a").click()

#Send keys to login form
username = driver.find_element_by_id("userId")
username.send_keys("[USER]")
password = driver.find_element_by_id("password")
password.send_keys("[PASSWORD]")
password.submit()

# Request Advanced Chart page
driver.get("https://screener.fidelity.com/ftgw/etf/gotoCL/snapshot/advancedChart.jhtml?symbols=TSLA&useHtml5=true")

# Click Indicators
driver.find_element(By.XPATH, ".//*[@id='chart-container']/tab-chart/div/div[2]/advanced-chart/div/div[1]/fmr-advanced-chart-menu/div/div[1]/div[2]/div[5]").click()

# Click Stochastic Slow
driver.find_element(By.XPATH, ".//*[@id='chart-container']/tab-chart/div/div[2]/advanced-chart/div/div[1]/fmr-advanced-chart-menu/div/div[2]/div[3]/div[1]/div[8]").click()

# Click Indicators
driver.find_element(By.XPATH, ".//*[@id='chart-container']/tab-chart/div/div[2]/advanced-chart/div/div[1]/fmr-advanced-chart-menu/div/div[1]/div[2]/div[5]").click()

# Click Social Sentiment
driver.find_element(By.XPATH, ".//*[@id='chart-container']/tab-chart/div/div[2]/advanced-chart/div/div[1]/fmr-advanced-chart-menu/div/div[2]/div[3]/div[2]/div[8]").click()

# Click OK
driver.find_element(By.XPATH, "html/body/div[8]/div/div/div[2]/div/div[3]/div/button").click()

# Click Export
driver.find_element(By.XPATH, ".//*[@id='chart-container']/tab-chart/div/div[2]/div/export-menu/div/dropdown-menu/div/div[1]/div").click()

# Click Export by Spreadsheet
driver.find_element(By.XPATH, ".//*[@id='chart-container']/tab-chart/div/div[2]/div/export-menu/div/dropdown-menu/div/div[2]/dropdown-menu-item[1]/div/div").click()
