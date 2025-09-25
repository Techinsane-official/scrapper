'use client'

interface RetailerDistributionProps {
  data: Record<string, number>
}

export default function RetailerDistribution({ data }: RetailerDistributionProps) {
  const total = Object.values(data).reduce((sum, count) => sum + count, 0)
  const retailers = Object.entries(data).sort(([,a], [,b]) => b - a)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Retailer Distribution</h2>
      
      <div className="space-y-3">
        {retailers.map(([retailer, count]) => {
          const percentage = total > 0 ? (count / total) * 100 : 0
          
          return (
            <div key={retailer} className="flex items-center">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {retailer}
                  </span>
                  <span className="text-sm text-gray-500">
                    {count} ({percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {retailers.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <p className="text-gray-500">No retailer data available</p>
          <p className="text-gray-400 text-sm">Start scraping to see distribution</p>
        </div>
      )}
    </div>
  )
}
