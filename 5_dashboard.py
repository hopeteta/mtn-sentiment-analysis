# MTN Rwanda AI-Based Sentiment Analytics System
# Role-Based Access | Admin + Analyst | MTN Brand Design

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from google_play_scraper import reviews, Sort
from fpdf import FPDF
import tempfile
import os
import csv
import re
from datetime import datetime

# ─────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────
st.set_page_config(
    page_title="MTN Rwanda Sentiment Analytics",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────
# MTN Brand Styling
# ─────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
        font-family: 'Segoe UI', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 2px solid #FFCC00;
    }
    .mtn-header {
        background: linear-gradient(135deg, #1a1a1a 60%, #FFCC00 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(255,204,0,0.3);
    }
    .mtn-header h1 {
        color: #FFCC00;
        font-size: 1.5rem;
        margin: 0;
        font-weight: 700;
    }
    .mtn-header p {
        color: #ffffff;
        font-size: 0.8rem;
        margin: 0;
    }
    .mtn-badge {
        background-color: #FFCC00;
        color: #1a1a1a;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #FFCC00;
        border-left: 4px solid #FFCC00;
        padding-left: 10px;
        margin: 1rem 0 0.5rem 0;
    }
    .login-card {
        background: #2a2a2a;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 4px 30px rgba(255,204,0,0.15);
        border: 1px solid rgba(255,204,0,0.3);
        border-top: 5px solid #FFCC00;
    }
    .login-title {
        font-size: 2rem;
        font-weight: 900;
        color: #FFCC00;
        text-align: center;
        letter-spacing: 3px;
    }
    .login-subtitle {
        font-size: 0.85rem;
        color: #aaaaaa;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .stButton > button {
        background-color: #FFCC00 !important;
        color: #1a1a1a !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button {
        background-color: #1a1a1a !important;
        color: #FFCC00 !important;
        font-weight: 700 !important;
        border: 2px solid #FFCC00 !important;
        border-radius: 8px !important;
    }
    div[data-testid="metric-container"] {
        background-color: #2a2a2a;
        border: 1.5px solid #FFCC00;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        box-shadow: 0 2px 6px rgba(255,204,0,0.1);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.75rem !important;
        color: #FFCC00 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    hr {
        border-color: #FFCC00;
        opacity: 0.2;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Users File
# ─────────────────────────────────────────
USERS_FILE = 'data/users.csv'

DEFAULT_USERS = {
    "mtn_admin": {"password": "mtn2026", "role": "admin", "display": "Administrator"},
}

def load_users():
    users = dict(DEFAULT_USERS)
    if os.path.exists(USERS_FILE):
        df = pd.read_csv(USERS_FILE)
        for _, row in df.iterrows():
            users[row['username']] = {
                "password": row['password'],
                "role": "analyst",
                "display": row['username']
            }
    return users

def save_analyst(username, password, contact):
    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['username', 'password', 'contact', 'created_at'])
        writer.writerow([username, password, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def username_exists(username):
    users = load_users()
    return username in users

# ─────────────────────────────────────────
# Login Page
# ─────────────────────────────────────────
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
<div class='login-card'>
<div style='text-align:center; margin-bottom:0.5rem;'>
<span style='font-size:2.5rem;'>🟡</span>
</div>
<div class='login-title'>MTN RWANDA</div>
<div class='login-subtitle'>AI-Based Sentiment Analytics System</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])

        with tab1:
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_pass")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login →", use_container_width=True, key="login_btn"):
                users = load_users()
                if username in users and users[username]["password"] == password:
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = users[username]["role"]
                    st.session_state['username'] = username
                    st.session_state['display'] = users[username]["display"]
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password. Please try again.")

        with tab2:
            st.markdown("<small style='color:#aaa;'>Create an analyst account to access live reviews and sentiment testing.</small>", unsafe_allow_html=True)
            new_username = st.text_input("👤 Username", placeholder="Letters only (e.g. johnmtn)", key="reg_user")
            new_email = st.text_input("📧 Email Address", placeholder="e.g. john@mtn.com", key="reg_email")
            new_password = st.text_input("🔒 Password", type="password", placeholder="Create a password", key="reg_pass")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Repeat your password", key="reg_confirm")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True, key="reg_btn"):
                if not new_username:
                    st.error("❌ Please enter a username.")
                elif not re.match("^[a-zA-Z]+$", new_username):
                    st.error("❌ Username must contain letters only. No numbers or special characters.")
                elif len(new_username) < 3:
                    st.error("❌ Username must be at least 3 characters long.")
                elif not new_email:
                    st.error("❌ Please enter your email address.")
                elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", new_email):
                    st.error("❌ Please enter a valid email address.")
                elif not new_password:
                    st.error("❌ Please enter a password.")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                elif new_password != confirm_password:
                    st.error("❌ Passwords do not match.")
                elif username_exists(new_username):
                    st.error("❌ Username already exists. Please choose another.")
                else:
                    save_analyst(new_username, new_password, new_email)
                    st.success(f"✅ Account created! You can now login as {new_username}.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; font-size:0.75rem; color:#666;'>MTN Rwanda © 2026 | Final Year Project</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Sentiment Function
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# Load Historical Data
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('data/mtn_reviews_analysed.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

# ─────────────────────────────────────────
# Fetch Live Reviews
# ─────────────────────────────────────────
def fetch_live_reviews():
    with st.spinner("Fetching latest reviews from Google Play Store..."):
        result, _ = reviews(
            'com.mtn1app',
            lang='en',
            country='rw',
            sort=Sort.NEWEST,
            count=100
        )
        df_live = pd.DataFrame(result)
        if len(df_live) == 0:
            return None
        df_live = df_live[['userName', 'content', 'score', 'at']]
        df_live.columns = ['username', 'review', 'rating', 'date']
        df_live = df_live.dropna(subset=['review'])
        sentiments = []
        scores = []
        for review_text in df_live['review']:
            sentiment, score = get_sentiment(review_text)
            sentiments.append(sentiment)
            scores.append(score)
        df_live['sentiment'] = sentiments
        df_live['confidence_score'] = scores
        return df_live

# ─────────────────────────────────────────
# Generate PDF Report
# ─────────────────────────────────────────
def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "MTN Rwanda - Sentiment Analysis Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Total Reviews Analysed: {len(df)}", ln=True, align="C")
    pdf.ln(5)

    pos = len(df[df['sentiment'] == 'positive'])
    neu = len(df[df['sentiment'] == 'neutral'])
    neg = len(df[df['sentiment'] == 'negative'])

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Positive: {pos} ({round(pos/len(df)*100,1) if len(df)>0 else 0}%)", ln=True)
    pdf.cell(0, 7, f"Neutral: {neu} ({round(neu/len(df)*100,1) if len(df)>0 else 0}%)", ln=True)
    pdf.cell(0, 7, f"Negative: {neg} ({round(neg/len(df)*100,1) if len(df)>0 else 0}%)", ln=True)
    pdf.ln(5)

    sentiment_counts = df['sentiment'].value_counts()
    colors_map = {'positive': '#27ae60', 'negative': '#c0392b', 'neutral': '#5d8aa8'}
    colors = [colors_map.get(s, '#888888') for s in sentiment_counts.index]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.set_title("Sentiment Distribution")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        fig.savefig(tmpfile.name, bbox_inches='tight')
        chart_path = tmpfile.name
    plt.close(fig)

    pdf.image(chart_path, x=55, w=100)
    os.unlink(chart_path)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Review Details", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(110, 7, "Review", border=1)
    pdf.cell(40, 7, "Sentiment", border=1)
    pdf.cell(30, 7, "Rating", border=1, ln=True)

    pdf.set_font("Helvetica", "", 8)
    for _, row in df.head(100).iterrows():
        review_text = str(row['review'])[:60].encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(110, 6, review_text, border=1)
        pdf.cell(40, 6, str(row['sentiment']), border=1)
        pdf.cell(30, 6, str(row['rating']), border=1, ln=True)

    return bytes(pdf.output())

# ─────────────────────────────────────────
# Convert to CSV
# ─────────────────────────────────────────
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ─────────────────────────────────────────
# Analyst Dashboard
# ─────────────────────────────────────────
def analyst_dashboard():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('display', '')}")
        st.markdown("**Role:** Analyst")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.session_state['username'] = None
            st.rerun()

    st.markdown("""
<div class='mtn-header'>
<div>
<h1>📊 MTN Rwanda Sentiment System</h1>
<p>Live Review Analysis and Sentiment Tester</p>
</div>
<div class='mtn-badge'>ANALYST VIEW</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🔄 Live Review Analysis</div>", unsafe_allow_html=True)
    st.markdown("<small>Fetch and analyse the latest MTN Rwanda reviews in real time.</small>", unsafe_allow_html=True)

    if st.button("🔄 Fetch Latest Reviews", use_container_width=True):
        df_live = fetch_live_reviews()
        if df_live is not None:
            st.success(f"✅ Fetched and analysed {len(df_live)} latest reviews!")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Positive", len(df_live[df_live['sentiment'] == 'positive']))
            with col2:
                st.metric("Neutral", len(df_live[df_live['sentiment'] == 'neutral']))
            with col3:
                st.metric("Negative", len(df_live[df_live['sentiment'] == 'negative']))
            st.dataframe(
                df_live[['username', 'review', 'sentiment', 'rating']],
                use_container_width=True
            )
            st.info("ℹ️ These live reviews are not stored permanently.")
            col1, col2 = st.columns(2)
            with col1:
                live_pdf = generate_pdf_report(df_live)
                st.download_button(
                    "📥 Download PDF",
                    data=live_pdf,
                    file_name="live_sentiment_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="analyst_pdf"
                )
            with col2:
                live_csv = convert_to_csv(df_live)
                st.download_button(
                    "📊 Download CSV",
                    data=live_csv,
                    file_name="live_sentiment_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="analyst_csv"
                )
        else:
            st.warning("No new reviews found at this time.")

    st.divider()

    st.markdown("<div class='section-title'>🤖 Live Sentiment Tester</div>", unsafe_allow_html=True)
    user_input = st.text_area("", placeholder="e.g. MTN network is very slow today...")
    if st.button("Analyse Sentiment →", use_container_width=True):
        if user_input.strip() == "":
            st.warning("Please enter a review first!")
        else:
            analysis = TextBlob(user_input)
            polarity = analysis.sentiment.polarity
            if polarity > 0.1:
                sentiment = "POSITIVE"
                color = "green"
                emoji = "😊"
            elif polarity < -0.1:
                sentiment = "NEGATIVE"
                color = "red"
                emoji = "😠"
            else:
                sentiment = "NEUTRAL"
                color = "gray"
                emoji = "😐"
            st.markdown(f"### Result: :{color}[{emoji} {sentiment}]")
            st.markdown(f"**Polarity Score:** {round(polarity, 3)}")

# ─────────────────────────────────────────
# Admin Dashboard
# ─────────────────────────────────────────
def admin_dashboard():
    df = load_data()

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('display', '')}")
        st.markdown("**Role:** Administrator")
        st.divider()
        st.markdown("**🔍 Filter Reviews**")
        sentiment_filter = st.multiselect(
            "Sentiment",
            options=['positive', 'neutral', 'negative'],
            default=['positive', 'neutral', 'negative']
        )
        rating_filter = st.multiselect(
            "Star Rating",
            options=[1, 2, 3, 4, 5],
            default=[1, 2, 3, 4, 5]
        )
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.session_state['username'] = None
            st.rerun()

    filtered_df = df[
        (df['sentiment'].isin(sentiment_filter)) &
        (df['rating'].isin(rating_filter))
    ]

    st.markdown("""
<div class='mtn-header'>
<div>
<h1>📊 MTN Rwanda Sentiment System</h1>
<p>Full Historical Analysis and Management Dashboard</p>
</div>
<div class='mtn-badge'>ADMIN VIEW</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📈 Overview</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews", len(filtered_df))
    with col2:
        pos_pct = round(len(filtered_df[filtered_df['sentiment'] == 'positive']) / len(filtered_df) * 100, 1) if len(filtered_df) > 0 else 0
        st.metric("Positive", f"{pos_pct}%")
    with col3:
        neg_pct = round(len(filtered_df[filtered_df['sentiment'] == 'negative']) / len(filtered_df) * 100, 1) if len(filtered_df) > 0 else 0
        st.metric("Negative", f"{neg_pct}%")
    with col4:
        avg = round(filtered_df['rating'].mean(), 1) if len(filtered_df) > 0 else 0
        st.metric("Avg Rating", f"{avg}/5")

    st.divider()

    st.markdown("<div class='section-title'>📄 Export Report</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        pdf_bytes = generate_pdf_report(filtered_df)
        st.download_button(
            "📥 Download PDF Report",
            data=pdf_bytes,
            file_name="mtn_sentiment_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col2:
        csv_bytes = convert_to_csv(filtered_df)
        st.download_button(
            "📊 Download CSV",
            data=csv_bytes,
            file_name="mtn_sentiment_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()

    st.markdown("<div class='section-title'>📊 Sentiment Charts</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Sentiment Distribution**")
        sentiment_counts = filtered_df['sentiment'].value_counts()
        colors_map = {'positive': '#27ae60', 'negative': '#c0392b', 'neutral': '#5d8aa8'}
        colors = [colors_map.get(s, '#888888') for s in sentiment_counts.index]
        fig, ax = plt.subplots(figsize=(3, 3))
        fig.patch.set_facecolor('#2a2a2a')
        ax.set_facecolor('#2a2a2a')
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%',
               colors=colors, startangle=140,
               textprops={'color': 'white', 'fontsize': 8})
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("**Sentiment Count**")
        fig, ax = plt.subplots(figsize=(3, 3))
        fig.patch.set_facecolor('#2a2a2a')
        ax.set_facecolor('#2a2a2a')
        sns.countplot(
            data=filtered_df,
            x='sentiment',
            order=['positive', 'neutral', 'negative'],
            palette=['#27ae60', '#5d8aa8', '#c0392b'],
            ax=ax
        )
        for p in ax.patches:
            ax.annotate(str(int(p.get_height())),
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=9, color='white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
        plt.close()

    st.divider()

    st.markdown("<div class='section-title'>📅 Sentiment Trends Over Time</div>", unsafe_allow_html=True)
    filtered_df['month'] = filtered_df['date'].dt.to_period('M').astype(str)
    monthly = filtered_df.groupby(['month', 'sentiment']).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor('#2a2a2a')
    ax.set_facecolor('#2a2a2a')
    monthly.plot(kind='line', color=['#c0392b', '#5d8aa8', '#27ae60'], marker='o', ax=ax)
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color('white')
    legend.get_frame().set_facecolor('#2a2a2a')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.divider()

    st.markdown("<div class='section-title'>🔄 Live Review Analysis</div>", unsafe_allow_html=True)
    if st.button("🔄 Fetch Latest Reviews", use_container_width=True):
        df_live = fetch_live_reviews()
        if df_live is not None:
            st.success(f"✅ Fetched and analysed {len(df_live)} latest reviews!")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Positive", len(df_live[df_live['sentiment'] == 'positive']))
            with col2:
                st.metric("Neutral", len(df_live[df_live['sentiment'] == 'neutral']))
            with col3:
                st.metric("Negative", len(df_live[df_live['sentiment'] == 'negative']))
            st.dataframe(
                df_live[['username', 'review', 'sentiment', 'rating']],
                use_container_width=True
            )
            st.info("ℹ️ These live reviews are not stored permanently.")
            col1, col2 = st.columns(2)
            with col1:
                live_pdf = generate_pdf_report(df_live)
                st.download_button(
                    "📥 Download Live PDF",
                    data=live_pdf,
                    file_name="live_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="admin_live_pdf"
                )
            with col2:
                live_csv = convert_to_csv(df_live)
                st.download_button(
                    "📊 Download Live CSV",
                    data=live_csv,
                    file_name="live_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="admin_live_csv"
                )
        else:
            st.warning("No new reviews found at this time.")

    st.divider()

    st.markdown("<div class='section-title'>🤖 Live Sentiment Tester</div>", unsafe_allow_html=True)
    user_input = st.text_area("", placeholder="e.g. MTN network is very slow today...")
    if st.button("Analyse Sentiment →", use_container_width=True):
        if user_input.strip() == "":
            st.warning("Please enter a review first!")
        else:
            analysis = TextBlob(user_input)
            polarity = analysis.sentiment.polarity
            if polarity > 0.1:
                sentiment = "POSITIVE"
                color = "green"
                emoji = "😊"
            elif polarity < -0.1:
                sentiment = "NEGATIVE"
                color = "red"
                emoji = "😠"
            else:
                sentiment = "NEUTRAL"
                color = "gray"
                emoji = "😐"
            st.markdown(f"### Result: :{color}[{emoji} {sentiment}]")
            st.markdown(f"**Polarity Score:** {round(polarity, 3)}")

    st.divider()

    st.markdown("<div class='section-title'>📋 Historical Reviews Table</div>", unsafe_allow_html=True)
    st.markdown(f"<small>Showing {len(filtered_df)} reviews</small>", unsafe_allow_html=True)
    st.dataframe(
        filtered_df[['username', 'review', 'sentiment', 'rating', 'date']],
        use_container_width=True
    )

# ─────────────────────────────────────────
# Main App Logic
# ─────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    if st.session_state.get('role') == 'admin':
        admin_dashboard()
    else:
        analyst_dashboard()
else:
    login_page()