# SNOTEL MCP Server

A Model Context Protocol (MCP) server built with FastMCP for accessing USDA SNOTEL (SNOwpack TELemetry) weather and snow data through the AWDB (Air and Water Database) REST API.

This server provides AI assistants like Claude with access to real-time and historical snow conditions, weather data, and snowpack analysis from over 800 SNOTEL stations across the western United States.

## Features

### 🏔️ Station Discovery
- **Find by State**: Get all SNOTEL stations in any state
- **Find by Location**: Search for stations within a radius of coordinates
- **Station Details**: Access comprehensive station metadata

### 📊 Data Access
- **Historical Data**: Retrieve snow depth, SWE, temperature, and precipitation
- **Recent Conditions**: Get latest readings and recent trends
- **Custom Date Ranges**: Query any time period with daily resolution

### 📈 Analysis Tools
- **Snowpack Trends**: Analyze peak conditions and seasonal patterns
- **Storm Tracking**: Identify snowfall events and accumulations
- **Statistical Summaries**: Calculate averages, maximums, and snow day counts

## Quick Start

### Prerequisites
- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/example/snotel-mcp-server.git
cd snotel-mcp-server

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Or install development dependencies
uv pip install -e ".[dev]"
```

### Running the Server

FastMCP handles all transport configuration automatically:

```bash
# Run with default stdio transport
python -m snotel_mcp_server

# Or if installed
snotel-mcp-server
```

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "snotel": {
      "command": "python",
      "args": ["-m", "snotel_mcp_server"],
      "cwd": "/path/to/snotel-mcp-server"
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcpServers": {
    "snotel": {
      "command": "snotel-mcp-server"
    }
  }
}
```

## Available Tools

### `find_snotel_stations`
Find SNOTEL stations by state or geographic location.

**Parameters:**
- `state` (optional): State abbreviation (e.g., "CO", "MT")
- `latitude` (optional): Latitude for location search
- `longitude` (optional): Longitude for location search  
- `radius_miles` (optional): Search radius in miles (default: 50)
- `network` (optional): Network type (default: "SNTL")

**Examples:**
```
Find all SNOTEL stations in Colorado
Find SNOTEL stations within 25 miles of Aspen, Colorado (39.1911, -106.8175)
```

### `get_station_info`
Get detailed information about a specific SNOTEL station.

**Parameters:**
- `station_triplet` (required): Station identifier (e.g., "713:CO:SNTL")

**Example:**
```
Get information about Red Mountain Pass station (713:CO:SNTL)
```

### `get_station_data`
Retrieve raw snow and weather data from a station in JSON format.

**Parameters:**
- `station_triplet` (required): Station identifier
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `elements` (optional): Data types ["SNWD", "WTEQ", "TOBS", "PREC"]
- `duration_name` (optional): Duration of measurements ["DAILY", "HOURLY", "MONTHLY"]

**Returns:** Raw JSON data from the SNOTEL API

**Examples:**
```
Get raw JSON data from Red Mountain Pass for March 2025
Get hourly temperature data from Wolf Creek Pass for a specific day
Get monthly averages for a station over a year
```

### `get_recent_conditions`
Get recent conditions from a station (last 30 days by default).

**Parameters:**
- `station_triplet` (required): Station identifier
- `days` (optional): Number of recent days (default: 30)

**Example:**
```
What are current conditions at Loveland Pass?
Show me the last 14 days of data from Independence Pass
```

### `analyze_snowpack_trends`
Analyze snowpack trends and calculate statistics for a time period.

**Parameters:**
- `station_triplet` (required): Station identifier
- `start_date` (required): Analysis start date
- `end_date` (required): Analysis end date

**Examples:**
```
Analyze snowpack trends at Wolf Creek for the 2024-2025 season
Compare peak snow conditions between March 2024 and March 2025 at Red Mountain Pass
```

## Example Conversations

### Finding Stations
```
User: "Find SNOTEL stations near Aspen, Colorado"
Assistant: I'll find SNOTEL stations near Aspen for you.

[Uses find_snotel_stations with coordinates for Aspen]

Found 5 SNOTEL stations within 50 miles of Aspen:
• Independence Pass (589:CO:SNTL) - 12,095 ft
• Grizzly Peak (457:CO:SNTL) - 11,900 ft  
• Schofield Pass (737:CO:SNTL) - 10,707 ft
...
```

### Getting Current Conditions
```
User: "What are current snow conditions at Red Mountain Pass?"
Assistant: I'll check the current conditions at Red Mountain Pass.

[Uses get_recent_conditions for station 713:CO:SNTL]

Recent Conditions: Red Mountain Pass (713:CO:SNTL)
Latest Reading: 2025-05-26
• Snow Depth: 21.0"
• Snow Water Equivalent: 8.2"
• Temperature: 29.3°F
```

### Analyzing Trends
```
User: "How did March 2025 compare to typical March conditions at Wolf Creek?"
Assistant: I'll analyze March 2025 snowpack trends at Wolf Creek.

[Uses analyze_snowpack_trends for March 2025]

March 2025 Analysis:
• Peak Depth: 156" on March 15th
• Total New Snow: 67"
• Snow Days: 12
• Above average snowfall for March
```

## Data Elements

The server supports these common SNOTEL measurements:

- **SNWD**: Snow depth (inches)
- **WTEQ**: Snow water equivalent (inches)  
- **TOBS**: Observed air temperature (°F)
- **PREC**: Precipitation increment (inches)
- **TMAX**: Maximum air temperature (°F)
- **TMIN**: Minimum air temperature (°F)

## API Reference

The server connects to the USDA AWDB REST API:
- **Base URL**: `https://wcc.sc.egov.usda.gov/awdbRestApi`
- **Documentation**: [Swagger UI](https://wcc.sc.egov.usda.gov/awdbRestApi/swagger-ui/index.html)
- **Rate Limits**: Be respectful with API usage

## Development

### Project Structure
```
snotel-mcp-server/
├── src/
│   └── snotel_mcp_server/
│       ├── __init__.py     # FastMCP server implementation
│       └── __main__.py     # Module entry point
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
├── README.md               # This file
├── tests/                  # Test files
│   └── test_tools.py       # MCP tool tests
└── examples/               # Usage examples
    └── example_usage.py    # Example usage
```

### Running Tests
```bash
# Install development dependencies
uv pip install -e ".[dev]"
# Or install from requirements.txt
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage (requires pytest-cov)
pytest --cov=src/snotel_mcp_server tests/

# Run specific test file
pytest tests/test_tools.py -v
```

### Code Quality
```bash
# Format code
black snotel_mcp_server.py
isort snotel_mcp_server.py

# Lint code
ruff check snotel_mcp_server.py

# Type checking
mypy snotel_mcp_server.py
```

## Configuration

### Environment Variables
- `AWDB_API_BASE`: Override default API base URL
- `AWDB_TIMEOUT`: Request timeout in seconds (default: 30)

### Logging
The server supports configurable logging levels. Set the log level via environment variable:

```bash
# Show API requests and responses (recommended for debugging)
LOGLEVEL=INFO python -m snotel_mcp_server

# Show detailed debug information
LOGLEVEL=DEBUG python -m snotel_mcp_server

# Show only warnings and errors (default)
LOGLEVEL=WARNING python -m snotel_mcp_server
```

**Log Levels:**
- `DEBUG`: Most verbose, shows all internal operations
- `INFO`: Shows API requests, responses, and general operations
- `WARNING`: Shows only warnings and errors (default)
- `ERROR`: Shows only errors

## Troubleshooting

### Common Issues

**Connection Errors**
- Check internet connectivity to USDA servers
- Verify API endpoint is accessible
- Check for proxy/firewall restrictions

**No Data Returned**
- Verify station triplet format (e.g., "713:CO:SNTL")  
- Check date ranges are valid
- Some stations may have data gaps

**Station Not Found**
- Use `find_snotel_stations` to verify station exists
- Check state abbreviation is correct
- Ensure station is active

### Debug Mode
Enable detailed logging to see all API requests:
```bash
LOGLEVEL=INFO python -m snotel_mcp_server
```

For maximum verbosity:
```bash
LOGLEVEL=DEBUG python -m snotel_mcp_server
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Model Context Protocol](https://github.com/modelcontextprotocol) - The MCP specification and SDKs
- [Claude Desktop](https://claude.ai/download) - AI assistant with MCP support
- [USDA SNOTEL](https://www.wcc.nrcs.usda.gov/snow/) - Official SNOTEL program information

## Acknowledgments

- USDA Natural Resources Conservation Service for providing the SNOTEL network and API
- Anthropic for creating the Model Context Protocol
- The open source community for the underlying tools and libraries

---

**Happy Snow Tracking! 🎿❄️**
