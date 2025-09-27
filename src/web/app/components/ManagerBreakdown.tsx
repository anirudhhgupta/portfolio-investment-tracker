'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Holding {
  manager_name: string
  current_market_value: number
  current_investment_value: number
  pl_amount: number
}

interface ManagerBreakdownProps {
  holdings: Holding[]
}

export default function ManagerBreakdown({ holdings }: ManagerBreakdownProps) {
  // Group holdings by manager
  const managerData = holdings.reduce((acc, holding) => {
    const manager = holding.manager_name
    if (!acc[manager]) {
      acc[manager] = {
        name: manager,
        investment: 0,
        currentValue: 0,
        pl: 0,
        count: 0
      }
    }
    acc[manager].investment += holding.current_investment_value
    acc[manager].currentValue += holding.current_market_value
    acc[manager].pl += holding.pl_amount
    acc[manager].count += 1
    return acc
  }, {} as Record<string, any>)

  // Convert to chart data and sort by current value
  const chartData = Object.values(managerData)
    .sort((a: any, b: any) => b.currentValue - a.currentValue)

  const formatCurrency = (amount: number) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(1)}Cr`
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`
    }
    return `₹${(amount / 1000).toFixed(0)}K`
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const returnPct = data.investment > 0 ? ((data.pl / data.investment) * 100).toFixed(2) : '0.00'
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          <p className="text-sm text-blue-600">Investment: {formatCurrency(data.investment)}</p>
          <p className="text-sm text-green-600">Current: {formatCurrency(data.currentValue)}</p>
          <p className="text-sm text-gray-600">P&L: {formatCurrency(data.pl)} ({returnPct}%)</p>
          <p className="text-sm text-gray-500">{data.count} holdings</p>
        </div>
      )
    }
    return null
  }

  // Custom label function for x-axis to truncate long names
  const formatXAxisLabel = (value: string) => {
    if (value.length <= 10) return value
    return value.substring(0, 8) + '...'
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Manager Performance</h3>
      
      {chartData.length > 0 ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
                interval={0}
                fontSize={12}
                tickFormatter={formatXAxisLabel}
              />
              <YAxis 
                tickFormatter={formatCurrency}
                fontSize={12}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="investment" 
                fill="#93C5FD" 
                name="Investment"
                radius={[0, 0, 4, 4]}
              />
              <Bar 
                dataKey="currentValue" 
                fill="#3B82F6" 
                name="Current Value"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-80 flex items-center justify-center">
          <p className="text-gray-500">No data available</p>
        </div>
      )}

      {/* Summary Table */}
      {chartData.length > 0 && (
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 font-medium text-gray-700">Manager</th>
                <th className="text-right py-2 font-medium text-gray-700">Holdings</th>
                <th className="text-right py-2 font-medium text-gray-700">Investment</th>
                <th className="text-right py-2 font-medium text-gray-700">Current Value</th>
                <th className="text-right py-2 font-medium text-gray-700">Return %</th>
              </tr>
            </thead>
            <tbody>
              {chartData.map((manager: any, index) => {
                const returnPct = manager.investment > 0 ? ((manager.pl / manager.investment) * 100) : 0
                return (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-2 text-gray-900">{manager.name}</td>
                    <td className="py-2 text-right text-gray-600">{manager.count}</td>
                    <td className="py-2 text-right text-gray-900">{formatCurrency(manager.investment)}</td>
                    <td className="py-2 text-right text-gray-900">{formatCurrency(manager.currentValue)}</td>
                    <td className={`py-2 text-right font-medium ${
                      returnPct >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}