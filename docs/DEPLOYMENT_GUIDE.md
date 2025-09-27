# Portfolio Tracker - Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

### Step 1: Initialize Git Repository
```bash
cd /Users/anirudhgupta/Code/inv-tracker
git init
git add .
git commit -m "Initial commit: Portfolio Investment Tracker

✅ Next.js 14 web application with TypeScript
✅ Interactive dashboard with charts and filtering
✅ Automatic latest month data detection
✅ Responsive design for all devices
✅ API endpoints for portfolio data
✅ Complete Python extraction pipeline
✅ Vercel deployment configuration

🚀 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 2: Create GitHub Repository
```bash
# Create a new repository on GitHub: portfolio-investment-tracker
# Then connect your local repo:

git remote add origin https://github.com/YOUR_USERNAME/portfolio-investment-tracker.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Vercel
1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub
2. **Click "New Project"**
3. **Import your GitHub repository:** `portfolio-investment-tracker`
4. **Configure project:**
   - Framework Preset: **Next.js**
   - Root Directory: `./` (default)
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
5. **Click "Deploy"**

### Step 4: Your Live URL
After deployment, you'll get a URL like:
```
https://portfolio-investment-tracker.vercel.app
```

## 📋 Monthly Update Workflow

### 1. Add New Month Data
```bash
# Create new month folder
mkdir "Data/September 2025"

# Upload your PDF reports to the new folder
# - INDMoney PDF
# - Kotak PDF  
# - Yes Bank PDF
# - Client Associates PDF
# - IIFL 360 One PDF
# - Motilal Oswal PDF
```

### 2. Extract Data
```bash
# Run extraction script (automatically uses latest month)
python3 portfolio_extractor.py
```

### 3. Deploy Updates
```bash
# Commit and push changes
git add .
git commit -m "📊 Portfolio update: September 2025

- Added new portfolio reports
- Total value: ₹XX.XX Crores
- Return: +XX.XX%
- Holdings: XX assets across 6 managers

🚀 Generated with Claude Code"

git push origin main
```

Vercel will automatically deploy your updates in ~2 minutes!

## 🔧 Environment Setup

### Local Development
```bash
# Install dependencies
npm install

# Extract portfolio data
python3 portfolio_extractor.py

# Start development server
npm run dev

# Open browser
open http://localhost:3000
```

### Production Environment Variables (Vercel)
No environment variables needed for basic deployment. The app reads from `extracted_portfolio_data.json`.

## 📊 Features Overview

### 🌐 **Web Dashboard**
- **Real-time Portfolio Stats** - Investment, current value, P&L, returns
- **Interactive Charts** - Asset allocation & manager performance
- **Advanced Filtering** - Search, filter by manager/asset type, sort options
- **Responsive Design** - Works on desktop, tablet, mobile
- **Modern UI** - Clean interface with Tailwind CSS

### 🤖 **Automatic Data Processing**
- **Latest Month Detection** - Automatically uses newest data folder
- **Smart File Matching** - Handles different PDF naming patterns
- **Deduplication** - Removes duplicate holdings across managers
- **Investment Date Extraction** - Parses dates from complex PDF structures

### 📈 **Analytics**
- **Manager Performance** - Compare returns across wealth managers
- **Asset Allocation** - Visual breakdown by investment types
- **P&L Tracking** - Profit/loss with percentage returns
- **Investment Timeline** - Track when each position was opened

## 🛡️ Security & Privacy

### Data Protection
- ✅ **No PDF files in Git** - Sensitive documents excluded via .gitignore
- ✅ **No personal data in repository** - Only aggregated portfolio stats
- ✅ **HTTPS by default** - Vercel provides SSL certificates
- ✅ **No external API calls** - Data stays within your deployment

### Access Control
- **Public dashboard** - Anyone with URL can view (customize as needed)
- **No authentication** - Add auth if you need private access
- **Vercel security** - Built-in DDoS protection and security headers

## 🔄 CI/CD Pipeline

### Automatic Deployments
```
Local Changes → Git Push → GitHub → Vercel → Live Site
```

### Build Process
1. **Install dependencies** (`npm install`)
2. **Build Next.js app** (`npm run build`)
3. **Deploy to Vercel Edge Network**
4. **Live in ~2 minutes**

### Preview Deployments
- **Pull Requests** automatically get preview URLs
- **Branch deployments** for testing new features
- **Production deploys** only from main branch

## 📱 Mobile Experience

### Responsive Design
- **Mobile-first approach** - Optimized for phones and tablets
- **Touch-friendly interface** - Easy navigation on mobile devices
- **Adaptive charts** - Charts scale beautifully on small screens
- **Fast loading** - Optimized for mobile networks

## 🚨 Troubleshooting

### Common Issues

**1. Build Failed**
```bash
# Check for TypeScript errors
npm run build

# Fix any compilation errors
# Then commit and push again
```

**2. No Data Showing**
```bash
# Ensure extracted_portfolio_data.json exists
ls -la extracted_portfolio_data.json

# Re-run extraction if missing
python3 portfolio_extractor.py
```

**3. Old Data Showing**
```bash
# Verify you're using the latest month folder
ls -la "Data/"

# Check the extraction script output
python3 portfolio_extractor.py
```

**4. Vercel Deployment Issues**
- Check **Vercel dashboard** for build logs
- Ensure **package.json** has all dependencies
- Verify **vercel.json** configuration

### Debug Mode
```bash
# Enable verbose logging in browser console
# Check Network tab for API calls
# Verify data is loading from /api/portfolio
```

## 📊 Performance Monitoring

### Vercel Analytics
- **Page views** and **user engagement**
- **Core Web Vitals** performance metrics
- **Geographic distribution** of users
- **Device and browser** analytics

### Performance Optimizations
- ✅ **Static generation** for fast loading
- ✅ **Code splitting** for efficient bundles
- ✅ **Image optimization** automatic by Vercel
- ✅ **CDN distribution** via Vercel Edge Network

## 🔮 Future Enhancements

### Phase 2 Features
- [ ] **File Upload Interface** - Upload PDFs directly via web
- [ ] **Historical Tracking** - Track portfolio changes over time
- [ ] **Email Alerts** - Get notified of significant changes
- [ ] **Advanced Analytics** - Benchmarking and performance metrics
- [ ] **User Authentication** - Private portfolio access

### Technical Roadmap
- [ ] **Database Integration** - PostgreSQL for historical data
- [ ] **Background Jobs** - Automated data processing
- [ ] **API Enhancements** - RESTful API for external access
- [ ] **Mobile App** - React Native companion app

---

## 🎯 Success Metrics

After deployment, your portfolio tracker will provide:

- **📊 Real-time Portfolio Insights** - Always up-to-date investment data
- **🚀 Fast Performance** - Sub-second load times globally
- **📱 Mobile Access** - Check portfolio anywhere, anytime
- **🔄 Easy Updates** - Monthly updates in just 3 commands
- **💰 Cost Effective** - Free hosting on Vercel for personal use
- **🔒 Secure & Private** - Your data stays protected

**Live URL:** `https://your-portfolio-tracker.vercel.app`

---

**Deployed with ❤️ on Vercel**  
**Created with Claude Code**  
**Technology:** Next.js + TypeScript + Tailwind CSS