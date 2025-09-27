import { NextResponse } from 'next/server'
import path from 'path'
import fs from 'fs'

export async function GET() {
  try {
    // Read the extracted portfolio data
    const dataPath = path.join(process.cwd(), '..', '..', 'data', 'output', 'extracted_portfolio_data.json')
    
    if (!fs.existsSync(dataPath)) {
      return NextResponse.json(
        { error: 'Portfolio data not found. Please run the extraction script first.' },
        { status: 404 }
      )
    }

    const rawData = JSON.parse(fs.readFileSync(dataPath, 'utf8'))
    
    // Apply the same filtering logic as dashboard.py
    // Filter out invalid entries (like disclaimers)
    const data = rawData.filter((item: any) => {
      // Skip entries with zero market value or obvious disclaimer text
      return (item.current_market_value > 0 && 
              !item.asset_name.startsWith('*') &&
              !item.asset_name.startsWith('Disclaimer'))
    })
    
    // Calculate summary statistics
    const totalInvestment = data.reduce((sum: number, holding: any) => sum + holding.current_investment_value, 0)
    const totalMarketValue = data.reduce((sum: number, holding: any) => sum + holding.current_market_value, 0)
    const totalPL = totalMarketValue - totalInvestment
    const totalPLPercentage = totalInvestment > 0 ? (totalPL / totalInvestment) * 100 : 0

    // Group by manager (using exact same logic as dashboard.py)
    const managerBreakdown = data.reduce((acc: any, holding: any) => {
      const manager = holding.manager_name
      if (!acc[manager]) {
        acc[manager] = {
          count: 0,
          investment: 0,
          market_value: 0,
          asset_types: new Set()
        }
      }
      acc[manager].count += 1
      acc[manager].investment += holding.current_investment_value
      acc[manager].market_value += holding.current_market_value
      acc[manager].asset_types.add(holding.asset_type)
      return acc
    }, {})

    // Group by asset type (using exact same logic as dashboard.py)
    const assetBreakdown = data.reduce((acc: any, holding: any) => {
      const assetType = holding.asset_type
      if (!acc[assetType]) {
        acc[assetType] = {
          count: 0,
          investment: 0,
          market_value: 0
        }
      }
      acc[assetType].count += 1
      acc[assetType].investment += holding.current_investment_value
      acc[assetType].market_value += holding.current_market_value
      return acc
    }, {})

    // Convert Sets to arrays for JSON serialization (same as dashboard.py)
    const managerBreakdownFormatted = Object.fromEntries(
      Object.entries(managerBreakdown).map(([key, value]: [string, any]) => [
        key, 
        { ...value, asset_types: Array.from(value.asset_types) }
      ])
    )

    return NextResponse.json({
      holdings: data,
      summary: {
        totalHoldings: data.length,
        totalInvestment,
        totalMarketValue,
        totalPL,
        totalPLPercentage,
        lastUpdated: new Date().toISOString()
      },
      managerBreakdown: managerBreakdownFormatted,
      assetBreakdown
    })
  } catch (error) {
    console.error('Error reading portfolio data:', error)
    return NextResponse.json(
      { error: 'Failed to load portfolio data' },
      { status: 500 }
    )
  }
}

export async function POST() {
  return NextResponse.json(
    { error: 'Portfolio extraction via API not yet implemented. Please run the Python script locally.' },
    { status: 501 }
  )
}