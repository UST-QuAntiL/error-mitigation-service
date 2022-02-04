import os
from api import create_app

app = create_app(os.getenv("FLASK_CONFIG") or "default")


# Get coverage with:
# coverage run --branch --include 'api/*' -m unittest discover
# coverage report
# coverage xml
@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    testresult = unittest.TextTestRunner(verbosity=2).run(tests)

    if testresult.wasSuccessful():
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    app.run()