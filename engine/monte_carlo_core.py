"""
Monte Carlo Core Engine
Vectorized simulation engine using NumPy for high-performance probabilistic analysis

Copyright (c) 2025 eesb99@gmail.com
Licensed under the MIT License - see LICENSE file for details
DMCA-Free: Original work
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class DistributionType(Enum):
    """Supported probability distributions"""
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    EXPONENTIAL = "exponential"
    BETA = "beta"
    GAMMA = "gamma"


@dataclass
class Variable:
    """Represents a simulation variable with its distribution"""
    name: str
    distribution: DistributionType
    params: Dict[str, float]

    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate random samples from the variable's distribution"""
        rng = random_state if random_state is not None else np.random

        if self.distribution == DistributionType.NORMAL:
            return rng.normal(self.params['mean'], self.params['std'], size)

        elif self.distribution == DistributionType.LOGNORMAL:
            return rng.lognormal(self.params['mean'], self.params['sigma'], size)

        elif self.distribution == DistributionType.UNIFORM:
            return rng.uniform(self.params['min'], self.params['max'], size)

        elif self.distribution == DistributionType.TRIANGULAR:
            return rng.triangular(
                self.params['left'],
                self.params['mode'],
                self.params['right'],
                size
            )

        elif self.distribution == DistributionType.EXPONENTIAL:
            return rng.exponential(self.params['scale'], size)

        elif self.distribution == DistributionType.BETA:
            return rng.beta(self.params['a'], self.params['b'], size)

        elif self.distribution == DistributionType.GAMMA:
            return rng.gamma(self.params['shape'], self.params['scale'], size)

        else:
            raise ValueError(f"Unsupported distribution: {self.distribution}")


class MonteCarloEngine:
    """High-performance Monte Carlo simulation engine"""

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize Monte Carlo engine

        Args:
            random_seed: Seed for reproducibility (None for non-deterministic)
        """
        self.random_state = np.random.RandomState(random_seed) if random_seed is not None else None

    def run_simulation(
        self,
        variables: List[Variable],
        outcome_function: Callable,
        num_simulations: int = 10000,
        correlation_matrix: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation

        Args:
            variables: List of Variable objects defining uncertainty
            outcome_function: Function that takes dict of variable values and returns outcome
            num_simulations: Number of Monte Carlo iterations
            correlation_matrix: Optional correlation matrix for multivariate sampling

        Returns:
            Dictionary with simulation results and statistics
        """

        # Generate samples for all variables
        samples = {}
        for var in variables:
            samples[var.name] = var.sample(num_simulations, self.random_state)

        # Apply correlation if specified
        if correlation_matrix is not None:
            samples = self._apply_correlation(samples, correlation_matrix, variables)

        # Calculate outcomes
        outcomes = np.array([
            outcome_function({name: samples[name][i] for name in samples})
            for i in range(num_simulations)
        ])

        # Calculate statistics
        results = {
            'outcomes': outcomes,
            'statistics': self._calculate_statistics(outcomes),
            'percentiles': self._calculate_percentiles(outcomes),
            'samples': samples,
            'num_simulations': num_simulations
        }

        return results

    def _apply_correlation(
        self,
        samples: Dict[str, np.ndarray],
        corr_matrix: np.ndarray,
        variables: List[Variable]
    ) -> Dict[str, np.ndarray]:
        """Apply correlation structure to samples using Cholesky decomposition"""

        # Validate correlation matrix
        if not np.allclose(corr_matrix, corr_matrix.T, atol=1e-8):
            raise ValueError("Correlation matrix must be symmetric")

        # Check positive definite (all eigenvalues > 0)
        eigvals = np.linalg.eigvals(corr_matrix)
        if not np.all(eigvals > -1e-10):  # Allow small numerical errors
            raise ValueError("Correlation matrix must be positive definite")

        # Convert samples to matrix (variables x simulations)
        var_names = [v.name for v in variables]
        sample_matrix = np.array([samples[name] for name in var_names])

        # Transform to standard normal
        uniform = stats.norm.cdf(sample_matrix)
        standard_normal = stats.norm.ppf(uniform)

        # Apply Cholesky decomposition
        try:
            L = np.linalg.cholesky(corr_matrix)
            correlated_normal = L @ standard_normal
        except np.linalg.LinAlgError as e:
            raise ValueError(f"Correlation matrix Cholesky decomposition failed: {e}")

        # Transform back to uniform then to original distributions
        correlated_uniform = stats.norm.cdf(correlated_normal)

        # Transform back to original distributions
        correlated_samples = {}
        for i, var in enumerate(variables):
            # Get inverse CDF (PPF) of the variable's distribution
            if var.distribution == DistributionType.NORMAL:
                correlated_samples[var.name] = stats.norm.ppf(
                    correlated_uniform[i],
                    loc=var.params['mean'],
                    scale=var.params['std']
                )
            elif var.distribution == DistributionType.UNIFORM:
                correlated_samples[var.name] = stats.uniform.ppf(
                    correlated_uniform[i],
                    loc=var.params['min'],
                    scale=var.params['max'] - var.params['min']
                )
            else:
                # For other distributions, use the original samples (approximation)
                correlated_samples[var.name] = samples[var.name]

        return correlated_samples

    def _calculate_statistics(self, outcomes: np.ndarray) -> Dict[str, float]:
        """Calculate statistical measures of outcomes"""
        return {
            'mean': float(np.mean(outcomes)),
            'median': float(np.median(outcomes)),
            'std': float(np.std(outcomes)),
            'variance': float(np.var(outcomes)),
            'min': float(np.min(outcomes)),
            'max': float(np.max(outcomes)),
            'skewness': float(stats.skew(outcomes)),
            'kurtosis': float(stats.kurtosis(outcomes))
        }

    def _calculate_percentiles(self, outcomes: np.ndarray) -> Dict[str, float]:
        """Calculate percentile values"""
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        return {
            f'P{p}': float(np.percentile(outcomes, p))
            for p in percentiles
        }

    def calculate_confidence_interval(
        self,
        outcomes: np.ndarray,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for outcomes"""
        alpha = 1 - confidence_level
        lower = np.percentile(outcomes, alpha/2 * 100)
        upper = np.percentile(outcomes, (1 - alpha/2) * 100)
        return (float(lower), float(upper))

    def sensitivity_analysis(
        self,
        variables: List[Variable],
        outcome_function: Callable,
        outcomes: np.ndarray,
        samples: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Calculate sensitivity of outcome to each input variable
        Uses Spearman rank correlation
        """
        sensitivity = {}

        for var in variables:
            # Calculate Spearman correlation between variable and outcome
            correlation, _ = stats.spearmanr(samples[var.name], outcomes)
            sensitivity[var.name] = float(correlation ** 2)  # R-squared

        # Sort by influence
        sensitivity = dict(sorted(sensitivity.items(), key=lambda x: abs(x[1]), reverse=True))
        return sensitivity


def create_variable_from_dict(var_dict: Dict[str, Any]) -> Variable:
    """Helper function to create Variable from dictionary"""
    return Variable(
        name=var_dict['name'],
        distribution=DistributionType(var_dict['distribution']),
        params=var_dict['params']
    )
