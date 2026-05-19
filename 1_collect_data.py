
from google_play_scraper import reviews, Sort
import pandas as pd

print("Starting to collect MTN Rwanda reviews...")

all_reviews = []

languages = ['en', 'fr']  # English and French

for lang in languages:
    print(f"Collecting {lang} reviews...")
    result, _ = reviews(
        'com.mtn1app',
        lang=lang,
        country='rw',
        sort=Sort.NEWEST,
        count=500        
    )
    all_reviews.extend(result)
    print(f"Got {len(result)} reviews in {lang}")


df = pd.DataFrame(all_reviews)


df = df[['userName', 'content', 'score', 'at']]


df.columns = ['username', 'review', 'rating', 'date']


df = df.drop_duplicates(subset=['review'])


df = df.dropna(subset=['review'])


df.to_csv('data/mtn_reviews.csv', index=False)

print(f"Done! Total reviews collected: {len(df)}")
print(df.head())