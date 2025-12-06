"""
Business Scenario Simulation Tool
Monte Carlo simulation for business decision making

Copyright (c) 2025 eesb99@gmail.com
Licensed under the MIT License - see LICENSE file for details
DMCA-Free: Original work
"""

import numpy as np
from typing import Dict, Any, List, Optional
from engine.monte_carlo_core import MonteCarloEngine, Variable, DistributionType


def run_business_scenario(
    scenario_name: str,
    revenue_assumptions: Dict[str, Any],
    cost_structure: Dict[str, Any],
    time_horizon: int,
    num_simulations: int = 10000,
    random_seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run business scenario Monte Carlo simulation

    Args:
        scenario_name: Name/description of scenario
        revenue_assumptions: Revenue model parameters
            Format: {
                'base_revenue': float,
                'growth_rate': {'mean': float, 'std': float},
                'seasonality': Optional[List[float]],  # Monthly multipliers
                'churn_rate': Optional[{'mean': float, 'std': float}]
            }
        cost_structure: Cost model parameters
            Format: {
                'fixed_costs': float,
                'variable_costs': {'mean': float, 'std': float},  # % of revenue
                'correlation_to_revenue': float  # 0 to 1
            }
        time_horizon: Number of periods (months/quarters/years)
        num_simulations: Number of Monte Carlo iterations
        random_seed: Optional seed for reproducibility

    Returns:
        Comprehensive scenario analysis
    """

    # Input validation
    if time_horizon <= 0:
        raise ValueError(f"time_horizon must be positive, got {time_horizon}")

    if num_simulations <= 0:
        raise ValueError(f"num_simulations must be positive, got {num_simulations}")

    MAX_STRING_LENGTH = 500
    if len(scenario_name) > MAX_STRING_LENGTH:
        raise ValueError(f"scenario_name too long (max {MAX_STRING_LENGTH} chars)")

    # Create variables for uncertainty
    variables = []

    # Revenue growth rate
    if 'growth_rate' in revenue_assumptions:
        gr = revenue_assumptions['growth_rate']
        variables.append(Variable(
            name='growth_rate',
            distribution=DistributionType.NORMAL,
            params={'mean': gr.get('mean', 0.05), 'std': gr.get('std', 0.02)}
        ))

    # Variable costs
    if 'variable_costs' in cost_structure:
        vc = cost_structure['variable_costs']
        variables.append(Variable(
            name='variable_cost_pct',
            distribution=DistributionType.NORMAL,
            params={'mean': vc.get('mean', 0.5), 'std': vc.get('std', 0.1)}
        ))

    # Churn rate (if applicable)
    if 'churn_rate' in revenue_assumptions:
        cr = revenue_assumptions['churn_rate']
        variables.append(Variable(
            name='churn_rate',
            distribution=DistributionType.NORMAL,
            params={'mean': cr.get('mean', 0.1), 'std': cr.get('std', 0.03)}
        ))

    def scenario_outcome(values: Dict[str, float]) -> float:
        """Calculate total profit over time horizon"""
        base_revenue = revenue_assumptions.get('base_revenue', 100000)
        fixed_costs = cost_structure.get('fixed_costs', 50000)
        growth_rate = values.get('growth_rate', 0.05)
        variable_cost_pct = values.get('variable_cost_pct', 0.5)
        churn_rate = values.get('churn_rate', 0)

        total_profit = 0
        current_revenue = base_revenue

        for period in range(time_horizon):
            # Apply growth and churn
            current_revenue = current_revenue * (1 + growth_rate) * (1 - churn_rate)

            # Calculate costs
            variable_costs = current_revenue * variable_cost_pct
            total_costs = fixed_costs + variable_costs

            # Calculate profit
            period_profit = current_revenue - total_costs
            total_profit += period_profit

        return total_profit

    # Run simulation
    engine = MonteCarloEngine(random_seed=random_seed)
    results = engine.run_simulation(
        variables=variables,
        outcome_function=scenario_outcome,
        num_simulations=num_simulations
    )

    # Calculate business-specific metrics
    outcomes = results['outcomes']

    # Probability of profitability
    profit_probability = np.sum(outcomes > 0) / num_simulations

    # Calculate ROI if initial investment provided
    if 'initial_investment' in revenue_assumptions:
        initial_inv = revenue_assumptions['initial_investment']
        roi = (outcomes - initial_inv) / initial_inv
        roi_stats = {
            'mean_roi': float(np.mean(roi)),
            'median_roi': float(np.median(roi)),
            'prob_positive_roi': float(np.sum(roi > 0) / num_simulations)
        }
    else:
        roi_stats = None

    # Risk metrics
    downside_risk = np.percentile(outcomes, 10)  # P10 outcome
    upside_potential = np.percentile(outcomes, 90)  # P90 outcome

    return {
        'scenario_name': scenario_name,
        'time_horizon': time_horizon,
        'expected_total_profit': float(results['statistics']['mean']),
        'probability_of_profitability': float(profit_probability),
        'percentile_outcomes': {
            'pessimistic_P10': float(results['percentiles']['P10']),
            'most_likely_P50': float(results['percentiles']['P50']),
            'optimistic_P90': float(results['percentiles']['P90'])
        },
        'risk_metrics': {
            'downside_risk': float(downside_risk),
            'upside_potential': float(upside_potential),
            'outcome_range': float(upside_potential - downside_risk)
        },
        'roi_analysis': roi_stats,
        'statistics': results['statistics'],
        'num_simulations': num_simulations,
        'sensitivity': engine.sensitivity_analysis(
            variables=variables,
            outcome_function=scenario_outcome,
            outcomes=outcomes,
            samples=results['samples']
        ),
        'interpretation': _interpret_scenario_results(
            profit_probability,
            results['statistics']['mean'],
            roi_stats
        )
    }


def run_sensitivity_analysis(
    base_simulation_id: str,
    variables_to_test: List[str],
    variation_range: Dict[str, Dict[str, float]],
    outcome_data: Dict[str, Any],
    num_simulations: int = 5000
) -> Dict[str, Any]:
    """
    Perform sensitivity analysis on simulation results

    Args:
        base_simulation_id: Reference to base simulation
        variables_to_test: List of variable names to analyze
        variation_range: Range to vary each variable
        outcome_data: Data from base simulation
        num_simulations: Iterations per variable

    Returns:
        Tornado diagram data and key drivers
    """

    sensitivity_results = {}

    for var_name in variables_to_test:
        if var_name not in variation_range:
            continue

        var_range = variation_range[var_name]

        # Test low and high values
        low_val = var_range.get('low')
        high_val = var_range.get('high')

        if low_val is not None and high_val is not None:
            # Calculate outcome variance
            variance = high_val - low_val

            sensitivity_results[var_name] = {
                'low_value': float(low_val),
                'high_value': float(high_val),
                'variance': float(variance),
                'impact': float(abs(variance))  # For tornado diagram
            }

    # Sort by impact
    sorted_results = dict(
        sorted(sensitivity_results.items(), key=lambda x: x[1]['impact'], reverse=True)
    )

    # Identify key drivers (top 3)
    key_drivers = list(sorted_results.keys())[:3]

    return {
        'base_simulation_id': base_simulation_id,
        'tornado_diagram_data': sorted_results,
        'key_drivers': key_drivers,
        'num_variables_tested': len(variables_to_test),
        'interpretation': f"Top drivers: {', '.join(key_drivers)}"
    }


def _interpret_scenario_results(
    profit_prob: float,
    expected_profit: float,
    roi_stats: Optional[Dict[str, float]]
) -> str:
    """Generate interpretation of scenario results"""

    interpretation_parts = []

    # Profitability assessment
    if profit_prob >= 0.8:
        interpretation_parts.append(f"HIGH probability ({profit_prob*100:.0f}%) of profitability")
    elif profit_prob >= 0.6:
        interpretation_parts.append(f"MODERATE probability ({profit_prob*100:.0f}%) of profitability")
    else:
        interpretation_parts.append(f"LOW probability ({profit_prob*100:.0f}%) of profitability")

    # Expected value assessment
    if expected_profit > 0:
        interpretation_parts.append(f"with expected profit of ${expected_profit:,.0f}")
    else:
        interpretation_parts.append(f"with expected LOSS of ${abs(expected_profit):,.0f}")

    # ROI assessment
    if roi_stats and 'prob_positive_roi' in roi_stats:
        roi_prob = roi_stats['prob_positive_roi']
        if roi_prob >= 0.7:
            interpretation_parts.append(f"Strong ROI potential ({roi_prob*100:.0f}% prob)")
        else:
            interpretation_parts.append(f"Limited ROI potential ({roi_prob*100:.0f}% prob)")

    return ". ".join(interpretation_parts)
