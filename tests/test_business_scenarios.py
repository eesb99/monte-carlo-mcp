"""
Unit tests for business scenario simulation tools
"""

import pytest
import numpy as np
from tools.business_scenarios import (
    run_business_scenario,
    run_sensitivity_analysis,
    _interpret_scenario_results
)


class TestRunBusinessScenario:
    """Tests for run_business_scenario function"""

    def test_basic_scenario(self):
        """Test basic business scenario simulation"""
        result = run_business_scenario(
            scenario_name="Basic Test Scenario",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        assert 'scenario_name' in result
        assert 'expected_total_profit' in result
        assert 'probability_of_profitability' in result
        assert 'percentile_outcomes' in result
        assert 'risk_metrics' in result

        assert result['scenario_name'] == "Basic Test Scenario"
        assert result['time_horizon'] == 12

    def test_profitability_calculation(self):
        """Test profitability probability calculation"""
        # High profit scenario
        result_high = run_business_scenario(
            scenario_name="High profit",
            revenue_assumptions={
                "base_revenue": 200000,
                "growth_rate": {"mean": 0.10, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 30000,
                "variable_costs": {"mean": 0.30, "std": 0.05}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        # Low profit scenario
        result_low = run_business_scenario(
            scenario_name="Low profit",
            revenue_assumptions={
                "base_revenue": 50000,
                "growth_rate": {"mean": 0.02, "std": 0.05}
            },
            cost_structure={
                "fixed_costs": 80000,
                "variable_costs": {"mean": 0.60, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        # High profit should have higher probability
        assert result_high['probability_of_profitability'] > result_low['probability_of_profitability']

    def test_roi_analysis(self):
        """Test ROI analysis when initial investment provided"""
        result = run_business_scenario(
            scenario_name="ROI Test",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.10, "std": 0.03},
                "initial_investment": 100000
            },
            cost_structure={
                "fixed_costs": 40000,
                "variable_costs": {"mean": 0.40, "std": 0.05}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        assert 'roi_analysis' in result
        assert result['roi_analysis'] is not None
        assert 'mean_roi' in result['roi_analysis']
        assert 'prob_positive_roi' in result['roi_analysis']

    def test_no_roi_analysis_without_investment(self):
        """Test that ROI analysis is None without initial investment"""
        result = run_business_scenario(
            scenario_name="No ROI Test",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        assert result['roi_analysis'] is None

    def test_churn_rate_impact(self):
        """Test impact of churn rate on outcomes"""
        # Scenario without churn
        result_no_churn = run_business_scenario(
            scenario_name="No churn",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.10, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.05}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        # Scenario with churn
        result_with_churn = run_business_scenario(
            scenario_name="With churn",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.10, "std": 0.02},
                "churn_rate": {"mean": 0.05, "std": 0.01}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.05}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        # No churn should have higher profit
        assert result_no_churn['expected_total_profit'] > result_with_churn['expected_total_profit']

    def test_sensitivity_analysis_included(self):
        """Test that sensitivity analysis is included in results"""
        result = run_business_scenario(
            scenario_name="Sensitivity test",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        assert 'sensitivity' in result
        assert len(result['sensitivity']) > 0

    def test_risk_metrics(self):
        """Test risk metrics calculation"""
        result = run_business_scenario(
            scenario_name="Risk metrics test",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        risk = result['risk_metrics']
        assert 'downside_risk' in risk
        assert 'upside_potential' in risk
        assert 'outcome_range' in risk

        # Upside should be greater than downside
        assert risk['upside_potential'] > risk['downside_risk']
        # Range should be positive
        assert risk['outcome_range'] > 0

    def test_percentile_outcomes(self):
        """Test percentile outcomes calculation"""
        result = run_business_scenario(
            scenario_name="Percentile test",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=1000,
            random_seed=42
        )

        percentiles = result['percentile_outcomes']
        assert 'pessimistic_P10' in percentiles
        assert 'most_likely_P50' in percentiles
        assert 'optimistic_P90' in percentiles

        # Should be in ascending order
        assert percentiles['pessimistic_P10'] < percentiles['most_likely_P50']
        assert percentiles['most_likely_P50'] < percentiles['optimistic_P90']

    def test_reproducibility(self):
        """Test reproducibility with same seed"""
        params = {
            "scenario_name": "Reproducibility",
            "revenue_assumptions": {
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            "cost_structure": {
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            "time_horizon": 12,
            "num_simulations": 500,
            "random_seed": 42
        }

        result1 = run_business_scenario(**params)
        result2 = run_business_scenario(**params)

        assert result1['expected_total_profit'] == result2['expected_total_profit']
        assert result1['probability_of_profitability'] == result2['probability_of_profitability']


class TestRunSensitivityAnalysis:
    """Tests for run_sensitivity_analysis function"""

    def test_basic_sensitivity(self):
        """Test basic sensitivity analysis"""
        result = run_sensitivity_analysis(
            base_simulation_id="test_sim_001",
            variables_to_test=["growth_rate", "variable_costs"],
            variation_range={
                "growth_rate": {"low": 0.03, "high": 0.07},
                "variable_costs": {"low": 0.40, "high": 0.60}
            },
            outcome_data={}
        )

        assert 'tornado_diagram_data' in result
        assert 'key_drivers' in result
        assert 'num_variables_tested' in result

        assert result['base_simulation_id'] == "test_sim_001"
        assert result['num_variables_tested'] == 2

    def test_key_drivers_identification(self):
        """Test that key drivers are properly identified"""
        result = run_sensitivity_analysis(
            base_simulation_id="test_sim_002",
            variables_to_test=["var1", "var2", "var3", "var4"],
            variation_range={
                "var1": {"low": 10, "high": 90},  # High impact
                "var2": {"low": 45, "high": 55},  # Low impact
                "var3": {"low": 20, "high": 80},  # Medium impact
                "var4": {"low": 0, "high": 100}   # Highest impact
            },
            outcome_data={}
        )

        # Should identify top 3 drivers
        assert len(result['key_drivers']) == 3
        # var4 should be first (highest impact)
        assert result['key_drivers'][0] == "var4"

    def test_tornado_diagram_sorting(self):
        """Test that tornado diagram is sorted by impact"""
        result = run_sensitivity_analysis(
            base_simulation_id="test_sim_003",
            variables_to_test=["low_impact", "high_impact", "medium_impact"],
            variation_range={
                "low_impact": {"low": 95, "high": 105},
                "high_impact": {"low": 50, "high": 150},
                "medium_impact": {"low": 70, "high": 130}
            },
            outcome_data={}
        )

        tornado_data = result['tornado_diagram_data']
        impacts = [data['impact'] for data in tornado_data.values()]

        # Should be in descending order
        assert impacts == sorted(impacts, reverse=True)

    def test_missing_variation_range(self):
        """Test handling of missing variation range"""
        result = run_sensitivity_analysis(
            base_simulation_id="test_sim_004",
            variables_to_test=["var1", "var2", "missing_var"],
            variation_range={
                "var1": {"low": 10, "high": 20},
                "var2": {"low": 30, "high": 40}
                # missing_var not in range
            },
            outcome_data={}
        )

        # Should only analyze variables with ranges
        assert len(result['tornado_diagram_data']) == 2
        assert 'missing_var' not in result['tornado_diagram_data']


class TestInterpretationFunctions:
    """Tests for interpretation helper functions"""

    def test_interpret_high_profit_scenario(self):
        """Test interpretation of high profit scenario"""
        interpretation = _interpret_scenario_results(
            profit_prob=0.90,
            expected_profit=500000,
            roi_stats={"prob_positive_roi": 0.85}
        )

        assert "HIGH probability" in interpretation
        assert "90%" in interpretation
        assert "500,000" in interpretation

    def test_interpret_low_profit_scenario(self):
        """Test interpretation of low profit scenario"""
        interpretation = _interpret_scenario_results(
            profit_prob=0.40,
            expected_profit=-50000,
            roi_stats=None
        )

        assert "LOW probability" in interpretation
        assert "LOSS" in interpretation

    def test_interpret_with_roi(self):
        """Test interpretation with ROI stats"""
        interpretation = _interpret_scenario_results(
            profit_prob=0.85,
            expected_profit=300000,
            roi_stats={"prob_positive_roi": 0.75}
        )

        assert "ROI" in interpretation
        assert "75%" in interpretation


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_time_horizon(self):
        """Test with zero time horizon"""
        with pytest.raises((ValueError, ZeroDivisionError)):
            run_business_scenario(
                scenario_name="Zero horizon",
                revenue_assumptions={
                    "base_revenue": 100000,
                    "growth_rate": {"mean": 0.05, "std": 0.02}
                },
                cost_structure={
                    "fixed_costs": 50000,
                    "variable_costs": {"mean": 0.50, "std": 0.10}
                },
                time_horizon=0,
                num_simulations=100
            )

    def test_negative_base_revenue(self):
        """Test handling of negative base revenue"""
        result = run_business_scenario(
            scenario_name="Negative revenue",
            revenue_assumptions={
                "base_revenue": -10000,  # Negative
                "growth_rate": {"mean": 0.05, "std": 0.02}
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.10}
            },
            time_horizon=12,
            num_simulations=100,
            random_seed=42
        )

        # Should result in negative profit
        assert result['expected_total_profit'] < 0

    def test_extreme_churn_rate(self):
        """Test with extreme (100%) churn rate"""
        result = run_business_scenario(
            scenario_name="100% churn",
            revenue_assumptions={
                "base_revenue": 100000,
                "growth_rate": {"mean": 0.10, "std": 0.02},
                "churn_rate": {"mean": 1.0, "std": 0.0}  # 100% churn
            },
            cost_structure={
                "fixed_costs": 50000,
                "variable_costs": {"mean": 0.50, "std": 0.05}
            },
            time_horizon=12,
            num_simulations=100,
            random_seed=42
        )

        # Revenue should approach zero with 100% churn
        # Expected profit should be very negative
        assert result['expected_total_profit'] < -500000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
