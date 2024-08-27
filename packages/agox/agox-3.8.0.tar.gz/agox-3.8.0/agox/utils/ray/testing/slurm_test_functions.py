import os
from agox.module import Module
from pathlib import Path
import logging
import time

class TestModule(Module):
    name = "TestModule"

    def __init__(self):
        super().__init__()

    def run(self, extra_str):
        print(f"Hello world: {extra_str}!")

def remote_module_function(test_module, *args, **kwargs):
    test_module.run(*args)
    return 0

def remote_function(*args, **kwargs):
    print(f"Hello world: {args}!")
    return 0

def log_slurm_info(logger):
    logging.info("SLURM environment variables:")
    for var, value in os.environ.items():
        if 'SLURM' in var:
            logger.info(f"{var}: {value}")

    logging.info("")

def test_stability(logger):
    os.environ["RAY_DEDUP_LOGS"] = "0"
    from agox.utils.ray import ray_startup, get_ray_pool

    logger.info('Event 1: Stability test started')

    # Start Ray
    ray_startup()
    logger.info('Event 2: Ray started')

    # Make a module:
    module = TestModule()
    logger.info('Event 3: Module created')

    # Get the ray pool
    pool, _ = get_ray_pool()
    logger.info('Event 4: Ray pool created')

    print(f"Pool: {pool}")
    pool.execute_on_actors(remote_function, [], ['1'], {})
    logger.info('Event 5: Function executed')
    time.sleep(2)

    # Add the module to the pool
    pool.add_module(module)
    logger.info('Event 6: Module added to pool')

    # Run the module
    pool.execute_on_actors(remote_module_function, [module.ray_key], ['1'], {})
    logger.info('Event 7: Module executed')

def slurm_test():
    
    submit_dir = os.getenv('SLURM_SUBMIT_DIR')
    array_task_id = os.getenv('SLURM_ARRAY_TASK_ID')

    if submit_dir is not None and array_task_id is not None:
        path = Path(submit_dir) / f"{array_task_id}/ray.log"
    else:
        path = Path('ray.log')

    print(f"Logging to: {path.resolve()}")

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=path, level=logging.DEBUG, format='%(asctime)s - %(message)s')
    logging.info('Event 0: Log file created.')

    log_slurm_info(logger)
    test_stability(logger)

