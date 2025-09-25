'use client'

interface PriceChange {
  product_id: string
  old_price: number
  new_price: number
  change_percentage: number
  detected_at: string
}

interface PriceMonitoringProps {
  data: {
    price_changes: PriceChange[]
  }
}

export default function PriceMonitoring({ data }: PriceMonitoringProps) {
  const priceChanges = data.price_changes || []

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Price Monitoring</h2>
        <span className="text-sm text-gray-500">
          {priceChanges.length} changes detected
        </span>
      </div>

      {priceChanges.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-gray-500">No price changes detected yet</p>
          <p className="text-gray-400 text-sm">Price monitoring will show changes here</p>
        </div>
      ) : (
        <div className="space-y-3">
          {priceChanges.slice(0, 10).map((change, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900">
                    Product {change.product_id.slice(0, 8)}...
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    change.change_percentage > 0 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {change.change_percentage > 0 ? '+' : ''}{change.change_percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  ${change.old_price} → ${change.new_price}
                </div>
              </div>
              <div className="text-xs text-gray-500">
                {new Date(change.detected_at).toLocaleTimeString()}
              </div>
            </div>
          ))}
          
          {priceChanges.length > 10 && (
            <div className="text-center pt-2">
              <button className="text-sm text-blue-600 hover:text-blue-800">
                View all {priceChanges.length} changes
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
