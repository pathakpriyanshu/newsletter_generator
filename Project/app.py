from flask import Flask, render_template, request, send_file
import feedparser
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# RSS Feed Sources  
RSS_FEEDS = {
    "General News": ["https://feeds.bbci.co.uk/news/rss.xml", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"],
    "Technology": ["https://techcrunch.com/feed/", "https://www.wired.com/feed/rss"],
    "Finance": ["https://www.bloomberg.com/feed/", "https://www.ft.com/rss/homepage"],
    "Sports": ["https://www.espn.com/espn/rss/news", "https://feeds.bbci.co.uk/sport/rss.xml"],
    "Entertainment": ["https://variety.com/feed/", "https://www.billboard.com/feed/"],
    "Science": ["https://www.nasa.gov/rss/dyn/breaking_news.rss", "https://www.sciencedaily.com/rss/all.xml"]
}

# Fetch articles from RSS feeds
def fetch_articles(categories):
    articles = []
    for category, percentage in categories.items():
        if category in RSS_FEEDS:
            feeds = RSS_FEEDS[category]
            for feed_url in feeds:
                feed = feedparser.parse(feed_url)
                articles.extend(feed.entries[:int(len(feed.entries) * (percentage / 100))])
    return articles

# Generate PDF Newsletter
def generate_pdf(articles):
    file_path = "newsletter.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Personalized Newsletter")
    c.setFont("Helvetica", 12)
    c.drawString(200, height - 70, f"Generated on {datetime.now().strftime('%Y-%m-%d')}")
    y_position = height - 100

    for article in articles:
        if y_position < 100:  # Start a new page if space is running out
            c.showPage()
            y_position = height - 50

        # Article Title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, article.title)
        y_position -= 20

        # Summary
        c.setFont("Helvetica", 10)
        summary = article.summary[:200] + "..."  # Limit summary length
        c.drawString(50, y_position, summary)
        y_position -= 20

        # Read More Link
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColorRGB(0, 0, 1)  # Blue color for link
        c.drawString(50, y_position, f"Read more: {article.link}")
        y_position -= 30  # Space before next article

    c.save()
    return file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Get form data (categories and percentages)
    categories = {
        request.form['category1']: int(request.form['slider1']),
        request.form['category2']: int(request.form['slider2']),
        request.form['category3']: int(request.form['slider3']),
        request.form['category4']: int(request.form['slider4']),
        request.form['category5']: int(request.form['slider5']),
    }
    
    # Fetch articles based on user preferences
    articles = fetch_articles(categories)
    
    # Generate PDF content
    pdf_path = generate_pdf(articles)
    
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
