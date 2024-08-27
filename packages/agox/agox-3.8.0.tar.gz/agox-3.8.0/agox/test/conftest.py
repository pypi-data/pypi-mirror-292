import pytest

def pytest_addoption(parser):
    parser.addoption('--rtol', type=float, default=1e-05)
    parser.addoption('--atol', type=float, default=1e-08)
    parser.addoption('--create_mode', default=False, action='store_true')

@pytest.fixture
def cmd_options(request):
    return {'tolerance':{'rtol':request.config.getoption('rtol'), 'atol':request.config.getoption('atol')},
            'create_mode':request.config.getoption('create_mode')}


@pytest.fixture(scope="module", autouse=True)
def ray_fix():
    import ray 
    from agox.utils.ray import reset_ray_pool
    if ray.is_initialized():
        reset_ray_pool()
    yield

def pytest_sessionstart(session):
    from agox.utils.ray import ray_startup
    ray_startup(cpu_count=2, memory=None, tmp_dir=None, include_dashboard=False, max_grace_period=0.0)
