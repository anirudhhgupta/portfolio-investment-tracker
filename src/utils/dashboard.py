#!/usr/bin/env python3
"""
Portfolio Dashboard
Creates a simple HTML dashboard from extracted portfolio data
"""

import json
import pandas as pd
from datetime import datetime
import os

def load_portfolio_data(json_file):
    """Load extracted portfolio data from JSON file"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Filter out invalid entries (like disclaimers)
    valid_data = []
    for item in data:
        # Skip entries with zero market value or obvious disclaimer text
        if (item['current_market_value'] > 0 and 
            not item['asset_name'].startswith('*') and
            not item['asset_name'].startswith('Disclaimer')):
            valid_data.append(item)
    
    return valid_data

def create_dashboard_html(portfolio_data):
    """Create modern interactive HTML dashboard"""
    
    # Calculate totals
    total_investment = sum(item['current_investment_value'] for item in portfolio_data)
    total_market_value = sum(item['current_market_value'] for item in portfolio_data)
    total_pl = total_market_value - total_investment
    total_pl_pct = (total_pl / total_investment * 100) if total_investment > 0 else 0
    
    # Group by manager
    managers_summary = {}
    for item in portfolio_data:
        manager = item['manager_name']
        if manager not in managers_summary:
            managers_summary[manager] = {
                'investment': 0,
                'market_value': 0,
                'count': 0,
                'asset_types': set()
            }
        managers_summary[manager]['investment'] += item['current_investment_value']
        managers_summary[manager]['market_value'] += item['current_market_value']
        managers_summary[manager]['count'] += 1
        managers_summary[manager]['asset_types'].add(item['asset_type'])
    
    # Group by asset type
    asset_summary = {}
    for item in portfolio_data:
        asset_type = item['asset_type']
        if asset_type not in asset_summary:
            asset_summary[asset_type] = {
                'investment': 0,
                'market_value': 0,
                'count': 0
            }
        asset_summary[asset_type]['investment'] += item['current_investment_value']
        asset_summary[asset_type]['market_value'] += item['current_market_value']
        asset_summary[asset_type]['count'] += 1
    
    # Convert portfolio data to JSON for JavaScript
    import json
    portfolio_json = json.dumps(portfolio_data, default=str)
    managers_json = json.dumps({k: {**v, 'asset_types': list(v['asset_types'])} for k, v in managers_summary.items()})
    assets_json = json.dumps(asset_summary)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portfolio Dashboard</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            :root {{
                --primary-color: #1e3a8a;
                --secondary-color: #3b82f6;
                --success-color: #10b981;
                --danger-color: #ef4444;
                --warning-color: #f59e0b;
                --info-color: #06b6d4;
                --dark-color: #1f2937;
                --light-color: #f8fafc;
                --border-color: #e2e8f0;
                --text-primary: #1e293b;
                --text-secondary: #64748b;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--light-color);
                color: var(--text-primary);
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 30px 0;
                margin-bottom: 30px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .header p {{
                font-size: 1.1rem;
                opacity: 0.9;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid var(--secondary-color);
                transition: transform 0.2s ease;
            }}
            
            .stat-card:hover {{
                transform: translateY(-2px);
            }}
            
            .stat-value {{
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 5px;
            }}
            
            .stat-label {{
                color: var(--text-secondary);
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .positive {{ color: var(--success-color); }}
            .negative {{ color: var(--danger-color); }}
            
            .charts-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 30px;
                margin-bottom: 30px;
            }}
            
            .chart-container {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .chart-title {{
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 20px;
                color: var(--text-primary);
            }}
            
            .table-container {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .table-header {{
                background: var(--primary-color);
                color: white;
                padding: 20px;
            }}
            
            .table-header h2 {{
                font-size: 1.5rem;
                font-weight: 600;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid var(--border-color);
            }}
            
            th {{
                background-color: #f8fafc;
                font-weight: 600;
                color: var(--text-primary);
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            tr:hover {{
                background-color: #f8fafc;
            }}
            
            .amount {{
                font-weight: 600;
            }}
            
            .manager-tag {{
                background: var(--secondary-color);
                color: white;
                padding: 4px 8px;
                border-radius: 6px;
                font-size: 0.8rem;
                font-weight: 500;
            }}
            
            .asset-type {{
                background: var(--info-color);
                color: white;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 0.75rem;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                
                .header h1 {{
                    font-size: 2rem;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .charts-grid {{
                    grid-template-columns: 1fr;
                }}
                
                table {{
                    font-size: 0.8rem;
                }}
                
                th, td {{
                    padding: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-chart-line"></i> Portfolio Dashboard</h1>
                <p>Investment Portfolio Analysis - {datetime.now().strftime('%B %Y')}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">₹{total_investment/10000000:.2f}Cr</div>
                    <div class="stat-label"><i class="fas fa-wallet"></i> Total Investment</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">₹{total_market_value/10000000:.2f}Cr</div>
                    <div class="stat-label"><i class="fas fa-chart-area"></i> Current Value</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {'positive' if total_pl >= 0 else 'negative'}">₹{abs(total_pl)/10000000:.2f}Cr</div>
                    <div class="stat-label"><i class="fas fa-{'arrow-up' if total_pl >= 0 else 'arrow-down'}"></i> P&L Amount</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {'positive' if total_pl_pct >= 0 else 'negative'}">{total_pl_pct:+.2f}%</div>
                    <div class="stat-label"><i class="fas fa-percentage"></i> Overall Return</div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <h3 class="chart-title"><i class="fas fa-pie-chart"></i> Asset Allocation</h3>
                    <canvas id="assetChart" width="400" height="300"></canvas>
                </div>
                <div class="chart-container">
                    <h3 class="chart-title"><i class="fas fa-users"></i> Manager Performance</h3>
                    <canvas id="managerChart" width="400" height="300"></canvas>
                </div>
            </div>
            
            <div class="table-container">
                <div class="table-header">
                    <h2><i class="fas fa-table"></i> Portfolio Holdings ({len(portfolio_data)} Assets)</h2>
                </div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Asset Name</th>
                                <th>Manager</th>
                                <th>Type</th>
                                <th>Investment</th>
                                <th>Current Value</th>
                                <th>P&L</th>
                                <th>Return %</th>
                                <th>IRR %</th>
                                <th>Inv. Date</th>
                            </tr>
                        </thead>
                        <tbody id="holdingsTable">
                            <!-- Table rows will be populated by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // Portfolio data
            const portfolioData = {portfolio_json};
            const managersData = {managers_json};
            const assetsData = {assets_json};
            
            // Helper functions
            function formatCurrency(amount) {{
                if (amount >= 10000000) {{
                    return `₹${{(amount/10000000).toFixed(2)}}Cr`;
                }} else if (amount >= 100000) {{
                    return `₹${{(amount/100000).toFixed(2)}}L`;
                }}
                return `₹${{amount.toLocaleString('en-IN')}}`;
            }}
            
            function formatPercentage(pct) {{
                return `${{pct >= 0 ? '+' : ''}}${{pct.toFixed(2)}}%`;
            }}
            
            // Asset Allocation Chart
            const assetCtx = document.getElementById('assetChart').getContext('2d');
            const assetLabels = Object.keys(assetsData);
            const assetValues = Object.values(assetsData).map(item => item.market_value);
            
            new Chart(assetCtx, {{
                type: 'doughnut',
                data: {{
                    labels: assetLabels,
                    datasets: [{{
                        data: assetValues,
                        backgroundColor: [
                            '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
                            '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${{context.label}}: ${{formatCurrency(value)}} (${{percentage}}%)`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Manager Performance Chart
            const managerCtx = document.getElementById('managerChart').getContext('2d');
            const managerLabels = Object.keys(managersData);
            const managerInvestments = Object.values(managersData).map(item => item.investment);
            const managerValues = Object.values(managersData).map(item => item.market_value);
            
            new Chart(managerCtx, {{
                type: 'bar',
                data: {{
                    labels: managerLabels,
                    datasets: [{{
                        label: 'Investment',
                        data: managerInvestments,
                        backgroundColor: '#94a3b8'
                    }}, {{
                        label: 'Current Value',
                        data: managerValues,
                        backgroundColor: '#3b82f6'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return `${{context.dataset.label}}: ${{formatCurrency(context.parsed.y)}}`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return formatCurrency(value);
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            // Populate Holdings Table
            const tableBody = document.getElementById('holdingsTable');
            portfolioData.forEach(holding => {{
                const row = document.createElement('tr');
                const pl = holding.current_market_value - holding.current_investment_value;
                const plPct = holding.current_investment_value > 0 ? (pl / holding.current_investment_value * 100) : 0;
                
                row.innerHTML = `
                    <td style="max-width: 300px; word-wrap: break-word;">${{holding.asset_name}}</td>
                    <td><span class="manager-tag">${{holding.manager_name}}</span></td>
                    <td><span class="asset-type">${{holding.asset_type}}</span></td>
                    <td class="amount">${{formatCurrency(holding.current_investment_value)}}</td>
                    <td class="amount">${{formatCurrency(holding.current_market_value)}}</td>
                    <td class="amount ${{pl >= 0 ? 'positive' : 'negative'}}">${{formatCurrency(Math.abs(pl))}}</td>
                    <td class="${{plPct >= 0 ? 'positive' : 'negative'}}">${{formatPercentage(plPct)}}</td>
                    <td class="positive">${{holding.irr_percentage ? holding.irr_percentage.toFixed(2) + '%' : 'N/A'}}</td>
                    <td>${{holding.investment_date || 'N/A'}}</td>
                `;
                tableBody.appendChild(row);
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

def main():
    """Main function to generate portfolio dashboard"""
    try:
        # Load portfolio data
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        json_file = os.path.join(project_root, "data", "output", "extracted_portfolio_data.json")
        
        if not os.path.exists(json_file):
            print(f"❌ Portfolio data file not found: {json_file}")
            print("Please run portfolio_extractor.py first to generate the data.")
            return
        
        print("📊 Loading portfolio data...")
        portfolio_data = load_portfolio_data(json_file)
        
        if not portfolio_data:
            print("❌ No valid portfolio data found.")
            return
        
        print(f"✅ Loaded {len(portfolio_data)} holdings")
        
        # Generate HTML dashboard
        print("🎨 Generating HTML dashboard...")
        html_content = create_dashboard_html(portfolio_data)
        
        # Save dashboard
        output_file = os.path.join(project_root, "data", "output", "dashboard.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard saved to: {output_file}")
        
        # Print summary
        total_investment = sum(item['current_investment_value'] for item in portfolio_data)
        total_market_value = sum(item['current_market_value'] for item in portfolio_data)
        total_pl = total_market_value - total_investment
        
        print(f"\\n📈 PORTFOLIO SUMMARY:")
        print(f"Total Investment: ₹{total_investment:,.2f}")
        print(f"Total Market Value: ₹{total_market_value:,.2f}")
        print(f"Total P&L: ₹{total_pl:,.2f}")
        print(f"Overall Return: {(total_pl/total_investment*100):+.2f}%")
        print(f"Number of Holdings: {len(portfolio_data)}")
        
        # Group by manager summary
        managers = {}
        for item in portfolio_data:
            manager = item['manager_name']
            if manager not in managers:
                managers[manager] = {'count': 0, 'value': 0}
            managers[manager]['count'] += 1
            managers[manager]['value'] += item['current_market_value']
        
        print(f"\\n👥 MANAGERS:")
        for manager, data in sorted(managers.items(), key=lambda x: x[1]['value'], reverse=True):
            print(f"  {manager}: {data['count']} holdings, ₹{data['value']/10000000:.2f}Cr")
        
        print(f"\\n🌐 Open dashboard: file://{output_file}")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()