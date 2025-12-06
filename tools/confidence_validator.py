"""
Confidence Validation Tool
Validates Claude's reasoning confidence using Monte Carlo simulation

Copyright (c) 2025 eesb99@gmail.com
Licensed under the MIT License - see LICENSE file for details
DMCA-Free: Original work
"""

import numpy as np
from typing import Dict, Any, List, Optional
from engine.monte_carlo_core import MonteCarloEngine, Variable, DistributionType, create_variable_from_dict


def validate_reasoning_confidence(
    decision_context: str,
    assumptions: Dict[str, Any],
    success_criteria: Dict[str, Any],
    num_simulations: int = 10000,
    random_seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validates confidence in a recommendation using Monte Carlo simulation

    Args:
        decision_context: Description of the decision being made
        assumptions: Dictionary of assumptions with uncertainty ranges
            Format: {
                'variable_name': {
                    'value': <base value>,
                    'distribution': 'normal|uniform|triangular',
                    'params': {distribution-specific parameters}
                }
            }
        success_criteria: Definition of success
            Format: {
                'metric': 'revenue|profit|roi|etc',
                'threshold': <minimum acceptable value>,
                'comparison': '>|<|>=|<='
            }
        num_simulations: Number of Monte Carlo iterations
        random_seed: Optional seed for reproducibility

    Returns:
        Dictionary with confidence analysis
    """

    # Input validation
    MAX_STRING_LENGTH = 500
    MAX_ASSUMPTIONS = 20

    if len(decision_context) > MAX_STRING_LENGTH:
        raise ValueError(f"decision_context too long (max {MAX_STRING_LENGTH} chars)")

    if len(assumptions) > MAX_ASSUMPTIONS:
        raise ValueError(f"Too many assumptions (max {MAX_ASSUMPTIONS})")

    if num_simulations <= 0:
        raise ValueError(f"num_simulations must be positive, got {num_simulations}")

    if num_simulations > 100000:
        raise ValueError(f"num_simulations too large (max 100,000), got {num_simulations}")

    # Parse assumptions into Variable objects
    variables = []
    for name, assumption in assumptions.items():
        if 'distribution' in assumption and 'params' in assumption:
            var = Variable(
                name=name,
                distribution=DistributionType(assumption['distribution']),
                params=assumption['params']
            )
            variables.append(var)

    # Define outcome function based on decision context
    def outcome_function(values: Dict[str, float]) -> float:
        """
        Calculate outcome based on variable values
        This is a simplified model - can be customized per use case
        """
        # Example: revenue = market_size * conversion_rate * price
        if 'market_size' in values and 'conversion_rate' in values:
            if 'price' in values:
                return values['market_size'] * values['conversion_rate'] * values['price']
            elif 'revenue_per_customer' in values:
                return values['market_size'] * values['conversion_rate'] * values['revenue_per_customer']

        # Generic sum of values for other cases
        return sum(values.values())

    # Run Monte Carlo simulation
    engine = MonteCarloEngine(random_seed=random_seed)
    results = engine.run_simulation(
        variables=variables,
        outcome_function=outcome_function,
        num_simulations=num_simulations
    )

    # Calculate success probability based on criteria
    threshold = success_criteria.get('threshold', 0)
    comparison = success_criteria.get('comparison', '>=')

    if comparison == '>=':
        success_count = np.sum(results['outcomes'] >= threshold)
    elif comparison == '>':
        success_count = np.sum(results['outcomes'] > threshold)
    elif comparison == '<=':
        success_count = np.sum(results['outcomes'] <= threshold)
    elif comparison == '<':
        success_count = np.sum(results['outcomes'] < threshold)
    else:
        success_count = np.sum(results['outcomes'] >= threshold)  # default

    confidence_level = success_count / num_simulations

    # Calculate sensitivity
    sensitivity = engine.sensitivity_analysis(
        variables=variables,
        outcome_function=outcome_function,
        outcomes=results['outcomes'],
        samples=results['samples']
    )

    # Determine confidence qualifier
    confidence_qualifier = _interpret_confidence(confidence_level)

    # Identify key risk factors
    key_risks = _identify_key_risks(sensitivity, assumptions, threshold=0.15)

    return {
        'decision_context': decision_context,
        'confidence_level': float(confidence_level),
        'confidence_qualifier': confidence_qualifier,
        'expected_outcome': results['statistics']['mean'],
        'percentiles': results['percentiles'],
        'confidence_interval_95': [
            float(results['percentiles']['P5']),
            float(results['percentiles']['P95'])
        ],
        'sensitivity_analysis': sensitivity,
        'key_risk_factors': key_risks,
        'num_simulations': num_simulations,
        'success_threshold': threshold,
        'statistics': results['statistics']
    }


def test_assumption_robustness(
    base_answer: str,
    critical_assumptions: List[Dict[str, Any]],
    stress_test_ranges: Dict[str, Dict[str, float]],
    outcome_function_str: str,
    num_scenarios: int = 1000,
    random_seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Stress-tests reasoning by varying critical assumptions

    Args:
        base_answer: The original recommendation
        critical_assumptions: List of assumptions the answer depends on
        stress_test_ranges: How far to stress each assumption
        outcome_function_str: String description of outcome calculation
        num_scenarios: Number of stress test scenarios
        random_seed: Optional seed for reproducibility

    Returns:
        Robustness analysis with breaking points
    """

    # Create variables from critical assumptions
    variables = [create_variable_from_dict(a) for a in critical_assumptions]

    # Simple outcome function (can be customized)
    def outcome_function(values: Dict[str, float]) -> float:
        return sum(values.values())

    # Run simulation
    engine = MonteCarloEngine(random_seed=random_seed)
    results = engine.run_simulation(
        variables=variables,
        outcome_function=outcome_function,
        num_simulations=num_scenarios
    )

    # Analyze where answer might change
    # This is simplified - in practice would need more sophisticated logic
    outcomes = results['outcomes']
    threshold = np.median(outcomes)  # Assume base answer is at median

    # Find scenarios where outcome is significantly different
    significant_deviation = np.std(outcomes) * 1.5
    breaking_scenarios = np.abs(outcomes - threshold) > significant_deviation

    breaking_points = []
    if np.any(breaking_scenarios):
        indices = np.where(breaking_scenarios)[0][:5]  # Top 5 breaking scenarios
        for idx in indices:
            scenario = {var.name: float(results['samples'][var.name][idx]) for var in variables}
            breaking_points.append({
                'scenario': scenario,
                'outcome': float(outcomes[idx]),
                'deviation_from_base': float(outcomes[idx] - threshold)
            })

    robustness_score = 1.0 - (np.sum(breaking_scenarios) / num_scenarios)

    return {
        'base_answer': base_answer,
        'robustness_score': float(robustness_score),
        'breaking_points': breaking_points,
        'confidence_qualifier': _interpret_robustness(robustness_score),
        'num_scenarios_tested': num_scenarios,
        'stress_test_summary': {
            'stable_scenarios': int(np.sum(~breaking_scenarios)),
            'unstable_scenarios': int(np.sum(breaking_scenarios)),
            'outcome_range': [float(np.min(outcomes)), float(np.max(outcomes))]
        }
    }


def _interpret_confidence(confidence: float) -> str:
    """Interpret confidence level as qualitative assessment"""
    if confidence >= 0.9:
        return "VERY HIGH"
    elif confidence >= 0.75:
        return "HIGH"
    elif confidence >= 0.6:
        return "MODERATE"
    elif confidence >= 0.4:
        return "LOW"
    else:
        return "VERY LOW"


def _interpret_robustness(robustness: float) -> str:
    """Interpret robustness score"""
    if robustness >= 0.9:
        return "ROBUST (answer stable across scenarios)"
    elif robustness >= 0.75:
        return "MODERATELY ROBUST (answer mostly stable)"
    elif robustness >= 0.5:
        return "SOMEWHAT FRAGILE (answer changes in many scenarios)"
    else:
        return "FRAGILE (answer highly sensitive to assumptions)"


def _identify_key_risks(
    sensitivity: Dict[str, float],
    assumptions: Dict[str, Any],
    threshold: float = 0.15
) -> List[Dict[str, Any]]:
    """Identify key risk factors based on sensitivity analysis"""
    key_risks = []

    for var_name, influence in sensitivity.items():
        if influence > threshold:
            risk_info = {
                'variable': var_name,
                'influence': float(influence),
                'description': f"{var_name} has {influence*100:.1f}% influence on outcome"
            }

            # Add distribution info if available
            if var_name in assumptions:
                risk_info['distribution'] = assumptions[var_name].get('distribution', 'unknown')

            key_risks.append(risk_info)

    return key_risks
