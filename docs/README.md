# Portfolio Investment Tracker - Web Version

A modern Next.js web application for portfolio management that extracts, consolidates, and analyzes investment data from multiple wealth managers' PDF reports.

## 🌐 Live Demo

**Deployed on Vercel:** [Your Portfolio Tracker](https://portfolio-tracker-yourapp.vercel.app)

## 📊 Overview

This web application automatically processes PDF portfolio statements from various wealth managers, extracts holding details with investment dates, and generates an interactive dashboard for portfolio analysis.

**Portfolio Value:** ₹40.17+ Crores across **6 Wealth Managers**
- **IND Money** (US Stocks) - ₹14.4L
- **Client Associates** (AIF) - ₹10.6Cr  
- **Yes Bank** (Mutual Funds) - ₹16.4L
- **Kotak** (Mutual Funds, Direct Equity, Bonds, AIF) - ₹20.8Cr
- **Motilal Oswal** (Direct Equity + AIF) - ₹3.2Cr
- **IIFL 360 One** (AIF + Unlisted Equity) - ₹8.5Cr

## 🚀 Features

### 📱 **Interactive Web Dashboard**
- **Real-time Portfolio Stats** - Total investment, current value, P&L with visual indicators
- **Advanced Filtering** - Search by asset name, filter by manager, asset type, sort by various metrics
- **Interactive Charts** - Asset allocation pie chart and manager performance bar chart
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices
- **Modern UI** - Clean, professional interface with Tailwind CSS

### 📈 **Data Visualization**
- **Asset Allocation Chart** - Visual breakdown by asset types (Mutual Funds, AIF, Direct Equity, etc.)
- **Manager Performance Chart** - Comparative analysis of returns by wealth manager
- **Holdings Table** - Detailed view with investment dates, P&L, and return percentages
- **Summary Cards** - Key metrics with trend indicators

### 🔧 **Backend Integration**
- **Automatic Latest Month Detection** - Dynamically selects the most recent data folder
- **RESTful API** - Clean API endpoints for portfolio data
- **Smart File Matching** - Pattern-based file detection for different months
- **Data Validation** - Error handling and data consistency checks

## 🏗️ Architecture

### Web Application Stack
```
portfolio-tracker/
├── app/                          # Next.js 14 App Router
│   ├── api/portfolio/           # API endpoints
│   ├── components/              # React components
│   ├── globals.css              # Global styles
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Main dashboard
├── Data/                        # Portfolio data by month
│   ├── August 2025/            # Latest month folder
│   └── April 2025/             # Previous month folder
├── portfolio_extractor.py      # Python extraction script
├── dashboard.py                # Legacy dashboard generator
└── package.json                # Dependencies and scripts
```

### Technology Stack
- **Frontend:** Next.js 14, React 18, TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **Icons:** Lucide React
- **Deployment:** Vercel
- **Analytics:** Vercel Analytics

## 📋 Quick Start

### Development Setup

1. **Clone Repository:**
```bash
git clone <your-repo-url>
cd portfolio-tracker
```

2. **Install Dependencies:**
```bash
npm install
```

3. **Extract Portfolio Data:**
```bash
# Run Python extraction script first
python3 portfolio_extractor.py
```

4. **Start Development Server:**
```bash
npm run dev
```

5. **Open Browser:**
```bash
open http://localhost:3000
```

### Production Deployment (Vercel)

1. **Connect to Vercel:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

2. **Automatic Deployments:**
- Push to main branch triggers automatic deployment
- Pull requests create preview deployments
- Vercel handles build optimization and CDN

## 🔄 Data Flow

### 1. **Data Extraction (Local)**
```bash
python3 portfolio_extractor.py
```
- Scans `Data/` directory for latest month folder
- Extracts data from all PDF files using pattern matching
- Generates `extracted_portfolio_data.json`

### 2. **Web Application (Vercel)**
- API endpoint reads JSON data
- React components render interactive dashboard
- Real-time filtering and sorting
- Responsive charts and tables

### 3. **Monthly Updates**
1. Create new folder: `Data/September 2025/`
2. Upload new PDF reports
3. Run extraction script: `python3 portfolio_extractor.py`
4. Commit and push to trigger deployment

## 📊 API Endpoints

### `GET /api/portfolio`
Returns complete portfolio data with summary statistics.

**Response:**
```json
{
  "holdings": [...],
  "summary": {
    "totalHoldings": 47,
    "totalInvestment": 270729009.37,
    "totalMarketValue": 401769655.28,
    "totalPL": 131040645.91,
    "totalPLPercentage": 48.40
  },
  "managerBreakdown": {...},
  "assetBreakdown": {...}
}
```

## 🎨 UI Components

### **PortfolioStats**
- Total investment, current value, P&L, return percentage
- Color-coded trend indicators
- Responsive card layout

### **HoldingsTable**
- Sortable table with all portfolio holdings
- Truncated asset names with hover tooltips
- P&L indicators with trend arrows
- Investment date tracking

### **AssetAllocation**
- Interactive pie chart with hover tooltips
- Legend with values and percentages
- Responsive design for all screen sizes

### **ManagerBreakdown**
- Bar chart comparing manager performance
- Investment vs current value comparison
- Summary table with return percentages

## 🔧 Configuration

### Environment Variables
```bash
# .env.local (for local development)
NODE_ENV=development
```

### Vercel Configuration
```json
{
  "buildCommand": "npm run build",
  "framework": "nextjs",
  "functions": {
    "app/api/portfolio/route.ts": {
      "maxDuration": 30
    }
  }
}
```

## 📱 Mobile Responsiveness

- **Responsive Grid Layout** - Adapts to screen sizes
- **Touch-Friendly Interface** - Optimized for mobile interaction
- **Collapsible Navigation** - Mobile-first design approach
- **Optimized Charts** - Charts scale appropriately on small screens

## 🚀 Performance Optimizations

- **Next.js 14 App Router** - Latest performance optimizations
- **Static Generation** - Fast page loads
- **Code Splitting** - Efficient bundle sizes
- **Vercel Edge Network** - Global CDN deployment
- **Optimized Images** - Automatic image optimization

## 🔒 Security

- **No Sensitive Data in Git** - PDF files and extracted data excluded
- **Environment Variables** - Secure configuration management
- **Client-Side Rendering** - No server-side sensitive data exposure
- **Vercel Security** - Built-in DDoS protection and SSL

## 📈 Current Status

**Live Portfolio:** ₹40.17+ Crores (+48.40% returns)
- **47 Holdings** across 6 managers
- **Latest Data:** August 2025
- **Auto-Update:** Monthly via script + git push

## 🔮 Future Enhancements

### Phase 2 Features
- [ ] **File Upload Interface** - Direct PDF upload via web UI
- [ ] **Real-time Updates** - Automatic data refresh
- [ ] **Performance Tracking** - Historical trend analysis
- [ ] **Mobile App** - React Native version
- [ ] **Email Integration** - Automated report fetching
- [ ] **User Authentication** - Multi-user support

### Technical Improvements
- [ ] **Python API Integration** - Server-side extraction
- [ ] **Database Storage** - PostgreSQL/MongoDB integration
- [ ] **Caching Layer** - Redis for performance
- [ ] **Background Jobs** - Automated processing
- [ ] **Advanced Analytics** - XIRR calculations, benchmarking

## 🤝 Contributing

### Development Workflow
1. Fork repository
2. Create feature branch
3. Make changes and test locally
4. Submit pull request
5. Vercel creates preview deployment
6. Review and merge

### Code Style
- **TypeScript** - Strict type checking
- **ESLint** - Code quality enforcement
- **Prettier** - Code formatting
- **Component-based** - Modular React architecture

---

**Deployed with ❤️ on Vercel**  
**Last Updated:** September 2025  
**Technology:** Next.js 14 + TypeScript + Tailwind CSS