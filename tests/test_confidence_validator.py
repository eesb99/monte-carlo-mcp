"""
Unit tests for confidence validation tools
"""

import pytest
import numpy as np
from tools.confidence_validator import (
    validate_reasoning_confidence,
    test_assumption_robustness,
    _interpret_confidence,
    _interpret_robustness,
    _identify_key_risks
)


class TestValidateReasoningConfidence:
    """Tests for validate_reasoning_confidence function"""

    def test_basic_validation(self):
        """Test basic confidence validation"""
        result = validate_reasoning_confidence(
            decision_context="Test investment decision",
            assumptions={
                "roi": {
                    "distribution": "normal",
                    "params": {"mean": 0.15, "std": 0.05}
                }
            },
            success_criteria={"threshold": 0.10, "comparison": ">="},
            num_simulations=1000,
            random_seed=42
        )

        assert 'decision_context' in result
        assert 'confidence_level' in result
        assert 'expected_outcome' in result
        assert 'percentiles' in result
        assert 'sensitivity_analysis' in result

        assert 0 <= result['confidence_level'] <= 1
        assert result['decision_context'] == "Test investment decision"

    def test_high_confidence_scenario(self):
        """Test scenario with high confidence"""
        result = validate_reasoning_confidence(
            decision_context="High confidence test",
            assumptions={
                "value": {
                    "distribution": "normal",
                    "params": {"mean": 100, "std": 5}  # Low uncertainty
                }
            },
            success_criteria={"threshold": 80, "comparison": ">="},
            num_simulations=1000,
            random_seed=42
        )

        # With mean=100 and threshold=80, confidence should be very high
        assert result['confidence_level'] > 0.95

    def test_low_confidence_scenario(self):
        """Test scenario with low confidence"""
        result = validate_reasoning_confidence(
            decision_context="Low confidence test",
            assumptions={
                "value": {
                    "distribution": "normal",
                    "params": {"mean": 100, "std": 30}  # High uncertainty
                }
            },
            success_criteria={"threshold": 120, "comparison": ">="},
            num_simulations=1000,
            random_seed=42
        )

        # With mean=100 and threshold=120, confidence should be low
        assert result['confidence_level'] < 0.5

    def test_different_comparison_operators(self):
        """Test different comparison operators"""
        base_assumptions = {
            "value": {
                "distribution": "normal",
                "params": {"mean": 100, "std": 10}
            }
        }

        # Test >=
        result_gte = validate_reasoning_confidence(
            "Test >=",
            base_assumptions,
            {"threshold": 90, "comparison": ">="},
            1000,
            42
        )

        # Test >
        result_gt = validate_reasoning_confidence(
            "Test >",
            base_assumptions,
            {"threshold": 90, "comparison": ">"},
            1000,
            42
        )

        # >= should have slightly higher or equal confidence than >
        assert result_gte['confidence_level'] >= result_gt['confidence_level']

    def test_multiple_assumptions(self):
        """Test with multiple assumptions"""
        result = validate_reasoning_confidence(
            decision_context="Multiple assumptions",
            assumptions={
                "market_size": {
                    "distribution": "uniform",
                    "params": {"min": 400000, "max": 600000}
                },
                "conversion_rate": {
                    "distribution": "normal",
                    "params": {"mean": 0.03, "std": 0.01}
                },
                "revenue_per_customer": {
                    "distribution": "normal",
                    "params": {"mean": 2000, "std": 500}
                }
            },
            success_criteria={"threshold": 30000000, "comparison": ">="},
            num_simulations=1000,
            random_seed=42
        )

        assert 'sensitivity_analysis' in result
        # Should have sensitivity for all three variables
        assert len(result['sensitivity_analysis']) == 3

    def test_reproducibility(self):
        """Test that results are reproducible with same seed"""
        params = {
            "decision_context": "Reproducibility test",
            "assumptions": {
                "x": {"distribution": "normal", "params": {"mean": 100, "std": 10}}
            },
            "success_criteria": {"threshold": 90, "comparison": ">="},
            "num_simulations": 500,
            "random_seed": 42
        }

        result1 = validate_reasoning_confidence(**params)
        result2 = validate_reasoning_confidence(**params)

        assert result1['confidence_level'] == result2['confidence_level']
        assert result1['expected_outcome'] == result2['expected_outcome']

    def test_key_risk_identification(self):
        """Test that key risk factors are properly identified"""
        result = validate_reasoning_confidence(
            decision_context="Risk identification test",
            assumptions={
                "high_impact": {
                    "distribution": "normal",
                    "params": {"mean": 100, "std": 30}  # High variance
                },
                "low_impact": {
                    "distribution": "normal",
                    "params": {"mean": 10, "std": 1}  # Low variance
                }
            },
            success_criteria={"threshold": 100, "comparison": ">="},
            num_simulations=1000,
            random_seed=42
        )

        assert 'key_risk_factors' in result
        # high_impact should be identified as key risk
        risk_vars = [r['variable'] for r in result['key_risk_factors']]
        assert 'high_impact' in risk_vars


class TestAssumptionRobustness:
    """Tests for test_assumption_robustness function"""

    def test_basic_robustness(self):
        """Test basic assumption robustness testing"""
        result = test_assumption_robustness(
            base_answer="Invest in Project A",
            critical_assumptions=[
                {
                    "name": "roi",
                    "distribution": "normal",
                    "params": {"mean": 0.15, "std": 0.05}
                }
            ],
            stress_test_ranges={
                "roi": {"min": 0.05, "max": 0.25}
            },
            outcome_function_str="sum of assumptions",
            num_scenarios=500,
            random_seed=42
        )

        assert 'base_answer' in result
        assert 'robustness_score' in result
        assert 'breaking_points' in result
        assert 'confidence_qualifier' in result

        assert 0 <= result['robustness_score'] <= 1
        assert result['base_answer'] == "Invest in Project A"

    def test_robust_scenario(self):
        """Test scenario with high robustness"""
        result = test_assumption_robustness(
            base_answer="Stable recommendation",
            critical_assumptions=[
                {
                    "name": "stable_var",
                    "distribution": "normal",
                    "params": {"mean": 100, "std": 5}  # Low variance
                }
            ],
            stress_test_ranges={
                "stable_var": {"min": 80, "max": 120}
            },
            outcome_function_str="stable outcome",
            num_scenarios=500,
            random_seed=42
        )

        # Should have high robustness score
        assert result['robustness_score'] > 0.7

    def test_breaking_points_identified(self):
        """Test that breaking points are identified"""
        result = test_assumption_robustness(
            base_answer="Fragile recommendation",
            critical_assumptions=[
                {
                    "name": "volatile_var",
                    "distribution": "uniform",
                    "params": {"min": 0, "max": 200}  # High variance
                }
            ],
            stress_test_ranges={
                "volatile_var": {"min": 0, "max": 200}
            },
            outcome_function_str="volatile outcome",
            num_scenarios=500,
            random_seed=42
        )

        # Should have some breaking points
        assert len(result['breaking_points']) > 0


class TestInterpretationFunctions:
    """Tests for interpretation helper functions"""

    def test_interpret_confidence(self):
        """Test confidence interpretation"""
        assert _interpret_confidence(0.95) == "VERY HIGH"
        assert _interpret_confidence(0.85) == "HIGH"
        assert _interpret_confidence(0.65) == "MODERATE"
        assert _interpret_confidence(0.50) == "LOW"
        assert _interpret_confidence(0.30) == "VERY LOW"

    def test_interpret_robustness(self):
        """Test robustness interpretation"""
        assert "ROBUST" in _interpret_robustness(0.95)
        assert "MODERATELY ROBUST" in _interpret_robustness(0.80)
        assert "FRAGILE" in _interpret_robustness(0.30).upper()

    def test_identify_key_risks(self):
        """Test key risk identification"""
        sensitivity = {
            "high_risk": 0.75,
            "medium_risk": 0.30,
            "low_risk": 0.05
        }

        assumptions = {
            "high_risk": {"distribution": "normal"},
            "medium_risk": {"distribution": "uniform"},
            "low_risk": {"distribution": "normal"}
        }

        risks = _identify_key_risks(sensitivity, assumptions, threshold=0.20)

        assert len(risks) == 2  # high_risk and medium_risk
        assert risks[0]['variable'] == "high_risk"  # Should be first
        assert risks[0]['influence'] == 0.75


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_variance_assumption(self):
        """Test with zero variance (deterministic) assumption"""
        result = validate_reasoning_confidence(
            decision_context="Zero variance test",
            assumptions={
                "deterministic": {
                    "distribution": "normal",
                    "params": {"mean": 100, "std": 0.0001}  # Near zero variance
                }
            },
            success_criteria={"threshold": 90, "comparison": ">="},
            num_simulations=100,
            random_seed=42
        )

        # Should still work, confidence should be very high or very low
        assert result['confidence_level'] in [0.0, 1.0] or 0.95 < result['confidence_level'] <= 1.0

    def test_threshold_at_mean(self):
        """Test threshold exactly at mean"""
        result = validate_reasoning_confidence(
            decision_context="Threshold at mean",
            assumptions={
                "x": {
                    "distribution": "normal",
                    "params": {"mean": 100, "std": 10}
                }
            },
            success_criteria={"threshold": 100, "comparison": ">="},
            num_simulations=1000,
            random_seed=42
        )

        # Confidence should be around 50%
        assert 0.45 < result['confidence_level'] < 0.55

    def test_invalid_distribution(self):
        """Test with invalid distribution type"""
        with pytest.raises((ValueError, KeyError)):
            validate_reasoning_confidence(
                decision_context="Invalid distribution",
                assumptions={
                    "x": {
                        "distribution": "invalid_type",
                        "params": {"mean": 100}
                    }
                },
                success_criteria={"threshold": 90, "comparison": ">="},
                num_simulations=100
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
