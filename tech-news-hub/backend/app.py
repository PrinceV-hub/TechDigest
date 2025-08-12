from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import feedparser
from datetime import datetime, timezone
import hashlib
import os
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tech_news.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# News Article Model
class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(1000), nullable=False)
    source_name = db.Column(db.String(100), nullable=False)
    published_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content_hash = db.Column(db.String(64), unique=True, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'source_url': self.source_url,
            'source_name': self.source_name,
            'published_time': self.published_time.isoformat() if self.published_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# RSS Feed Sources
RSS_FEEDS = [
    {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/'},
    {'name': 'Ars Technica', 'url': 'http://feeds.arstechnica.com/arstechnica/index'},
    {'name': 'Wired', 'url': 'https://www.wired.com/feed/rss'},
    {'name': 'The Verge', 'url': 'https://www.theverge.com/rss/index.xml'},
    {'name': 'Engadget', 'url': 'https://www.engadget.com/rss.xml'},
    {'name': 'MIT Technology Review', 'url': 'https://www.technologyreview.com/feed/'},
    {'name': 'IEEE Spectrum', 'url': 'https://spectrum.ieee.org/rss'},
    {'name': 'VentureBeat', 'url': 'https://venturebeat.com/feed/'}
]

def clean_text(text):
    """Clean and format text content"""
    if not text:
        return ""
    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    # Clean up whitespace
    text = ' '.join(text.split())
    return text[:1000]  # Limit summary length

def generate_content_hash(title, url):
    """Generate unique hash for article to prevent duplicates"""
    content = f"{title}{url}"
    return hashlib.sha256(content.encode()).hexdigest()

def parse_published_time(time_struct):
    """Parse RSS time to datetime object"""
    try:
        if time_struct:
            return datetime(*time_struct[:6], tzinfo=timezone.utc)
    except:
        pass
    return datetime.now(timezone.utc)

def fetch_news():
    """Fetch news from all RSS feeds"""
    print(f"Starting news fetch at {datetime.now()}")
    new_articles = 0
    
    for feed_info in RSS_FEEDS:
        try:
            print(f"Fetching from {feed_info['name']}...")
            feed = feedparser.parse(feed_info['url'])
            
            for entry in feed.entries[:10]:  # Limit to 10 latest articles per source
                try:
                    title = clean_text(entry.title)
                    summary = clean_text(entry.get('summary', entry.get('description', '')))
                    url = entry.link
                    
                    # Skip if essential data is missing
                    if not title or not url:
                        continue
                    
                    # Generate content hash to prevent duplicates
                    content_hash = generate_content_hash(title, url)
                    
                    # Check if article already exists
                    existing = NewsArticle.query.filter_by(content_hash=content_hash).first()
                    if existing:
                        continue
                    
                    # Parse publication time
                    published_time = parse_published_time(entry.get('published_parsed'))
                    
                    # Create new article
                    article = NewsArticle(
                        title=title,
                        summary=summary if summary else title,  # Use title as summary if no summary
                        source_url=url,
                        source_name=feed_info['name'],
                        published_time=published_time,
                        content_hash=content_hash
                    )
                    
                    db.session.add(article)
                    new_articles += 1
                    
                except Exception as e:
                    print(f"Error processing article from {feed_info['name']}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching from {feed_info['name']}: {e}")
            continue
    
    try:
        db.session.commit()
        print(f"Successfully added {new_articles} new articles")
    except Exception as e:
        db.session.rollback()
        print(f"Error saving to database: {e}")

# API Routes
@app.route('/api/news', methods=['GET'])
def get_news():
    """Get latest news articles"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        source = request.args.get('source', '')
        
        query = NewsArticle.query
        
        if source:
            query = query.filter_by(source_name=source)
        
        articles = query.order_by(NewsArticle.published_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'articles': [article.to_dict() for article in articles.items],
            'total': articles.total,
            'pages': articles.pages,
            'current_page': page,
            'has_next': articles.has_next,
            'has_prev': articles.has_prev
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sources', methods=['GET'])
def get_sources():
    """Get available news sources"""
    sources = db.session.query(NewsArticle.source_name).distinct().all()
    return jsonify([source[0] for source in sources])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    try:
        total_articles = NewsArticle.query.count()
        sources_count = db.session.query(NewsArticle.source_name).distinct().count()
        latest_update = db.session.query(NewsArticle.created_at).order_by(
            NewsArticle.created_at.desc()
        ).first()
        
        return jsonify({
            'total_articles': total_articles,
            'sources_count': sources_count,
            'latest_update': latest_update[0].isoformat() if latest_update else None,
            'update_frequency': '3 hours'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fetch-now', methods=['POST'])
def fetch_now():
    """Manually trigger news fetch"""
    try:
        fetch_news()
        return jsonify({'message': 'News fetch completed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Initialize scheduler
def init_scheduler():
    """Initialize the background scheduler"""
    scheduler = BackgroundScheduler(daemon=True)
    # Fetch news every 3 hours
    scheduler.add_job(fetch_news, 'interval', hours=3, id='news_fetcher')
    scheduler.start()
    return scheduler

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Fetch initial news if database is empty
        if NewsArticle.query.count() == 0:
            print("Database is empty. Fetching initial news...")
            fetch_news()
    
    # Start scheduler
    scheduler = init_scheduler()
    
    try:
        # Run Flask app
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
    except KeyboardInterrupt:
        print("Shutting down...")
        scheduler.shutdown()