from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

#  YouTube search results
driver.get("https://www.youtube.com/results?search_query=Computer+Science")

wait = WebDriverWait(driver, 10)
time.sleep(3)  # extra time for dynamic content

data = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a#video-title")))

links = []
for i in data:
    href = i.get_attribute('href')
    if href and 'watch?v=' in href:  # Only append if href exists and is a video
        links.append(href)

print(f"Found {len(links)} videos")

df = pd.DataFrame(columns=['video_id', 'title', 'description', 'category'])

# Set category
v_category = "Computer Science"

# Process first 5 videos in search
for x in links[:5]:
    try:
        driver.get(x)
        time.sleep(2)  # time for page to load
        v_id = x.split('v=')[-1]  
        
        try:
            v_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "yt-formatted-string.style-scope.ytd-watch-metadata"))).text
        except:
            try:
                v_title = driver.find_element(By.CSS_SELECTOR, "meta[property='og:title']").get_attribute('content')
            except:
                v_title = "Title not available"
        
        try:
            expand_button = wait.until(EC.element_to_be_clickable((By.ID, "expand")))
            expand_button.click()
            time.sleep(1)  
        except:
            print("Could not find or click expand button")
        
        try:
            v_description = wait.until(EC.presence_of_element_located((By.ID, "description-inline-expander"))).text
        except:
            try:
                v_description = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-expandable-video-description-body-text"))).text
            except:
                v_description = "Description not available"
        
        print(f"Found title: {v_title}") 
        print(f"Found description length: {len(v_description)}")  #
        # Add data to DataFrame
        df.loc[len(df)] = [v_id, v_title, v_description, v_category]
        print(f"Successfully scraped video: {v_title}")
        
    except TimeoutException:
        print(f"Timeout while processing video: {x}")
    except Exception as e:
        print(f"Error processing video {x}: {str(e)}")

driver.quit()

# Save to Excel
excel_filename = "youtube_data.xlsx"
df.to_excel(excel_filename, index=False)
print(f"Data saved to {excel_filename}")
