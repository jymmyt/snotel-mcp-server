#!/usr/bin/env python3
"""Test the FastMCP implementation using FastMCP Client"""

import asyncio
import sys
sys.path.insert(0, 'src')

from fastmcp import Client
from snotel_mcp_server import mcp

async def test_tools():
    """Test all SNOTEL tools using FastMCP Client"""
    
    # Create a client pointing directly at the server object
    client = Client(mcp)
    
    async with client:
        print("Testing find_snotel_stations...")
        print("-" * 50)
        result = await client.call_tool("find_snotel_stations", {"state": "CO"})
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
        
        print("Testing get_station_info...")
        print("-" * 50)
        result = await client.call_tool("get_station_info", {"station_triplet": "713:CO:SNTL"})
        print(result)
        print()
        
        print("Testing get_station_data...")
        print("-" * 50)
        result = await client.call_tool("get_station_data", {
            "station_triplet": "713:CO:SNTL",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        })
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
        
        print("Testing get_station_data with duration_name...")
        print("-" * 50)
        result = await client.call_tool("get_station_data", {
            "station_triplet": "713:CO:SNTL",
            "start_date": "2024-01-01",
            "end_date": "2024-01-01",
            "duration_name": "HOURLY"
        })
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
        
        print("Testing get_recent_conditions...")
        print("-" * 50)
        result = await client.call_tool("get_recent_conditions", {
            "station_triplet": "713:CO:SNTL",
            "days": 7
        })
        print(result)
        print()
        
        print("Testing analyze_snowpack_trends...")
        print("-" * 50)
        result = await client.call_tool("analyze_snowpack_trends", {
            "station_triplet": "713:CO:SNTL",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31"
        })
        print(result)

if __name__ == "__main__":
    asyncio.run(test_tools())