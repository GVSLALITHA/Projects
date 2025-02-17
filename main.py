from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Setup WebDriver
driver = webdriver.Chrome()

# IMDb URL (Replace if needed)
url = "https://www.imdb.com/list/ls501426757/?sort=list_order,asc&st_dt=&mode=detail&page={}"
driver.get(url)
time.sleep(3)  # Allow page to load

# Initialize lists
movie_names = []
ratings = []
storylines = []
movie_durations = []

# Corrected XPath to select multiple list items
movie_items = driver.find_elements(By.XPATH, '//*[@id="__next"]/main/div/section/div/section/div/div[1]/section/div[2]/ul/li')
# //*[@id="__next"]/main/div/section/div/section/div/div[1]/section/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/span/div/span/span[1]
#  //*[@id="__next"]/main/div/section/div/section/div/div[1]/section/div[2]/ul/li[1]/div/div/div/div[2]/div/div
# //*[@id="__next"]/main/div/section/div/section/div/div[1]/section/div[2]/ul/li[1]/div/div/div/div[1]/div[2]/div[2]/span[2]
# Loop through each movie item
for movie_item in movie_items:
    try:
        # Extract movie name
        movie_name = movie_item.find_element(By.XPATH, './div/div/div/div[1]/div[2]/div[1]/a/h3').text.strip()
        movie_names.append(movie_name)
        rating = movie_item.find_element(By.XPATH, './div/div/div/div[1]/div[2]/span/div/span/span[1]').text.strip()
        ratings.append(rating)
        storyline = movie_item.find_element(By.XPATH, './div/div/div/div[2]/div/div').text.strip()
        storylines.append(storyline)
        duration = movie_item.find_element(By.XPATH, './div/div/div/div[1]/div[2]/div[2]/span[2]').text.strip()
        movie_durations.append(duration)

       
        
    except Exception as e:
        print(f"Error extracting movie name: {e}")

# Close WebDriver
driver.quit()

# Create DataFrame
df = pd.DataFrame({
    "Movie Name": movie_names,
    "Rating": ratings,
    "Storyline": storylines,
    "Duration": movie_durations
})

# Save DataFrame to CSV
df.to_csv("imdb_movies.csv", index=False)

# Print DataFrame
print(df)