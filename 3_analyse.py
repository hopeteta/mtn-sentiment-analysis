

import pandas as pd
from textblob import TextBlob

print("Loading cleaned reviews...")
df = pd.read_csv('data/mtn_reviews_cleaned.csv')
print(f"Loaded {len(df)} reviews")


def get_sentiment(text):
    try:
        analysis = TextBlob(str(text))
        polarity = analysis.sentiment.polarity
        
        
        if polarity > 0.1:
            return 'positive', polarity
        elif polarity < -0.1:
            return 'negative', polarity
        else:
            return 'neutral', polarity
            
    except:
        return 'neutral', 0.0

print("Starting sentiment analysis...")

sentiments = []
scores = []

for i, review in enumerate(df['cleaned_review']):
    sentiment, score = get_sentiment(review)
    sentiments.append(sentiment)
    scores.append(score)
    
    if (i + 1) % 100 == 0:
        print(f"Analysed {i + 1} of {len(df)} reviews...")


df['sentiment'] = sentiments
df['confidence_score'] = scores

df.to_csv('data/mtn_reviews_analysed.csv', index=False)


print("\n✅ Analysis Complete!")
print(f"Total reviews analysed: {len(df)}")
print("\nSentiment breakdown:")
print(df['sentiment'].value_counts())
print("\nExample results:")
print(df[['review', 'sentiment', 'confidence_score']].head(10))