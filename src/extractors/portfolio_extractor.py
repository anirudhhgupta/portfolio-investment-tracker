#!/usr/bin/env python3
"""
Portfolio Data Extraction Framework
Extracts standardized data from different wealth manager reports
"""

import pandas as pd
import pdfplumber
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import json

class PortfolioExtractor:
    """Base class for portfolio data extraction"""
    
    def __init__(self):
        self.standard_schema = {
            'manager_name': '',
            'asset_type': '',
            'asset_name': '', 
            'current_investment_value': 0.0,
            'current_market_value': 0.0,
            'value_as_of_date': '',
            'pl_amount': 0.0,
            'pl_percentage': 0.0,
            'irr_percentage': 0.0,  # Added IRR field
            'investment_date': '',
            'raw_data': {}  # Store original data for debugging
        }
    
    def clean_currency_value(self, value_str: str) -> float:
        """Convert currency strings to float values"""
        if pd.isna(value_str) or not value_str or str(value_str).strip() == '-' or str(value_str).strip() == '':
            return 0.0
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[₹$,\s]', '', str(value_str))
        
        # Handle different formats
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> str:
        """Standardize date formats to YYYY-MM-DD"""
        if not date_str:
            return ''
        
        # Common date patterns
        patterns = [
            r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # DD MMM YYYY
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(date_str))
            if match:
                try:
                    if len(match.groups()) == 3:
                        if '-' in date_str:  # YYYY-MM-DD
                            return date_str[:10]
                        else:  # DD/MM/YYYY or DD MMM YYYY
                            day, month, year = match.groups()
                            if month.isalpha():
                                # Convert month name to number
                                month_map = {
                                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                                    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                                    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                                }
                                month = month_map.get(month.lower()[:3], '01')
                            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
        
        return date_str

class INDMoneyExtractor(PortfolioExtractor):
    """Extract data from IND Money PDF reports with USD to INR conversion"""
    
    def __init__(self):
        super().__init__()
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
        from currency_converter import CurrencyConverter
        self.currency_converter = CurrencyConverter()
    
    def parse_date_from_period(self, period_str: str) -> str:
        """Extract date from period string like 'AUGUST - 2025'"""
        if not period_str:
            return ''
        
        try:
            # Look for month-year pattern
            match = re.search(r'([A-Z]+)\s*-\s*(\d{4})', period_str.upper())
            if match:
                month_name, year = match.groups()
                
                month_map = {
                    'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04',
                    'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUGUST': '08',
                    'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12'
                }
                
                month_num = month_map.get(month_name.upper(), '12')
                # Use last day of month as report date
                if month_num in ['01', '03', '05', '07', '08', '10', '12']:
                    day = '31'
                elif month_num in ['04', '06', '09', '11']:
                    day = '30'
                else:  # February
                    day = '28'
                
                return f"{year}-{month_num}-{day}"
        except:
            pass
        
        return ''
    
    def get_holding_dates_from_excel(self, excel_path: str) -> Dict[str, str]:
        """Extract holding dates from Excel file"""
        holding_dates = {}
        
        try:
            df = pd.read_excel(excel_path, engine='xlrd')
            
            # Find the data starting from row with 'Stock Symbol'
            start_row = None
            for idx, row in df.iterrows():
                if 'Stock Symbol' in str(row.values):
                    start_row = idx + 1
                    break
            
            if start_row is None:
                return holding_dates
            
            # Extract symbol and holding since date
            for idx in range(start_row, len(df)):
                try:
                    row = df.iloc[idx]
                    symbol = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ''
                    holding_since = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else ''
                    
                    if symbol and holding_since and symbol not in ['Disclaimer:-']:
                        # Parse date from format like "14 Apr 2025, 09:22 PM"
                        date_match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', holding_since)
                        if date_match:
                            day, month, year = date_match.groups()
                            month_map = {
                                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                            }
                            month_num = month_map.get(month.lower()[:3], '01')
                            holding_dates[symbol] = f"{year}-{month_num}-{day.zfill(2)}"
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error reading Excel for holding dates: {e}")
        
        return holding_dates
    
    def extract(self, file_path: str, excel_path: str = None) -> List[Dict[str, Any]]:
        """Extract portfolio data from IND Money PDF file (with optional Excel for dates)"""
        try:
            holdings = []
            
            # Get holding dates from Excel if provided
            holding_dates = {}
            if excel_path:
                holding_dates = self.get_holding_dates_from_excel(excel_path)
            
            with pdfplumber.open(file_path) as pdf:
                # Extract report date from first page
                report_date = ''
                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    
                    # Look for period information
                    period_match = re.search(r'Monthly Statement Period:\s*([A-Z]+\s*-\s*\d{4})', first_page_text)
                    if period_match:
                        report_date = self.parse_date_from_period(period_match.group(1))
                
                # Get exchange rate for the report date
                exchange_rate = self.currency_converter.get_usd_to_inr_rate(report_date)
                
                # Scan all pages for holdings data instead of looking for one specific page
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Look for holdings-related content
                    has_holdings_keywords = any(keyword in text.upper() for keyword in [
                        'HOLDINGS', 'SYMBOL', 'MARKET PRICE', 'COST BASIS', 'QUANTITY',
                        'PORTFOLIO', 'STOCK', 'SHARES', 'USD', 'UNREALIZED'
                    ])
                    
                    # Skip if no holdings data found
                    if not has_holdings_keywords:
                        continue
                    
                    # Skip summary pages
                    is_summary_only = ('SUMMARY' in text.upper() and 
                                     'DETAILED' not in text.upper() and
                                     text.count('Total') > 2)
                    
                    if is_summary_only:
                        continue
                    
                    print(f"Processing IND Money page {page_num + 1} - Holdings data found")
                    
                    # Extract holdings table
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 3:
                            continue
                        
                        # Look for holdings table by checking headers
                        header_found = False
                        header_row_idx = -1
                        
                        # Check first few rows for headers
                        for i in range(min(3, len(table))):
                            if table[i] and any('Symbol' in str(cell) for cell in table[i] if cell):
                                header_found = True
                                header_row_idx = i
                                break
                        
                        if not header_found:
                            continue
                        
                        # Process data rows (skip header and any rows before it)
                        for row_idx, row in enumerate(table[header_row_idx + 1:], header_row_idx + 1):
                            if not row or len(row) < 5:
                                continue
                            
                            symbol = str(row[0]).strip() if row[0] else ''
                            description = str(row[1]).strip() if len(row) > 1 and row[1] else ''
                            
                            # Skip non-stock rows
                            if not symbol or symbol.startswith('*') or symbol == 'Symbol' or symbol in ['Total', 'Grand Total']:
                                continue
                            
                            try:
                                holding = self.standard_schema.copy()
                                holding['manager_name'] = 'IND Money'
                                holding['asset_type'] = 'US Stocks'
                                holding['asset_name'] = f"{symbol} - {description[:30]}"
                                holding['value_as_of_date'] = report_date
                                
                                # Get investment date from Excel data
                                holding['investment_date'] = holding_dates.get(symbol, '')
                                
                                # Extract USD values (flexible column detection)
                                market_value_usd = 0
                                cost_basis_usd = 0
                                
                                # Look for market value and cost basis in different columns
                                for col_idx, cell in enumerate(row):
                                    if cell:
                                        value = self.clean_currency_value(cell)
                                        # Market value is typically larger and in later columns
                                        if value > 100 and col_idx >= 3:  # Column 4+ with significant value
                                            if market_value_usd == 0 or col_idx == 4:  # Prefer column 4
                                                market_value_usd = value
                                        # Cost basis is typically in later columns
                                        if value > 100 and col_idx >= 6:  # Column 7+ with significant value
                                            if cost_basis_usd == 0 or col_idx == 7:  # Prefer column 7
                                                cost_basis_usd = value
                                
                                # Convert to INR
                                holding['current_market_value'] = market_value_usd * exchange_rate
                                holding['current_investment_value'] = cost_basis_usd * exchange_rate
                                
                                # Calculate P&L in INR
                                holding['pl_amount'] = holding['current_market_value'] - holding['current_investment_value']
                                if holding['current_investment_value'] > 0:
                                    holding['pl_percentage'] = (holding['pl_amount'] / holding['current_investment_value']) * 100
                                
                                holding['raw_data'] = {
                                    'symbol': symbol,
                                    'market_value_usd': market_value_usd,
                                    'cost_basis_usd': cost_basis_usd,
                                    'exchange_rate': exchange_rate,
                                    'page': page_num + 1,
                                    'table_index': table_idx,
                                    'row_index': row_idx
                                }
                                
                                if holding['current_market_value'] > 0:
                                    holdings.append(holding)
                                    print(f"Added: {symbol} - Market: ${market_value_usd:.2f}, Cost: ${cost_basis_usd:.2f}")
                                
                            except Exception as e:
                                print(f"Error processing row {row_idx}: {e}")
                                continue
            
            return holdings
            
        except Exception as e:
            print(f"Error extracting IND Money data: {e}")
            return []

class ClientAssociatesExtractor(PortfolioExtractor):
    """Extract data from Client Associates PDF reports"""
    
    def extract(self, file_path: str, password: str) -> List[Dict[str, Any]]:
        """Extract portfolio data from Client Associates PDF with comprehensive page scanning"""
        try:
            holdings = []
            
            with pdfplumber.open(file_path, password=password) as pdf:
                # Extract report date from first page
                report_date = ''
                first_page_text = pdf.pages[0].extract_text()
                date_match = re.search(r'Report Date : (\d{2}/\d{2}/\d{4})', first_page_text)
                if date_match:
                    report_date = self.parse_date(date_match.group(1))
                
                # Scan all pages for holdings data
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Look for holdings-related content
                    has_holdings_keywords = any(keyword in text.upper() for keyword in [
                        'SECURITY', 'AIF', 'FUND', 'EQUITY', 'DEBT', 'MARKET VALUE', 
                        'TOTAL COST', 'UNIT COST', 'QUANTITY', 'IRR%', 'G/L'
                    ])
                    
                    # Skip if no holdings data found
                    if not has_holdings_keywords:
                        continue
                    
                    # Skip pure summary pages
                    is_summary_only = ('RETURN (XIRR)' in text and 
                                     'SECURITY' not in text)
                    
                    if is_summary_only:
                        continue
                    
                    print(f"Processing Client Associates page {page_num + 1} - Holdings data found")
                    
                    # Client Associates has a specific text format where holdings data is in lines
                    # Parse text line by line to extract holdings
                    text_lines = text.split('\n')
                    current_category = ''
                    
                    for i, line in enumerate(text_lines):
                        line = line.strip()
                        
                        # Identify category sections
                        if line in ['Equity', 'Debt']:
                            current_category = line
                            continue
                        
                        # Skip header lines and separators
                        if not line or line in ['-', 'PRIVATE AND CONFIDENTIAL'] or 'Report Date' in line:
                            continue
                        
                        # Look for fund lines with specific patterns
                        # Format: "Fund Name Date" followed by numeric data on same or next line
                        if any(keyword in line for keyword in ['Fund', 'AIF', 'Alpha', 'Growth']) and any(char.isdigit() for char in line):
                            parts = line.split()
                            
                            # Extract fund name (first few words before date)
                            fund_name_parts = []
                            date_found = False
                            investment_date = ''
                            
                            for part in parts:
                                # Check if this looks like a date (dd/mm/yyyy)
                                if re.match(r'\d{2}/\d{2}/\d{4}', part):
                                    date_found = True
                                    investment_date = self.parse_date(part)
                                    break
                                else:
                                    fund_name_parts.append(part)
                            
                            if not date_found or not fund_name_parts:
                                continue
                            
                            fund_name = ' '.join(fund_name_parts)
                            
                            # Extract numeric values from current line and potentially next line
                            numeric_values = []
                            total_cost = 0
                            market_value = 0
                            pl_amount = 0
                            pl_percentage = 0
                            irr_percentage = 0
                            
                            # Find date position to orient other values
                            date_index = -1
                            for j, part in enumerate(parts):
                                if re.match(r'\d{2}/\d{2}/\d{4}', part):
                                    date_index = j
                                    break
                            
                            if date_index > 0:
                                # First, check if the next line contains only numeric data (separate data line)
                                use_next_line_data = False
                                next_line_values = []
                                
                                # Check next few lines for pure numeric data
                                for line_offset in [1, 2, 3]:  # Check next 3 lines
                                    if i + line_offset < len(text_lines):
                                        candidate_line = text_lines[i + line_offset].strip()
                                        # Skip very short lines or obvious non-data lines
                                        if len(candidate_line) < 20 or candidate_line in ['Jan-23', '23', 'Feb-23']:
                                            continue
                                            
                                        # Check if line is purely numeric data
                                        if candidate_line and all(c.isdigit() or c in '., ' for c in candidate_line):
                                            # Convert candidate line to values
                                            candidate_values = []
                                            for part in candidate_line.split():
                                                try:
                                                    clean_part = re.sub(r'[,]', '', part)
                                                    if '.' in clean_part or clean_part.isdigit():
                                                        value = float(clean_part)
                                                        candidate_values.append(value)
                                                except ValueError:
                                                    continue
                                            
                                            # If candidate line has 10 values, it's the complete numeric data
                                            if len(candidate_values) == 10:
                                                next_line_values = candidate_values
                                                use_next_line_data = True
                                                break
                                
                                if use_next_line_data:
                                    # Use only the next line data (10 values: positions 8=IRR, 9=% Assets)
                                    converted_values = next_line_values
                                else:
                                    # Extract values after the date from current line
                                    value_parts = parts[date_index + 1:]
                                    
                                    # Convert Indian number format to float
                                    converted_values = []
                                    for part in value_parts:
                                        try:
                                            # Handle Indian comma format: 99,99,500 -> 9999500
                                            clean_part = re.sub(r'[,]', '', part)
                                            if '.' in clean_part or clean_part.isdigit():
                                                value = float(clean_part)
                                                converted_values.append(value)
                                        except ValueError:
                                            continue
                                
                                # Client Associates typical order after date:
                                # Quantity, UnitCost, TotalCost, MarketPrice, MarketValue, Income, TotalG/L, %G/L, IRR%, %Assets
                                if len(converted_values) >= 5:
                                    # Based on the format: after date we have numbers in specific positions
                                    # Position 0: Quantity (small number)
                                    # Position 1: Unit Cost (medium number)  
                                    # Position 2: Total Cost (large number)
                                    # Position 3: Market Price (medium number)
                                    # Position 4: Market Value (large number)
                                    # Position 5: Income (usually 0)
                                    # Position 6: Total G/L (large number)
                                    # Position 7: % G/L (percentage)
                                    # Position 8: IRR% (percentage) - THIS IS WHAT WE WANT
                                    # Position 9: % Assets (percentage)
                                    
                                    if len(converted_values) >= 5:
                                        # Total Cost is typically position 2
                                        total_cost = converted_values[2] if len(converted_values) > 2 else 0
                                        
                                        # Market Value is typically position 4
                                        market_value = converted_values[4] if len(converted_values) > 4 else 0
                                        
                                        # Calculate P&L
                                        pl_amount = market_value - total_cost
                                        
                                        # P&L percentage is typically position 7 (but we'll calculate it ourselves)
                                        if total_cost > 0:
                                            pl_percentage = (pl_amount / total_cost) * 100
                                        
                                        # IRR is position 8 (the actual IRR, not % of Assets)
                                        if len(converted_values) > 8:
                                            irr_percentage = converted_values[8]
                                
                            # Create holding if we have valid data
                            if total_cost > 1000 and market_value > 1000:
                                holding = self.standard_schema.copy()
                                holding['manager_name'] = 'Client Associates'
                                holding['asset_type'] = 'AIF'
                                holding['asset_name'] = fund_name
                                holding['value_as_of_date'] = report_date
                                holding['investment_date'] = investment_date if 'investment_date' in locals() else ''
                                holding['current_investment_value'] = total_cost
                                holding['current_market_value'] = market_value
                                holding['pl_amount'] = pl_amount
                                holding['pl_percentage'] = pl_percentage
                                holding['irr_percentage'] = irr_percentage
                                
                                holding['raw_data'] = {
                                    'category': current_category,
                                    'line_number': i + 1,
                                    'page': page_num + 1,
                                    'numeric_values': converted_values if 'converted_values' in locals() else [],
                                    'raw_line': line,
                                    'irr_percentage': irr_percentage
                                }
                                
                                holdings.append(holding)
                                print(f"Added: {fund_name[:50]} - Investment: ₹{total_cost:,.0f}, Current: ₹{market_value:,.0f}")
                    
                    # Also try table extraction as backup
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Look for the main holdings table with Security header
                        header_found = False
                        for row in table[:3]:  # Check first 3 rows for headers
                            if row and any(cell and 'Security' in str(cell) for cell in row):
                                header_found = True
                                break
                        
                        if not header_found:
                            continue
                        
                        # Process data rows
                        for row_idx, row in enumerate(table):
                            if not row or len(row) < 8:
                                continue
                            
                            security_name = str(row[0]).strip() if row[0] else ''
                            
                            # Skip header rows and category rows
                            if (not security_name or 
                                security_name in ['Security', 'Equity', 'Debt', '-', 'Equity - Total'] or
                                'Date' in security_name):
                                continue
                            
                            # Look for fund names
                            if any(keyword in security_name for keyword in ['Fund', 'AIF', 'Alpha', 'Growth']):
                                try:
                                    investment_date = self.parse_date(str(row[1])) if len(row) > 1 else ''
                                    total_cost = self.clean_currency_value(row[6]) if len(row) > 6 else 0
                                    market_value = self.clean_currency_value(row[8]) if len(row) > 8 else 0
                                    pl_amount = self.clean_currency_value(row[10]) if len(row) > 10 else 0
                                    pl_percentage = self.clean_currency_value(row[11]) if len(row) > 11 else 0
                                    
                                    if total_cost > 1000 and market_value > 1000:
                                        # Check if we already have this holding from text parsing
                                        duplicate = any(
                                            h['asset_name'] == security_name and 
                                            abs(h['current_investment_value'] - total_cost) < 1000
                                            for h in holdings
                                        )
                                        
                                        if not duplicate:
                                            holding = self.standard_schema.copy()
                                            holding['manager_name'] = 'Client Associates'
                                            holding['asset_type'] = 'AIF'
                                            holding['asset_name'] = security_name
                                            holding['value_as_of_date'] = report_date
                                            holding['investment_date'] = investment_date
                                            holding['current_investment_value'] = total_cost
                                            holding['current_market_value'] = market_value
                                            holding['pl_amount'] = pl_amount
                                            holding['pl_percentage'] = pl_percentage
                                            
                                            holding['raw_data'] = {
                                                'page': page_num + 1,
                                                'table_index': table_idx,
                                                'row_index': row_idx,
                                                'source': 'table'
                                            }
                                            
                                            holdings.append(holding)
                                            print(f"Added from table: {security_name[:50]} - Investment: ₹{total_cost:,.0f}, Current: ₹{market_value:,.0f}")
                                
                                except Exception as e:
                                    print(f"Error processing table row: {e}")
                                    continue
            
            return holdings
            
        except Exception as e:
            print(f"Error extracting Client Associates data: {e}")
            return []

class YesBankExtractor(PortfolioExtractor):
    """Extract data from Yes Bank PDF reports"""
    
    def extract(self, file_path: str, password: str) -> List[Dict[str, Any]]:
        """Extract detailed portfolio data from Yes Bank WMS Investment Summary Report"""
        try:
            holdings = []
            
            with pdfplumber.open(file_path, password=password) as pdf:
                # Extract report date from first page
                report_date = '2025-08-31'  # Default based on NAV date mentioned in PDF
                
                # Look for all pages with investment data (starting from page 6)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Skip early pages - start from page 6 onwards
                    if page_num < 5:
                        continue
                    
                    # Look for investment-related content
                    has_investment_keywords = any(keyword in text.upper() for keyword in [
                        'FUND', 'SCHEME', 'PLAN', 'EQUITY', 'DEBT', 'INDEX', 'GROWTH', 'DIVIDEND'
                    ])
                    
                    # Also check for specific fund names or investment structures
                    has_fund_data = any(pattern in text.upper() for pattern in [
                        'PRUDENTIAL', 'FLEXICAP', 'MULTICAP', 'MIDCAP', 'NIFTY', 'INDEX'
                    ])
                    
                    # Skip if no investment data found
                    if not has_investment_keywords and not has_fund_data:
                        continue
                    
                    # Skip pure summary pages (very short with only totals)
                    is_summary_only = ('Grand Total' in text and 
                                     'Category/' not in text and 
                                     len(text.split('\n')) < 15 and
                                     text.count(',') < 10)
                    
                    if is_summary_only:
                        continue
                    
                    print(f"Processing Yes Bank page {page_num + 1} - Investment data found")
                    
                    # Use table extraction for more accurate parsing
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Skip pure header tables (check if it has actual fund data)
                        has_fund_names = any(
                            table[i][0] and any(keyword in str(table[i][0]).upper() for keyword in ['FUND', 'SCHEME', 'PLAN', 'INDEX'])
                            for i in range(len(table))
                            if table[i] and table[i][0]
                        )
                        
                        if not has_fund_names:
                            continue
                        
                        # Each table represents a fund category
                        # Row 0: Category (e.g., "Equity- Flexi Cap")
                        # Row 1: Fund name with embedded data
                        # Row 2: Separate financial data
                        
                        category = ''
                        fund_name = ''
                        
                        if len(table) >= 1 and table[0] and table[0][0]:
                            category = str(table[0][0]).strip()
                        
                        # Check if this table has individual fund data embedded in text
                        individual_funds = []
                        
                        # Look for individual funds in rows 1 and 2
                        for row_idx in [1, 2]:
                            if len(table) > row_idx and table[row_idx] and table[row_idx][0]:
                                fund_text = str(table[row_idx][0]).strip()
                                if fund_text and fund_text != '':
                                    # Parse individual fund data if it has embedded numbers
                                    if re.search(r'\d+,\d+,\d+\.\d+', fund_text):
                                        # Extract fund name and financial data
                                        lines = fund_text.split('\n')
                                        fund_name_lines = []
                                        financial_data = None
                                        
                                        for line in lines:
                                            # If line contains financial data pattern
                                            if re.search(r'\d+,\d+,\d+\.\d+.*\d+\.\d+.*\d+,\d+,\d+\.\d+', line):
                                                financial_data = line
                                                
                                                # Extract fund name part from this line (before the numbers)
                                                words = line.split()
                                                fund_name_in_line = []
                                                for word in words:
                                                    # Stop when we hit the first number with commas
                                                    if re.match(r'\d+,\d+,\d+\.\d+', word):
                                                        break
                                                    fund_name_in_line.append(word)
                                                
                                                if fund_name_in_line:
                                                    fund_name_lines.extend(fund_name_in_line)
                                                break
                                            else:
                                                fund_name_lines.append(line.strip())
                                        
                                        if financial_data:
                                            fund_name = ' '.join(fund_name_lines).strip()
                                            # Parse financial data: find the numbers
                                            numbers = re.findall(r'\d+,\d+,\d+\.\d+', financial_data)
                                            if len(numbers) >= 2:
                                                investment_amount = self.clean_currency_value(numbers[0])
                                                current_value = self.clean_currency_value(numbers[1])
                                                
                                                individual_funds.append({
                                                    'name': fund_name,
                                                    'investment': investment_amount,
                                                    'current': current_value,
                                                    'raw_data': financial_data
                                                })
                        
                        # If we found individual funds, process them
                        if individual_funds:
                            for fund in individual_funds:
                                if fund['investment'] > 1000 and fund['current'] > 1000:
                                    holding = self.standard_schema.copy()
                                    holding['manager_name'] = 'Yes Bank'
                                    holding['asset_type'] = self._classify_asset_type(category, fund['name'])
                                    holding['asset_name'] = fund['name']
                                    holding['value_as_of_date'] = report_date
                                    holding['current_investment_value'] = fund['investment']
                                    holding['current_market_value'] = fund['current']
                                    holding['pl_amount'] = fund['current'] - fund['investment']
                                    
                                    if fund['investment'] > 0:
                                        holding['pl_percentage'] = (holding['pl_amount'] / fund['investment']) * 100
                                    
                                    holding['raw_data'] = {
                                        'category': category,
                                        'table_index': table_idx,
                                        'raw_financial_data': fund['raw_data'],
                                        'page': page_num + 1
                                    }
                                    
                                    holdings.append(holding)
                                    print(f"Added: {fund['name'][:50]} - Investment: ₹{fund['investment']:,.0f}, Current: ₹{fund['current']:,.0f}")
                        
                        else:
                            # Handle simple case with separate financial data row
                            if len(table) >= 2 and table[1] and table[1][0]:
                                # Extract fund name from first part before numbers
                                full_text = str(table[1][0]).strip()
                                # Find where the fund name ends (before numbers start)
                                lines = full_text.split('\n')
                                fund_name_parts = []
                                for line in lines:
                                    # If line contains mostly numbers/decimals, stop
                                    if re.search(r'\d+,\d+,\d+\.\d+', line):
                                        break
                                    fund_name_parts.append(line.strip())
                                fund_name = ' '.join(fund_name_parts).strip()
                            
                            # Get financial data from row 2 (index 1 after category)
                            if len(table) >= 3 and table[2] and len(table[2]) >= 4:
                                try:
                                    investment_str = str(table[2][1]) if table[2][1] else ''
                                    current_value_str = str(table[2][3]) if table[2][3] else ''
                                    
                                    investment_amount = self.clean_currency_value(investment_str)
                                    current_value = self.clean_currency_value(current_value_str)
                                    
                                    if investment_amount > 1000 and current_value > 1000 and fund_name:
                                        holding = self.standard_schema.copy()
                                        holding['manager_name'] = 'Yes Bank'
                                        holding['asset_type'] = self._classify_asset_type(category, fund_name)
                                        holding['asset_name'] = fund_name
                                        holding['value_as_of_date'] = report_date
                                        holding['current_investment_value'] = investment_amount
                                        holding['current_market_value'] = current_value
                                        holding['pl_amount'] = current_value - investment_amount
                                        
                                        if investment_amount > 0:
                                            holding['pl_percentage'] = (holding['pl_amount'] / investment_amount) * 100
                                        
                                        holding['raw_data'] = {
                                            'category': category,
                                            'table_index': table_idx,
                                            'investment_str': investment_str,
                                            'current_value_str': current_value_str,
                                            'page': page_num + 1
                                        }
                                        
                                        holdings.append(holding)
                                        print(f"Added: {fund_name[:50]} - Investment: ₹{investment_amount:,.0f}, Current: ₹{current_value:,.0f}")
                                
                                except Exception as e:
                                    print(f"Error parsing table {table_idx}: {e}")
                                    continue
            
            return holdings
            
        except Exception as e:
            print(f"Error extracting Yes Bank data: {e}")
            return []
    
    def _is_financial_data_line(self, line: str) -> bool:
        """Check if a line contains financial data (amounts with commas)"""
        # Look for patterns like "9,99,950.00 7.84 10,65,893.41"
        import re
        pattern = r'\d+,\d+,\d+\.\d+.*\d+\.\d+.*\d+,\d+,\d+\.\d+'
        return bool(re.search(pattern, line))
    
    def _classify_asset_type(self, category: str, fund_name: str) -> str:
        """Classify the asset type based on category and fund name"""
        if 'Index' in category or 'INDEX' in fund_name.upper() or 'ETF' in category:
            return 'Index Funds/ETFs'
        elif 'Equity' in category:
            return 'Equity Mutual Funds'
        elif 'Debt' in category:
            return 'Debt Mutual Funds'
        elif 'Hybrid' in category:
            return 'Hybrid Mutual Funds'
        else:
            return 'Mutual Funds'

class IIFL360OneExtractor(PortfolioExtractor):
    """Extract data from IIFL 360 One PDF reports"""
    
    def parse_date_from_text(self, text: str) -> str:
        """Extract report date from text"""
        if not text:
            return ''
        
        # Look for date pattern like "31 Aug 2025"
        date_match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', text)
        if date_match:
            day, month, year = date_match.groups()
            
            month_map = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            
            month_num = month_map.get(month.lower()[:3], '01')
            return f"{year}-{month_num}-{day.zfill(2)}"
        
        return ''
    
    def _classify_asset_type(self, instrument_name: str, text_context: str) -> str:
        """Classify the asset type based on instrument name and context"""
        instrument_upper = instrument_name.upper()
        context_upper = text_context.upper()
        
        if 'AIF' in instrument_upper or 'AIF' in context_upper:
            return 'AIF'
        elif 'UNLISTED' in context_upper or 'UNLISTED' in instrument_upper:
            return 'Unlisted Equity'
        elif 'MANAGED ACCOUNTS' in context_upper or 'DIVERSIFIED ALPHA' in instrument_upper:
            return 'AIF'
        elif 'EQUITY' in context_upper or 'EQUITY' in instrument_upper:
            return 'Direct Equity'
        elif 'DEBT' in context_upper or 'BOND' in instrument_upper:
            return 'Debt/Bonds'
        else:
            return 'Other'
    
    def extract(self, file_path: str, password: str) -> List[Dict[str, Any]]:
        """Extract detailed portfolio data from IIFL 360 One PDF with comprehensive page scanning"""
        try:
            holdings = []
            
            with pdfplumber.open(file_path, password=password) as pdf:
                # Extract report date from first page
                report_date = ''
                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    report_date = self.parse_date_from_text(first_page_text)
                
                # Scan all pages for holdings data (skip first 3 pages which are usually summary)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Skip early pages - start from page 4 onwards
                    if page_num < 3:
                        continue
                    
                    # Look for holdings-related content
                    has_holdings_keywords = any(keyword in text.upper() for keyword in [
                        'DETAILED HOLDING', 'HOLDING STATEMENT', 'MANAGED ACCOUNTS', 
                        'UNLISTED EQUITY', 'INSTRUMENT NAME', 'PORTFOLIO MANAGER',
                        'HOLDING COST', 'NET ASSET VALUE', 'AIF'
                    ])
                    
                    # Also check for specific instrument patterns
                    has_instrument_data = any(pattern in text.upper() for pattern in [
                        'ABAKKUS', 'DIVERSIFIED', 'ALPHA FUND', 'NATIONAL STOCK EXCHANGE',
                        'PORTFOLIO MANAGER', 'QUANTITY'
                    ])
                    
                    # Skip if no holdings data found
                    if not has_holdings_keywords and not has_instrument_data:
                        continue
                    
                    # Skip pure summary pages or transaction pages
                    is_summary_only = ('SUMMARY OF TOTAL PORTFOLIO' in text and 
                                     'INSTRUMENT NAME' not in text and
                                     'DETAILED HOLDING' not in text)
                    
                    is_transaction_only = ('TRANSACTION STATEMENT' in text or 
                                         'CORPORATE ACTION' in text) and 'HOLDING STATEMENT' not in text
                    
                    if is_summary_only or is_transaction_only:
                        continue
                    
                    print(f"Processing IIFL page {page_num + 1} - Holdings data found")
                    
                    # IIFL has a specific format where instrument data is in text lines, not clean tables
                    # Parse text line by line to extract holdings
                    text_lines = text.split('\n')
                    current_category = ''
                    
                    i = 0
                    while i < len(text_lines):
                        line = text_lines[i].strip()
                        
                        # Identify category sections
                        if any(keyword in line.upper() for keyword in [
                            'MANAGED ACCOUNTS EQUITY', 'UNLISTED EQUITY', 'DIRECT EQUITY', 'DEBT'
                        ]):
                            current_category = line
                            i += 1
                            continue
                        
                        # Look for instrument data patterns
                        # IIFL format: "ABAKKUS ASSET 9,502.181 10,000,000.00 16,077,020.96..."
                        if line and any(pattern in line.upper() for pattern in [
                            'ABAKKUS', 'DIVERSIFIED', 'NATIONAL STOCK EXCHANGE', 'FUND'
                        ]):
                            
                            # Extract instrument name and numerical data
                            parts = line.split()
                            instrument_name_parts = []
                            numeric_values = []
                            
                            for part in parts:
                                # If it's a number (with possible commas and decimals)
                                if re.match(r'^[\d,]+\.?\d*$', part):
                                    try:
                                        value = self.clean_currency_value(part)
                                        if value > 0:
                                            numeric_values.append(value)
                                    except:
                                        pass
                                else:
                                    # Part of instrument name (if no % symbols)
                                    if '%' not in part and not re.match(r'^\d{2}-\w{3}-\d{2}$', part):
                                        instrument_name_parts.append(part)
                            
                            # Build full instrument name from subsequent lines if needed
                            instrument_name = ' '.join(instrument_name_parts)
                            
                            # Look ahead for continuation lines to build complete instrument name
                            j = i + 1
                            while j < len(text_lines) and j < i + 10:  # Look max 10 lines ahead
                                next_line = text_lines[j].strip()
                                # If line contains fund-related keywords, it's part of the name
                                if next_line and any(keyword in next_line.upper() for keyword in [
                                    'FUND', 'MANAGER', 'ALPHA', 'CLASS', 'AIF', 'CATEGORY', 'LIMITED', 'PRIVATE'
                                ]):
                                    # Don't include lines with only financial data or percentages
                                    if not re.search(r'[\d,]+\.?\d*\s*%', next_line) and len(next_line) > 3:
                                        instrument_name += ' ' + next_line
                                elif next_line and 'BSE' in next_line.upper() or 'INDEX' in next_line.upper():
                                    # Include exchange/index information
                                    instrument_name += ' ' + next_line
                                elif not next_line or any(keyword in next_line.upper() for keyword in [
                                    'TOTAL', 'UNLISTED', 'MANAGED', 'GAIN/LOSS', 'PRICE'
                                ]):
                                    # Stop if we hit a new section
                                    break
                                j += 1
                            
                            # Extract financial values from the numeric data
                            if len(numeric_values) >= 3:
                                # For IIFL format: quantity, holding_cost, current_value are common
                                quantity = numeric_values[0] if numeric_values[0] < 100000 else 0
                                holding_cost = 0
                                current_value = 0
                                
                                # Find holding cost and current value (usually the largest amounts)
                                large_amounts = [v for v in numeric_values if v > 100000]
                                if len(large_amounts) >= 2:
                                    holding_cost = large_amounts[0]
                                    current_value = large_amounts[1]
                                
                                # Create holding if valid
                                if holding_cost > 1000 and current_value > 1000 and instrument_name:
                                    holding = self.standard_schema.copy()
                                    holding['manager_name'] = 'IIFL 360 One'
                                    holding['asset_type'] = self._classify_asset_type(instrument_name, current_category)
                                    holding['asset_name'] = instrument_name.strip()[:100]
                                    holding['value_as_of_date'] = report_date
                                    holding['current_investment_value'] = holding_cost
                                    holding['current_market_value'] = current_value
                                    holding['pl_amount'] = current_value - holding_cost
                                    
                                    if holding_cost > 0:
                                        holding['pl_percentage'] = (holding['pl_amount'] / holding_cost) * 100
                                    
                                    holding['raw_data'] = {
                                        'category': current_category,
                                        'line_number': i + 1,
                                        'quantity': quantity,
                                        'page': page_num + 1,
                                        'numeric_values': numeric_values,
                                        'raw_line': line
                                    }
                                    
                                    holdings.append(holding)
                                    print(f"Added: {instrument_name.strip()[:50]} - Investment: ₹{holding_cost:,.0f}, Current: ₹{current_value:,.0f}")
                        
                        i += 1
                    
                    # Also check tables for any additional data we might have missed
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # Look for rows with large financial amounts
                        for row in table:
                            if not row:
                                continue
                            
                            # Extract all numeric values from the row
                            numeric_values = []
                            for cell in row:
                                if cell:
                                    value = self.clean_currency_value(cell)
                                    if value > 100000:  # Significant amounts only
                                        numeric_values.append(value)
                            
                            # Skip table extraction for IIFL as it creates duplicate/summary entries
                            # The text-based extraction above is more accurate for individual holdings
                            pass
            
            return holdings
            
        except Exception as e:
            print(f"Error extracting IIFL 360 One data: {e}")
            return []

class KotakExtractor(PortfolioExtractor):
    """Extract data from Kotak PDF reports with duplicate detection"""
    
    def __init__(self):
        super().__init__()
        # Define potential duplicate patterns to match with other wealth managers
        self.duplicate_patterns = [
            # AIF patterns that might be duplicated with Client Associates
            {'pattern': r'ALTACURA.*AI.*ABSOLUTE.*RETURN.*FUND', 'manager': 'Client Associates'},
            {'pattern': r'ASK.*GROWTH.*INDIA.*FUND', 'manager': 'Client Associates'},  
            {'pattern': r'WHITE.*OAK.*INDIA.*EQUITY.*FUND', 'manager': 'Client Associates'},
            {'pattern': r'ACCURACAP.*ALPHA', 'manager': 'Client Associates'},
            {'pattern': r'WHITE.*SPACE.*ALPHA.*FUND', 'manager': 'Client Associates'},
        ]
    
    def extract(self, file_path: str, password: str) -> List[Dict[str, Any]]:
        """Extract portfolio data from Kotak PDF with comprehensive page scanning"""
        try:
            holdings = []
            
            with pdfplumber.open(file_path, password=password) as pdf:
                # Extract report date from first page
                report_date = '2025-08-31'  # Default based on the file name
                
                # Scan all pages for holdings data (pages 5-13 contain detailed holdings)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Skip non-holdings pages
                    if page_num < 4:  # Skip summary pages
                        continue
                    
                    # Look for holdings-related content
                    has_holdings_keywords = any(keyword in text.upper() for keyword in [
                        'HOLDING STATEMENT', 'INSTRUMENT NAME', 'MARKET VALUE', 
                        'HOLDING COST', 'UNREALISED', 'EQUITY', 'FUND', 'MUTUAL FUNDS'
                    ])
                    
                    # Skip if no holdings data found
                    if not has_holdings_keywords:
                        continue
                    
                    # Skip transaction pages and notes
                    is_transaction_page = 'PORTFOLIO ACTIVITY' in text.upper() or 'Activity Date' in text
                    is_notes_page = 'Returns are based on XIRR' in text
                    
                    if is_transaction_page or is_notes_page:
                        continue
                    
                    print(f"Processing Kotak page {page_num + 1} - Holdings data found")
                    
                    # First, extract investment dates from raw text
                    investment_dates = self._extract_investment_dates_from_text(text)
                    
                    # Extract holdings using table extraction
                    tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 3:
                            continue
                        
                        # Look for the main holdings table
                        header_found = False
                        data_start_row = -1
                        
                        # Check for table headers and find column indices (check multiple header rows)
                        purchase_date_col = -1
                        for row_idx, row in enumerate(table[:5]):  # Check more rows for multi-row headers
                            if row and any(cell and 'Instrument Name' in str(cell) for cell in row):
                                header_found = True
                                data_start_row = row_idx + 1
                                
                                # Debug: show main headers
                                print(f"Kotak headers found on page {page_num + 1}: {[str(cell) for cell in row if cell]}")
                                
                                # Check the next few rows for additional header information like "First Purchase Date"
                                for next_row_idx in range(row_idx + 1, min(row_idx + 3, len(table))):
                                    if next_row_idx < len(table) and table[next_row_idx]:
                                        next_row = table[next_row_idx]
                                        print(f"Checking sub-header row {next_row_idx + 1}: {[str(cell) for cell in next_row if cell]}")
                                        
                                        # Look for First Purchase Date in this row
                                        for col_idx, cell in enumerate(next_row):
                                            cell_str = str(cell).upper() if cell else ''
                                            if ('FIRST' in cell_str and 'PURCHASE' in cell_str) or 'PURCHASE DATE' in cell_str:
                                                purchase_date_col = col_idx
                                                data_start_row = next_row_idx + 1  # Data starts after this sub-header
                                                print(f"Found purchase date column at index {col_idx}: {cell}")
                                                break
                                        
                                        if purchase_date_col >= 0:
                                            break
                                break
                        
                        if not header_found:
                            continue
                        
                        # Skip header rows and find the actual data
                        current_category = ''
                        
                        for row_idx in range(len(table)):
                            row = table[row_idx]
                            if not row:
                                continue
                            
                            # Extract instrument name from first column
                            instrument_name = str(row[0]).strip() if row[0] else ''
                            
                            # Skip headers, category rows, and totals
                            if (not instrument_name or 
                                'Instrument Name' in instrument_name or
                                'Bal. No. Of' in instrument_name or
                                'Total' in instrument_name or
                                'Category' in instrument_name or
                                instrument_name in ['-', '']):
                                continue
                            
                            # Identify category sections
                            if any(keyword in instrument_name.upper() for keyword in [
                                'MUTUAL FUNDS', 'DIRECT EQUITY', 'OTHER PRODUCTS', 'BONDS', 'BANK ACCOUNTS'
                            ]):
                                current_category = instrument_name
                                continue
                            
                            # Look for actual holdings with financial data
                            # Skip if this is just a numeric row without instrument name
                            if (self._is_numeric_string(instrument_name) or 
                                len(instrument_name.replace(',', '').replace('.', '')) < 5):
                                continue
                            
                            # Check if the next row contains numeric data
                            numeric_row = None
                            if row_idx + 1 < len(table):
                                next_row = table[row_idx + 1]
                                if next_row and any(self._is_numeric_string(str(cell)) for cell in next_row if cell):
                                    numeric_row = next_row
                            
                            # If current row has numeric data, use it directly
                            if any(self._is_numeric_string(str(cell)) for cell in row[1:] if cell):
                                numeric_row = row
                            
                            # Filter out specific transaction IDs and problematic entries
                            is_transaction_ref = (
                                instrument_name.upper().startswith('INE0TLC') or  # Specific ISIN code
                                (len(instrument_name) < 15 and instrument_name.upper().startswith('INE'))  # Short ISIN codes
                            )
                            
                            is_valid_instrument = instrument_name and len(instrument_name) > 10 and not is_transaction_ref
                            
                            if numeric_row and is_valid_instrument:
                                try:
                                    # Look up investment date for this instrument
                                    investment_date = investment_dates.get(instrument_name, '')
                                    
                                    holding = self._extract_holding_from_row(
                                        instrument_name, numeric_row, current_category, report_date, page_num + 1, purchase_date_col, investment_date
                                    )
                                    
                                    if holding and holding['current_market_value'] > 1000:
                                        holdings.append(holding)
                                        print(f"Added: {instrument_name[:50]} - Cost: ₹{holding['current_investment_value']:,.0f}, Current: ₹{holding['current_market_value']:,.0f}")
                                
                                except Exception as e:
                                    print(f"Error processing Kotak row: {e}")
                                    continue
            
            return holdings
            
        except Exception as e:
            print(f"Error extracting Kotak data: {e}")
            return []
    
    def _extract_investment_dates_from_text(self, text: str) -> Dict[str, str]:
        """Extract investment dates from raw text by finding 'Txn. DD/MM/YY' patterns"""
        investment_dates = {}
        
        if not text:
            return investment_dates
        
        lines = text.split('\n')
        current_instrument = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for instrument names (various patterns for different asset types)
            is_potential_instrument = (
                # Lines with specific keywords (funds, bonds, companies) 
                (len(line) > 8 and 
                 any(keyword in line.upper() for keyword in ['FUND', 'GROWTH', 'LTD', 'LIMITED', 'NCD', 'BD', 'CORPORATION', 'SERVICES', 'BANK', 'SCHEME']) and
                 not line.startswith(('Txn.', 'Asset', 'Seg.', 'Total')) and
                 not any(char.isdigit() for char in line[:10]) and  # Avoid pure numeric lines
                 # Avoid category lines
                 line not in ['Direct Equity', 'E-Retail/E-Commerce', 'LIFE INSURANCE', 'PRIVATE SECTOR BANK', 'COMPUTERS - SOFTWARE & CONSULTING'])
            )
            
            if is_potential_instrument:
                current_instrument = line.strip()
            
            # Look for transaction date lines in various formats
            elif (line.startswith(('Txn.', 'Asset', 'Seg.')) or 
                  re.search(r'(Txn\.|Asset|Seg\.)\s*\d{1,2}/\d{1,2}/\d{2,4}', line)) and current_instrument:
                # Extract date from various formats: "Txn. 7/04/22", "Asset 30/09/22", "Seg. 7/05/24" 
                date_match = re.search(r'(?:Txn\.|Asset|Seg\.)\s*(\d{1,2}/\d{1,2}/\d{2,4})', line)
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        # Convert to standard format
                        investment_date = self.parse_date(date_str)
                        investment_dates[current_instrument] = investment_date
                        print(f"Found investment date for {current_instrument[:50]}: {investment_date}")
                    except:
                        continue
                current_instrument = None  # Reset after finding date
        
        return investment_dates
    
    def _is_numeric_string(self, s: str) -> bool:
        """Check if string contains numeric data (amount)"""
        if not s:
            return False
        # Remove common non-numeric characters and check if it's a number
        cleaned = re.sub(r'[,\s₹\-]', '', str(s))
        return cleaned.replace('.', '').isdigit() and len(cleaned) > 2
    
    def _extract_holding_from_row(self, instrument_name: str, row: List, category: str, report_date: str, page_num: int, purchase_date_col: int = -1, investment_date: str = '') -> Dict[str, Any]:
        """Extract holding data from a table row"""
        
        # Find holding cost and market value from the row
        holding_cost = 0
        market_value = 0
        
        # Kotak format typically has: [Qty, Avg Price, Holding Cost, Price Per Unit, Market Value, ...]
        for i, cell in enumerate(row):
            if cell:
                value = self.clean_currency_value(cell)
                # Look for large amounts that could be holding cost or market value
                if value > 10000:  # Significant amounts
                    if i >= 2 and holding_cost == 0:  # Typically holding cost comes first
                        holding_cost = value
                    elif i >= 4 and market_value == 0:  # Market value comes later
                        market_value = value
        
        # If we couldn't find both values, try a different approach
        if holding_cost == 0 or market_value == 0:
            amounts = []
            for cell in row:
                if cell:
                    value = self.clean_currency_value(cell)
                    if value > 10000:
                        amounts.append(value)
            
            if len(amounts) >= 2:
                holding_cost = amounts[0]
                market_value = amounts[1]
        
        if holding_cost > 0 and market_value > 0:
            holding = self.standard_schema.copy()
            holding['manager_name'] = 'Kotak'
            asset_type = self._classify_kotak_asset_type(category, instrument_name)
            holding['asset_type'] = asset_type
            holding['asset_name'] = instrument_name.strip()
            holding['value_as_of_date'] = report_date
            holding['current_investment_value'] = holding_cost
            
            # Use the investment date parameter (extracted from text) or fallback to table column
            if investment_date:
                holding['investment_date'] = investment_date
            else:
                # Fallback: Extract investment date from the specific First Purchase Date column
                fallback_date = ''
                if purchase_date_col >= 0 and purchase_date_col < len(row) and row[purchase_date_col]:
                    cell_str = str(row[purchase_date_col]).strip()
                    # Look for date patterns in the specific column
                    date_patterns = [
                        r'\d{1,2}/\d{1,2}/\d{2,4}',
                        r'\d{1,2}-\d{1,2}-\d{2,4}',
                        r'\d{1,2}\.\d{1,2}\.\d{2,4}'
                    ]
                    for pattern in date_patterns:
                        if re.match(pattern, cell_str):
                            try:
                                fallback_date = self.parse_date(cell_str)
                                break
                            except:
                                continue
                
                holding['investment_date'] = fallback_date
            
            # For bonds, use invested value as current value since they're fixed value assets
            if asset_type == 'Bonds':
                holding['current_market_value'] = holding_cost  # Use invested value
                holding['pl_amount'] = 0  # No P&L for bonds
                holding['pl_percentage'] = 0
            else:
                holding['current_market_value'] = market_value
                holding['pl_amount'] = market_value - holding_cost
                if holding_cost > 0:
                    holding['pl_percentage'] = (holding['pl_amount'] / holding_cost) * 100
            
            # Check for potential duplicates
            holding['potential_duplicate'] = self._check_for_duplicates(instrument_name)
            
            holding['raw_data'] = {
                'category': category,
                'page': page_num,
                'raw_row': row,
                'instrument_name': instrument_name
            }
            
            return holding
        
        return None
    
    def _classify_kotak_asset_type(self, category: str, instrument_name: str) -> str:
        """Classify the asset type based on category and instrument name"""
        category_upper = category.upper() if category else ''
        instrument_upper = instrument_name.upper()
        
        if 'AIF' in instrument_upper or 'CLASS A1' in instrument_upper:
            return 'AIF'
        elif 'MUTUAL FUNDS' in category_upper or 'FUND' in instrument_upper:
            return 'Mutual Funds'
        elif 'BONDS' in category_upper or 'NCD' in instrument_upper or 'BD' in instrument_upper:
            return 'Bonds'
        elif 'DIRECT EQUITY' in category_upper or 'LTD' in instrument_upper:
            return 'Direct Equity'
        elif 'BANK' in category_upper or 'CASH' in category_upper:
            return 'Cash/Bank'
        else:
            return 'Other'
    
    def _check_for_duplicates(self, instrument_name: str) -> List[str]:
        """Check if this instrument might be a duplicate from another wealth manager"""
        potential_duplicates = []
        
        for pattern_info in self.duplicate_patterns:
            if re.search(pattern_info['pattern'], instrument_name.upper()):
                potential_duplicates.append(pattern_info['manager'])
        
        return potential_duplicates

class MotilalOswalExtractor(PortfolioExtractor):
    """Extract detailed data from Motilal Oswal PDF reports"""
    
    def parse_date_from_text(self, text: str) -> str:
        """Extract report date from text"""
        if not text:
            return ''
        
        # Look for date pattern like "26 Sep 2025"
        date_match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', text)
        if date_match:
            day, month, year = date_match.groups()
            
            month_map = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            
            month_num = month_map.get(month.lower()[:3], '01')
            return f"{year}-{month_num}-{day.zfill(2)}"
        
        return ''
    
    def extract_direct_equity(self, page, report_date: str) -> List[Dict[str, Any]]:
        """Extract direct equity holdings"""
        holdings = []
        
        try:
            tables = page.extract_tables()
            
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                # Look for equity table with ISIN column
                header = table[0] if table else []
                if any('ISIN' in str(cell) for cell in header if cell):
                    
                    for row in table[1:]:  # Skip header
                        if not row or len(row) < 10:
                            continue
                        
                        sector = str(row[0]).strip() if row[0] else ''
                        security = str(row[1]).strip() if row[1] else ''
                        isin = str(row[2]).strip() if row[2] else ''
                        
                        # Skip totals and empty rows
                        if not security or 'Total' in security or not isin or security == '-':
                            continue
                        
                        holding = self.standard_schema.copy()
                        holding['manager_name'] = 'Motilal Oswal'
                        holding['asset_type'] = 'Direct Equity'
                        holding['asset_name'] = security
                        holding['value_as_of_date'] = report_date
                        
                        # Extract values from equity table
                        if len(row) > 11:
                            holding['current_investment_value'] = self.clean_currency_value(row[11])
                        if len(row) > 13:
                            holding['current_market_value'] = self.clean_currency_value(row[13])
                        
                        # Calculate P&L from the difference (more reliable than PDF column)
                        holding['pl_amount'] = holding['current_market_value'] - holding['current_investment_value']
                        
                        # Calculate P&L percentage
                        if holding['current_investment_value'] > 0:
                            holding['pl_percentage'] = (holding['pl_amount'] / holding['current_investment_value']) * 100
                        
                        holding['raw_data'] = {
                            'sector': sector,
                            'isin': isin,
                            'page': 'Direct Equity'
                        }
                        
                        if holding['current_market_value'] > 0:
                            holdings.append(holding)
                            
        except Exception as e:
            print(f"Error extracting direct equity: {e}")
        
        return holdings
    
    def extract_aif_holdings(self, page, report_date: str) -> List[Dict[str, Any]]:
        """Extract AIF holdings"""
        holdings = []
        
        try:
            tables = page.extract_tables()
            
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                # Look for AIF table with Instrument column
                header = table[0] if table else []
                if any('Instrument' in str(cell) for cell in header if cell):
                    
                    for row in table[1:]:  # Skip header
                        if not row or len(row) < 8:
                            continue
                        
                        category = str(row[0]).strip() if row[0] else ''
                        instrument = str(row[1]).strip() if row[1] else ''
                        asset_class = str(row[3]).strip() if row[3] else ''
                        
                        # Skip totals and empty rows
                        if not instrument or 'Total' in category or not asset_class or instrument == '-':
                            continue
                        
                        holding = self.standard_schema.copy()
                        holding['manager_name'] = 'Motilal Oswal'
                        holding['asset_type'] = 'AIF'
                        holding['asset_name'] = instrument
                        holding['value_as_of_date'] = report_date
                        
                        # Extract AIF values
                        if len(row) > 5:
                            holding['current_investment_value'] = self.clean_currency_value(row[5])
                        if len(row) > 6:
                            holding['current_market_value'] = self.clean_currency_value(row[6])
                        
                        # Calculate P&L from the difference (more reliable than PDF column)
                        holding['pl_amount'] = holding['current_market_value'] - holding['current_investment_value']
                        
                        # Calculate P&L percentage
                        if holding['current_investment_value'] > 0:
                            holding['pl_percentage'] = (holding['pl_amount'] / holding['current_investment_value']) * 100
                        
                        holding['raw_data'] = {
                            'category': category,
                            'xirr': self.clean_currency_value(row[11]) if len(row) > 11 else 0,
                            'page': 'AIF'
                        }
                        
                        if holding['current_market_value'] > 0:
                            holdings.append(holding)
                            
        except Exception as e:
            print(f"Error extracting AIF holdings: {e}")
        
        return holdings
    
    def extract(self, file_path: str, password: str) -> List[Dict[str, Any]]:
        """Extract detailed portfolio data from Motilal Oswal PDF with comprehensive page scanning"""
        try:
            holdings = []
            
            with pdfplumber.open(file_path, password=password) as pdf:
                # Extract report date from first page
                report_date = ''
                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    report_date = self.parse_date_from_text(first_page_text)
                
                # Scan all pages for holdings data (skip first 2 pages which are usually summary)
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    # Skip early pages - start from page 3 onwards
                    if page_num < 2:
                        continue
                    
                    # Look for equity holdings content
                    has_equity_keywords = any(keyword in text.upper() for keyword in [
                        'DIRECT EQUITY', 'EQUITY HOLDING', 'ISIN', 'SECTOR', 'SECURITY',
                        'MARKET VALUE', 'INVESTMENT VALUE', 'UNREALIZED'
                    ])
                    
                    # Look for AIF holdings content
                    has_aif_keywords = any(keyword in text.upper() for keyword in [
                        'AIF', 'ALTERNATIVE INVESTMENT', 'INSTRUMENT', 'ASSET CLASS',
                        'PORTFOLIO MANAGEMENT', 'FUND MANAGER', 'XIRR'
                    ])
                    
                    # Skip if no relevant holdings data found
                    if not has_equity_keywords and not has_aif_keywords:
                        continue
                    
                    # Skip pure summary pages
                    is_summary_only = ('SUMMARY' in text.upper() and 
                                     'DETAILED' not in text.upper() and
                                     text.count('Total') > 3)
                    
                    if is_summary_only:
                        continue
                    
                    print(f"Processing Motilal Oswal page {page_num + 1} - Holdings data found")
                    
                    # Try to extract Direct Equity holdings
                    if has_equity_keywords:
                        equity_holdings = self.extract_direct_equity(page, report_date)
                        if equity_holdings:
                            holdings.extend(equity_holdings)
                            print(f"Found {len(equity_holdings)} equity holdings on page {page_num + 1}")
                    
                    # Try to extract AIF holdings
                    if has_aif_keywords:
                        aif_holdings = self.extract_aif_holdings(page, report_date)
                        if aif_holdings:
                            holdings.extend(aif_holdings)
                            print(f"Found {len(aif_holdings)} AIF holdings on page {page_num + 1}")
            
            return holdings
            
        except Exception as e:
            print(f"Error extracting Motilal Oswal data: {e}")
            return []

def remove_duplicates(all_holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate holdings across wealth managers"""
    
    # Group holdings by manager
    holdings_by_manager = {}
    for holding in all_holdings:
        manager = holding['manager_name']
        if manager not in holdings_by_manager:
            holdings_by_manager[manager] = []
        holdings_by_manager[manager].append(holding)
    
    # Keep track of removed duplicates
    removed_duplicates = []
    clean_holdings = []
    
    # Priority order: Client Associates > Other managers (since Client Associates has more detailed data)
    manager_priority = ['Client Associates', 'IND Money', 'Yes Bank', 'Motilal Oswal', 'IIFL 360 One', 'Kotak']
    
    # Build a map of assets already seen from higher priority managers
    seen_assets = set()
    
    for manager in manager_priority:
        if manager not in holdings_by_manager:
            continue
        
        for holding in holdings_by_manager[manager]:
            asset_key = create_asset_key(holding['asset_name'])
            
            if asset_key in seen_assets:
                # This is a duplicate - skip it
                removed_duplicates.append({
                    'duplicate_holding': holding,
                    'original_manager': get_original_manager(seen_assets, asset_key, clean_holdings)
                })
                print(f"🚨 REMOVED DUPLICATE: {holding['asset_name'][:50]} from {manager} (already in {get_original_manager(seen_assets, asset_key, clean_holdings)})")
            else:
                # This is the first time we see this asset - keep it
                seen_assets.add(asset_key)
                clean_holdings.append(holding)
    
    print(f"\\n📊 DEDUPLICATION SUMMARY:")
    print(f"Original holdings: {len(all_holdings)}")
    print(f"Duplicate holdings removed: {len(removed_duplicates)}")
    print(f"Clean holdings: {len(clean_holdings)}")
    
    return clean_holdings

def create_asset_key(asset_name: str) -> str:
    """Create a normalized key for asset matching - includes investment dates to distinguish different tranches"""
    key = asset_name.upper()
    
    # Extract date patterns to distinguish different investment tranches
    date_match = re.search(r'(\d{1,2}[-/]\w{3}[-/]\d{2,4})', key)
    date_suffix = f"_{date_match.group(1)}" if date_match else ""
    
    # For specific known funds, extract the core identifier but keep class/series info
    if 'ASK' in key and 'GROWTH' in key and 'INDIA' in key:
        # Include series/class info for ASK funds
        series_match = re.search(r'(SERIES\s*\w+|CLASS\s*\w+)', key)
        series_suffix = f"_{series_match.group(1)}" if series_match else ""
        return f'ASK GROWTH INDIA{series_suffix}{date_suffix}'
    elif 'ALTACURA' in key and 'AI' in key and 'ABSOLUTE' in key and 'RETURN' in key:
        # For Altacura funds, use the full name as it contains unique identifiers
        # Different series have different dates: "25-" vs "23-F" vs "23-Feb-23"
        return key.replace(' ', '_')
    elif 'WHITE' in key and 'OAK' in key and 'INDIA' in key and ('EQUITY' in key or 'VI' in key):
        return f'WHITE OAK INDIA EQUITY{date_suffix}'
    elif 'ACCURACAP' in key and ('ALPHA' in key or 'PRIME' in key):
        return f'ACCURACAP ALPHA{date_suffix}'
    elif 'WHITE' in key and 'SPACE' in key and 'ALPHA' in key:
        # For White Space funds, use the full name as Fund 1 vs Fund 2 are different
        return key.replace(' ', '_')
    elif 'MOTILAL OSWAL' in key and ('ALTERNATIVE' in key or 'FOUNDERS' in key or 'SELECT' in key):
        if 'SELECT' in key and ('OPP' in key or 'OPPORTUNITIES' in key):
            return 'MOTILAL OSWAL SELECT OPPORTUNITIES'
        elif 'FOUNDERS' in key or ('MOTILAL' in key and 'OSWL' in key and 'ANCHORS' in key):
            return 'MOTILAL OSWAL FOUNDERS'
        else:
            return 'MOTILAL OSWAL ALTERNATIVE'
    
    # For other funds, use generic normalization
    key = re.sub(r'\\(DEMAT\\)', '', key)
    key = re.sub(r'\\(ERSTWHILE.*?\\)', '', key)
    key = re.sub(r'\\bCLASS A1\\b|\\bCL A1\\b|\\bCLASS B1\\b|\\bCL B1\\b|\\bCL D4\\b', '', key)
    key = re.sub(r'\\bDIRECT PLAN\\b|\\bREGULAR PLAN\\b', '', key)
    key = re.sub(r'\\bGROWTH\\b', '', key)
    key = re.sub(r'\\bLTD\\b|\\bLIMITED\\b', '', key)
    key = re.sub(r'\\bLLP\\b', '', key)
    key = re.sub(r'\\bFUND\\b', '', key)
    key = re.sub(r'\\bAIF\\b', '', key)
    key = re.sub(r'\\bEQUITY\\b', '', key)
    key = re.sub(r'\\bVI\\b', '', key)
    key = re.sub(r'\\bTRUST\\b', '', key)
    key = re.sub(r'\\bINVESTMENT\\b', '', key)
    key = re.sub(r'\\bALTERNATIVE\\b', '', key)
    key = re.sub(r'\\bSERIES\\b|\\bSR\\b', '', key)
    key = re.sub(r'\\bI\\b|\\bIV\\b', '', key)
    key = re.sub(r'[-\\s]+', ' ', key)
    key = re.sub(r'\\s*-\\s*25-', '', key)
    key = re.sub(r'\\s*6W\\s*12A', '', key)
    key = re.sub(r'\\s*OPT\\s*1', '', key)
    key = re.sub(r'\\s+', ' ', key).strip()
    
    return key

def get_original_manager(seen_assets: set, asset_key: str, clean_holdings: List[Dict[str, Any]]) -> str:
    """Find which manager originally had this asset"""
    for holding in clean_holdings:
        if create_asset_key(holding['asset_name']) == asset_key:
            return holding['manager_name']
    return "Unknown"

def get_latest_data_folder() -> str:
    """Get the latest month folder from data/input directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(project_root, "data", "input")
    
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Get all subdirectories
    month_folders = [f for f in os.listdir(data_dir) 
                    if os.path.isdir(os.path.join(data_dir, f)) and not f.startswith('.')]
    
    if not month_folders:
        raise FileNotFoundError("No month folders found in Data directory")
    
    # Parse and sort by date
    month_dates = []
    for folder in month_folders:
        try:
            # Parse "April 2025", "August 2025" etc.
            month_year = datetime.strptime(folder, "%B %Y")
            month_dates.append((month_year, folder))
        except ValueError:
            print(f"Warning: Could not parse folder name '{folder}' as month/year")
            continue
    
    if not month_dates:
        raise ValueError("No valid month folders found (expected format: 'Month YYYY')")
    
    # Sort by date and get latest
    latest_month = max(month_dates, key=lambda x: x[0])[1]
    latest_path = os.path.join(data_dir, latest_month)
    
    print(f"📅 Using latest data folder: {latest_month}")
    return latest_path

def main():
    """Main function to test extractors with latest month data"""
    base_path = get_latest_data_folder()
    
    # Initialize extractors
    extractors = {
        'IND Money': INDMoneyExtractor(),
        'Client Associates': ClientAssociatesExtractor(),
        'Yes Bank': YesBankExtractor(),
        'Kotak': KotakExtractor(),
        'Motilal Oswal': MotilalOswalExtractor(),
        'IIFL 360 One': IIFL360OneExtractor()
    }
    
    # Dynamic file matching
    def find_file_by_pattern(directory: str, pattern: str) -> Optional[str]:
        """Find file in directory matching pattern"""
        if not os.path.exists(directory):
            return None
        
        for filename in os.listdir(directory):
            if pattern.lower() in filename.lower():
                return os.path.join(directory, filename)
        return None
    
    all_holdings = []
    
    # IND Money
    ind_file = find_file_by_pattern(base_path, "INDMoney")
    ind_excel = find_file_by_pattern(base_path, "IND-HOLDINGS_REPORT")
    if ind_file:
        ind_holdings = extractors['IND Money'].extract(ind_file, ind_excel)
        all_holdings.extend(ind_holdings)
        print(f"IND Money: Extracted {len(ind_holdings)} holdings from {os.path.basename(ind_file)}")
    else:
        print("⚠️  IND Money file not found")
    
    # Client Associates  
    ca_file = find_file_by_pattern(base_path, "Client Associates")
    if ca_file:
        ca_holdings = extractors['Client Associates'].extract(ca_file, "caswgu")
        all_holdings.extend(ca_holdings)
        print(f"Client Associates: Extracted {len(ca_holdings)} holdings from {os.path.basename(ca_file)}")
    else:
        print("⚠️  Client Associates file not found")
    
    # Yes Bank
    yb_file = find_file_by_pattern(base_path, "Yes Bank")
    if yb_file:
        yb_holdings = extractors['Yes Bank'].extract(yb_file, "1505671327071974")
        all_holdings.extend(yb_holdings)
        print(f"Yes Bank: Extracted {len(yb_holdings)} holdings from {os.path.basename(yb_file)}")
    else:
        print("⚠️  Yes Bank file not found")
    
    # Kotak
    kotak_file = find_file_by_pattern(base_path, "Kotak")
    if kotak_file:
        kotak_holdings = extractors['Kotak'].extract(kotak_file, "swat2707")
        all_holdings.extend(kotak_holdings)
        print(f"Kotak: Extracted {len(kotak_holdings)} holdings from {os.path.basename(kotak_file)}")
    else:
        print("⚠️  Kotak file not found")
    
    # Motilal Oswal
    mo_file = find_file_by_pattern(base_path, "Motilal Oswal")
    if mo_file:
        mo_holdings = extractors['Motilal Oswal'].extract(mo_file, "ADFPG0415P")
        all_holdings.extend(mo_holdings)
        print(f"Motilal Oswal: Extracted {len(mo_holdings)} holdings from {os.path.basename(mo_file)}")
    else:
        print("⚠️  Motilal Oswal file not found")
    
    # IIFL 360 One
    iifl_file = find_file_by_pattern(base_path, "IIFL 360 One")
    if iifl_file:
        iifl_holdings = extractors['IIFL 360 One'].extract(iifl_file, "ADFPG0415P")
        all_holdings.extend(iifl_holdings)
        print(f"IIFL 360 One: Extracted {len(iifl_holdings)} holdings from {os.path.basename(iifl_file)}")
    else:
        print("⚠️  IIFL 360 One file not found")
    
    print(f"\nTotal holdings extracted (before deduplication): {len(all_holdings)}")
    
    # Remove duplicates
    clean_holdings = remove_duplicates(all_holdings)
    
    # Save extracted data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_file = os.path.join(project_root, "data", "output", "extracted_portfolio_data.json")
    with open(output_file, 'w') as f:
        json.dump(clean_holdings, f, indent=2, default=str)
    
    print(f"Data saved to: {output_file}")
    
    # Show summary
    if clean_holdings:
        total_investment = sum(h['current_investment_value'] for h in clean_holdings)
        total_market_value = sum(h['current_market_value'] for h in clean_holdings)
        total_pl = total_market_value - total_investment
        
        print(f"\n=== PORTFOLIO SUMMARY ===")
        print(f"Total Investment Value: ₹{total_investment:,.2f}")
        print(f"Total Market Value: ₹{total_market_value:,.2f}")
        print(f"Total P&L: ₹{total_pl:,.2f}")
        if total_investment > 0:
            print(f"Total Return %: {(total_pl/total_investment)*100:.2f}%")

if __name__ == "__main__":
    main()