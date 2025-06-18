#!/usr/bin/env python3
"""
SNOTEL MCP Server using fastmcp
Provides access to USDA SNOTEL (SNOwpack TELemetry) data via the AWDB REST API
"""

import logging

# Configure logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP

log_level = os.getenv('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize FastMCP server
mcp = FastMCP("snotel-mcp-server")

# SNOTEL API configuration
API_BASE = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
DEFAULT_TIMEOUT = 30


class SnotelAPIClient:
    """Client for USDA AWDB REST API"""
    
    def __init__(self, base_url: str = API_BASE, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
    
    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make HTTP request to AWDB API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_params = params or {}
        
        # Log the complete request details
        logger = logging.getLogger(__name__)
        logger.info(f"SNOTEL API Request: {url}")
        logger.info(f"Request Parameters: {request_params}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=request_params)
            logger.info(f"Response Status: {response.status_code}")
            logger.info(f"Response URL: {response.url}")
            response.raise_for_status()
            return response.json()
    
    async def get_stations(self, 
                          state: Optional[str] = None,
                          network: str = "SNTL",
                          lat: Optional[float] = None,
                          lon: Optional[float] = None,
                          radius: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get SNOTEL stations"""
        params = {}
        
        if state:
            params["stationTriplets"] = f"*:{state.upper()}:{network}"
        elif lat and lon and radius:
            params["latitude"] = lat
            params["longitude"] = lon
            params["radius"] = radius
            params["networks"] = network
            params["logicalAnd"] = "true"
        else:
            params["networks"] = network
        
        data = await self._request("stations", params)
        return data if isinstance(data, list) else data.get("stations", [])
    
    async def get_station_data(self,
                              station_triplet: str,
                              start_date: str,
                              end_date: str,
                              elements: Optional[List[str]] = None,
                              duration: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get station measurement data"""
        if elements is None:
            elements = ["SNWD", "WTEQ", "TOBS", "PREC"]
        
        params = {
            "stationTriplets": station_triplet,
            "elements": ",".join(elements),
            "beginDate": start_date,
            "endDate": end_date,
            "ordinal": "1",
            "duration": duration
        }
        
        # if duration_name:
        #     params["duration"] = duration_name
        
        data = await self._request("data", params)
        return data if isinstance(data, list) else data.get("stations", [])


# Create global API client
api_client = SnotelAPIClient()


@mcp.tool()
async def find_snotel_stations(
    state: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_miles: Optional[float] = 50,
    network: str = "SNTL"
) -> str:
    """
    Find SNOTEL stations by state or location.
    
    Args:
        state: State abbreviation (e.g., 'CO', 'MT')
        latitude: Latitude for location-based search
        longitude: Longitude for location-based search
        radius_miles: Search radius in miles (default: 50)
        network: Network type (default: SNTL)
    
    Returns:
        Formatted list of SNOTEL stations
    """
    try:
        stations = await api_client.get_stations(
            state=state,
            network=network,
            lat=latitude,
            lon=longitude,
            radius=radius_miles
        )
        
        if not stations:
            return "No SNOTEL stations found with the given criteria."
        
        result = f"Found {len(stations)} SNOTEL stations"
        if state:
            result += f" in {state}"
        elif latitude and longitude:
            result += f" within {radius_miles} miles of ({latitude}, {longitude})"
        result += ":\n\n"
        
        for station in stations[:20]:  # Limit to first 20
            triplet = station.get("stationTriplet", "")
            name = station.get("name", "Unknown")
            lat = station.get("latitude", 0)
            lon = station.get("longitude", 0)
            elev = station.get("elevation", 0)
            county = station.get("countyName", "")
            
            result += f"• **{name}** ({triplet})\n"
            result += f"  Location: {lat:.4f}, {lon:.4f}\n"
            result += f"  Elevation: {elev:,.0f} ft\n"
            if county:
                result += f"  County: {county}\n"
            result += "\n"
        
        if len(stations) > 20:
            result += f"... and {len(stations) - 20} more stations\n"
        
        return result
        
    except Exception as e:
        return f"Error finding stations: {str(e)}"


@mcp.tool()
async def get_station_info(station_triplet: str) -> str:
    """
    Get detailed information about a specific SNOTEL station.
    
    Args:
        station_triplet: Station identifier (e.g., '713:CO:SNTL')
    
    Returns:
        Detailed station information
    """
    try:
        # Parse triplet
        parts = station_triplet.split(":")
        if len(parts) != 3:
            return "Invalid station triplet format. Expected format: 'id:state:network'"
        
        stations = await api_client.get_stations(state=parts[1], network=parts[2])
        
        # Find matching station
        station = None
        for s in stations:
            if s.get("stationTriplet") == station_triplet:
                station = s
                break
        
        if not station:
            return f"Station {station_triplet} not found"
        
        name = station.get("name", "Unknown")
        lat = station.get("latitude", 0)
        lon = station.get("longitude", 0)
        elev = station.get("elevation", 0)
        state = station.get("state", "")
        network = station.get("networkCd", "")
        county = station.get("countyName", "")
        
        result = f"**{name}** ({station_triplet})\n\n"
        result += f"• **Location**: {lat:.4f}, {lon:.4f}\n"
        result += f"• **Elevation**: {elev:,.0f} feet\n"
        result += f"• **State**: {state}\n"
        result += f"• **Network**: {network}\n"
        if county:
            result += f"• **County**: {county}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting station info: {str(e)}"


@mcp.tool()
async def get_station_data(
    station_triplet: str,
    start_date: str,
    end_date: str,
    duration: str,
    elements: Optional[List[str]] = None,
    
) -> str:
    """
    Get snow and weather data from a SNOTEL station.
    
    Args:
        station_triplet: Station identifier (e.g., '713:CO:SNTL')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        duration: Duration of measurements (e.g., 'DAILY', 'HOURLY', 'MONTHLY')
        elements: Data elements to retrieve (default: SNWD, WTEQ, TOBS, PREC)
        
    
    Returns:
        Raw JSON data from SNOTEL API
    """
    import json
    logger = logging.getLogger(__name__)
    logger.info(f"get_station_data: {station_triplet} {start_date} {end_date} {elements} {duration}")
    try:
        data = await api_client.get_station_data(
            station_triplet, start_date, end_date, elements, duration
        )
        
        if not data:
            return f"No data found for {station_triplet} from {start_date} to {end_date}"
        
        # Return the raw JSON data
        return json.dumps(data, indent=2)
        
    except Exception as e:
        return f"Error getting station data: {str(e)}"


@mcp.tool()
async def get_recent_conditions(
    station_triplet: str,
    days: int = 30
) -> str:
    """
    Get recent snow conditions from a station.
    
    Args:
        station_triplet: Station identifier (e.g., '713:CO:SNTL')
        days: Number of recent days (default: 30)
    
    Returns:
        Recent conditions summary
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = await api_client.get_station_data(
            station_triplet,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if not data:
            return f"No recent data available for {station_triplet}"
        
        # Parse measurements (same as get_station_data)
        measurements = []
        for station in data:
            if station.get("stationTriplet") == station_triplet:
                station_data = station.get("data", [])
                
                element_data = {}
                for item in station_data:
                    element = item.get("stationElement", {})
                    code = element.get("elementCode", "")
                    values = item.get("values", [])
                    element_data[code] = values
                
                dates = set()
                for values in element_data.values():
                    for v in values:
                        dates.add(v.get("date"))
                
                for date in sorted(dates):
                    record = {"date": date}
                    for code, values in element_data.items():
                        for v in values:
                            if v.get("date") == date:
                                record[code] = v.get("value")
                                break
                    measurements.append(record)
        
        if not measurements:
            return f"No measurements found for {station_triplet}"
        
        # Get latest conditions
        latest = measurements[-1] if measurements else None
        
        result = f"**Recent Conditions: {station_triplet}**\n"
        result += f"Last {days} days ({len(measurements)} records)\n\n"
        
        if latest:
            result += f"**Latest Reading ({latest['date']})**:\n"
            if "SNWD" in latest and latest["SNWD"] is not None:
                result += f"• Snow Depth: {latest['SNWD']:.1f}\"\n"
            if "WTEQ" in latest and latest["WTEQ"] is not None:
                result += f"• Snow Water Equivalent: {latest['WTEQ']:.1f}\"\n"
            if "TOBS" in latest and latest["TOBS"] is not None:
                result += f"• Temperature: {latest['TOBS']:.1f}°F\n"
            if "PREC" in latest and latest["PREC"] is not None:
                result += f"• Recent Precipitation: {latest['PREC']:.2f}\"\n"
        
        # Calculate statistics
        snow_depths = [r.get("SNWD", 0) for r in measurements if r.get("SNWD") is not None]
        if snow_depths:
            result += f"\n**{days}-Day Snow Depth Summary**:\n"
            result += f"• Maximum: {max(snow_depths):.1f}\"\n"
            result += f"• Minimum: {min(snow_depths):.1f}\"\n"
            result += f"• Average: {sum(snow_depths)/len(snow_depths):.1f}\"\n"
        
        return result
        
    except Exception as e:
        return f"Error getting recent conditions: {str(e)}"


@mcp.tool()
async def analyze_snowpack_trends(
    station_triplet: str,
    start_date: str,
    end_date: str
) -> str:
    """
    Analyze snowpack trends and calculate statistics.
    
    Args:
        station_triplet: Station identifier (e.g., '713:CO:SNTL')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        JSON string containing snowpack analysis with:
        - snow_depth_analysis: Peak depth, average depth, days with snow
        - swe_analysis: Peak SWE (Snow Water Equivalent), average SWE
        - snowfall_analysis: Total new snow, individual snowfall events with dates and amounts,
          biggest snowfall day, and average snowfall per snow day
        - measurements: Raw daily measurements for all requested elements
    """
    import json
    
    try:
        data = await api_client.get_station_data(
            station_triplet, start_date, end_date
        )
        
        if not data:
            return json.dumps({"error": f"No data available for analysis: {station_triplet}"})
        
        # Parse measurements
        measurements = []
        for station in data:
            if station.get("stationTriplet") == station_triplet:
                station_data = station.get("data", [])
                
                element_data = {}
                for item in station_data:
                    element = item.get("stationElement", {})
                    code = element.get("elementCode", "")
                    values = item.get("values", [])
                    element_data[code] = values
                
                dates = set()
                for values in element_data.values():
                    for v in values:
                        dates.add(v.get("date"))
                
                for date in sorted(dates):
                    record = {"date": date}
                    for code, values in element_data.items():
                        for v in values:
                            if v.get("date") == date:
                                record[code] = v.get("value")
                                break
                    measurements.append(record)
        
        if not measurements:
            return json.dumps({"error": "No measurements found for analysis"})
        
        result = {
            "station_triplet": station_triplet,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_records": len(measurements),
            "snow_depth_analysis": {},
            "swe_analysis": {},
            "snowfall_analysis": {},
            "measurements": measurements
        }
        
        # Snow depth analysis
        snow_depths = [(r["date"], r["SNWD"]) for r in measurements 
                      if "SNWD" in r and r["SNWD"] is not None]
        
        if snow_depths:
            depths = [d[1] for d in snow_depths]
            peak_depth = max(depths)
            peak_date = [d[0] for d in snow_depths if d[1] == peak_depth][0]
            
            result["snow_depth_analysis"] = {
                "peak_depth": {
                    "value": round(peak_depth, 1),
                    "date": peak_date,
                    "unit": "inches"
                },
                "average_depth": round(sum(depths)/len(depths), 1),
                "days_with_snow": len([d for d in depths if d > 0]),
                "total_observations": len(depths)
            }
        
        # SWE analysis
        swes = [(r["date"], r["WTEQ"]) for r in measurements 
                if "WTEQ" in r and r["WTEQ"] is not None]
        
        if swes:
            swe_values = [s[1] for s in swes]
            peak_swe = max(swe_values)
            peak_swe_date = [s[0] for s in swes if s[1] == peak_swe][0]
            
            result["swe_analysis"] = {
                "peak_swe": {
                    "value": round(peak_swe, 2),
                    "date": peak_swe_date,
                    "unit": "inches"
                },
                "average_swe": round(sum(swe_values)/len(swe_values), 2),
                "total_observations": len(swe_values)
            }
        
        # Snowfall analysis
        snowfall_days = []
        for i in range(1, len(snow_depths)):
            prev_depth = snow_depths[i-1][1]
            curr_depth = snow_depths[i][1]
            if curr_depth > prev_depth:
                snowfall_days.append({
                    "date": snow_depths[i][0],
                    "amount": round(curr_depth - prev_depth, 1)
                })
        
        if snowfall_days:
            snowfall_amounts = [s["amount"] for s in snowfall_days]
            total_snowfall = sum(snowfall_amounts)
            max_daily = max(snowfall_amounts)
            max_daily_record = [s for s in snowfall_days if s["amount"] == max_daily][0]
            
            result["snowfall_analysis"] = {
                "total_new_snow": round(total_snowfall, 1),
                "snow_days": len(snowfall_days),
                "biggest_day": {
                    "amount": round(max_daily, 1),
                    "date": max_daily_record["date"],
                    "unit": "inches"
                },
                "average_per_snow_day": round(total_snowfall/len(snowfall_days), 1),
                "snowfall_events": snowfall_days
            }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error analyzing snowpack trends: {str(e)}"})


# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")