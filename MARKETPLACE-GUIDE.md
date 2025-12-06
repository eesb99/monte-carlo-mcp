# Monte Carlo MCP Marketplace Plugin Guide

## Overview

This is the marketplace plugin version of Monte Carlo MCP, designed for easy installation and distribution through Claude Code's plugin marketplace system.

## Structure

```
monte-carlo-mcp-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Plugin metadata and configuration
├── run.sh                     # Entry point script (auto-setup + server launch)
├── setup.sh                   # Virtual environment setup script
├── requirements.txt           # Python dependencies
├── server.py                  # MCP server implementation
├── engine/                    # Monte Carlo simulation engine
├── tools/                     # Tool implementations
├── utils/                     # Utility modules
├── data/                      # Data directories (auto-created)
├── tests/                     # Test suite
└── docs/                      # Documentation
```

## Installation

### Automatic Setup

The plugin uses automatic setup via `run.sh`:

1. On first run, `run.sh` detects missing venv
2. Calls `setup.sh` to create venv and install dependencies
3. Launches server with venv Python

### Manual Setup

If needed, you can run setup manually:

```bash
cd ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace
./setup.sh
```

## Environment Variables

The plugin uses the following environment variables:

- `DATA_DIR`: Points to `${CLAUDE_PLUGIN_ROOT}/data` (portable)
- `CACHE_ENABLED`: Set to "true" for caching simulation results
- `MAX_SIMULATIONS`: Maximum number of simulations (default: 50000)

These are configured in `.claude-plugin/marketplace.json` and automatically resolved at runtime.

## Dependencies

- Python 3.11+
- mcp >= 1.16.0
- numpy >= 2.3.0
- scipy >= 1.16.0
- pytest >= 7.0.0 (for testing)

## Testing

Run the test suite:

```bash
cd ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace
./venv/bin/python -m pytest tests/ -v
```

Expected: All tests pass, 98% coverage maintained.

## Tools Provided

The plugin exposes 4 Monte Carlo simulation tools:

1. **validate_reasoning_confidence** - Quantify confidence in recommendations
2. **test_assumption_robustness** - Stress-test assumptions to find breaking points
3. **run_business_scenario** - Comprehensive business Monte Carlo simulation
4. **run_sensitivity_analysis** - Tornado diagram analysis of key drivers

## Migration from Manual Installation

If migrating from manual conda installation:

1. Backup your current installation
2. Remove manual config from `.mcp.json`
3. Restart Claude Code
4. Plugin will auto-setup on first use

## Troubleshooting

### Venv Creation Fails

Ensure Python 3.11+ is installed:

```bash
python3 --version
```

### Dependencies Fail to Install

Try upgrading pip first:

```bash
./venv/bin/pip install --upgrade pip
```

### MCP Shows "Capabilities: none"

Check for import errors:

```bash
./venv/bin/python server.py
```

## License

MIT License - See LICENSE file for details.

## Author

THIAN SEONG YEE
eesb99@gmail.com
