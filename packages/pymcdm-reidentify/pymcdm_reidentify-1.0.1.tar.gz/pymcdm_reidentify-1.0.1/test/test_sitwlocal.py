import pytest
import numpy as np
from mealpy.swarm_based.PSO import OriginalPSO
from pymcdm.methods import TOPSIS, COMET
from pymcdm.methods.comet_tools import MethodExpert, get_local_weights
from pymcdm_reidentify.methods import SITWLocal
from unittest.mock import Mock


@pytest.fixture
def setup_data():
    np.random.seed(0)
    matrix = np.random.random((10, 2))
    types = np.array([-1, 1])
    weights = np.array([0.5, 0.5])
    base_method = TOPSIS()
    comet_model = COMET(COMET.make_cvalues(matrix, 3), MethodExpert(base_method, weights, types))
    y_train = np.array([get_local_weights(comet_model, alt, percent_step=0.01) for alt in matrix])
    stoch = OriginalPSO(epoch=10, pop_size=5)
    model = SITWLocal(stoch.solve, base_method, types)
    return model, matrix, y_train


def test_initialization(setup_data):
    model, matrix, y_train = setup_data
    assert model.base is not None
    assert model.types is not None
    assert model.weights is None
    assert np.array_equal(model.lb, np.zeros_like(model.types))
    assert np.array_equal(model.ub, np.ones_like(model.types))


def test_fit(setup_data):
    model, matrix, y_train = setup_data
    model.fit(matrix, y_train, log_to=None)
    assert model.weights is not None
    assert np.isclose(np.sum(model.weights), 1)


def test_call(setup_data):
    model, matrix, y_train = setup_data
    model.fit(matrix, y_train, log_to=None)
    optimal_weights = model()
    assert optimal_weights is not None
    assert np.isclose(np.sum(optimal_weights), 1)


def test_fitness(setup_data):
    model, matrix, y_train = setup_data
    solutions = np.random.random(2)
    fitness_value = model.fitness(solutions)
    assert isinstance(fitness_value, float)
    assert fitness_value >= 0


def test_fit_with_predefined_solution(setup_data):
    model, matrix, y_train = setup_data
    predefined_solution = np.random.random(2)
    model.method = Mock(return_value=Mock(solution=predefined_solution))
    model.fit(matrix, y_train, log_to=None)
    assert np.allclose(model.weights, predefined_solution / np.sum(predefined_solution))


def test_call_after_fit(setup_data):
    model, matrix, y_train = setup_data
    model.fit(matrix, y_train, log_to=None)
    optimal_weights = model()
    assert optimal_weights is not None
    assert np.isclose(np.sum(optimal_weights), 1)


def test_lb_ub_correctness(setup_data):
    model, matrix, y_train = setup_data
    assert np.all(model.lb == 0)
    assert np.all(model.ub == 1)
    assert len(model.lb) == len(model.ub) == len(model.types)


def test_weights_sum_to_one_after_fit(setup_data):
    model, matrix, y_train = setup_data
    model.fit(matrix, y_train, log_to=None)
    assert np.isclose(np.sum(model.weights), 1)


def test_fitness_normalizes_weights(setup_data):
    model, matrix, y_train = setup_data
    unnormalized_weights = np.random.random(2)
    model.fitness(unnormalized_weights)
    normalized_weights = unnormalized_weights / np.sum(unnormalized_weights)
    assert np.isclose(np.sum(normalized_weights), 1)
