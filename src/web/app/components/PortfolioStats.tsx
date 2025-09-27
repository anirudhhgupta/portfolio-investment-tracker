import { DollarSign, TrendingUp, TrendingDown, Target } from 'lucide-react'

interface Holding {
  current_investment_value: number
  current_market_value: number
  pl_amount: number
  pl_percentage: number
}

interface PortfolioStatsProps {
  holdings: Holding[]
}

export default function PortfolioStats({ holdings }: PortfolioStatsProps) {
  const totalInvestment = holdings.reduce((sum, h) => sum + h.current_investment_value, 0)
  const totalMarketValue = holdings.reduce((sum, h) => sum + h.current_market_value, 0)
  const totalPL = totalMarketValue - totalInvestment
  const totalPLPercentage = totalInvestment > 0 ? (totalPL / totalInvestment) * 100 : 0

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

  const stats = [
    {
      title: 'Total Investment',
      value: formatCurrency(totalInvestment),
      icon: Target,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Current Value',
      value: formatCurrency(totalMarketValue),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Total P&L',
      value: formatCurrency(totalPL),
      icon: totalPL >= 0 ? TrendingUp : TrendingDown,
      color: totalPL >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: totalPL >= 0 ? 'bg-green-50' : 'bg-red-50'
    },
    {
      title: 'Return %',
      value: formatPercentage(totalPLPercentage),
      icon: totalPLPercentage >= 0 ? TrendingUp : TrendingDown,
      color: totalPLPercentage >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: totalPLPercentage >= 0 ? 'bg-green-50' : 'bg-red-50'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-full ${stat.bgColor}`}>
                <Icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}