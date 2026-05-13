
import pandas as pd
import re
import nltk

# Download required nltk data (only needed first time)
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords

print("Loading reviews...")
df = pd.read_csv('data/mtn_reviews.csv')
print(f"Loaded {len(df)} reviews")


def clean_text(text):
    # Convert to string in case of numbers
    text = str(text)
    
    text = text.lower()
    
    text = re.sub(r'http\S+', '', text)
    
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text

print("Cleaning reviews...")

df['cleaned_review'] = df['review'].apply(clean_text)

df = df[df['cleaned_review'].str.len() > 10]

df.to_csv('data/mtn_reviews_cleaned.csv', index=False)

print(f"Done! {len(df)} reviews after cleaning")
print("\nExample - Before and after cleaning:")
print("BEFORE:", df['review'].iloc[0])
print("AFTER: ", df['cleaned_review'].iloc[0])