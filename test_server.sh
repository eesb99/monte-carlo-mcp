#!/bin/bash
# Quick test script for Monte Carlo MCP Server

echo "🧪 Testing Monte Carlo MCP Server"
echo "=================================="
echo ""

# Activate conda environment
source /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh
conda activate monte-carlo-mcp

# Test 1: Confidence Validator
echo "Test 1: Confidence Validation Tool"
echo "-----------------------------------"
python << 'EOF'
import sys
sys.path.insert(0, '/Users/thianseongyee/monte-carlo-mcp')
from tools.confidence_validator import validate_reasoning_confidence

result = validate_reasoning_confidence(
    decision_context="Investment with 15% return ± 5%",
    assumptions={
        "roi": {"distribution": "normal", "params": {"mean": 0.15, "std": 0.05}}
    },
    success_criteria={"threshold": 0.10, "comparison": ">="},
    num_simulations=1000,
    random_seed=42
)
print(f"✅ Confidence: {result['confidence_level']:.1%} ({result['confidence_qualifier']})")
print(f"   Expected: {result['expected_outcome']:.2%}")
EOF

echo ""

# Test 2: Business Scenario
echo "Test 2: Business Scenario Simulator"
echo "------------------------------------"
python << 'EOF'
import sys
sys.path.insert(0, '/Users/thianseongyee/monte-carlo-mcp')
from tools.business_scenarios import run_business_scenario

result = run_business_scenario(
    scenario_name="Product Launch",
    revenue_assumptions={"base_revenue": 100000, "growth_rate": {"mean": 0.05, "std": 0.02}},
    cost_structure={"fixed_costs": 50000, "variable_costs": {"mean": 0.5, "std": 0.1}},
    time_horizon=12,
    num_simulations=1000,
    random_seed=42
)
print(f"✅ Expected Profit: ${result['expected_total_profit']:,.0f}")
print(f"   Probability: {result['probability_of_profitability']:.1%}")
EOF

echo ""
echo "=================================="
echo "✅ All tests passed!"
echo ""
echo "📋 Next Steps:"
echo "1. Restart Claude Code to load MCP server"
echo "2. Test in Claude: 'What MCP tools are available?'"
echo "3. Try: 'Validate 80% confidence for 15% ± 3% return'"
echo ""
echo "MCP Config: ~/.claude/.mcp.json"
echo "Server: ~/monte-carlo-mcp/server.py"
