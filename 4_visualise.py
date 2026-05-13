

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


print("Loading analysed reviews...")
df = pd.read_csv('data/mtn_reviews_analysed.csv')
print(f"Loaded {len(df)} reviews")


sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


sentiment_counts = df['sentiment'].value_counts()

plt.figure(figsize=(8, 8))
colors = ['#2ecc71', '#e74c3c', '#95a5a6']  # green, red, gray
plt.pie(
    sentiment_counts,
    labels=sentiment_counts.index,
    autopct='%1.1f%%',
    colors=colors,
    startangle=140,
    textprops={'fontsize': 14}
)
plt.title('MTN Rwanda App - Overall Sentiment Distribution', fontsize=16, fontweight='bold')
plt.savefig('data/chart1_sentiment_pie.png', bbox_inches='tight')
plt.close()
print("Chart 1 saved!")


plt.figure(figsize=(8, 6))
ax = sns.countplot(
    data=df,
    x='sentiment',
    order=['positive', 'neutral', 'negative'],
    palette=['#2ecc71', '#95a5a6', '#e74c3c']
)
plt.title('MTN Rwanda App - Sentiment Count', fontsize=16, fontweight='bold')
plt.xlabel('Sentiment', fontsize=13)
plt.ylabel('Number of Reviews', fontsize=13)


for p in ax.patches:
    ax.annotate(
        str(int(p.get_height())),
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='bottom', fontsize=13, fontweight='bold'
    )

plt.savefig('data/chart2_sentiment_bar.png', bbox_inches='tight')
plt.close()
print("Chart 2 saved!")


plt.figure(figsize=(8, 6))
ax = sns.countplot(
    data=df,
    x='rating',
    palette='RdYlGn'
)
plt.title('MTN Rwanda App - Star Rating Distribution', fontsize=16, fontweight='bold')
plt.xlabel('Star Rating (1=Worst, 5=Best)', fontsize=13)
plt.ylabel('Number of Reviews', fontsize=13)

for p in ax.patches:
    ax.annotate(
        str(int(p.get_height())),
        (p.get_x() + p.get_width() / 2., p.get_height()),
        ha='center', va='bottom', fontsize=13, fontweight='bold'
    )

plt.savefig('data/chart3_rating_distribution.png', bbox_inches='tight')
plt.close()
print("Chart 3 saved!")


plt.figure(figsize=(10, 6))
rating_sentiment = df.groupby(['rating', 'sentiment']).size().unstack(fill_value=0)
rating_sentiment.plot(
    kind='bar',
    color=['#e74c3c', '#95a5a6', '#2ecc71'],
    figsize=(10, 6)
)
plt.title('MTN Rwanda - Sentiment by Star Rating', fontsize=16, fontweight='bold')
plt.xlabel('Star Rating', fontsize=13)
plt.ylabel('Number of Reviews', fontsize=13)
plt.xticks(rotation=0)
plt.legend(title='Sentiment')
plt.savefig('data/chart4_sentiment_vs_rating.png', bbox_inches='tight')
plt.close()
print("Chart 4 saved!")

df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M')

monthly = df.groupby(['month', 'sentiment']).size().unstack(fill_value=0)

monthly.plot(
    kind='line',
    color=['#e74c3c', '#95a5a6', '#2ecc71'],
    figsize=(12, 6),
    marker='o'
)
plt.title('MTN Rwanda - Sentiment Trends Over Time', fontsize=16, fontweight='bold')
plt.xlabel('Month', fontsize=13)
plt.ylabel('Number of Reviews', fontsize=13)
plt.xticks(rotation=45)
plt.legend(title='Sentiment')
plt.tight_layout()
plt.savefig('data/chart5_sentiment_over_time.png', bbox_inches='tight')
plt.close()
print("Chart 5 saved!")

print("\n✅ All 5 charts saved in the data folder!")
print("Open the data folder in VS Code to view them.")