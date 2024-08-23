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
        
        result = {}
        
        # Process main data
        main_data = data['data']
        result.update(self._process_main_data(main_data))
        
        # Process included data
        included = data.get('included', [])
        result.update(self._process_included_data(included))
        
        # Process metadata
        metadata = data.get('meta', {})
        result.update(self._process_metadata(metadata))
        
        return result

    def _process_main_data(self, main_data: Dict) -> Dict:
        """Process the main data section."""
        result = {
            'id': main_data.get('id'),
            'type': main_data.get('type'),
        }
        
        # Process attributes
        attributes = main_data.get('attributes', {})
        for key, value in attributes.items():
            result[f'attr_{key}'] = value
        
        # Process relationships
        relationships = main_data.get('relationships', {})
        for rel_key, rel_value in relationships.items():
            if rel_value and 'data' in rel_value:
                rel_data = rel_value['data']
                if rel_data:
                    result[f'rel_{rel_key}_id'] = rel_data.get('id')
                    result[f'rel_{rel_key}_type'] = rel_data.get('type')
                else:
                    result[f'rel_{rel_key}'] = None
        
        return result

    def _process_included_data(self, included: List[Dict]) -> Dict:
        """Process the included data section."""
        result = {}
        for item in included:
            item_type = item.get('type')
            item_id = item.get('id')
            item_attributes = item.get('attributes', {})
            
            for key, value in item_attributes.items():
                result[f'incl_{item_type}_{item_id}_{key}'] = value
            
            # Process meta data in included items
            item_meta = item.get('meta', {})
            for meta_key, meta_value in item_meta.items():
                if isinstance(meta_value, dict):
                    for sub_key, sub_value in meta_value.items():
                        result[f'incl_{item_type}_{item_id}_meta_{meta_key}_{sub_key}'] = sub_value
                else:
                    result[f'incl_{item_type}_{item_id}_meta_{meta_key}'] = meta_value
        
        return result

    def _process_metadata(self, metadata: Dict) -> Dict:
        """Process the metadata section."""
        result = {}
        
        # Process top-level metadata
        for key, value in metadata.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    result[f'meta_{key}_{sub_key}'] = sub_value
            else:
                result[f'meta_{key}'] = value
        
        # Process market data
        market_data = metadata.get('marketData', {})
        for key, value in market_data.items():
            result[f'meta_marketData_{key}'] = value
        
        # Process chart times
        chart_times = metadata.get('chartTimes', {})
        for key, value in chart_times.items():
            result[f'meta_chartTimes_{key}'] = value
        
        # Process content counters
        content_counters = metadata.get('contentCounters', {})
        for key, value in content_counters.items():
            result[f'meta_contentCounters_{key}'] = value
        
        # Process show ratings
        show_ratings = metadata.get('showRatings', {})
        for key, value in show_ratings.items():
            result[f'meta_showRatings_{key}'] = value
        
        # Process available data
        available_data = metadata.get('availableData', {})
        for key, value in available_data.items():
            result[f'meta_availableData_{key}'] = value
        
        # Process routes data
        routes_data = metadata.get('routesData', {})
        for route, route_info in routes_data.items():
            for key, value in route_info.items():
                result[f'meta_routesData_{route}_{key}'] = value
        
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
