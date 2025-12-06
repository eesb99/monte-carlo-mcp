"""
Unit tests for Monte Carlo core engine
"""

import pytest
import numpy as np
from engine.monte_carlo_core import (
    MonteCarloEngine,
    Variable,
    DistributionType,
    create_variable_from_dict
)


class TestVariable:
    """Tests for Variable class"""

    def test_normal_distribution_sampling(self):
        """Test normal distribution sampling"""
        var = Variable(
            name="test_normal",
            distribution=DistributionType.NORMAL,
            params={'mean': 100, 'std': 10}
        )
        samples = var.sample(1000, random_state=np.random.RandomState(42))

        assert len(samples) == 1000
        assert 80 < np.mean(samples) < 120  # Within 2 std devs
        assert 5 < np.std(samples) < 15

    def test_uniform_distribution_sampling(self):
        """Test uniform distribution sampling"""
        var = Variable(
            name="test_uniform",
            distribution=DistributionType.UNIFORM,
            params={'min': 50, 'max': 150}
        )
        samples = var.sample(1000, random_state=np.random.RandomState(42))

        assert len(samples) == 1000
        assert np.min(samples) >= 50
        assert np.max(samples) <= 150
        assert 90 < np.mean(samples) < 110  # Should be ~100

    def test_triangular_distribution_sampling(self):
        """Test triangular distribution sampling"""
        var = Variable(
            name="test_triangular",
            distribution=DistributionType.TRIANGULAR,
            params={'left': 0, 'mode': 50, 'right': 100}
        )
        samples = var.sample(1000, random_state=np.random.RandomState(42))

        assert len(samples) == 1000
        assert np.min(samples) >= 0
        assert np.max(samples) <= 100

    def test_unsupported_distribution(self):
        """Test that unsupported distribution raises error"""
        var = Variable(
            name="test_invalid",
            distribution="invalid_dist",  # Not a DistributionType
            params={}
        )
        with pytest.raises(ValueError):
            var.sample(100)


class TestMonteCarloEngine:
    """Tests for MonteCarloEngine class"""

    def test_reproducibility_with_seed(self):
        """Test that simulations are reproducible with same seed"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10}),
            Variable("y", DistributionType.UNIFORM, {'min': 50, 'max': 150})
        ]

        def outcome_func(values):
            return values['x'] + values['y']

        engine1 = MonteCarloEngine(random_seed=42)
        results1 = engine1.run_simulation(variables, outcome_func, 100)

        engine2 = MonteCarloEngine(random_seed=42)
        results2 = engine2.run_simulation(variables, outcome_func, 100)

        np.testing.assert_array_equal(results1['outcomes'], results2['outcomes'])

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10})
        ]

        def outcome_func(values):
            return values['x']

        engine1 = MonteCarloEngine(random_seed=42)
        results1 = engine1.run_simulation(variables, outcome_func, 100)

        engine2 = MonteCarloEngine(random_seed=123)
        results2 = engine2.run_simulation(variables, outcome_func, 100)

        assert not np.array_equal(results1['outcomes'], results2['outcomes'])

    def test_statistics_calculation(self):
        """Test statistical measures calculation"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10})
        ]

        def outcome_func(values):
            return values['x']

        engine = MonteCarloEngine(random_seed=42)
        results = engine.run_simulation(variables, outcome_func, 1000)

        stats = results['statistics']
        assert 'mean' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'variance' in stats

        # Check mean is close to expected
        assert 95 < stats['mean'] < 105

    def test_percentiles_calculation(self):
        """Test percentile calculation"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10})
        ]

        def outcome_func(values):
            return values['x']

        engine = MonteCarloEngine(random_seed=42)
        results = engine.run_simulation(variables, outcome_func, 1000)

        percentiles = results['percentiles']
        assert 'P10' in percentiles
        assert 'P50' in percentiles
        assert 'P90' in percentiles

        # P50 should be close to mean for normal distribution
        assert abs(percentiles['P50'] - results['statistics']['mean']) < 2

    def test_sensitivity_analysis(self):
        """Test sensitivity analysis calculation"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10}),
            Variable("y", DistributionType.NORMAL, {'mean': 50, 'std': 5})
        ]

        def outcome_func(values):
            # x has 2x the impact of y
            return 2 * values['x'] + values['y']

        engine = MonteCarloEngine(random_seed=42)
        results = engine.run_simulation(variables, outcome_func, 1000)

        sensitivity = engine.sensitivity_analysis(
            variables, outcome_func, results['outcomes'], results['samples']
        )

        assert 'x' in sensitivity
        assert 'y' in sensitivity
        # x should have higher influence than y
        assert sensitivity['x'] > sensitivity['y']

    def test_confidence_interval(self):
        """Test confidence interval calculation"""
        outcomes = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        engine = MonteCarloEngine()

        lower, upper = engine.calculate_confidence_interval(outcomes, 0.9)

        assert lower < upper
        assert lower >= np.min(outcomes)
        assert upper <= np.max(outcomes)

    def test_correlation_application(self):
        """Test correlation matrix application"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10}),
            Variable("y", DistributionType.NORMAL, {'mean': 50, 'std': 5})
        ]

        # Perfect positive correlation
        corr_matrix = np.array([[1.0, 0.9], [0.9, 1.0]])

        def outcome_func(values):
            return values['x'] + values['y']

        engine = MonteCarloEngine(random_seed=42)
        results = engine.run_simulation(
            variables, outcome_func, 100, correlation_matrix=corr_matrix
        )

        # With high correlation, x and y should move together
        correlation = np.corrcoef(
            results['samples']['x'],
            results['samples']['y']
        )[0, 1]

        assert correlation > 0.5  # Should be positively correlated


class TestHelperFunctions:
    """Test helper functions"""

    def test_create_variable_from_dict(self):
        """Test variable creation from dictionary"""
        var_dict = {
            'name': 'test_var',
            'distribution': 'normal',
            'params': {'mean': 100, 'std': 10}
        }

        var = create_variable_from_dict(var_dict)

        assert var.name == 'test_var'
        assert var.distribution == DistributionType.NORMAL
        assert var.params == {'mean': 100, 'std': 10}


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_simulations(self):
        """Test with zero simulations - should handle gracefully"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10})
        ]

        def outcome_func(values):
            return values['x']

        engine = MonteCarloEngine()
        # This might raise an error or return empty results
        # depending on implementation
        with pytest.raises((ValueError, IndexError)):
            engine.run_simulation(variables, outcome_func, 0)

    def test_single_variable(self):
        """Test with single variable"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10})
        ]

        def outcome_func(values):
            return values['x']

        engine = MonteCarloEngine(random_seed=42)
        results = engine.run_simulation(variables, outcome_func, 100)

        assert len(results['outcomes']) == 100
        assert 'x' in results['samples']

    def test_large_number_of_simulations(self):
        """Test with large number of simulations"""
        variables = [
            Variable("x", DistributionType.NORMAL, {'mean': 100, 'std': 10})
        ]

        def outcome_func(values):
            return values['x']

        engine = MonteCarloEngine()
        results = engine.run_simulation(variables, outcome_func, 50000)

        assert len(results['outcomes']) == 50000
        # Mean should converge to expected value
        assert abs(results['statistics']['mean'] - 100) < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
