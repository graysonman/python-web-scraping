from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# Define constants
PRODUCT_URL_TEMPLATE = "https://www.adiglobaldistribution.us/Product/{}"
CATALOG_URL = ""

def check_captcha(driver):
    #Detect if captch is present
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(), 'www.adiglobaldistribution.us')]")))
        return True
    except UnexpectedAlertPresentException:
        print("found alert")
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        print(f"Handled unexpected alert with text: {alert_text}")
    except TimeoutException:
        return False  # The element was not found within the timeout period, CAPTCHA is not present

def pause_captcha(driver, url):
    driver.get(url)
    
    print("CAPTCHA detected. Please solve the CAPTCHA to proceed.")
    input("After you have solved the CAPTCHA, press ENTER to continue...")

    # After the CAPTCHA is solved switch back to main tab
    driver.switch_to.window(driver.window_handles[0])

    return True

def fetch_price(product_id, driver):
    url = PRODUCT_URL_TEMPLATE.format(product_id)
    driver.get(url)

    # Use WebDriverWait to ensure the element loads
    wait = WebDriverWait(driver, 10)  # adjust as needed number field

    # Check for captcha presence and if it exists then call the program pause
    if check_captcha(driver):
        pause_captcha(driver, url)
        
    # If there is no page found with the product id then add it to a delete file 
    try:
        page_not_found = "Sorry! The page you’re looking for can’t be found."
        if page_not_found in driver.find_element(By.TAG_NAME, "h1").text:
            print(f"Product {product_id} does not exist.")
            return "delete"
    except NoSuchElementException:
        pass

    # Check for main price location and then the price location of products with multiple different colors or types
    try:
        main_price_text = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[1]/div/div[3]/div/div/div/div/div/div[3]/div/section/div/div[3]/div[1]/div/div[2]/div[1]/isc-product-price-na-redesign/span/span[1]/span/div/span[1]"))).text
        main_price = int(main_price_text.replace(',',''))
        decimal_value = int(wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[1]/div/div[3]/div/div/div/div/div/div[3]/div/section/div/div[3]/div[1]/div/div[2]/div[1]/isc-product-price-na-redesign/span/span[1]/span/div/sup[2]"))).text)
    except TimeoutException:
        try:
            main_price_text = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[1]/div/div[2]/div/div/div/div/div/div[3]/div/section/div/div[3]/div[1]/div/div[2]/div[1]/isc-product-price-na-redesign/span/span[1]/span/div/span[1]"))).text
            main_price = int(main_price_text.replace(',',''))
            decimal_value = int(wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[9]/div[1]/div/div[2]/div/div/div/div/div/div[3]/div/section/div/div[3]/div[1]/div/div[2]/div[1]/isc-product-price-na-redesign/span/span[1]/span/div/sup[2]"))).text)
 
        except:
            print(f"Failed to locate price elements for {product_id}.")
            return None

    full_price = main_price + (decimal_value / 100.0)
    print(full_price)
    return full_price

def update_catalog(product_id, price, driver):
    driver.get(CATALOG_URL)
    
    if '*' not in product_id:
        product_id = "*" + product_id
    
    wait = WebDriverWait(driver, 30)  # adjust as needed number field
    try:
        #Search in connectwise manage inside the vendor sku. needs to be in first field 
        #search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div[1]/div/table/tbody[2]/tr[2]/td[2]/div/div/div/input")))
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "Vendor_SKU-input")))
        time.sleep(1)
        search_box.click()
        time.sleep(1)
        search_box.send_keys(product_id)
        time.sleep(1)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)    
        if 'ProductList' in driver.current_url and 'ProductCatalogDetail' not in driver.current_url:
                click_product_id = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]/table/tbody[2]/tr[1]/td[3]/div/a")))
                click_product_id.click()
        time.sleep(2)
        
        wait = WebDriverWait(driver, 20)  # adjust as needed number field

        # Update the unit cost and unit price fields
        unit_cost_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'UnitCost')]")))
        #unit_cost_field = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td/div/div[2]/div[1]/table/tbody/tr[1]/td/div/table[1]/tbody/tr[8]/td[3]/div/div/div/div/input")))
        time.sleep(1)
        driver.execute_script(f"arguments[0].value = '{price}';", unit_cost_field)
        time.sleep(1)

        unit_price_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'UnitPrice')]")))
        #unit_price_field = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]/div/div[3]/div/div[2]/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody/tr/td[1]/table/tbody/tr[1]/td/div/div[2]/div[1]/table/tbody/tr[1]/td/div/table[1]/tbody/tr[6]/td[3]/div/div/div/div/input")))
        time.sleep(1)
        rounded_price = round(price * 1.5, 2)
        print(rounded_price)
        time.sleep(1)
        driver.execute_script(f"arguments[0].value = '{rounded_price}';", unit_price_field)

        # Save and close button
        driver.execute_script("document.querySelector('[class*=\"cw_ToolbarButton_SaveAndClose\"]').click();")

        time.sleep(1)

    except StaleElementReferenceException:
        print("Stale element found. Retrying this product.")
        fetch_price(product_id, driver)
    
def main():
    # Load product IDs from a text file
    with open('parts.txt', 'r') as f:
        product_ids = [line.strip() for line in f if line.strip()]

    chrome_options = Options()

    # Driver control options. Headless is best practice for bots
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.headless = True
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        for product_id in product_ids:
            price = fetch_price(product_id, driver)
            if price == "delete":
                print(f"Product with ID {product_id} should be deleted!")
                with open('tobedeleted.txt', 'a') as f:
                    f.write(str(product_id) + '\n')
            elif isinstance(price, float):
                update_catalog(product_id, price, driver)
                print(f"Updated Product ID {product_id}!")
            else:
                print(f"Found a product, {product_id} that I dont know what to do.")
                with open('unknown.txt' , 'a') as f:
                    f.write(str(product_id) + '\n')

    finally:
        #driver.close()
        print(product_id +" completed")

if __name__ == '__main__':
    main()
