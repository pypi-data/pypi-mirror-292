import pytest
import numpy as np
import itertools
from unittest.mock import Mock
from mealpy.swarm_based.PSO import OriginalPSO
from pymcdm.methods import COMET, TOPSIS
from pymcdm.methods.comet_tools import MethodExpert
from pymcdm_reidentify.methods import SITCOM
from pymcdm.correlations import spearman


@pytest.fixture
def setup_data():
    np.random.seed(0)
    matrix = np.random.random((10, 2))
    types = np.array([-1, 1])
    weights = np.array([0.5, 0.5])
    cvalues = COMET.make_cvalues(matrix, 2)
    comet = COMET(cvalues, MethodExpert(TOPSIS(), weights, types))
    preference = comet(matrix)
    rank = comet.rank(preference)
    stoch = OriginalPSO(epoch=10, pop_size=5)
    model = SITCOM(stoch.solve, cvalues)
    return model, matrix, rank, cvalues


def test_initialization(setup_data):
    model, matrix, rank, cvalues = setup_data
    assert model.cvalues == cvalues
    assert len(model.lb) == len(model.ub)
    assert len(model.lb) == len(list(itertools.product(*cvalues)))
    assert model.model is not None


def test_fit(setup_data):
    model, matrix, rank, cvalues = setup_data
    model.fit(matrix, rank, log_to=None)
    assert model.model.p is not None


def test_call(setup_data):
    model, matrix, rank, cvalues = setup_data
    model.fit(matrix, rank, log_to=None)
    preferences = model(matrix)
    assert preferences is not None
    assert len(preferences) == len(list(itertools.product(*cvalues)))


def test_fitness(setup_data):
    model, matrix, rank, cvalues = setup_data
    model.fit(matrix, rank, log_to=None)
    solutions = np.random.random(len(model.lb))
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1


def test_fitness_with_different_correlation(setup_data):
    model, matrix, rank, cvalues = setup_data
    model.fit(matrix, rank, log_to=None)
    solutions = np.random.random(len(model.lb))
    fitness_value = model.fitness(solutions, correlation=spearman)
    assert isinstance(fitness_value, float)
    assert 0 <= fitness_value <= 1


def test_fit_with_predefined_solution(setup_data):
    model, matrix, rank, cvalues = setup_data
    predefined_solution = np.random.random(len(model.lb))
    model.method = Mock(return_value=Mock(solution=predefined_solution))
    model.fit(matrix, rank, log_to=None)
    assert np.allclose(model.model.p, predefined_solution)


def test_call_after_fit(setup_data):
    model, matrix, rank, cvalues = setup_data
    model.fit(matrix, rank, log_to=None)
    preferences = model(matrix)
    assert preferences is not None
    assert len(preferences) == len(list(itertools.product(*cvalues)))


def test_lb_ub_correctness(setup_data):
    model, matrix, rank, cvalues = setup_data
    assert all(lb == 0 for lb in model.lb)
    assert all(ub == 1 for ub in model.ub)
    assert len(model.lb) == len(model.ub)
