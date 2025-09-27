import { TrendingUp, TrendingDown } from 'lucide-react'

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
  raw_data: any
}

interface HoldingsTableProps {
  holdings: Holding[]
}

export default function HoldingsTable({ holdings }: HoldingsTableProps) {
  const formatCurrency = (amount: number) => {
    if (amount >= 10000000) { // 1 crore
      return `₹${(amount / 10000000).toFixed(2)}Cr`
    } else if (amount >= 100000) { // 1 lakh
      return `₹${(amount / 100000).toFixed(2)}L`
    }
    return `₹${amount.toLocaleString('en-IN')}`
  }

  const formatPercentage = (percentage: number) => {
    return `${percentage >= 0 ? '+' : ''}${percentage.toFixed(2)}%`
  }

  const formatUSD = (amount: number) => {
    return `$${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  const hasUSDValues = (holding: Holding) => {
    return holding.raw_data && 
           holding.raw_data.market_value_usd !== undefined && 
           holding.raw_data.cost_basis_usd !== undefined
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Portfolio Holdings</h3>
        <p className="text-sm text-gray-600">Detailed view of all investments</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Asset Name
              </th>
              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Manager
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Investment (₹)
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Investment ($)
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Current (₹)
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Current ($)
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                P&L (₹)
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                P&L %
              </th>
              <th className="px-2 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                IRR %
              </th>
              <th className="px-2 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Inv. Date
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {holdings.map((holding, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {/* Asset Name */}
                <td className="px-2 py-2">
                  <div className="text-xs font-medium text-gray-900" title={holding.asset_name}>
                    {holding.asset_name}
                  </div>
                </td>
                
                {/* Asset Type */}
                <td className="px-2 py-2">
                  <span className="text-xs text-gray-700">{holding.asset_type}</span>
                </td>
                
                {/* Manager */}
                <td className="px-2 py-2">
                  <span className="text-xs text-gray-700">{holding.manager_name}</span>
                </td>
                
                {/* Investment (₹) */}
                <td className="px-2 py-2 text-right">
                  <span className="text-xs font-medium text-gray-900">
                    {formatCurrency(holding.current_investment_value)}
                  </span>
                </td>
                
                {/* Investment ($) */}
                <td className="px-2 py-2 text-right">
                  {hasUSDValues(holding) ? (
                    <span className="text-xs text-gray-700">
                      {formatUSD(holding.raw_data.cost_basis_usd)}
                    </span>
                  ) : (
                    <span className="text-xs text-gray-400">-</span>
                  )}
                </td>
                
                {/* Current (₹) */}
                <td className="px-2 py-2 text-right">
                  <span className="text-xs font-medium text-gray-900">
                    {formatCurrency(holding.current_market_value)}
                  </span>
                </td>
                
                {/* Current ($) */}
                <td className="px-2 py-2 text-right">
                  {hasUSDValues(holding) ? (
                    <span className="text-xs text-gray-700">
                      {formatUSD(holding.raw_data.market_value_usd)}
                    </span>
                  ) : (
                    <span className="text-xs text-gray-400">-</span>
                  )}
                </td>
                
                {/* P&L (₹) */}
                <td className="px-2 py-2 text-right">
                  <div className="flex items-center justify-end">
                    {holding.pl_amount >= 0 ? (
                      <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
                    ) : (
                      <TrendingDown className="h-3 w-3 text-red-500 mr-1" />
                    )}
                    <span className={`text-xs font-medium ${
                      holding.pl_amount >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(Math.abs(holding.pl_amount))}
                    </span>
                  </div>
                </td>
                
                {/* P&L % */}
                <td className="px-2 py-2 text-right">
                  <span className={`text-xs font-medium ${
                    holding.pl_percentage >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercentage(holding.pl_percentage)}
                  </span>
                </td>
                
                {/* IRR % */}
                <td className="px-2 py-2 text-right">
                  <span className="text-xs font-medium text-blue-600">
                    {holding.irr_percentage ? `${holding.irr_percentage.toFixed(2)}%` : 'N/A'}
                  </span>
                </td>
                
                {/* Investment Date */}
                <td className="px-2 py-2 text-center">
                  <span className="text-xs text-gray-500">
                    {holding.investment_date || 'N/A'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {holdings.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No holdings found</p>
        </div>
      )}
    </div>
  )
}