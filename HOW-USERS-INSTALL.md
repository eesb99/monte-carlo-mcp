# How to Install Monte Carlo MCP Plugin

## Quick Start

Monte Carlo MCP is a Claude Code plugin that provides 4 specialized tools for Monte Carlo simulation and business risk analysis.

## Installation Methods

### Method 1: Marketplace Installation (Recommended)

**Coming soon:** When published to Claude Code marketplace:

```bash
claude plugin marketplace add eesb99/monte-carlo-mcp
claude plugin install monte-carlo-business
```

### Method 2: Local Plugin Installation

For testing or local development:

1. **Copy plugin to Claude Code plugins directory:**
   ```bash
   cp -r monte-carlo-mcp-marketplace ~/.claude/plugins/marketplaces/
   ```

2. **Restart Claude Code**
   - Close and reopen Claude Code
   - Plugin will auto-setup on first use

3. **Verify installation:**
   - Use `/mcp` command to check status
   - Should show: `monte-carlo-business (connected, 4 tools)`

## What Gets Installed

When you install the plugin, it will:

1. Create a Python virtual environment (`venv/`)
2. Install required dependencies:
   - mcp >= 1.16.0
   - numpy >= 2.3.0
   - scipy >= 1.16.0
   - pytest >= 7.0.0
3. Create data directories:
   - `data/input/` - User data files
   - `data/cache/` - Simulation cache
   - `data/exports/` - Output files

## System Requirements

- macOS, Linux, or Windows with WSL
- Python 3.11 or higher
- ~500MB disk space
- Internet connection (for initial dependency installation)

## Available Tools

After installation, you'll have access to 4 tools:

1. **validate_reasoning_confidence**
   - Quantify confidence in business recommendations
   - Run 10,000+ Monte Carlo simulations in <2 seconds
   - Get probability of success, expected outcomes, sensitivity analysis

2. **test_assumption_robustness**
   - Stress-test critical assumptions
   - Find breaking points where recommendations change
   - Identify key risk factors

3. **run_business_scenario**
   - Comprehensive business scenario analysis
   - Revenue forecasting with uncertainty
   - Profitability analysis and ROI calculations

4. **run_sensitivity_analysis**
   - Tornado diagram sensitivity analysis
   - Identify key drivers of uncertainty
   - Prioritize risk mitigation efforts

## Usage Example

```python
# Example: Validate confidence in a business decision
result = mcp.validate_reasoning_confidence(
    decision_context="Should we invest $500K in new product line?",
    assumptions={
        "market_size": {"distribution": "normal", "params": {"mean": 500000, "std": 100000}},
        "conversion_rate": {"distribution": "beta", "params": {"a": 8, "b": 92}},
        "unit_margin": {"distribution": "triangular", "params": {"low": 15, "mode": 20, "high": 25}}
    },
    success_criteria={"threshold": 0, "comparison": ">="},
    num_simulations=10000
)

print(f"Confidence: {result['confidence_level']:.1%}")
print(f"Expected profit: ${result['expected_outcome']:,.0f}")
```

## Verification

After installation, verify everything works:

```bash
cd ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace
./venv/bin/python -m pytest tests/ -v
```

All tests should pass.

## Troubleshooting

### Plugin doesn't appear in Claude Code

1. Check plugin directory: `ls ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace/`
2. Verify `run.sh` is executable: `chmod +x ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace/run.sh`
3. Restart Claude Code completely

### Dependencies fail to install

1. Check Python version: `python3 --version` (need 3.11+)
2. Try manual setup: `cd ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace && ./setup.sh`
3. Check for error messages in setup output

### Tools return errors

1. Test server manually: `./venv/bin/python server.py`
2. Check for import errors or missing dependencies
3. Verify data directories exist: `ls data/`

## Uninstallation

To remove the plugin:

```bash
rm -rf ~/.claude/plugins/marketplaces/monte-carlo-mcp-marketplace
```

Then restart Claude Code.

## Support

For issues or questions:
- Email: eesb99@gmail.com
- Check MARKETPLACE-GUIDE.md for detailed documentation
- Review README.md for tool usage examples

## License

MIT License - Free to use for personal and commercial projects.
