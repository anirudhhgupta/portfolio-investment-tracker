#!/usr/bin/env python3
"""
Currency Converter
Handles currency conversion for portfolio data
"""

import json
import os
from datetime import datetime, timedelta
import requests

class CurrencyConverter:
    """Handle currency conversions with caching"""
    
    def __init__(self, cache_file="exchange_rates_cache.json"):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.api_base = "https://api.exchangerate-api.com/v4/latest"
    
    def load_cache(self):
        """Load cached exchange rates"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_cache(self):
        """Save exchange rates to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def is_cache_valid(self, currency, hours=24):
        """Check if cached rate is still valid"""
        if currency not in self.cache:
            return False
        
        cache_time = datetime.fromisoformat(self.cache[currency]['timestamp'])
        return datetime.now() - cache_time < timedelta(hours=hours)
    
    def get_exchange_rate(self, from_currency="USD", to_currency="INR"):
        """Get exchange rate with caching"""
        cache_key = f"{from_currency}_{to_currency}"
        
        # Check cache first
        if self.is_cache_valid(cache_key):
            return self.cache[cache_key]['rate']
        
        try:
            # Fetch from API
            url = f"{self.api_base}/{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rate = data['rates'].get(to_currency)
            
            if rate:
                # Cache the result
                self.cache[cache_key] = {
                    'rate': rate,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'exchangerate-api'
                }
                self.save_cache()
                return rate
                
        except Exception as e:
            print(f"Warning: Could not fetch exchange rate for {from_currency} to {to_currency}: {e}")
        
        # Fallback rates if API fails
        fallback_rates = {
            'USD_INR': 83.25,  # Approximate rate
            'EUR_INR': 90.50,
            'GBP_INR': 105.75
        }
        
        if cache_key in fallback_rates:
            print(f"Using fallback rate for {from_currency} to {to_currency}")
            return fallback_rates[cache_key]
        
        return None
    
    def convert_amount(self, amount, from_currency="USD", to_currency="INR"):
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate:
            return amount * rate
        
        print(f"Warning: Could not convert {amount} {from_currency} to {to_currency}")
        return amount
    
    def format_currency(self, amount, currency="INR"):
        """Format currency amount for display"""
        if currency == "INR":
            if amount >= 10000000:  # 1 crore
                return f"₹{amount/10000000:.2f}Cr"
            elif amount >= 100000:  # 1 lakh
                return f"₹{amount/100000:.2f}L"
            else:
                return f"₹{amount:,.2f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"

def test_converter():
    """Test currency converter functionality"""
    converter = CurrencyConverter()
    
    print("🔄 Testing Currency Converter")
    print("=" * 40)
    
    # Test USD to INR conversion
    usd_amount = 1000
    inr_amount = converter.convert_amount(usd_amount, "USD", "INR")
    print(f"${usd_amount} USD = {converter.format_currency(inr_amount, 'INR')}")
    
    # Test formatting
    test_amounts = [50000, 500000, 5000000, 50000000]
    print(f"\n💰 Currency Formatting Examples:")
    for amount in test_amounts:
        print(f"₹{amount:,} = {converter.format_currency(amount, 'INR')}")
    
    # Show cache info
    print(f"\n📋 Exchange Rate Cache:")
    for key, data in converter.cache.items():
        print(f"  {key}: {data['rate']:.4f} (cached {data['timestamp'][:19]})")

if __name__ == "__main__":
    test_converter()