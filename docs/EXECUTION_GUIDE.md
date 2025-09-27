# Portfolio Investment Tracker - Execution Guide

## Manual Command Execution Order

Follow these steps to run the portfolio tracker system manually:

### 1. Setup and Prerequisites

```bash
# Install required Python packages
pip install pandas pdfplumber xlrd requests
```

### 2. Data Extraction (Primary Command)

```bash
# Extract portfolio data from all PDF/Excel files
python3 portfolio_extractor.py
```

**What this does:**
- Reads all PDF and Excel files from `Portfolio Reports Samples/` directory
- Extracts holdings data from each wealth manager
- Consolidates data into standardized format
- Outputs `extracted_portfolio_data.json`

**Expected Output:**
```
Extracting data from IND Money...
Found 15 holdings in PDF
Cross-referencing with Excel for investment dates...
Extracting data from Motilal Oswal...
Found 3 Direct Equity holdings on page 3
Found 2 AIF holdings on page 6
Extracting data from Yes Bank...
Found 7 Mutual Fund holdings
Extracting data from Kotak...
Found 25 holdings across multiple asset types
All data extracted successfully!
```

### 3. Dashboard Generation (Secondary Command)

```bash
# Generate interactive HTML dashboard
python3 dashboard.py
```

**What this does:**
- Reads `extracted_portfolio_data.json`
- Generates interactive HTML dashboard
- Creates summary cards, charts, and filterable tables
- Outputs `dashboard.html`

**Expected Output:**
```
Generated dashboard with 45 total holdings
Total Portfolio Value: ₹40.17 Crores
Dashboard saved as: dashboard.html
```

### 4. View Results

```bash
# Open dashboard in default browser
open dashboard.html
```

## File Dependencies

### Required Input Files
```
Portfolio Reports Samples/
├── INDMoney - 2025-08 2.pdf
├── IND-HOLDINGS_REPORTXX29736710-2025-09-13-V04.xls
├── Motilal Oswal -Portfolio_Holding_Summary_Encrypted (1).pdf
├── Yes Bank - CS_00953_XXXXXXXX13_090925161545_YF_monthly.pdf
├── Kotak - EquityStatement-XXXXXXXX13-30-Sep-2025.pdf
└── Client Associates - Portfolio Aug'25.pdf
```

### Generated Output Files
```
├── extracted_portfolio_data.json    # Consolidated portfolio data
├── dashboard.html                   # Interactive dashboard
└── exchange_rates_cache.json       # Currency conversion cache
```

## Troubleshooting Commands

### Check PDF Files
```bash
# List all PDF files in the directory
ls -la "Portfolio Reports Samples/"*.pdf

# Check if PDFs are password protected
python3 -c "import pdfplumber; print(pdfplumber.open('Portfolio Reports Samples/Motilal Oswal -Portfolio_Holding_Summary_Encrypted (1).pdf', password='ADFPG0415P').pages)"
```

### Validate JSON Output
```bash
# Check if extraction was successful
python3 -c "import json; data=json.load(open('extracted_portfolio_data.json')); print(f'Total holdings: {len(data)}')"

# View portfolio summary
python3 -c "import json; data=json.load(open('extracted_portfolio_data.json')); total=sum(h['current_market_value'] for h in data); print(f'Total Value: ₹{total:,.0f}')"
```

### Debug Currency Conversion
```bash
# Check exchange rate cache
python3 -c "import json; rates=json.load(open('exchange_rates_cache.json')); print(rates)"

# Test currency converter
python3 -c "from currency_converter import CurrencyConverter; cc=CurrencyConverter(); print(f'Rate: {cc.get_usd_to_inr_rate(\"2025-08-31\")}')"
```

## Advanced Options

### Extract Single Manager
```python
# In portfolio_extractor.py, comment out other extractors
# Run only specific extractor for testing
python3 portfolio_extractor.py
```

### Force Exchange Rate Update
```bash
# Delete cache to fetch fresh rates
rm exchange_rates_cache.json
python3 portfolio_extractor.py
```

### Debug Mode
```bash
# Add debug prints to see detailed extraction
# Uncomment debug statements in portfolio_extractor.py
python3 portfolio_extractor.py
```

## Complete Workflow Example

```bash
# Full execution sequence
cd /Users/anirudhgupta/Code/inv-tracker

# Step 1: Extract data
python3 portfolio_extractor.py

# Step 2: Generate dashboard
python3 dashboard.py

# Step 3: Open results
open dashboard.html

# Step 4: Verify data (optional)
python3 -c "
import json
data = json.load(open('extracted_portfolio_data.json'))
print(f'Holdings: {len(data)}')
print(f'Managers: {len(set(h[\"manager_name\"] for h in data))}')
print(f'Total Value: ₹{sum(h[\"current_market_value\"] for h in data):,.0f}')
"
```

## Expected Execution Time

- **Data Extraction:** 30-60 seconds (depending on PDF complexity)
- **Dashboard Generation:** 5-10 seconds
- **Total Runtime:** ~1-2 minutes

## Common Error Solutions

### PDF Password Errors
```bash
# Check current-assets.txt for correct passwords
cat current-assets.txt
```

### Missing Dependencies
```bash
# Install all required packages
pip install pandas pdfplumber xlrd requests openpyxl
```

### Permission Errors
```bash
# Make scripts executable
chmod +x portfolio_extractor.py dashboard.py
```

### File Not Found Errors
```bash
# Verify file paths and names match exactly
ls -la "Portfolio Reports Samples/"
```

---

**Note:** This guide assumes all PDF files are placed in the `Portfolio Reports Samples/` directory with the exact filenames as specified in the code.