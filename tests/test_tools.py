"""Tests for SNOTEL MCP Server tools"""
import pytest
import pytest_asyncio
from unittest.mock import patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from snotel_mcp_server import mcp
from fastmcp import Client


@pytest_asyncio.fixture
async def client():
    """Create a FastMCP client for testing"""
    test_client = Client(mcp)
    async with test_client:
        yield test_client


@pytest.mark.asyncio
@patch('snotel_mcp_server.api_client.get_stations')
async def test_find_snotel_stations_tool(mock_get_stations, client):
    """Test the find_snotel_stations tool"""
    mock_get_stations.return_value = [
        {
            "stationTriplet": "713:CO:SNTL",
            "name": "Red Mountain Pass",
            "state": "CO",
            "networkCd": "SNTL",
            "latitude": 37.89,
            "longitude": -107.71,
            "elevation": 11080,
            "countyName": "San Juan"
        }
    ]
    
    result = await client.call_tool("find_snotel_stations", {"state": "CO"})
    result_text = result[0].text  # Extract text from TextContent
    
    assert "Found 1 SNOTEL stations in CO" in result_text
    assert "Red Mountain Pass" in result_text
    assert "713:CO:SNTL" in result_text
    assert "11,080 ft" in result_text


@pytest.mark.asyncio
@patch('snotel_mcp_server.api_client.get_stations')
async def test_get_station_info_tool(mock_get_stations, client):
    """Test the get_station_info tool"""
    mock_get_stations.return_value = [
        {
            "stationTriplet": "713:CO:SNTL",
            "name": "Red Mountain Pass",
            "state": "CO",
            "networkCd": "SNTL",
            "latitude": 37.89,
            "longitude": -107.71,
            "elevation": 11080,
            "countyName": "San Juan"
        }
    ]
    
    result = await client.call_tool("get_station_info", {"station_triplet": "713:CO:SNTL"})
    result_text = result[0].text  # Extract text from TextContent
    
    assert "Red Mountain Pass" in result_text
    assert "713:CO:SNTL" in result_text
    assert "37.8900, -107.7100" in result_text
    assert "11,080 feet" in result_text
    assert "San Juan" in result_text


@pytest.mark.asyncio
@patch('snotel_mcp_server.api_client.get_station_data')
async def test_get_station_data_tool(mock_get_data, client):
    """Test the get_station_data tool"""
    mock_get_data.return_value = [
        {
            "stationTriplet": "713:CO:SNTL",
            "data": [
                {
                    "stationElement": {"elementCode": "SNWD"},
                    "values": [{"date": "2024-01-01", "value": 45}]
                },
                {
                    "stationElement": {"elementCode": "WTEQ"},
                    "values": [{"date": "2024-01-01", "value": 12.5}]
                }
            ]
        }
    ]
    
    result = await client.call_tool("get_station_data", {
        "station_triplet": "713:CO:SNTL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-01"
    })
    result_text = result[0].text  # Extract text from TextContent
    
    # Now we're testing for raw JSON content
    assert "713:CO:SNTL" in result_text
    assert "2024-01-01" in result_text
    assert "SNWD" in result_text
    assert "WTEQ" in result_text
    assert "stationTriplet" in result_text
    assert "stationElement" in result_text


@pytest.mark.asyncio
@patch('snotel_mcp_server.api_client.get_station_data')
async def test_get_station_data_with_duration(mock_get_data, client):
    """Test the get_station_data tool with duration_name parameter"""
    mock_get_data.return_value = [
        {
            "stationTriplet": "713:CO:SNTL",
            "data": [
                {
                    "stationElement": {"elementCode": "SNWD", "durationName": "HOURLY"},
                    "values": [{"date": "2024-01-01T01:00", "value": 45}]
                }
            ]
        }
    ]
    
    result = await client.call_tool("get_station_data", {
        "station_triplet": "713:CO:SNTL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-01",
        "duration_name": "HOURLY"
    })
    result_text = result[0].text  # Extract text from TextContent
    
    # Verify the API client was called with duration_name
    mock_get_data.assert_called_with(
        "713:CO:SNTL", "2024-01-01", "2024-01-01", None, "HOURLY"
    )
    
    # Verify JSON content
    assert "713:CO:SNTL" in result_text


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """Test that the MCP server is properly initialized"""
    assert mcp is not None
    assert mcp.name == "snotel-mcp-server"


@pytest.mark.asyncio
async def test_all_tools_available(client):
    """Test that all expected tools are available through the client"""
    # List available tools through the client
    tools = await client.list_tools()
    tool_names = [tool.name for tool in tools]
    
    expected_tools = [
        "find_snotel_stations", 
        "get_station_info", 
        "get_station_data", 
        "get_recent_conditions", 
        "analyze_snowpack_trends"
    ]
    
    for tool in expected_tools:
        assert tool in tool_names
    
    # Verify we have exactly the expected number of tools
    assert len(tool_names) == len(expected_tools)


if __name__ == "__main__":
    pytest.main([__file__])