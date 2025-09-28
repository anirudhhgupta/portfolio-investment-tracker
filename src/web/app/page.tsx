import fs from 'fs'
import path from 'path'

interface Holding {
  manager_name: string
  asset_type: string
  asset_name: string
  current_investment_value: number
  current_market_value: number
  value_as_of_date: string
  pl_amount: number
  pl_percentage: number
  irr_percentage: number
  investment_date: string
}

export default async function Portfolio() {
  let holdings: Holding[] = []
  let error: string | null = null

  try {
    const dataPath = path.join(process.cwd(), '..', '..', 'data', 'output', 'extracted_portfolio_data.json')
    
    if (fs.existsSync(dataPath)) {
      const rawData = JSON.parse(fs.readFileSync(dataPath, 'utf8'))
      holdings = rawData.filter((item: any) => {
        return (item.current_market_value > 0 && 
                !item.asset_name.startsWith('*') &&
                !item.asset_name.startsWith('Disclaimer'))
      })
    } else {
      error = 'Portfolio data not found'
    }
  } catch (err) {
    error = 'Failed to load data'
  }

  const formatCurrency = (amount: number) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)}Cr`
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)}L`
    }
    return `₹${amount.toLocaleString('en-IN')}`
  }

  const formatPercentage = (percentage: number) => {
    return `${percentage >= 0 ? '+' : ''}${percentage.toFixed(2)}%`
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-700">{error}</p>
        </div>
      </div>
    )
  }

  const totalInvestment = holdings.reduce((sum, h) => sum + h.current_investment_value, 0)
  const totalMarketValue = holdings.reduce((sum, h) => sum + h.current_market_value, 0)
  const totalPL = totalMarketValue - totalInvestment
  const totalPLPercentage = totalInvestment > 0 ? (totalPL / totalInvestment) * 100 : 0

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold text-gray-900">Portfolio Tracker</h1>
            <div className="text-sm text-gray-600">
              {holdings.length} Holdings • Data as of August 2025
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Total Investment</div>
            <div className="text-2xl font-bold text-gray-900">{formatCurrency(totalInvestment)}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">Current Value</div>
            <div className="text-2xl font-bold text-gray-900">{formatCurrency(totalMarketValue)}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">P&L Amount</div>
            <div className={`text-2xl font-bold ${totalPL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(Math.abs(totalPL))}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-500">P&L Percentage</div>
            <div className={`text-2xl font-bold ${totalPLPercentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercentage(totalPLPercentage)}
            </div>
          </div>
        </div>

        {/* Holdings Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">Holdings</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Manager</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Investment</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Current</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">P&L %</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">IRR %</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {holdings.map((holding, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900">{holding.asset_name}</div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{holding.manager_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{holding.asset_type}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">{formatCurrency(holding.current_investment_value)}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">{formatCurrency(holding.current_market_value)}</td>
                    <td className={`px-4 py-3 text-sm text-right ${holding.pl_amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(Math.abs(holding.pl_amount))}
                    </td>
                    <td className={`px-4 py-3 text-sm text-right ${holding.pl_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPercentage(holding.pl_percentage)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 text-right">{holding.irr_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}