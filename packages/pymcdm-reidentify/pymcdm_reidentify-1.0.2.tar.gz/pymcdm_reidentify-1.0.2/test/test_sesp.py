import pytest
import numpy as np
from unittest.mock import Mock
from mealpy.swarm_based.PSO import OriginalPSO
from pymcdm.methods import SPOTIS
from pymcdm_reidentify.methods import SESP
from pymcdm.correlations import spearman


@pytest.fixture
def setup_data():
    np.random.seed(0)
    matrix = np.random.random((10, 2))
    types = np.array([-1, 1])
    weights = np.array([0.5, 0.5])
    bounds = np.array([[0, 1], [0, 1]])
    esp = np.array([0.5, 0.5])
    spotis = SPOTIS(bounds, esp)
    preference = spotis(matrix, weights, types)
    rank = spotis.rank(preference)
    stoch = OriginalPSO(epoch=10, pop_size=5)
    model = SESP(stoch.solve, SPOTIS(bounds), types)
    return model, matrix, rank, bounds, esp, weights, types


def test_initialization(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    assert model.base.bounds.shape == bounds.shape
    assert np.array_equal(model.types, types)
    assert model.weights is None
    assert model.lb.shape == (2,)
    assert model.ub.shape == (2,)


def test_fit(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    model.fit(matrix, rank, log_to=None)
    assert model.weights is not None
    assert np.isclose(model.weights.sum(), 1.0)


def test_call(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    model.fit(matrix, rank, log_to=None)
    esp_result = model()
    assert esp_result is not None
    assert esp_result.shape == (2,)


def test_fitness(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    model.fit(matrix, rank, log_to=None)
    solutions = np.array([0.5, 0.5])
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1


def test_fitness_with_different_correlation(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    model.fit(matrix, rank, log_to=None)
    solutions = np.array([0.5, 0.5])
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1


def test_fit_with_custom_weights(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    custom_weights = np.array([0.6, 0.4])
    model.weights = custom_weights
    model.fit(matrix, rank, log_to=None)
    assert np.array_equal(model.weights, custom_weights)


def test_fitness_with_custom_weights(setup_data):
    model, matrix, rank, bounds, esp, weights, types = setup_data
    custom_weights = np.array([0.6, 0.4])
    model.weights = custom_weights
    model.fit(matrix, rank, log_to=None)
    solutions = np.array([0.5, 0.5])
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1
