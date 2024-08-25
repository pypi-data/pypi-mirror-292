from setuptools import find_packages, setup

setup(
    name="wilhelm-graphdb-python",
    version="0.0.1",
    description="A package suitable for offline vocabulary processing and batch ingestion into Graph databases, " +
                "such as Neo4j and ArangoDB",
    url="https://github.com/QubitPi/wilhelm-graphdb-python",
    author="Jiaqi (Hutao of Emberfire)",
    author_email="jack20220723@gmail.com",
    license="Apache-2.0",
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=["neo4j"],
    zip_safe=False,
    include_package_data=True,
    setup_requires=["setuptools-pep8", "isort"],
    test_suite='tests',
)
