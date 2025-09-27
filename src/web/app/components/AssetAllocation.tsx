'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

interface Holding {
  asset_type: string
  current_market_value: number
}

interface AssetAllocationProps {
  holdings: Holding[]
}

const COLORS = [
  '#3B82F6', // Blue
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#EF4444', // Red
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#84CC16', // Lime
  '#F97316', // Orange
]

export default function AssetAllocation({ holdings }: AssetAllocationProps) {
  // Group holdings by asset type
  const assetData = holdings.reduce((acc, holding) => {
    const assetType = holding.asset_type
    if (!acc[assetType]) {
      acc[assetType] = 0
    }
    acc[assetType] += holding.current_market_value
    return acc
  }, {} as Record<string, number>)

  // Convert to chart data
  const chartData = Object.entries(assetData)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)

  const total = chartData.reduce((sum, item) => sum + item.value, 0)

  const formatCurrency = (amount: number) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(1)}Cr`
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`
    }
    return `₹${amount.toLocaleString('en-IN')}`
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      const percentage = ((data.value / total) * 100).toFixed(1)
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{data.name}</p>
          <p className="text-sm text-gray-600">{formatCurrency(data.value)}</p>
          <p className="text-sm text-gray-600">{percentage}% of portfolio</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h3>
      
      {chartData.length > 0 ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                dataKey="value"
                stroke="#fff"
                strokeWidth={2}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-80 flex items-center justify-center">
          <p className="text-gray-500">No data available</p>
        </div>
      )}

      {/* Legend */}
      {chartData.length > 0 && (
        <div className="mt-4 space-y-2">
          {chartData.map((item, index) => {
            const percentage = ((item.value / total) * 100).toFixed(1)
            return (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-gray-700">{item.name}</span>
                </div>
                <div className="text-right">
                  <div className="font-medium">{formatCurrency(item.value)}</div>
                  <div className="text-xs text-gray-500">{percentage}%</div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}