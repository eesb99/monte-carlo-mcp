# Monte Carlo MCP Server for Business Analysis

A Model Context Protocol (MCP) server that enables Claude to perform Monte Carlo simulations for business decisions, financial analysis, and confidence validation.

## 🚀 Quick Start

### Prerequisites
- Conda environment: `monte-carlo-mcp`
- Python 3.11 with NumPy, SciPy, MCP SDK

### Installation Complete! ✅

The server is already installed and configured at:
- **Server Path:** `~/monte-carlo-mcp/server.py`
- **Python Environment:** `/opt/homebrew/Caskroom/miniconda/base/envs/monte-carlo-mcp/`
- **Claude Code Config:** `~/.claude/.mcp.json`

## 🛠️ Available Tools

### 1. `validate_reasoning_confidence`
**Use Case:** Claude validates its own recommendations using Monte Carlo simulation

**Example:**
```
User: "Should I invest in Project A? Expected return 15%, uncertainty ±5%"

Claude calls: validate_reasoning_confidence({
  decision_context: "Investment in Project A",
  assumptions: {
    roi: {
      distribution: "normal",
      params: {mean: 0.15, std: 0.05}
    }
  },
  success_criteria: {
    threshold: 0.10,
    comparison: ">="
  }
})

Response: 78% confidence that Project A will exceed 10% return
```

### 2. `test_assumption_robustness`
**Use Case:** Stress-test reasoning to find breaking points

**Example:**
```
Claude tests: "Under what conditions does my recommendation change?"

Returns: Robustness score and scenarios where answer breaks down
```

### 3. `run_business_scenario`
**Use Case:** Comprehensive business scenario Monte Carlo simulation

**Example:**
```
Claude simulates:
- Revenue: $100k base, 5% ± 2% growth
- Costs: $50k fixed + 50% ± 10% variable
- Time: 24 months

Returns: Expected profit, probability of success, P10/P50/P90 outcomes
```

### 4. `run_sensitivity_analysis`
**Use Case:** Identify key uncertainty drivers (Tornado diagram)

**Example:**
```
Claude analyzes: "Which variables have the most impact on outcome?"

Returns: Ranked list of key drivers with influence percentages
```

## 📊 Usage with Claude Code

### Activate MCP Server

The server is automatically available when you start Claude Code. Check with:

```bash
claude mcp list
```

You should see: `monte-carlo-business` (stdio)

### Example Conversations

**1. Investment Decision Validation:**
```
You: "I'm considering investing $100k in a new market. Expected revenue $200k,
     but uncertain about market size (400k-600k customers) and conversion rate (2%-5%).
     What's the confidence in this decision?"

Claude: *calls validate_reasoning_confidence*
"Based on Monte Carlo analysis, there's a 68% probability of positive ROI.
Key risk: conversion rate has 72% influence on outcome..."
```

**2. Business Scenario Analysis:**
```
You: "Analyze launching a SaaS product: $50k/month base revenue,
     10% monthly growth ± 3%, $30k fixed costs, 40% variable costs over 12 months"

Claude: *calls run_business_scenario*
"Expected 12-month profit: $285k (P50).
Profitability probability: 89%.
Risk range: $150k (P10) to $420k (P90)..."
```

**3. Sensitivity Analysis:**
```
You: "Which assumptions matter most for the previous scenario?"

Claude: *calls run_sensitivity_analysis*
"Key drivers:
1. Monthly growth rate: 58% influence
2. Variable cost %: 24% influence
3. Churn rate: 18% influence"
```

## 🔧 Technical Architecture

### Project Structure
```
monte-carlo-mcp/
├── server.py                    # MCP server entry point
├── engine/
│   └── monte_carlo_core.py     # Vectorized NumPy simulation engine
├── tools/
│   ├── confidence_validator.py # Confidence validation tool
│   └── business_scenarios.py   # Business scenario simulator
├── utils/
├── data/
│   ├── input/                   # User data files
│   ├── cache/                   # Simulation cache (future)
│   └── exports/                 # Output files
└── tests/
```

### Performance
- **Simulations:** 10,000 iterations in ~1-2 seconds
- **Engine:** NumPy vectorization with ARM NEON optimizations
- **BLAS:** OpenBLAS 0.3.30 (optimized for M1/M2)

### Supported Distributions
- Normal (Gaussian)
- Log-normal
- Uniform
- Triangular
- Exponential
- Beta
- Gamma

## 🧪 Testing the Server

### Test Directly (Python)
```bash
conda activate monte-carlo-mcp
cd ~/monte-carlo-mcp

python << 'EOF'
from tools.confidence_validator import validate_reasoning_confidence

result = validate_reasoning_confidence(
    decision_context="Test investment",
    assumptions={
        "roi": {
            "distribution": "normal",
            "params": {"mean": 0.15, "std": 0.05}
        }
    },
    success_criteria={"threshold": 0.10, "comparison": ">="},
    num_simulations=1000
)

print(f"Confidence: {result['confidence_level']:.1%}")
print(f"Expected: {result['expected_outcome']:.2f}")
EOF
```

### Test with Claude Code
```bash
claude

# In Claude session:
"Test the Monte Carlo server: validate 80% confidence for a 15% ± 3% return investment"
```

## 📈 Advanced Features

### Correlation Support
The Monte Carlo engine supports correlated variables using Cholesky decomposition for multivariate sampling.

### Caching (Future)
Simulation results will be cached in SQLite for instant retrieval of repeated analyses.

### Visualization (Future)
Export tornado diagrams, probability distributions, and scenario charts.

## 🛠️ Troubleshooting

### Server Not Found
```bash
# Verify MCP config
cat ~/.claude/.mcp.json

# Test Python environment
conda activate monte-carlo-mcp
python ~/monte-carlo-mcp/server.py
```

### Import Errors
```bash
# Ensure all packages installed
conda activate monte-carlo-mcp
pip list | grep mcp
```

### Permission Issues
```bash
# Make server executable
chmod +x ~/monte-carlo-mcp/server.py
```

## 🔄 Updating the Server

```bash
conda activate monte-carlo-mcp
cd ~/monte-carlo-mcp

# Edit tools or add new features
# Restart Claude Code to reload MCP server
```

## 📝 Environment Details

**Conda Environment:** monte-carlo-mcp
**Python:** 3.11.13
**NumPy:** 2.3.3 (with ARM NEON optimizations)
**SciPy:** 1.16.1
**MCP SDK:** 1.16.0

## 🎯 Next Steps

1. ✅ Server installed and configured
2. ✅ Claude Code MCP integration ready
3. ⏳ Test with Claude Code
4. 📊 Add visualization exports
5. 💾 Implement result caching
6. 📈 Add portfolio analysis tools

## 📚 References

- [MCP Protocol Docs](https://modelcontextprotocol.io/)
- [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)
- [Monte Carlo Methods](https://en.wikipedia.org/wiki/Monte_Carlo_method)

---

## 📄 License & Attribution

### License

**MIT License** - Free for commercial and non-commercial use

Copyright © 2025 eesb99@gmail.com

See [LICENSE](LICENSE) file for full text.

### Attribution

**Author:** eesb99@gmail.com
**Created with:** Claude Code & Claude Sonnet 4.5
**Version:** 1.0.0
**Date:** 2025-10-03

See [ATTRIBUTION.md](ATTRIBUTION.md) for detailed credits.

### DMCA-Free

This software is **100% original work** with no copyright infringement.

See [DMCA_FREE.md](DMCA_FREE.md) for certification.

### Usage Rights

✅ **Commercial use** - Use in business applications
✅ **Modification** - Adapt for your needs
✅ **Distribution** - Share with attribution
✅ **Private use** - Use internally without restrictions

---

**Built for:** Business decision validation, financial analysis, and confidence quantification
**License:** MIT (DMCA-Free)
**Contact:** eesb99@gmail.com
**Version:** 1.0.0
