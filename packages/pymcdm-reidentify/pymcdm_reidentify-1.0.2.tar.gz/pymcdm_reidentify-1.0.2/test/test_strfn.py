import pytest
import numpy as np
from mealpy.swarm_based.PSO import OriginalPSO
from pymcdm.methods import TOPSIS
from pymcdm_reidentify.methods import STRFN
from pymcdm_reidentify.methods.strfn import _TRFN
from unittest.mock import Mock


@pytest.fixture
def setup_data():
    np.random.seed(0)
    matrix = np.random.random((10, 2))
    types = np.array([-1, 1])
    weights = np.array([0.5, 0.5])
    bounds = np.array([[0, 1], [0, 1]])
    base_method = TOPSIS()
    preference = base_method(matrix, weights, types)
    rank = base_method.rank(preference)
    stoch = OriginalPSO(epoch=10, pop_size=5)
    model = STRFN(stoch.solve, base_method, bounds, weights)
    return model, matrix, rank, weights, bounds


def test_initialization(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    assert model.base is not None
    assert model.weights is not None
    assert np.array_equal(model.lb, [0, 0])
    assert np.array_equal(model.ub, [1, 1])


def test_get_fuzzy_numbers(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    cores = np.array([0.5, 0.5, 0.5, 0.5])
    fuzzy_numbers = model.get_fuzzy_numbers(cores)
    assert len(fuzzy_numbers) == len(cores) // 2
    for fn in fuzzy_numbers:
        assert callable(fn)
        assert isinstance(fn, type(_TRFN(0, 0.5, 0.5, 1)))


def test_fit(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    model.fit(matrix, rank, log_to=None)
    assert model.weights is not None


def test_call_after_fit(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    model.fit(matrix, rank, log_to=None)
    optimal_weights = model()
    assert optimal_weights is not None
    assert np.isclose(np.sum(optimal_weights), 1)


def test_lb_ub_correctness(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    assert np.all(model.lb == [0, 0])
    assert np.all(model.ub == [1, 1])
    assert len(model.lb) == len(model.ub) == 4


def test_fit_with_predefined_solution(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    predefined_solution = np.array([0.4, 0.6, 0.4, 0.6])
    model.method = Mock(return_value=Mock(solution=predefined_solution))
    model.fit(matrix, rank, log_to=None)
    assert np.allclose(model.weights, predefined_solution[:len(model.weights)] / np.sum(predefined_solution[:len(model.weights)]))


def test_normalization_fuzzy_numbers(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    cores = np.array([0.5, 0.5, 0.5, 0.5])
    fuzzy_numbers = model.get_fuzzy_numbers(cores)
    assert all(isinstance(fn, type(_TRFN(0, 0.5, 0.5, 1))) for fn in fuzzy_numbers)


def test_weights_sum_to_one_after_fit(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    model.fit(matrix, rank, log_to=None)
    assert np.isclose(np.sum(model.weights), 1)


def test_fuzzy_numbers_correctness(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    cores = np.array([0.5, 0.5, 0.5, 0.5])
    fuzzy_numbers = model.get_fuzzy_numbers(cores)
    for fn, lb, core, ub in zip(fuzzy_numbers, model.lb[::2], cores[::2], model.ub[1::2]):
        assert callable(fn)
        assert fn(lb) == 0
        assert fn(core) == 1
        assert fn(ub) == 0


def test_fit_and_call_consistency(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    model.fit(matrix, rank, log_to=None)
    optimal_weights = model()
    assert np.isclose(np.sum(optimal_weights), 1)


def test_fitness_function_normalizes_solutions(setup_data):
    model, matrix, rank, weights, bounds = setup_data
    unnormalized_solutions = np.array([0.5, 0.5, 0.5, 0.5])
    fitness_value = model.fitness(unnormalized_solutions)
    assert isinstance(fitness_value, float)
    assert fitness_value >= 0
