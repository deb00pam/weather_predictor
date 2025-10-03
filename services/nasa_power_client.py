import httpx
import asyncio
from datetime import datetime, date
from typing import Dict, List, Optional
import pandas as pd
from dateutil.relativedelta import relativedelta

class NASAPowerClient:
    """
    Client for NASA POWER (Prediction of Worldwide Energy Resources) API
    Fetches historical weather data for risk analysis
    """
    
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.timeout = 30.0
        
        # NASA POWER parameters for weather risk analysis
        self.weather_parameters = [
            "T2M_MIN",      # Temperature at 2 Meters Minimum (°C)
            "T2M_MAX",      # Temperature at 2 Meters Maximum (°C) 
            "T2M",          # Temperature at 2 Meters Average (°C)
            "WS10M",        # Wind Speed at 10 Meters (m/s)
            "PRECTOTCORR",  # Precipitation Corrected (mm/day)
            "RH2M",         # Relative Humidity at 2 Meters (%)
            "PS"            # Surface Pressure (kPa)
        ]
    
    async def get_historical_data(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        years_of_history: int = 10
    ) -> Dict:
        """
        Fetch historical weather data from NASA POWER API
        
        Args:
            latitude: Location latitude (-90 to 90)
            longitude: Location longitude (-180 to 180)  
            start_date: Target start date for analysis
            end_date: Target end date for analysis
            years_of_history: Number of historical years to analyze
            
        Returns:
            Dictionary containing historical weather data
        """
        try:
            # Calculate historical date range
            historical_start = start_date - relativedelta(years=years_of_history)
            historical_end = end_date - relativedelta(years=1)  # Exclude current year
            
            # Build NASA POWER API URL
            parameters_str = ",".join(self.weather_parameters)
            url = (
                f"{self.base_url}?"
                f"parameters={parameters_str}&"
                f"community=AG&"  # Agroclimatology community
                f"longitude={longitude}&"
                f"latitude={latitude}&"
                f"start={historical_start.strftime('%Y%m%d')}&"
                f"end={historical_end.strftime('%Y%m%d')}&"
                f"format=JSON"
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                
                # Process and structure the data
                processed_data = self._process_nasa_data(data, start_date, end_date)
                
                return processed_data
                
        except httpx.HTTPError as e:
            raise Exception(f"NASA POWER API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching NASA POWER data: {str(e)}")
    
    def _process_nasa_data(self, raw_data: Dict, target_start: date, target_end: date) -> Dict:
        """
        Process raw NASA POWER data into structured format for risk analysis
        """
        try:
            parameters_data = raw_data.get("properties", {}).get("parameter", {})
            
            # Convert to pandas DataFrame for easier manipulation
            df_data = {}
            dates = []
            
            # Extract dates and convert to datetime objects
            for date_str in list(parameters_data.get("T2M", {}).keys()):
                try:
                    date_obj = datetime.strptime(date_str, "%Y%m%d").date()
                    dates.append(date_obj)
                except ValueError:
                    continue
            
            # Extract weather parameters
            for param in self.weather_parameters:
                if param in parameters_data:
                    values = []
                    for date_str in [d.strftime("%Y%m%d") for d in dates]:
                        value = parameters_data[param].get(date_str)
                        # Handle missing values (-999 is NASA's missing data indicator)
                        if value == -999 or value is None:
                            values.append(None)
                        else:
                            values.append(float(value))
                    df_data[param] = values
            
            # Create DataFrame
            df = pd.DataFrame(df_data, index=dates)
            df = df.dropna()  # Remove rows with missing data
            
            # Filter data for target date range (same month/day across years)
            target_data = self._filter_target_period(df, target_start, target_end)
            
            # Calculate statistics
            statistics = self._calculate_statistics(target_data)
            
            # Calculate unique years in the data
            unique_years = 0
            if not target_data.empty:
                try:
                    # Convert index to datetime if it's not already
                    if hasattr(target_data.index, 'year'):
                        unique_years = len(target_data.index.year.unique())
                    else:
                        # Handle case where index might be date objects
                        years = set()
                        for idx in target_data.index:
                            if hasattr(idx, 'year'):
                                years.add(idx.year)
                        unique_years = len(years)
                except AttributeError:
                    unique_years = len(target_data) // 365 if len(target_data) > 0 else 0
            
            return {
                "location": {
                    "latitude": raw_data.get("geometry", {}).get("coordinates", [None, None])[1],
                    "longitude": raw_data.get("geometry", {}).get("coordinates", [None, None])[0]
                },
                "target_period": {
                    "start_date": target_start.isoformat(),
                    "end_date": target_end.isoformat()
                },
                "historical_data": target_data.to_dict('records') if not target_data.empty else [],
                "statistics": statistics,
                "data_years": unique_years,
                "metadata": {
                    "source": "NASA POWER API",
                    "parameters": self.weather_parameters,
                    "total_records": len(target_data)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error processing NASA POWER data: {str(e)}")
    
    def _filter_target_period(self, df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
        """
        Filter historical data to match target date range (same days across multiple years)
        """
        if df.empty:
            return pd.DataFrame()
        
        filtered_data = []
        filtered_indices = []
        
        for index, row in df.iterrows():
            # Convert index to date if needed
            if isinstance(index, str):
                try:
                    check_date = datetime.strptime(index, "%Y%m%d").date()
                except ValueError:
                    continue
            elif hasattr(index, 'date'):
                check_date = index.date()
            elif isinstance(index, date):
                check_date = index
            else:
                continue
            
            # Check if this date falls within the target period (month/day)
            if self._is_date_in_target_period(check_date, start_date, end_date):
                filtered_data.append(row)
                filtered_indices.append(index)
        
        if filtered_data:
            result_df = pd.DataFrame(filtered_data, index=filtered_indices)
            return result_df
        else:
            return pd.DataFrame()
    
    def _is_date_in_target_period(self, check_date: date, start_date: date, end_date: date) -> bool:
        """
        Check if a date falls within the target period (considering only month/day)
        """
        # Convert dates to (month, day) tuples for comparison
        check_md = (check_date.month, check_date.day)
        start_md = (start_date.month, start_date.day)
        end_md = (end_date.month, end_date.day)
        
        # Handle date ranges that cross year boundary
        if start_md <= end_md:
            return start_md <= check_md <= end_md
        else:
            return check_md >= start_md or check_md <= end_md
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate statistical summaries of weather parameters
        """
        if df.empty:
            return {}
        
        stats = {}
        for param in self.weather_parameters:
            if param in df.columns and not df[param].isna().all():
                stats[param] = {
                    "mean": float(df[param].mean()),
                    "min": float(df[param].min()),
                    "max": float(df[param].max()),
                    "std": float(df[param].std()),
                    "percentile_25": float(df[param].quantile(0.25)),
                    "percentile_75": float(df[param].quantile(0.75)),
                    "count": int(df[param].count())
                }
        
        return stats