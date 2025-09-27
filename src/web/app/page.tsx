'use client'

import { useState, useEffect } from 'react'
import { Search, Filter, TrendingUp, TrendingDown, DollarSign, Target, Calendar, BarChart3 } from 'lucide-react'
import PortfolioStats from './components/PortfolioStats'
import HoldingsTable from './components/HoldingsTable'
import AssetAllocation from './components/AssetAllocation'
import ManagerBreakdown from './components/ManagerBreakdown'

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

export default function Dashboard() {
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [filteredHoldings, setFilteredHoldings] = useState<Holding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedManager, setSelectedManager] = useState('all')
  const [selectedAssetType, setSelectedAssetType] = useState('all')
  const [sortField, setSortField] = useState<keyof Holding>('current_market_value')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')

  // Load portfolio data
  useEffect(() => {
    const loadPortfolioData = async () => {
      try {
        const response = await fetch('/api/portfolio')
        if (!response.ok) {
          throw new Error('Failed to load portfolio data')
        }
        const data = await response.json()
        setHoldings(data.holdings)
        setFilteredHoldings(data.holdings)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
        setLoading(false)
      }
    }

    loadPortfolioData()
  }, [])

  // Apply filters
  useEffect(() => {
    let filtered = holdings

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(holding =>
        holding.asset_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        holding.manager_name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Manager filter
    if (selectedManager !== 'all') {
      filtered = filtered.filter(holding => holding.manager_name === selectedManager)
    }

    // Asset type filter
    if (selectedAssetType !== 'all') {
      filtered = filtered.filter(holding => holding.asset_type === selectedAssetType)
    }

    // Sort
    filtered.sort((a, b) => {
      const aVal = a[sortField]
      const bVal = b[sortField]
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'desc' ? bVal - aVal : aVal - bVal
      }
      
      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      if (sortDirection === 'desc') {
        return bStr.localeCompare(aStr)
      }
      return aStr.localeCompare(bStr)
    })

    setFilteredHoldings(filtered)
  }, [holdings, searchTerm, selectedManager, selectedAssetType, sortField, sortDirection])

  // Get unique values for filters
  const managers = Array.from(new Set(holdings.map(h => h.manager_name))).sort()
  const assetTypes = Array.from(new Set(holdings.map(h => h.asset_type))).sort()

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <BarChart3 className="h-12 w-12 text-primary-500 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading portfolio data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <TrendingDown className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-2">Error loading portfolio data</p>
          <p className="text-gray-500 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Portfolio Tracker</h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              <span>Data as of August 2025</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Portfolio Overview */}
        <PortfolioStats holdings={filteredHoldings} />

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <AssetAllocation holdings={filteredHoldings} />
          <ManagerBreakdown holdings={filteredHoldings} />
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search holdings..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Manager Filter */}
            <div className="relative">
              <select
                className="w-full px-3 py-2 pr-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 cursor-pointer"
                value={selectedManager}
                onChange={(e) => setSelectedManager(e.target.value)}
              >
                <option value="all">All Managers</option>
                {managers.map(manager => (
                  <option key={manager} value={manager}>{manager}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            {/* Asset Type Filter */}
            <div className="relative">
              <select
                className="w-full px-3 py-2 pr-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 cursor-pointer"
                value={selectedAssetType}
                onChange={(e) => setSelectedAssetType(e.target.value)}
              >
                <option value="all">All Asset Types</option>
                {assetTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            {/* Sort */}
            <div className="relative">
              <select
                className="w-full px-3 py-2 pr-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 cursor-pointer"
                value={`${sortField}-${sortDirection}`}
                onChange={(e) => {
                  const [field, direction] = e.target.value.split('-')
                  setSortField(field as keyof Holding)
                  setSortDirection(direction as 'asc' | 'desc')
                }}
              >
                <option value="current_market_value-desc">Value (High to Low)</option>
                <option value="current_market_value-asc">Value (Low to High)</option>
                <option value="pl_percentage-desc">P&L % (High to Low)</option>
                <option value="pl_percentage-asc">P&L % (Low to High)</option>
                <option value="asset_name-asc">Name (A to Z)</option>
                <option value="asset_name-desc">Name (Z to A)</option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Active Filters Pills */}
          {(searchTerm || selectedManager !== 'all' || selectedAssetType !== 'all') && (
            <div className="mt-4 flex flex-wrap gap-2">
              {searchTerm && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                  <Search className="h-3 w-3" />
                  Search: "{searchTerm}"
                  <button
                    onClick={() => setSearchTerm('')}
                    className="ml-1 hover:text-blue-900"
                  >
                    ×
                  </button>
                </span>
              )}
              {selectedManager !== 'all' && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  Manager: {selectedManager}
                  <button
                    onClick={() => setSelectedManager('all')}
                    className="ml-1 hover:text-green-900"
                  >
                    ×
                  </button>
                </span>
              )}
              {selectedAssetType !== 'all' && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                  Asset: {selectedAssetType}
                  <button
                    onClick={() => setSelectedAssetType('all')}
                    className="ml-1 hover:text-purple-900"
                  >
                    ×
                  </button>
                </span>
              )}
              {(sortField !== 'current_market_value' || sortDirection !== 'desc') && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">
                  Sort: {sortField === 'current_market_value' ? 'Value' : 
                        sortField === 'pl_percentage' ? 'P&L %' : 
                        sortField === 'asset_name' ? 'Name' : sortField} 
                  ({sortDirection === 'desc' ? 'High→Low' : 'Low→High'})
                </span>
              )}
            </div>
          )}

          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <span>Showing {filteredHoldings.length} of {holdings.length} holdings</span>
            {filteredHoldings.length !== holdings.length && (
              <button
                onClick={() => {
                  setSearchTerm('')
                  setSelectedManager('all')
                  setSelectedAssetType('all')
                }}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Clear filters
              </button>
            )}
          </div>
        </div>

        {/* Holdings Table */}
        <HoldingsTable holdings={filteredHoldings} />
      </div>
    </div>
  )
}