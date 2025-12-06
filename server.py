#!/usr/bin/env python3
"""
Monte Carlo MCP Server
Exposes Monte Carlo simulation tools to Claude Code via Model Context Protocol

Copyright (c) 2025 eesb99@gmail.com
Licensed under the MIT License - see LICENSE file for details

Author: eesb99@gmail.com
Version: 1.0.0
DMCA-Free: Original work - see DMCA_FREE.md
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from tools.confidence_validator import validate_reasoning_confidence, test_assumption_robustness
from tools.business_scenarios import run_business_scenario, run_sensitivity_analysis


# Initialize MCP server
app = Server("monte-carlo-business")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Monte Carlo simulation tools"""
    return [
        Tool(
            name="validate_reasoning_confidence",
            description="""Validates confidence in Claude's recommendation using Monte Carlo simulation.

            Use this when:
            - Making business decisions with uncertain variables
            - Claude wants to quantify confidence in a recommendation
            - Analyzing probability of success given assumptions

            Returns: Confidence level, expected outcome, sensitivity analysis, and key risk factors.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "decision_context": {
                        "type": "string",
                        "description": "Description of the decision being made"
                    },
                    "assumptions": {
                        "type": "object",
                        "description": "Dict of assumptions with uncertainty. Each assumption should have 'distribution' and 'params' keys. Example: {'market_size': {'distribution': 'normal', 'params': {'mean': 500000, 'std': 100000}}",
                        "additionalProperties": True
                    },
                    "success_criteria": {
                        "type": "object",
                        "description": "Definition of success with 'threshold' and 'comparison' (>=, >, <=, <)",
                        "properties": {
                            "threshold": {"type": "number"},
                            "comparison": {"type": "string", "enum": [">=", ">", "<=", "<"]}
                        },
                        "required": ["threshold"]
                    },
                    "num_simulations": {
                        "type": "integer",
                        "description": "Number of Monte Carlo iterations (default: 10000)",
                        "default": 10000
                    },
                    "random_seed": {
                        "type": "integer",
                        "description": "Optional seed for reproducibility"
                    }
                },
                "required": ["decision_context", "assumptions", "success_criteria"]
            }
        ),
        Tool(
            name="test_assumption_robustness",
            description="""Tests robustness of Claude's reasoning by stress-testing critical assumptions.

            Use this when:
            - Need to find breaking points where recommendation changes
            - Testing sensitivity to extreme scenarios
            - Validating stability of conclusions

            Returns: Robustness score, breaking points, and stability analysis.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_answer": {
                        "type": "string",
                        "description": "The original recommendation or answer"
                    },
                    "critical_assumptions": {
                        "type": "array",
                        "description": "List of critical assumptions with name, distribution, and params",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "distribution": {"type": "string"},
                                "params": {"type": "object"}
                            }
                        }
                    },
                    "stress_test_ranges": {
                        "type": "object",
                        "description": "Ranges to stress each variable",
                        "additionalProperties": True
                    },
                    "outcome_function_str": {
                        "type": "string",
                        "description": "Description of how outcome is calculated"
                    },
                    "num_scenarios": {
                        "type": "integer",
                        "description": "Number of stress test scenarios (default: 1000)",
                        "default": 1000
                    }
                },
                "required": ["base_answer", "critical_assumptions", "stress_test_ranges", "outcome_function_str"]
            }
        ),
        Tool(
            name="run_business_scenario",
            description="""Runs comprehensive business scenario Monte Carlo simulation.

            Use this for:
            - Revenue forecasting with uncertainty
            - Profitability analysis
            - Business case validation
            - Strategic planning scenarios

            Returns: Expected profit, probability of success, percentile outcomes, ROI analysis, and sensitivity.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario_name": {
                        "type": "string",
                        "description": "Name or description of the business scenario"
                    },
                    "revenue_assumptions": {
                        "type": "object",
                        "description": "Revenue model with base_revenue, growth_rate {mean, std}, optional churn_rate",
                        "properties": {
                            "base_revenue": {"type": "number"},
                            "growth_rate": {
                                "type": "object",
                                "properties": {
                                    "mean": {"type": "number"},
                                    "std": {"type": "number"}
                                }
                            },
                            "churn_rate": {
                                "type": "object",
                                "properties": {
                                    "mean": {"type": "number"},
                                    "std": {"type": "number"}
                                }
                            },
                            "initial_investment": {"type": "number"}
                        },
                        "required": ["base_revenue"]
                    },
                    "cost_structure": {
                        "type": "object",
                        "description": "Cost model with fixed_costs, variable_costs {mean, std}",
                        "properties": {
                            "fixed_costs": {"type": "number"},
                            "variable_costs": {
                                "type": "object",
                                "properties": {
                                    "mean": {"type": "number"},
                                    "std": {"type": "number"}
                                }
                            }
                        },
                        "required": ["fixed_costs"]
                    },
                    "time_horizon": {
                        "type": "integer",
                        "description": "Number of periods (months/quarters/years)"
                    },
                    "num_simulations": {
                        "type": "integer",
                        "description": "Number of Monte Carlo iterations (default: 10000)",
                        "default": 10000
                    }
                },
                "required": ["scenario_name", "revenue_assumptions", "cost_structure", "time_horizon"]
            }
        ),
        Tool(
            name="run_sensitivity_analysis",
            description="""Performs tornado diagram sensitivity analysis on simulation results.

            Use this to:
            - Identify key drivers of uncertainty
            - Create tornado diagrams
            - Prioritize risk mitigation efforts

            Returns: Tornado diagram data and ranked key drivers.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_simulation_id": {
                        "type": "string",
                        "description": "Reference to base simulation"
                    },
                    "variables_to_test": {
                        "type": "array",
                        "description": "List of variable names to analyze",
                        "items": {"type": "string"}
                    },
                    "variation_range": {
                        "type": "object",
                        "description": "Range for each variable with 'low' and 'high' values",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "low": {"type": "number"},
                                "high": {"type": "number"}
                            }
                        }
                    },
                    "outcome_data": {
                        "type": "object",
                        "description": "Data from base simulation"
                    }
                },
                "required": ["base_simulation_id", "variables_to_test", "variation_range", "outcome_data"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from Claude"""

    try:
        if name == "validate_reasoning_confidence":
            result = validate_reasoning_confidence(
                decision_context=arguments['decision_context'],
                assumptions=arguments['assumptions'],
                success_criteria=arguments['success_criteria'],
                num_simulations=arguments.get('num_simulations', 10000),
                random_seed=arguments.get('random_seed')
            )

            # Format response for Claude
            response = f"""## Confidence Validation Results

**Decision:** {result['decision_context']}

**Confidence Level:** {result['confidence_level']:.1%} ({result['confidence_qualifier']})

**Expected Outcome:** {result['expected_outcome']:,.2f}

**95% Confidence Interval:** [{result['confidence_interval_95'][0]:,.2f}, {result['confidence_interval_95'][1]:,.2f}]

**Key Risk Factors:**
"""
            for risk in result['key_risk_factors']:
                response += f"- {risk['variable']}: {risk['influence']*100:.1f}% influence on outcome\n"

            response += f"\n**Percentile Analysis:**\n"
            response += f"- Pessimistic (P10): {result['percentiles']['P10']:,.2f}\n"
            response += f"- Most Likely (P50): {result['percentiles']['P50']:,.2f}\n"
            response += f"- Optimistic (P90): {result['percentiles']['P90']:,.2f}\n"

            response += f"\n*Based on {result['num_simulations']:,} Monte Carlo simulations*"

            return [TextContent(type="text", text=response)]

        elif name == "test_assumption_robustness":
            result = test_assumption_robustness(
                base_answer=arguments['base_answer'],
                critical_assumptions=arguments['critical_assumptions'],
                stress_test_ranges=arguments['stress_test_ranges'],
                outcome_function_str=arguments['outcome_function_str'],
                num_scenarios=arguments.get('num_scenarios', 1000),
                random_seed=arguments.get('random_seed')
            )

            response = f"""## Assumption Robustness Analysis

**Original Answer:** {result['base_answer']}

**Robustness Score:** {result['robustness_score']:.1%} - {result['confidence_qualifier']}

**Scenarios Tested:** {result['num_scenarios_tested']:,}
- Stable: {result['stress_test_summary']['stable_scenarios']}
- Unstable: {result['stress_test_summary']['unstable_scenarios']}

**Breaking Points (where answer changes):**
"""
            for i, bp in enumerate(result['breaking_points'][:3], 1):
                response += f"\n{i}. Deviation: {bp['deviation_from_base']:+,.2f}\n"
                response += f"   Scenario: {bp['scenario']}\n"

            return [TextContent(type="text", text=response)]

        elif name == "run_business_scenario":
            result = run_business_scenario(
                scenario_name=arguments['scenario_name'],
                revenue_assumptions=arguments['revenue_assumptions'],
                cost_structure=arguments['cost_structure'],
                time_horizon=arguments['time_horizon'],
                num_simulations=arguments.get('num_simulations', 10000),
                random_seed=arguments.get('random_seed')
            )

            response = f"""## Business Scenario Analysis: {result['scenario_name']}

**Time Horizon:** {result['time_horizon']} periods

**Expected Total Profit:** ${result['expected_total_profit']:,.0f}

**Probability of Profitability:** {result['probability_of_profitability']:.1%}

**Outcome Scenarios:**
- Pessimistic (P10): ${result['percentile_outcomes']['pessimistic_P10']:,.0f}
- Most Likely (P50): ${result['percentile_outcomes']['most_likely_P50']:,.0f}
- Optimistic (P90): ${result['percentile_outcomes']['optimistic_P90']:,.0f}

**Risk Assessment:**
- Downside Risk: ${result['risk_metrics']['downside_risk']:,.0f}
- Upside Potential: ${result['risk_metrics']['upside_potential']:,.0f}
- Range: ${result['risk_metrics']['outcome_range']:,.0f}
"""

            if result.get('roi_analysis'):
                roi = result['roi_analysis']
                response += f"\n**ROI Analysis:**\n"
                response += f"- Expected ROI: {roi['mean_roi']:.1%}\n"
                response += f"- Probability of Positive ROI: {roi['prob_positive_roi']:.1%}\n"

            response += f"\n**Interpretation:** {result['interpretation']}\n"
            response += f"\n*Based on {result['num_simulations']:,} Monte Carlo simulations*"

            return [TextContent(type="text", text=response)]

        elif name == "run_sensitivity_analysis":
            result = run_sensitivity_analysis(
                base_simulation_id=arguments['base_simulation_id'],
                variables_to_test=arguments['variables_to_test'],
                variation_range=arguments['variation_range'],
                outcome_data=arguments['outcome_data']
            )

            response = f"""## Sensitivity Analysis

**Base Simulation:** {result['base_simulation_id']}

**Key Drivers (Tornado Diagram):**
"""
            for var, data in result['tornado_diagram_data'].items():
                response += f"- {var}: Impact = {data['impact']:,.2f} (range: {data['low_value']:.2f} to {data['high_value']:.2f})\n"

            response += f"\n**Top 3 Drivers:** {', '.join(result['key_drivers'])}\n"
            response += f"\n{result['interpretation']}"

            return [TextContent(type="text", text=response)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
