from setuptools import setup, find_packages

def readme():
    with open("README.md", 'r') as f:
        return f.read()

setup(
    name = "dead_simple_interface",
    description = "A minimal (POC/cookbook) interface for a microservices archival repository" +
    " which uses idnests, archstor, the qremis api, etc",
    long_description = readme(),
    packages = find_packages(
        exclude = [
        ]
    ),
    install_requires = [
        'flask>0',
        'requests'
    ],
)
