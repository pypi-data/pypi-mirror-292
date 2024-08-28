import pytest
import numpy as np
from mealpy.swarm_based.PSO import OriginalPSO
from pymcdm.methods import TOPSIS
from pymcdm_reidentify.methods import SITW
from pymcdm.correlations import spearman
from unittest.mock import Mock


@pytest.fixture
def setup_data():
    np.random.seed(0)
    matrix = np.random.random((10, 2))
    types = np.array([-1, 1])
    weights = np.random.random(2)
    weights = weights / np.sum(weights)  # Unknown expert criteria weights
    preference = TOPSIS()(matrix, weights, types)
    rank = TOPSIS().rank(preference)
    stoch = OriginalPSO(epoch=10, pop_size=5)
    model = SITW(stoch.solve, TOPSIS(), types)
    return model, matrix, rank, weights


def test_initialization(setup_data):
    model, matrix, rank, weights = setup_data
    assert model.base is not None
    assert model.types is not None
    assert model.weights is None
    assert np.array_equal(model.lb, np.zeros_like(model.types))
    assert np.array_equal(model.ub, np.ones_like(model.types))


def test_fit(setup_data):
    model, matrix, rank, weights = setup_data
    model.fit(matrix, rank, log_to=None)
    assert model.weights is not None
    assert np.isclose(np.sum(model.weights), 1)


def test_call(setup_data):
    model, matrix, rank, weights = setup_data
    model.fit(matrix, rank, log_to=None)
    optimal_weights = model()
    assert optimal_weights is not None
    assert np.isclose(np.sum(optimal_weights), 1)


def test_fitness(setup_data):
    model, matrix, rank, weights = setup_data
    solutions = np.random.random(2)
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1


def test_fitness_with_different_correlation(setup_data):
    model, matrix, rank, weights = setup_data
    solutions = np.random.random(2)
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1


def test_fit_with_predefined_solution(setup_data):
    model, matrix, rank, weights = setup_data
    predefined_solution = np.random.random(2)
    model.method = Mock(return_value=Mock(solution=predefined_solution))
    model.fit(matrix, rank, log_to=None)
    assert np.allclose(model.weights, predefined_solution / np.sum(predefined_solution))


def test_call_after_fit(setup_data):
    model, matrix, rank, weights = setup_data
    model.fit(matrix, rank, log_to=None)
    optimal_weights = model()
    assert optimal_weights is not None
    assert np.isclose(np.sum(optimal_weights), 1)


def test_lb_ub_correctness(setup_data):
    model, matrix, rank, weights = setup_data
    assert np.all(model.lb == 0)
    assert np.all(model.ub == 1)
    assert len(model.lb) == len(model.ub) == len(model.types)


def test_weights_sum_to_one_after_fit(setup_data):
    model, matrix, rank, weights = setup_data
    model.fit(matrix, rank, log_to=None)
    assert np.isclose(np.sum(model.weights), 1)


def test_fitness_normalizes_weights(setup_data):
    model, matrix, rank, weights = setup_data
    unnormalized_weights = np.random.random(2)
    model.fitness(unnormalized_weights)
    normalized_weights = unnormalized_weights / np.sum(unnormalized_weights)
    assert np.isclose(np.sum(normalized_weights), 1)
