# Monte Carlo MCP Server - Project Structure

**Version:** 1.0.0
**Last Updated:** 2025-10-03

---

## 📁 Directory Structure

```
monte-carlo-mcp/
├── .claude/                      # Claude Code project settings
│   └── settings.local.json       # MCP server configuration
│
├── .gitignore                    # Git ignore patterns
├── .mcp.json                     # MCP server definition
│
├── docs/                         # Documentation
│   ├── CODE_REVIEW.md           # Comprehensive code review
│   └── TEST_SUMMARY.md          # Test results and coverage
│
├── data/                         # Data directories
│   ├── cache/                   # Simulation result cache (future)
│   ├── exports/                 # Output files (CSV, PDF, charts)
│   └── input/                   # User input files
│
├── engine/                       # Core Monte Carlo engine
│   ├── __init__.py
│   └── monte_carlo_core.py      # Vectorized NumPy simulation engine
│
├── tools/                        # MCP tools
│   ├── __init__.py
│   ├── confidence_validator.py  # Confidence validation tool
│   └── business_scenarios.py    # Business scenario simulator
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   ├── test_monte_carlo_core.py
│   ├── test_confidence_validator.py
│   └── test_business_scenarios.py
│
├── utils/                        # Utility modules (future expansion)
│   └── __init__.py
│
├── server.py                     # MCP server entry point
├── test_server.sh               # Quick test script
├── README.md                    # Main documentation
└── STRUCTURE.md                 # This file

```

---

## 📄 File Descriptions

### Configuration Files

| File | Purpose |
|------|---------|
| `.gitignore` | Git ignore patterns for Python, testing, IDE files |
| `.mcp.json` | MCP server configuration for Claude Code |
| `.claude/settings.local.json` | Project-specific MCP settings |

### Core Implementation

| File | Purpose | Lines |
|------|---------|-------|
| `server.py` | MCP server entry point with stdio transport | ~400 |
| `engine/monte_carlo_core.py` | Vectorized Monte Carlo engine with NumPy | ~250 |
| `tools/confidence_validator.py` | Confidence validation & robustness testing | ~250 |
| `tools/business_scenarios.py` | Business scenario simulation tools | ~200 |

### Testing

| File | Purpose | Tests |
|------|---------|-------|
| `tests/test_monte_carlo_core.py` | Core engine unit tests | 12 |
| `tests/test_confidence_validator.py` | Validator unit tests | 16 |
| `tests/test_business_scenarios.py` | Scenario unit tests | 19 |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation, setup, usage examples |
| `docs/CODE_REVIEW.md` | Comprehensive code quality review |
| `docs/TEST_SUMMARY.md` | Test results and coverage report |
| `STRUCTURE.md` | Project structure overview (this file) |

### Scripts

| File | Purpose |
|------|---------|
| `test_server.sh` | Quick test script for validating installation |

---

## 🔧 Component Dependencies

```
server.py
    ├── tools/confidence_validator.py
    │   └── engine/monte_carlo_core.py
    │
    └── tools/business_scenarios.py
        └── engine/monte_carlo_core.py
```

---

## 📦 External Dependencies

**Production:**
- `numpy` >= 2.3.3 (numerical computation)
- `scipy` >= 1.16.1 (statistical distributions)
- `mcp` >= 1.16.0 (Model Context Protocol SDK)
- `anthropic` (Claude API client)
- `openpyxl` (Excel file support)
- `sqlalchemy` (database support - future)

**Development:**
- `pytest` >= 8.4.2 (testing framework)
- `pytest-cov` >= 7.0.0 (coverage reporting)

---

## 🚀 Quick Reference

### Run Tests
```bash
cd ~/monte-carlo-mcp
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate monte-carlo-mcp
python -m pytest tests/ -v
```

### Test Server
```bash
cd ~/monte-carlo-mcp
./test_server.sh
```

### Start MCP Server
```bash
# Automatically started by Claude Code
# Configuration: ~/.claude/.mcp.json or .mcp.json
```

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~1,100 |
| **Test Coverage** | 98% |
| **Test Count** | 50 |
| **Modules** | 4 |
| **Tools** | 4 |
| **Distributions** | 7 |

---

## 🔄 Version History

### v1.0.0 (2025-10-03)
- ✅ Initial release
- ✅ 4 MCP tools implemented
- ✅ 98% test coverage
- ✅ Production-ready
- ✅ Documentation complete

---

## 📝 Notes

### Data Directories
- `data/cache/` - Future: SQLite cache for simulation results
- `data/exports/` - Future: Chart exports, PDF reports
- `data/input/` - User CSV/Excel files for simulation input

### Utils Directory
- Reserved for future utility modules
- Potential: visualization, caching, data loaders

### Clean Development
- `.gitignore` prevents pollution
- No `__pycache__` tracked
- No `.pytest_cache` tracked
- Clean production-ready structure

---

**Maintained by:** Monte Carlo MCP Development Team
**License:** MIT
**Status:** Production Ready ✅
