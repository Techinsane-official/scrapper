'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import { api } from '@/lib/api'
import { 
  MagnifyingGlassIcon,
  ArrowPathIcon,
  StarIcon,
  ShoppingCartIcon,
  EyeIcon
} from '@heroicons/react/24/outline'

export default function ProductsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  const { data: products, isLoading, error } = useQuery('products', () => api.getProducts(), {
    onError: (err: any) => {
      console.error('Error fetching products:', err)
    }
  })

  const filteredProducts = products?.filter((product: any) => {
    const matchesSearch = product.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.brand?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterStatus === 'all' || product.availability === filterStatus
    return matchesSearch && matchesFilter
  }) || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500" />
        <p className="ml-3 text-lg text-gray-600">Loading products...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Scraped Products</h1>
        <div className="text-sm text-gray-500">
          {products?.length || 0} products found
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search products by title or brand..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          
          <div className="md:w-48">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Products</option>
              <option value="in_stock">In Stock</option>
              <option value="out_of_stock">Out of Stock</option>
              <option value="limited">Limited</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products Grid */}
      {error ? (
        <div className="bg-white shadow rounded-lg p-6 text-center text-red-600">
          Failed to load products. Please try again.
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-6 text-center text-gray-500">
          {searchTerm || filterStatus !== 'all' 
            ? 'No products match your search criteria.' 
            : 'No products found. Create a scraping job to start collecting product data.'
          }
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product: any) => (
            <div key={product.id} className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
              {/* Product Image */}
              <div className="aspect-w-16 aspect-h-9 bg-gray-200">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.title}
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder-product.png'
                    }}
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                    <ShoppingCartIcon className="h-12 w-12 text-gray-400" />
                  </div>
                )}
              </div>
              
              {/* Product Info */}
              <div className="p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2 line-clamp-2">
                  {product.title}
                </h3>
                
                {product.brand && (
                  <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
                )}
                
                {/* Price */}
                <div className="flex items-center space-x-2 mb-3">
                  {product.price && (
                    <span className="text-xl font-bold text-green-600">
                      ${product.price}
                    </span>
                  )}
                  {product.original_price && product.original_price !== product.price && (
                    <span className="text-sm text-gray-500 line-through">
                      ${product.original_price}
                    </span>
                  )}
                </div>
                
                {/* Rating */}
                {product.rating && (
                  <div className="flex items-center space-x-1 mb-3">
                    <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="text-sm text-gray-600">{product.rating}</span>
                    {product.review_count && (
                      <span className="text-sm text-gray-500">
                        ({product.review_count} reviews)
                      </span>
                    )}
                  </div>
                )}
                
                {/* Availability */}
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    product.availability === 'in_stock' 
                      ? 'bg-green-100 text-green-800'
                      : product.availability === 'out_of_stock'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {product.availability?.replace('_', ' ') || 'Unknown'}
                  </span>
                  
                  <button className="text-primary-600 hover:text-primary-800">
                    <EyeIcon className="h-5 w-5" />
                  </button>
                </div>
                
                {/* Scraped Date */}
                <div className="mt-3 text-xs text-gray-400">
                  Scraped: {new Date(product.scraped_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
