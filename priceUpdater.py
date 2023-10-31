from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# Define constants
PRODUCT_URL_TEMPLATE = "https://www.adiglobaldistribution.us/Product/{}"
CATALOG_URL = ""

def fetch_price(product_id, driver):
    time.sleep(2)
    url = PRODUCT_URL_TEMPLATE.format(product_id)
    driver.get(url)

    # Use WebDriverWait to ensure the element loads
    wait = WebDriverWait(driver, 30)  # adjust as needed number field

    try:        
        main_price_text = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[9]/div[1]/div/div[3]/div/div/div/div/div/div[3]/div/section/div/div[3]/div[1]/div/div[2]/div[1]/isc-product-price-na-redesign/span/span[1]/span/div/span[1]"))).text
        main_price = int(main_price_text.replace(',',''))
    except:
        print("Failed to locate main_price element.")
        print("Page source:", driver.page_source)
        return None

    try:
        decimal_value = int(wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[9]/div[1]/div/div[3]/div/div/div/div/div/div[3]/div/section/div/div[3]/div[1]/div/div[2]/div[1]/isc-product-price-na-redesign/span/span[1]/span/div/sup[2]"))).text)
    except:
        print("Failed to locate decimal_value element.")
        print("Page source:", driver.page_source)
        return None

    full_price = main_price + (decimal_value / 100.0)
    print(full_price)
    return full_price

def update_catalog(product_id, price, driver):
    driver.get(CATALOG_URL)

    product_id = "*" + product_id
    
    wait = WebDriverWait(driver, 30)  # adjust as needed number field

    #Search in connectwise manage inside the vendor sku. needs to be in first field 
    search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div[1]/div/table/tbody[2]/tr[2]/td[2]/div/div/div/input")))
    #search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@id, 'Vendor_SKU-input')]"))
    time.sleep(1)
    search_box.click()
    time.sleep(1)
    search_box.send_keys(product_id)
    time.sleep(1)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)    
    if 'ProductList' in driver.current_url :
            click_product_id = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]/table/tbody[2]/tr[1]/td[3]/div/a")))
            click_product_id.click()
    time.sleep(2)
    
    wait = WebDriverWait(driver, 20)  # adjust as needed number field

    # Update the unit cost and unit price fields
    unit_cost_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'UnitCost')]")))
    #unit_cost_field = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td/div/div[2]/div[1]/table/tbody/tr[1]/td/div/table[1]/tbody/tr[8]/td[3]/div/div/div/div/input")))
    unit_cost_field.click()
    time.sleep(1)
    driver.execute_script(f"arguments[0].value = '{price}';", unit_cost_field)
    time.sleep(1)

    unit_price_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'UnitPrice')]")))
    #unit_price_field = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td/div/div[2]/div[1]/table/tbody/tr[1]/td/div/table[1]/tbody/tr[6]/td[3]/div/div/div/div/input")))
    unit_price_field.click()
    time.sleep(1)
    rounded_price = round(price * 1.5, 2)
    print(rounded_price)
    time.sleep(1)
    driver.execute_script(f"arguments[0].value = '{rounded_price}';", unit_price_field)

    # Save and close button
    driver.execute_script("document.querySelector('[class*=\"cw_ToolbarButton_SaveAndClose\"]').click();")

    time.sleep(1)
    
def main():
    # Load product IDs from a text file
    with open('parts.txt', 'r') as f:
        product_ids = [line.strip() for line in f if line.strip()]

    chrome_options = Options()

    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        for product_id in product_ids:
            price = fetch_price(product_id, driver)
            if price:
                update_catalog(product_id, price, driver)
                print(f"Updated Product ID {product_id}!")
            else:
                print(f"Product with ID {product_id} should be deleted!")
                with open('tobedeleted.txt', 'a') as f:
                    f.write(str(product_id) + '\n')

    finally:
        #driver.close()
        print(product_id +" completed")

if __name__ == '__main__':
    main()
    
