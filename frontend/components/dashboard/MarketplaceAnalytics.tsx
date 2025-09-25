'use client'

import { useQuery } from 'react-query'
import { api } from '@/lib/api'

interface MarketplaceAnalyticsProps {
  data: {
    total_products: number
    retailer_distribution: Record<string, number>
    retailer_avg_prices: Record<string, number>
    retailer_avg_ratings: Record<string, number>
    price_distribution: Record<string, number>
    quality_distribution: Record<string, number>
    availability_distribution: Record<string, number>
    avg_data_quality: number
    curated_products: number
  }
}

export default function MarketplaceAnalytics({ data }: MarketplaceAnalyticsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Marketplace Analytics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Retailer Distribution */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Retailer Distribution</h3>
          <div className="space-y-1">
            {Object.entries(data.retailer_distribution).map(([retailer, count]) => (
              <div key={retailer} className="flex justify-between text-sm">
                <span className="capitalize">{retailer}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Price Distribution */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Price Distribution</h3>
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span>Under $25</span>
              <span className="font-medium">{data.price_distribution.under_25}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>$25 - $50</span>
              <span className="font-medium">{data.price_distribution['25_50']}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>$50 - $100</span>
              <span className="font-medium">{data.price_distribution['50_100']}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>$100 - $500</span>
              <span className="font-medium">{data.price_distribution['100_500']}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Over $500</span>
              <span className="font-medium">{data.price_distribution.over_500}</span>
            </div>
          </div>
        </div>

        {/* Quality Distribution */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Data Quality</h3>
          <div className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="text-green-600">Excellent</span>
              <span className="font-medium">{data.quality_distribution.excellent}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-blue-600">Good</span>
              <span className="font-medium">{data.quality_distribution.good}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-yellow-600">Fair</span>
              <span className="font-medium">{data.quality_distribution.fair}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-red-600">Poor</span>
              <span className="font-medium">{data.quality_distribution.poor}</span>
            </div>
          </div>
        </div>

        {/* Availability Distribution */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Availability</h3>
          <div className="space-y-1">
            {Object.entries(data.availability_distribution).map(([status, count]) => (
              <div key={status} className="flex justify-between text-sm">
                <span className="capitalize">{status.replace('_', ' ')}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{data.total_products}</div>
          <div className="text-sm text-blue-800">Total Products</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{data.curated_products}</div>
          <div className="text-sm text-green-800">Curated Products</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">{(data.avg_data_quality * 100).toFixed(1)}%</div>
          <div className="text-sm text-purple-800">Avg Data Quality</div>
        </div>
      </div>
    </div>
  )
}
