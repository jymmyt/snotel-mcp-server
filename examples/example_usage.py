#!/usr/bin/env python3
"""
Example usage of the SNOTEL MCP Server tools
Shows how to use the SNOTEL API functions directly
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from snotel_mcp_server import (
    find_snotel_stations,
    get_station_info,
    get_station_data,
    get_recent_conditions,
    analyze_snowpack_trends
)

async def main():
    """Example usage of SNOTEL tools"""
    
    print("=== SNOTEL MCP Server Examples ===\n")
    
    # Example 1: Find SNOTEL stations in Colorado
    print("1. Finding Colorado SNOTEL Stations")
    print("-" * 40)
    result = await find_snotel_stations(state="CO")
    print(result[:500] + "..." if len(result) > 500 else result)
    print()
    
    # Example 2: Get station info for Red Mountain Pass
    print("2. Red Mountain Pass Station Info")
    print("-" * 40)
    result = await get_station_info("713:CO:SNTL")
    print(result)
    print()
    
    # Example 3: Get recent conditions
    print("3. Recent Conditions at Red Mountain Pass (last 7 days)")
    print("-" * 40)
    result = await get_recent_conditions("713:CO:SNTL", days=7)
    print(result)
    print()
    
    # Example 4: Find stations near Aspen
    print("4. SNOTEL Stations Near Aspen, CO")
    print("-" * 40)
    result = await find_snotel_stations(
        latitude=39.1911,
        longitude=-106.8175,
        radius_miles=25
    )
    print(result[:500] + "..." if len(result) > 500 else result)
    print()
    
    # Example 5: Get historical data (raw JSON)
    print("5. Historical Data for January 2024 (Raw JSON)")
    print("-" * 40)
    result = await get_station_data(
        "713:CO:SNTL",
        "2024-01-01",
        "2024-01-10"
    )
    print(result[:1000] + "..." if len(result) > 1000 else result)
    print()
    
    # Example 5b: Get hourly data
    print("5b. Hourly Data for One Day")
    print("-" * 40)
    result = await get_station_data(
        "713:CO:SNTL",
        "2024-01-01",
        "2024-01-01",
        duration_name="HOURLY"
    )
    print(result[:1000] + "..." if len(result) > 1000 else result)
    print()
    
    # Example 6: Analyze snowpack trends
    print("6. Snowpack Analysis for Winter 2023-2024")
    print("-" * 40)
    result = await analyze_snowpack_trends(
        "713:CO:SNTL",
        "2023-12-01",
        "2024-03-31"
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
