import numpy as np
import pandas as pd
from datetime import date, datetime
from typing import Dict, List, Tuple, Optional
import math

class WeatherRiskAnalyzer:
    """
    Analyzes historical weather data to calculate risk probabilities
    for various adverse weather conditions
    """
    
    def __init__(self):
        # Weather risk thresholds based on meteorological standards
        self.risk_thresholds = {
            "very_hot": {
                "parameter": "T2M_MAX",
                "threshold": 35.0,  # °C
                "comparison": "greater",
                "description": "Very Hot (>35°C)",
                "activity_impact": "Heat exhaustion risk, dehydration"
            },
            "very_cold": {
                "parameter": "T2M_MIN", 
                "threshold": 0.0,   # °C
                "comparison": "less",
                "description": "Very Cold (<0°C)",
                "activity_impact": "Hypothermia risk, frostbite"
            },
            "very_windy": {
                "parameter": "WS10M",
                "threshold": 15.0,  # m/s (≈33 mph)
                "comparison": "greater",
                "description": "Very Windy (>15 m/s)",
                "activity_impact": "Dangerous for camping, outdoor events"
            },
            "very_wet": {
                "parameter": "PRECTOTCORR",
                "threshold": 25.0,  # mm/day (≈1 inch)
                "comparison": "greater", 
                "description": "Very Wet (>25mm rain)",
                "activity_impact": "Flooding risk, outdoor events cancelled"
            }
        }
        
        # Activity-specific risk adjustments
        self.activity_adjustments = {
            "hiking": {
                "very_hot": 1.2,    # Higher risk for hiking
                "very_cold": 1.3,   # Higher risk for hiking
                "very_windy": 1.1,
                "very_wet": 1.2
            },
            "camping": {
                "very_hot": 1.1,
                "very_cold": 1.4,   # Very high risk for camping
                "very_windy": 1.3,   # High risk for camping
                "very_wet": 1.3
            },
            "fishing": {
                "very_hot": 1.0,
                "very_cold": 1.1,
                "very_windy": 1.2,   # Moderate risk for fishing
                "very_wet": 1.1
            },
            "general": {
                "very_hot": 1.0,
                "very_cold": 1.0,
                "very_windy": 1.0,
                "very_wet": 1.0
            }
        }
    
    def analyze_risk(
        self,
        historical_data: Dict,
        target_dates: Tuple[date, date],
        activity_type: str = "general"
    ) -> Dict:
        """
        Analyze weather risk based on historical data
        
        Args:
            historical_data: Historical weather data from NASA POWER
            target_dates: Tuple of (start_date, end_date) for the planned activity
            activity_type: Type of outdoor activity
            
        Returns:
            Risk assessment dictionary
        """
        try:
            # Extract historical records
            records = historical_data.get("historical_data", [])
            
            if not records:
                raise Exception("No historical data available for analysis")
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(records)
            
            # Calculate risk probabilities for each category
            risk_categories = []
            
            for risk_name, risk_config in self.risk_thresholds.items():
                risk_category = self._calculate_risk_probability(
                    df, risk_name, risk_config, activity_type
                )
                risk_categories.append(risk_category)
            
            # Calculate uncomfortable conditions (heat index)
            uncomfortable_risk = self._calculate_uncomfortable_risk(df, activity_type)
            risk_categories.append(uncomfortable_risk)
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk_score(risk_categories)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                risk_categories, overall_risk_score, activity_type
            )
            
            return {
                "location": historical_data.get("location", {}),
                "date_range": {
                    "start_date": target_dates[0].isoformat(),
                    "end_date": target_dates[1].isoformat()
                },
                "risk_categories": risk_categories,
                "overall_risk_score": overall_risk_score,
                "recommendations": recommendations,
                "historical_data_years": historical_data.get("data_years", 0),
                "activity_type": activity_type,
                "analysis_metadata": {
                    "total_historical_records": len(records),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing weather risk: {str(e)}")
    
    def _calculate_risk_probability(
        self,
        df: pd.DataFrame,
        risk_name: str,
        risk_config: Dict,
        activity_type: str
    ) -> Dict:
        """
        Calculate probability of a specific weather risk
        """
        parameter = risk_config["parameter"]
        threshold = risk_config["threshold"]
        comparison = risk_config["comparison"]
        
        if parameter not in df.columns:
            return {
                "category": risk_name,
                "probability": 0.0,
                "threshold_value": threshold,
                "risk_level": "unknown",
                "description": risk_config["description"],
                "activity_impact": risk_config["activity_impact"],
                "confidence": 0.0,
                "sample_size": 0,
                "historical_events": 0
            }
        
        # Remove missing values
        valid_data = df[parameter].dropna()
        
        if len(valid_data) == 0:
            return {
                "category": risk_name,
                "probability": 0.0,
                "threshold_value": threshold,
                "risk_level": "unknown",
                "description": risk_config["description"],
                "activity_impact": risk_config["activity_impact"],
                "confidence": 0.0,
                "sample_size": 0,
                "historical_events": 0
            }
        
        # Calculate probability based on threshold
        if comparison == "greater":
            risk_events = (valid_data > threshold).sum()
        elif comparison == "less":
            risk_events = (valid_data < threshold).sum()
        else:
            risk_events = 0
        
        base_probability = risk_events / len(valid_data)
        
        # Apply activity-specific adjustments
        activity_factor = self.activity_adjustments.get(activity_type, {}).get(risk_name, 1.0)
        adjusted_probability = min(base_probability * activity_factor, 1.0)
        
        # Calculate confidence based on sample size
        confidence = self._calculate_confidence(len(valid_data))
        
        # Determine risk level
        risk_level = self._determine_risk_level(adjusted_probability)
        
        return {
            "category": risk_name,
            "probability": round(adjusted_probability * 100, 1),  # Convert to percentage
            "threshold_value": threshold,
            "risk_level": risk_level,
            "description": risk_config["description"],
            "activity_impact": risk_config["activity_impact"],
            "confidence": round(confidence * 100, 1),
            "sample_size": len(valid_data),
            "historical_events": int(risk_events)
        }
    
    def _calculate_uncomfortable_risk(self, df: pd.DataFrame, activity_type: str) -> Dict:
        """
        Calculate risk of very uncomfortable conditions using heat index
        """
        if "T2M" not in df.columns or "RH2M" not in df.columns:
            return {
                "category": "very_uncomfortable",
                "probability": 0.0,
                "threshold_value": 40.0,
                "risk_level": "unknown",
                "description": "Very Uncomfortable (Heat Index >40°C)",
                "activity_impact": "Heat stress, exhaustion risk",
                "confidence": 0.0,
                "sample_size": 0,
                "historical_events": 0
            }
        
        # Calculate heat index for each record
        heat_indices = []
        
        for _, row in df.iterrows():
            if pd.notna(row["T2M"]) and pd.notna(row["RH2M"]):
                heat_index = self._calculate_heat_index(row["T2M"], row["RH2M"])
                if heat_index is not None:
                    heat_indices.append(heat_index)
        
        if not heat_indices:
            return {
                "category": "very_uncomfortable",
                "probability": 0.0,
                "threshold_value": 40.0,
                "risk_level": "unknown",
                "description": "Very Uncomfortable (Heat Index >40°C)",
                "activity_impact": "Heat stress, exhaustion risk",
                "confidence": 0.0,
                "sample_size": 0,
                "historical_events": 0
            }
        
        # Calculate probability of heat index > 40°C
        risk_events = sum(1 for hi in heat_indices if hi > 40.0)
        base_probability = risk_events / len(heat_indices)
        
        # Apply activity adjustment
        activity_factor = self.activity_adjustments.get(activity_type, {}).get("very_hot", 1.0)
        adjusted_probability = min(base_probability * activity_factor, 1.0)
        
        confidence = self._calculate_confidence(len(heat_indices))
        risk_level = self._determine_risk_level(adjusted_probability)
        
        return {
            "category": "very_uncomfortable",
            "probability": round(adjusted_probability * 100, 1),
            "threshold_value": 40.0,
            "risk_level": risk_level,
            "description": "Very Uncomfortable (Heat Index >40°C)",
            "activity_impact": "Heat stress, exhaustion risk",
            "confidence": round(confidence * 100, 1),
            "sample_size": len(heat_indices),
            "historical_events": risk_events
        }
    
    def _calculate_heat_index(self, temperature_c: float, humidity_percent: float) -> Optional[float]:
        """
        Calculate heat index given temperature in Celsius and relative humidity
        Returns heat index in Celsius
        """
        try:
            # Convert temperature to Fahrenheit for calculation
            temp_f = temperature_c * 9/5 + 32
            
            # Heat index calculation (Rothfusz equation)
            if temp_f < 80 or humidity_percent < 40:
                return temperature_c  # Heat index ≈ temperature when conditions are mild
            
            # Coefficients for the heat index equation
            c1 = -42.379
            c2 = 2.04901523
            c3 = 10.14333127
            c4 = -0.22475541
            c5 = -6.83783e-3
            c6 = -5.481717e-2
            c7 = 1.22874e-3
            c8 = 8.5282e-4
            c9 = -1.99e-6
            
            # Calculate heat index in Fahrenheit
            hi_f = (c1 + (c2 * temp_f) + (c3 * humidity_percent) + 
                   (c4 * temp_f * humidity_percent) + (c5 * temp_f**2) + 
                   (c6 * humidity_percent**2) + (c7 * temp_f**2 * humidity_percent) + 
                   (c8 * temp_f * humidity_percent**2) + (c9 * temp_f**2 * humidity_percent**2))
            
            # Convert back to Celsius
            heat_index_c = (hi_f - 32) * 5/9
            
            return heat_index_c
            
        except Exception:
            return None
    
    def _calculate_confidence(self, sample_size: int) -> float:
        """
        Calculate confidence score based on sample size
        """
        if sample_size >= 2000:  # ~5-6 years of daily data
            return 0.95
        elif sample_size >= 1000:  # ~3 years of daily data
            return 0.85
        elif sample_size >= 500:   # ~1-2 years of daily data
            return 0.75
        elif sample_size >= 100:   # ~3 months of daily data
            return 0.60
        else:
            return 0.40
    
    def _determine_risk_level(self, probability: float) -> str:
        """
        Determine risk level based on probability
        """
        if probability >= 0.3:    # 30%+
            return "very_high"
        elif probability >= 0.2:  # 20-29%
            return "high"
        elif probability >= 0.1:  # 10-19%
            return "moderate"
        else:                     # <10%
            return "low"
    
    def _calculate_overall_risk_score(self, risk_categories: List[Dict]) -> float:
        """
        Calculate overall risk score (0-100)
        """
        if not risk_categories:
            return 0.0
        
        # Weight different risk categories
        weights = {
            "very_hot": 0.25,
            "very_cold": 0.25,
            "very_windy": 0.20,
            "very_wet": 0.20,
            "very_uncomfortable": 0.10
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for category in risk_categories:
            category_name = category["category"]
            probability = category["probability"] / 100  # Convert back to 0-1 scale
            weight = weights.get(category_name, 0.1)
            
            weighted_score += probability * weight
            total_weight += weight
        
        if total_weight > 0:
            overall_score = (weighted_score / total_weight) * 100
        else:
            overall_score = 0.0
        
        return round(overall_score, 1)
    
    def _generate_recommendations(
        self,
        risk_categories: List[Dict],
        overall_risk_score: float,
        activity_type: str
    ) -> List[str]:
        """
        Generate personalized recommendations based on risk analysis
        """
        recommendations = []
        
        # Overall risk assessment
        if overall_risk_score >= 40:
            recommendations.append("⚠️ High overall weather risk detected. Consider postponing or relocating your activity.")
        elif overall_risk_score >= 25:
            recommendations.append("⚡ Moderate weather risk. Monitor conditions and prepare contingency plans.")
        elif overall_risk_score >= 10:
            recommendations.append("✓ Low to moderate weather risk. Standard precautions recommended.")
        else:
            recommendations.append("✅ Low weather risk. Good conditions expected for outdoor activities.")
        
        # Category-specific recommendations
        for category in risk_categories:
            if category["probability"] >= 20:  # 20%+ probability
                cat_name = category["category"]
                
                if cat_name == "very_hot":
                    recommendations.append("🌡️ High heat risk: Bring extra water, start early, seek shade during peak hours.")
                elif cat_name == "very_cold":
                    recommendations.append("❄️ Cold weather risk: Pack warm layers, check for frost warnings.")
                elif cat_name == "very_windy":
                    recommendations.append("💨 High wind risk: Secure equipment, avoid exposed areas.")
                elif cat_name == "very_wet":
                    recommendations.append("🌧️ Rain risk: Pack waterproof gear, check drainage conditions.")
                elif cat_name == "very_uncomfortable":
                    recommendations.append("🥵 Heat stress risk: Plan frequent breaks, avoid midday activities.")
        
        # Activity-specific recommendations
        if activity_type == "hiking":
            recommendations.append("🥾 Hiking tips: Inform others of your route, carry emergency supplies.")
        elif activity_type == "camping":
            recommendations.append("⛺ Camping tips: Check campsite drainage, secure tent properly.")
        elif activity_type == "fishing":
            recommendations.append("🎣 Fishing tips: Check water conditions, monitor weather changes.")
        
        # Add data quality note if needed
        avg_confidence = np.mean([cat["confidence"] for cat in risk_categories if "confidence" in cat])
        if avg_confidence < 70:
            recommendations.append("📊 Note: Limited historical data available. Consider checking recent local forecasts.")
        
        return recommendations