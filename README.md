# Portfolio Investment Tracker

A comprehensive portfolio management system that extracts, consolidates, and analyzes investment data from multiple wealth managers' PDF reports.

## 🏗️ Project Structure

```
portfolio-tracker/
├── 📂 src/                          # Source Code
│   ├── extractors/                  # PDF Data Extraction
│   │   └── portfolio_extractor.py   # Main extraction logic
│   ├── utils/                       # Utilities & Helpers
│   │   ├── dashboard.py             # Local HTML dashboard generator
│   │   └── currency_converter.py    # Currency conversion utilities
│   └── web/                         # Next.js Web Application
│       ├── app/                     # Next.js App Router
│       │   ├── components/          # React components
│       │   ├── api/                 # API endpoints
│       │   └── page.tsx             # Main dashboard page
│       ├── package.json             # Web app dependencies
│       └── [config files]           # Next.js configuration
├── 📂 data/                         # Data Files
│   ├── input/                       # Input PDF Reports (by month)
│   │   ├── August 2025/             # Latest month folder
│   │   └── April 2025/              # Previous months
│   └── output/                      # Generated Data Files
│       ├── extracted_portfolio_data.json
│       ├── dashboard.html           # Local HTML dashboard
│       └── exchange_rates_cache.json
├── 📂 scripts/                      # Automation Scripts
│   ├── extract_portfolio.py        # Run portfolio extraction
│   ├── generate_dashboard.py       # Generate local dashboard
│   └── run_web_app.sh              # Start web application
├── 📂 docs/                         # Documentation
│   ├── DEPLOYMENT_GUIDE.md         # Vercel deployment guide
│   └── EXECUTION_GUIDE.md          # Usage instructions
├── 📂 config/                       # Configuration Files
│   └── vercel.json                 # Vercel deployment config
└── current-assets.txt              # Working notes
```

## 🚀 Quick Start

### 1. Extract Portfolio Data
```bash
# From project root
python3 scripts/extract_portfolio.py
```

### 2. Generate Local HTML Dashboard
```bash
python3 scripts/generate_dashboard.py
# Opens: data/output/dashboard.html
```

### 3. Start Web Application
```bash
# Method 1: Using script
./scripts/run_web_app.sh

# Method 2: Direct command
cd src/web && npm run dev
# Opens: http://localhost:3000
```

## 📊 Features

### 🔍 **Data Extraction**
- **Automatic PDF Processing**: Extracts from 6 wealth managers
- **Smart Deduplication**: Removes duplicate holdings across managers
- **Investment Date Detection**: Parses complex date formats
- **Currency Conversion**: USD to INR for US stocks
- **Latest Month Auto-Detection**: Automatically uses newest data folder

### 🌐 **Web Dashboard** 
- **Interactive React Interface**: Modern, responsive design
- **Real-time Filtering**: Search, filter by manager/asset type
- **Advanced Sorting**: Multiple sort options
- **Visual Analytics**: Charts for asset allocation & manager performance
- **Complete Data View**: IRR, USD values, full asset names

### 🖥️ **Local Tools**
- **HTML Dashboard**: Static dashboard with Chart.js visualizations
- **Currency Utilities**: Exchange rate caching and conversion
- **Command Line Interface**: Easy-to-use scripts

## 📈 Portfolio Summary

- **Total Value**: ₹45.87+ Crores
- **Holdings**: 50+ assets across 6 managers
- **Return**: +43% overall performance
- **Managers**: IND Money, Client Associates, Kotak, Motilal Oswal, Yes Bank, IIFL 360 One

## 🔧 Technical Stack

- **Backend**: Python 3.9+ (pandas, pdfplumber, requests)
- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts (web), Chart.js (local)
- **Deployment**: Vercel (web), Local HTML (desktop)

## 📋 Monthly Workflow

1. **Add New Data**: Place PDF reports in `data/input/[Month Year]/`
2. **Extract Data**: Run `python3 scripts/extract_portfolio.py`
3. **View Locally**: Run `python3 scripts/generate_dashboard.py`
4. **Update Web**: The web app automatically uses the latest data
5. **Deploy**: Commit changes to auto-deploy to Vercel

## 🛠️ Development

### Local Development
```bash
# Install web dependencies
cd src/web && npm install

# Start development server
npm run dev
```

### Adding New Extractors
1. Add extraction logic to `src/extractors/portfolio_extractor.py`
2. Update the main extraction function
3. Test with sample PDFs

### Customizing the Dashboard
- **Web UI**: Edit components in `src/web/app/components/`
- **Local HTML**: Modify `src/utils/dashboard.py`
- **Styling**: Update Tailwind classes or CSS

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Complete Vercel deployment instructions
- **[Execution Guide](docs/EXECUTION_GUIDE.md)**: Detailed usage and troubleshooting

## 🔒 Security

- ✅ PDF files excluded from git (`.gitignore`)
- ✅ No sensitive data in repository
- ✅ Local-first data processing
- ✅ HTTPS deployment on Vercel

---

**Built with ❤️ for personal portfolio management**  
**Technology**: Python + Next.js + TypeScript + Tailwind CSS