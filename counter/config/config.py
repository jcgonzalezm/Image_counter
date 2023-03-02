import os

from counter.domain.actions import CountDetectedObjects
from counter.config.enviroments import DevelopmentEnviroment , ProductionEnviroment

def available_enviroments():
    return {'prod': prod_count_action,
            'dev': dev_count_action}


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(DevelopmentEnviroment.define_AI_framework(), 
                                DevelopmentEnviroment.define_database_type())


def prod_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(ProductionEnviroment.define_AI_framework(), 
                                ProductionEnviroment.define_database_type())     


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    try:
        count_action_fn = available_enviroments().get(env)
    except KeyError:
        raise KeyError(f"There is no enviroment of {env}. Avilable enviroments are: {list(available_enviroments().keys())}")
    return count_action_fn()


