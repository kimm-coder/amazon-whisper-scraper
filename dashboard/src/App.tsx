import { useState } from 'react'
import products from './data/products.json'
import { Product } from './types/Product'
import './App.css'

function StarRating({ rating }: { rating: number | null }) {
  if (rating === null) return <span className="no-rating">No ratings yet</span>

  const fullStars = Math.floor(rating)
  const hasHalf = rating % 1 >= 0.5
  const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0)

  return (
    <div className="star-rating">
      {[...Array(fullStars)].map((_, i) => (
        <span key={`full-${i}`} className="star full">★</span>
      ))}
      {hasHalf && <span className="star half">★</span>}
      {[...Array(emptyStars)].map((_, i) => (
        <span key={`empty-${i}`} className="star empty">☆</span>
      ))}
      <span className="rating-value">{rating.toFixed(1)}</span>
    </div>
  )
}

function ProductCard({ product }: { product: Product }) {
  const shortName = product.product_name.split('|')[0].trim()

  return (
    <div className="product-card">
      <a href={product.direct_link} target="_blank" rel="noopener noreferrer">
        <div className="product-image">
          <img src={product.main_photo} alt={shortName} />
        </div>
      </a>
      <div className="product-info">
        <h3 className="product-name" title={product.product_name}>
          {shortName}
        </h3>
        <div className="product-meta">
          <StarRating rating={product.star_rating} />
          {product.review_count !== null && (
            <span className="review-count">({product.review_count.toLocaleString()} reviews)</span>
          )}
        </div>
        <div className="product-price">{product.price}</div>
        {product.sales_rank && (
          <div className="sales-rank">{product.sales_rank}</div>
        )}
        <div className="product-asin">ASIN: {product.asin}</div>
        <a
          href={product.direct_link}
          target="_blank"
          rel="noopener noreferrer"
          className="view-button"
        >
          View on Amazon
        </a>
      </div>
    </div>
  )
}

function App() {
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'name' | 'price' | 'rating'>('name')

  const typedProducts: Product[] = products

  const filteredProducts = typedProducts
    .filter(p =>
      p.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.asin.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'price':
          const priceA = parseFloat(a.price.replace(/[^0-9.]/g, ''))
          const priceB = parseFloat(b.price.replace(/[^0-9.]/g, ''))
          return priceA - priceB
        case 'rating':
          return (b.star_rating ?? 0) - (a.star_rating ?? 0)
        default:
          return a.product_name.localeCompare(b.product_name)
      }
    })

  const totalProducts = typedProducts.length
  const avgRating = typedProducts
    .filter(p => p.star_rating !== null)
    .reduce((acc, p, _, arr) => acc + (p.star_rating ?? 0) / arr.length, 0)

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Whisper Ear Care</h1>
        <p className="subtitle">Amazon Store Products Dashboard</p>
      </header>

      <div className="stats-bar">
        <div className="stat">
          <span className="stat-value">{totalProducts}</span>
          <span className="stat-label">Products</span>
        </div>
        <div className="stat">
          <span className="stat-value">{avgRating.toFixed(1)}</span>
          <span className="stat-label">Avg Rating</span>
        </div>
      </div>

      <div className="controls">
        <input
          type="text"
          placeholder="Search products or ASIN..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'name' | 'price' | 'rating')}
          className="sort-select"
        >
          <option value="name">Sort by Name</option>
          <option value="price">Sort by Price</option>
          <option value="rating">Sort by Rating</option>
        </select>
      </div>

      <div className="products-grid">
        {filteredProducts.map((product) => (
          <ProductCard key={product.asin} product={product} />
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <p className="no-results">No products found matching "{searchTerm}"</p>
      )}
    </div>
  )
}

export default App
