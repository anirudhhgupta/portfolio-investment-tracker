# Portfolio Investment Tracker

A comprehensive portfolio management system that extracts, consolidates, and analyzes investment data from multiple wealth managers' PDF reports.

## 🏗️ Project Structure

```
portfolio-tracker/
├── src/                     # Source code
│   ├── extractors/         # PDF extraction logic
│   ├── utils/              # Utilities (dashboard, currency)
│   └── web/                # Next.js application
├── scripts/                # Execution scripts
├── data/                   # Data directory
│   ├── input/             # PDF files by month
│   └── output/            # Generated files
├── config/                # Configuration files
└── docs/                  # Documentation
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies  
cd src/web && npm install
```

### 2. Add Portfolio Data
```bash
# Place PDF files in monthly folders
data/input/[Month YYYY]/your-portfolio-files.pdf
```

### 3. Run Portfolio Analysis
```bash
# Extract data from PDFs
python3 scripts/extract_portfolio.py

# Generate local HTML dashboard  
python3 scripts/generate_dashboard.py

# Start web application
python3 scripts/run_web_app.sh
```

## 📊 Features

### 📈 **Multi-Manager Support**
- **Client Associates**: AIF, PMS, Mutual Funds
- **IIFL 360 One**: Premium investment products  
- **Kotak Securities**: Equity and debt holdings
- **Motilal Oswal**: Investment advisory portfolios
- **INDmoney**: Consolidated investment tracking
- **Yes Securities**: Trading and investment accounts

### 💰 **Advanced Analytics**
- **P&L Analysis**: Absolute and percentage returns
- **XIRR Calculations**: Time-weighted returns 
- **Currency Conversion**: USD to INR with live rates
- **Asset Allocation**: Visual breakdown by type and manager
- **Performance Metrics**: Comprehensive portfolio insights

### 🖥️ **Dual Interface**
- **Local Dashboard**: Static HTML with full functionality
- **Web Application**: Next.js with modern React components
- **Responsive Design**: Mobile and desktop optimized
- **Real-time Filtering**: Search, sort, and filter holdings

### 🔧 **Technical Stack**
- **Backend**: Python 3.8+ with pdfplumber for extraction
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Data Processing**: Pandas, NumPy for calculations  
- **Deployment**: Vercel-ready with static generation
- **Security**: Local processing, no sensitive data transmission

## 📁 Data Structure

### Input Structure
```
data/input/
└── August 2025/                    # Monthly folders
    ├── Client Associates - Portfolio Aug'25.pdf
    ├── IIFL 360 One - Report.pdf
    ├── Kotak - Holdings.pdf  
    ├── Motilal Oswal - Portfolio.pdf
    ├── IND Money - Holdings.xls
    └── Yes Bank - Monthly.pdf
```

### Output Structure  
```
data/output/
├── extracted_portfolio_data.json    # Consolidated data
├── dashboard.html                   # Local HTML dashboard
└── exchange_rates_cache.json       # Currency cache
```

## 🔍 Supported File Formats

| Manager | Format | Key Data Extracted |
|---------|--------|-------------------|
| Client Associates | PDF | Holdings, P&L, XIRR, Investment dates |
| IIFL 360 One | PDF | Market values, P&L, Asset allocation |  
| Kotak Securities | PDF | Current values, P&L percentages |
| Motilal Oswal | PDF | Portfolio holdings, Performance metrics |
| INDmoney | XLS | Consolidated holdings, Returns |
| Yes Securities | PDF | Trading accounts, Investment summary |

## 🎯 Key Metrics Tracked

- **Current Investment Value**: Total deployed capital
- **Current Market Value**: Present portfolio worth
- **P&L Amount**: Absolute gains/losses  
- **P&L Percentage**: Return percentages
- **XIRR**: Annualized internal rate of return
- **Asset Allocation**: Breakdown by equity/debt/alternatives
- **Manager Performance**: Comparative analysis

## 🛠️ Configuration

### Environment Variables
```bash
# Currency conversion API (optional)
EXCHANGE_RATE_API_KEY=your-api-key

# Deployment settings
VERCEL_PROJECT_ID=your-project-id  
```

### Customization
- **Data Extraction**: Modify `src/extractors/portfolio_extractor.py`
- **UI Components**: Edit React components in `src/web/app/components/`
- **Styling**: Update Tailwind classes and `globals.css`
- **Analytics**: Enhance calculations in utility functions

## 📊 Usage Examples

### Extract Latest Portfolio Data
```bash
python3 scripts/extract_portfolio.py
# Output: 45 holdings extracted, ₹31.98Cr → ₹45.72Cr (+42.97%)
```

### Generate Dashboard  
```bash
python3 scripts/generate_dashboard.py
# Output: dashboard.html with interactive charts
```

### Start Web Application
```bash
cd src/web && npm run dev
# Available at: http://localhost:3000
```

### Deploy to Vercel
```bash
vercel --prod
# Deployed URL: https://your-portfolio.vercel.app
```

## 🔐 Security Features

- ✅ **Local Processing**: All extraction happens locally
- ✅ **No Cloud Storage**: Sensitive data never leaves your machine  
- ✅ **PDF files excluded from git (`.gitignore`)**
- ✅ **No sensitive data in repository**
- ✅ **Local-first data processing**
- ✅ **HTTPS deployment on Vercel**

---

**Built with ❤️ for personal portfolio management**  
**Technology**: Python + Next.js + TypeScript + Tailwind CSS