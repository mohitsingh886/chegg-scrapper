import os
import sys
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Replace these with your login details and URLs
login_url = 'https://expert.chegg.com/auth/login'
username = 'King@straive.com'
password = 'Straive@5830'

# Text to search for
search_texts = ['code', 'program', 'function', 'c++', 'java', 'python', 'operating', 'language', 'assembly']

def login(driver):
    driver.get(login_url)
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
    
    # Find username field and enter username
    username_field = driver.find_element(By.NAME, 'username')
    username_field.send_keys(username)
    
    # Click submit button after entering username
    submit_button_username = driver.find_element(By.XPATH, '//button[@type="submit"]')
    submit_button_username.click()
    
    # Wait for the password field to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'password')))
    
    # Find password field and enter password
    password_field = driver.find_element(By.NAME, 'password')
    password_field.send_keys(password)
    
    # Click submit button after entering password
    submit_button_password = driver.find_element(By.XPATH, '//button[@type="submit"]')
    submit_button_password.click()

    # Wait for the login process to complete
    time.sleep(5)

def check_page_for_text(driver, url):
    driver.get(url)
    try:
        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'sc-iBYQkv')))
        # Find all elements with the specified class
        elements = driver.find_elements(By.CLASS_NAME, 'sc-iBYQkv')

        # Check text within each element
        for element in elements:
            page_content = element.text
            for text in search_texts:
                if text in page_content:
                    return True
        return False
    except Exception as e:
        print(f"Error checking page for text: {e}")
        return False

def main(credentials_path):
     # Initialize the WebDriver with automatic ChromeDriver management and headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Connect to Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open('chegg sheet').sheet1  # Replace with your Google Sheet name

    try:
        login(driver)
        
        # Get all URLs from the first column of the sheet
        urls_to_check = sheet.col_values(1)
        
        for i, url in enumerate(urls_to_check, start=1):
            if url.strip() == '':
                continue  # Skip empty cells
            
            found_text = 'found' if check_page_for_text(driver, url) else 'not found'
            sheet.update_cell(i, 2, found_text)  # Update the adjacent cell with the status

            if found_text == 'found':
                sheet.update_cell(i, 3, url)  # Update the third column with the found URL
            
            time.sleep(3)  # Pause between checks for visibility

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the WebDriver session
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/credentials.json")
        sys.exit(1)
    credentials_path = sys.argv[1]
    main(credentials_path)
