import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

class StockDataLoader:
    def __init__(self, base_url: str = "https://seekingalpha.com/api/v3/symbols/"):
        self.base_url = base_url

    def fetch_symbol_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data for a single symbol."""
        url = f"{self.base_url}{symbol}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def process_symbol_data(self, data: Optional[Dict]) -> Optional[Dict]:
        """Process the raw data for a symbol."""
        if data is None or 'data' not in data:
            return None
        
        main_data = data['data']
        attributes = main_data.get('attributes', {})
        metadata = data.get('meta', {})
        contentCounters = metadata.get('contentCounters', {})
        
        result = {
            'id': main_data.get('id'),
            'type': main_data.get('type'),
            'symbol': attributes.get('symbol'),
            'name': attributes.get('name'),
            'followersCount': attributes.get('followersCount'),
            'exchange': attributes.get('exchange'),
            'analysis': contentCounters.get('analysis'),
            'related_analysis': contentCounters.get('related_analysis'),
            'transcripts': contentCounters.get('transcripts'),
            'earning_slides': contentCounters.get('earning_slides'),
            'news': contentCounters.get('news'),
            'partnerNews': contentCounters.get('partnerNews'),
            'pressReleases': contentCounters.get('pressReleases'),
            'bulls_say': contentCounters.get('bulls_say'),
            'bears_say': contentCounters.get('bears_say'),
            'investing_groups': contentCounters.get('investing_groups'),
            'annual_dividends': contentCounters.get('annual_dividends'),
            'annual_earnings_estimates': contentCounters.get('annual_earnings_estimates'),
            'dividend_news': contentCounters.get('dividend_news'),
            'sec_filings': contentCounters.get('sec_filings'),
            'sec_filings_fin_and_news': contentCounters.get('sec_filings_fin_and_news'),
            'sec_filings_tenders': contentCounters.get('sec_filings_tenders'),
            'sec_filings_other': contentCounters.get('sec_filings_other'),
            'sec_filings_ownership': contentCounters.get('sec_filings_ownership'),
            'sector_rating_change_notices': contentCounters.get('sector_rating_change_notices'),
            'sector_quant_warnings': contentCounters.get('sector_quant_warnings'),
            'sector_dividend_safety_warnings': contentCounters.get('sector_dividend_safety_warnings'),
            'quarterly_revenue': contentCounters.get('quarterly_revenue'),
            'annual_revenue': contentCounters.get('annual_revenue'),
        }
        
        # Add market data
        market_data = attributes.get('marketData', {})
        result.update({
            'market_open': market_data.get('market_open'),
            'market_open_time': market_data.get('market_open_time'),
        })
        
        # Add content counters
        content_counters = attributes.get('contentCounters', {})
        result.update({
            'analysis_count': content_counters.get('analysis_count'),
            'news_count': content_counters.get('news_count'),
            'transcripts_count': content_counters.get('transcripts_count'),
        })
        
        return result

    def load_symbol_data(self, symbols: List[str], max_workers: int = 10) -> pd.DataFrame:
        """Load data for multiple symbols concurrently."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(self.fetch_symbol_data, symbol): symbol for symbol in symbols}
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    processed_data = self.process_symbol_data(data)
                    if processed_data:
                        results.append(processed_data)
                except Exception as exc:
                    print(f'{symbol} generated an exception: {exc}')
        
        return pd.DataFrame(results)

# Example usage
if __name__ == "__main__":
    loader = StockDataLoader()