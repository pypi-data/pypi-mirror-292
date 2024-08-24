# bugster/config_loader.py

import importlib.util
import sys


def load_customer_config(customer_id):
    config_path = f"/customer-configs/{customer_id}/config.py"
    login_strategy_path = f"/customer-configs/{customer_id}/login_strategy.py"

    # Load config
    spec = importlib.util.spec_from_file_location(f"{customer_id}_config", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    # Load login strategy
    spec = importlib.util.spec_from_file_location(
        f"{customer_id}_login_strategy", login_strategy_path
    )
    login_strategy_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(login_strategy_module)

    # Add modules to sys.modules
    sys.modules[f"{customer_id}_config"] = config_module
    sys.modules[f"{customer_id}_login_strategy"] = login_strategy_module

    return getattr(config_module, "CustomerConfig")
