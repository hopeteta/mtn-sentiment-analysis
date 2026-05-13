# Phase 1: Collecting MTN Rwanda App Reviews from Google Play Store

from google_play_scraper import reviews, Sort
import pandas as pd

print("Starting to collect MTN Rwanda reviews...")

all_reviews = []

# Collect in multiple languages to get more reviews
languages = ['en', 'fr']  # English and French

for lang in languages:
    print(f"Collecting {lang} reviews...")
    result, _ = reviews(
        'com.mtn1app',
        lang=lang,
        country='rw',
        sort=Sort.NEWEST,
        count=500        # 500 per language
    )
    all_reviews.extend(result)
    print(f"Got {len(result)} reviews in {lang}")

# Convert to table
df = pd.DataFrame(all_reviews)

# Keep only the columns we need
df = df[['userName', 'content', 'score', 'at']]

# Rename columns
df.columns = ['username', 'review', 'rating', 'date']

# Remove duplicates
df = df.drop_duplicates(subset=['review'])

# Remove empty reviews
df = df.dropna(subset=['review'])

# Save to CSV
df.to_csv('data/mtn_reviews.csv', index=False)

print(f"Done! Total reviews collected: {len(df)}")
print(df.head())