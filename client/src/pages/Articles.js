import React from 'react';
import "./../styles/Articles.css"

function Articles() {
  const articles = [
    { id: 1, title: "Article 1 Place Holder", url: "/" },
    { id: 2, title: "Article 2 Place Holder", url: "/"}
  ];

  return (
    <div className="main-container" style={{ padding: '20px', maxWidth: "600px", margin: '0 auto' }}>
      <h1>Articles</h1>
      <div className="article-list">
        {articles.map((article) => (
          <div key={article.id} className="article-row">
            <a href={article.url} className="article-link">
              {article.title}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Articles;