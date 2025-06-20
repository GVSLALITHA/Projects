
import os
import pandas as pd
import numpy as np
import psycopg2
 # Folder path containing the CSV files
folder_path = r"D:\AI-ML GUVI\Scrapping_Visualize\genere_sep_files"

# #  list of all CSV files in the folder 
csv_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".csv")][:6]

# # Read and merge the data
df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

# # Remove duplicates based on "Title" column (keep the first occurrence)
df.drop_duplicates(subset=["Title"], keep="first", inplace=True)

# #  Save the cleaned merged data 
output_file = os.path.join(folder_path, "movies_2024.csv")
df.to_csv(output_file, index=False)

print(f"Merged CSV file saved as: {output_file}")
#---------------------------DB Connect------------

import pandas as pd
import psycopg2

# Load CSV
df = pd.read_csv("D:\AI-ML GUVI\Scrapping_Visualize\genere_sep_files\movies_2024.csv")

# Optional: clean column names
df.columns = df.columns.str.strip().str.capitalize()

# DB connection
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="movies",
    user="postgres",
    password="kamakshi@5"
)
curr = conn.cursor()
# Create table if it doesn't exist
curr.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    genre VARCHAR(50),
    duration VARCHAR(50),
    rating VARCHAR(10),
    voting VARCHAR(20)
);
""")
# Insert data
for _, row in df.iterrows():
    curr.execute(
        "INSERT INTO movies(title, genre, duration, rating, voting) VALUES (%s, %s, %s, %s, %s)",
        (row["Title"], row["Genre"], row["Duration"], row["Rating"], row["Voting"])
    )

conn.commit()
curr.close()
conn.close()
