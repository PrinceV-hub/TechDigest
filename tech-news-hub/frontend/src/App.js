import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast, ToastContainer } from 'react-toastify';
import { formatDistanceToNow, parseISO } from 'date-fns';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch articles
  const fetchArticles = async (page = 1, source = '') => {
    try {
      setLoading(true);
      const params = { page, per_page: 20 };
      if (source) params.source = source;
      
      const response = await axios.get(`${API_BASE_URL}/news`, { params });
      
      setArticles(response.data.articles);
      setTotalPages(response.data.pages);
      setCurrentPage(page);
      
      // Check for new articles notification
      if (page === 1 && articles.length > 0 && response.data.articles.length > 0) {
        const latestArticleTime = response.data.articles[0].published_time;
        if (lastUpdate && latestArticleTime !== lastUpdate) {
          toast.success('🔄 New tech updates available!');
        }
        setLastUpdate(latestArticleTime);
      }
      
    } catch (err) {
      setError('Failed to fetch articles');
      toast.error('Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats');
    }
  };

  // Fetch sources
  const fetchSources = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/sources`);
      setSources(response.data);
    } catch (err) {
      console.error('Failed to fetch sources');
    }
  };

  // Manual fetch
  const handleManualFetch = async () => {
    try {
      toast.info('🔄 Fetching latest tech news...');
      await axios.post(`${API_BASE_URL}/fetch-now`);
      await fetchArticles(1, selectedSource);
      await fetchStats();
      toast.success('✅ News updated successfully!');
    } catch (err) {
      toast.error('Failed to fetch news');
    }
  };

  // Handle source filter
  const handleSourceChange = (source) => {
    setSelectedSource(source);
    setCurrentPage(1);
    fetchArticles(1, source);
  };

  // Handle pagination
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      fetchArticles(newPage, selectedSource);
    }
  };

  // Initial load
  useEffect(() => {
    fetchArticles();
    fetchStats();
    fetchSources();
  }, []);

  // Auto-refresh every 5 minutes to check for updates
  useEffect(() => {
    const interval = setInterval(() => {
      fetchArticles(1, selectedSource);
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [selectedSource]);

  if (loading && articles.length === 0) {
    return (
      <div className="app">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading latest tech news...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <ToastContainer position="top-right" />
      
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1 className="title">🚀 Tech News Hub</h1>
          <p className="subtitle">Latest technology updates every 3 hours</p>
          
          {/* Stats */}
          <div className="stats">
            <div className="stat-item">
              <span className="stat-number">{stats.total_articles || 0}</span>
              <span className="stat-label">Articles</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.sources_count || 0}</span>
              <span className="stat-label">Sources</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">3h</span>
              <span className="stat-label">Update Freq</span>
            </div>
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="controls">
        <div className="container">
          <div className="control-group">
            <select 
              value={selectedSource} 
              onChange={(e) => handleSourceChange(e.target.value)}
              className="source-filter"
            >
              <option value="">All Sources</option>
              {sources.map(source => (
                <option key={source} value={source}>{source}</option>
              ))}
            </select>
            
            <button onClick={handleManualFetch} className="refresh-btn">
              🔄 Refresh Now
            </button>
          </div>
          
          {stats.latest_update && (
            <p className="last-update">
              Last updated: {formatDistanceToNow(parseISO(stats.latest_update), { addSuffix: true })}
            </p>
          )}
        </div>
      </div>

      {/* Articles */}
      <main className="main">
        <div className="container">
          {error && (
            <div className="error">
              ⚠️ {error}
            </div>
          )}

          <div className="articles-grid">
            {articles.map((article) => (
              <article key={article.id} className="article-card">
                <div className="article-header">
                  <h2 className="article-title">
                    <a href={article.source_url} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                  </h2>
                  <div className="article-meta">
                    <span className="source">{article.source_name}</span>
                    <span className="time">
                      {formatDistanceToNow(parseISO(article.published_time), { addSuffix: true })}
                    </span>
                  </div>
                </div>
                
                <div className="article-content">
                  <p className="summary">{article.summary}</p>
                  <a 
                    href={article.source_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="read-more"
                  >
                    Read Full Article →
                  </a>
                </div>
              </article>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="page-btn"
              >
                ← Previous
              </button>
              
              <span className="page-info">
                Page {currentPage} of {totalPages}
              </span>
              
              <button 
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="page-btn"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>Tech News Hub - Automated technology updates every 3 hours</p>
          <p>Built with React + Flask • Data from {sources.length} trusted sources</p>
        </div>
      </footer>
    </div>
  );
}

export default App;