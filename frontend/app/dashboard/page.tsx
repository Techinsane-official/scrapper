'use client'

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Welcome to Scraper Dashboard
              </h1>
              <p className="text-gray-600 mb-8">
                Your professional e-commerce scraping platform
              </p>
              <div className="space-y-4">
                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    🚀 Dashboard Features
                  </h2>
                  <ul className="text-gray-600 space-y-2">
                    <li>• Create and manage scraping jobs</li>
                    <li>• Monitor job progress in real-time</li>
                    <li>• View scraped product data</li>
                    <li>• Export data in multiple formats</li>
                    <li>• Analytics and reporting</li>
                  </ul>
                </div>
                <div className="bg-blue-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800 mb-2">
                    Next Steps
                  </h3>
                  <p className="text-blue-700">
                    Set up your environment variables in Vercel to connect to the backend API and start scraping!
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}