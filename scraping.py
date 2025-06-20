from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os
genres = ["action", "comedy", "drama", "thriller", "romance"]
output_dir = r"D:\AI-ML GUVI\Scrapping_Visualize"
os.makedirs(output_dir, exist_ok=True)
driver = webdriver.Chrome()

for genre in genres:
    print(f"\nScraping Genre: {genre.capitalize()}")
    genre_url = f"https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&genres={genre}"
    driver.get(genre_url)
    time.sleep(2)

    all_movies = []

    while True:
        movie_blocks = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
        for movie in movie_blocks:
            try:
                title = movie.find_element(By.CSS_SELECTOR, "h3.ipc-title__text").text.strip()
            except:
                title = "N/A"

            try:
                duration_element = movie.find_element(By.XPATH, ".//span[contains(@class, 'dli-title-metadata-item') and (contains(text(),'h') or contains(text(),'m'))]")
                duration = duration_element.text.strip()
            except:
                duration = "N/A"

            try:
                rating = movie.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--rating").text.strip()
            except:
                rating = "N/A"

            try:
                voting = movie.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--voteCount").text.strip()
            except:
                voting = "N/A"

            movie_data = {
                "Title": title,
                "Genre": genre.capitalize(),
                "Duration": duration,
                "Rating": rating,
                "Voting": voting,
            }
            all_movies.append(movie_data)

        # Try to go to the next page
        try:
            next_button = driver.find_element(By.XPATH, '//a[@class="ipc-btn ipc-btn--single-padding ipc-btn--center-align-content ipc-btn--core-base ipc-btn--theme-baseAlt ipc-pagination-next ipc-btn--icon-leading"]')
            next_button.click()
            time.sleep(2)
        except:
            print("No more pages.")
            break
    if all_movies:
        df = pd.DataFrame(all_movies)
        df["Title"] = df["Title"].str.replace(r"^\d+\.\s*", "", regex=True)
        df["Voting"] = df["Voting"].str.replace(r"[()]", "", regex=True)
        df.index = df.index + 1

        genre_csv_path = os.path.join(output_dir, f"{genre}.csv")
        df.to_csv(genre_csv_path, index=False, encoding="utf-8")
        print(f"Saved {len(df)} movies to {genre_csv_path}")
    else:
        print("No movies found for this genre.")
driver.quit()
print("\n Scraping complete!")
