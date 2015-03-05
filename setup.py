from setuptools import setup, find_packages

setup(
    name='kluge_web',
    version='1.0',
    packages=find_packages(exclude=['tests']),
    test_suite="tests",
    scripts=["scripts/add_kluge_docs.sh"],
    install_requires=['statsd', 'protobuf', 'tornado', 'redis', 'Flask', 'Flask-Testing', 'Flask-RESTful']
)
