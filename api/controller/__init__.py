from api.controller import encoding, algorithms

MODULES = (encoding, algorithms)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
