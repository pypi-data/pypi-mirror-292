from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")  # Uncomment if you want to run in headless mode

# Setting up the Chrome driver with the service and options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# URL of the website
website = "https://super-swan-a61501.netlify.app"
driver.get(website)

# File to store recognized text
rec_file = f"{getcwd()}\\input.txt"

def listen():
    try:
        # Wait for the start button and click it to start listening
        start_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'startButton')))
        start_button.click()
        print("Listening...")

        output_text = ""

        while True:
            try:
                # Quickly poll for the presence of new text
                output_element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'output')))
                current_text = output_element.text.strip()

                # Capture and write any new text to the file
                if current_text:
                    if current_text != output_text:
                        output_text = current_text
                        print("User:", output_text)

            except Exception as e:
                print(f"An error occurred while processing text: {e}")

            # Minimal sleep for fast polling
            time.sleep(0.001)  # Reduced to 0.005 seconds for faster polling

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the browser is closed when done
        driver.quit()
        print("Browser closed.")

# Start listening
listen()
