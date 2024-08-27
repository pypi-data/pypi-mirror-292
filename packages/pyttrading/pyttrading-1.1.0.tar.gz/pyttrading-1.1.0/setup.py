from setuptools import find_packages, setup

setup(
    name='pyttrading',
    packages=find_packages(),
    version='1.1.0',
    description='Trading Library',
    author='CannavIT',
    install_requires=[
        'Backtesting==0.3.3',
        'requests==2.32.3',
        'pydantic==2.8.2',
        'scipy==1.12.0',
        'ta==0.11.0',
    ],
    tests_require=['pytest==4.4.2'],
    test_suite='tests',
    python_requires='>=3.6'
)

# pip uninstall -y pyttrading && python setup.py sdist && twine upload dist/* 

#! Caps Simulation
# {
#   "platformName": "iOS",
#   "appium:automationName": "XCUITest",
#   "appium:udid": "EA9AAE0F-118C-4F6E-9625-2A4B37B6CEE9"
# }