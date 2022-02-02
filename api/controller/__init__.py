from api.controller import cmgen, rem, mmgen

MODULES = (cmgen, rem, mmgen)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
