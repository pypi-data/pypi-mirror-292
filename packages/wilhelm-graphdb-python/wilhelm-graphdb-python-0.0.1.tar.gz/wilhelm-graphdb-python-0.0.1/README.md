Wilhelm Graph Database Python SDK
=================================

![Python Version][Python Version Badge]
[![Read the Docs][Read the Docs badge]][Read the Docs URL]
[![PyPI][PyPI project badge]][PyPI project url]
[![GitHub Workflow Status][GitHub Workflow Status badge]][GitHub Workflow Status URL]
[![Apache License badge]][Apache License URL]

Wilhelm Graph Database Python SDK offers a programmatic approach that offloads study sets from Quizlet and reloads them
into Graph Database, such as Neo4J and ArangoDB

To install the SDK, simply run

```console
pip install wilhelm-graphdb-python
```

Example Usage:

1. Make ready a Neo4J database instance. A free one can be obtained at https://console.neo4j.io
2. Set the following environment variables

   - `NEO4J_URI`- "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
   - `NEO4J_USERNAME`
   - `NEO4J_PASSWORD`

   where all of them are available 

3. Export a Quizlet set to a filed named __export.txt__, then
4. Load vocabulary into Neo4J database:

   ```python
   from wilhelm_graphdb_python.quizlet import processing_study_set
   from wilhelm_graphdb_python.neo4j_loader import load_into_database
   
   vocabulary = processing_study_set("export.txt")
   load_into_database(vocabulary)
   ```

License
-------

The use and distribution terms for [Wilhelm Graph Database Python SDK]() are covered by the [Apache License, Version 2.0].

<div align="center">
    <a href="https://opensource.org/licenses">
        <img align="center" width="50%" alt="License Illustration" src="https://github.com/QubitPi/QubitPi/blob/master/img/apache-2.png?raw=true">
    </a>
</div>

[Apache License badge]: https://img.shields.io/badge/Apache%202.0-F25910.svg?style=for-the-badge&logo=Apache&logoColor=white
[Apache License URL]: https://www.apache.org/licenses/LICENSE-2.0
[Apache License, Version 2.0]: http://www.apache.org/licenses/LICENSE-2.0.html

[GitHub Workflow Status badge]: https://img.shields.io/github/actions/workflow/status/QubitPi/wilhelm-graphdb-python/ci-cd.yml?logo=github&style=for-the-badge
[GitHub Workflow Status URL]: https://github.com/QubitPi/wilhelm-graphdb-python/actions/workflows/ci-cd.yml

[Python Version Badge]: https://img.shields.io/badge/Python-3.10-brightgreen?style=for-the-badge&logo=python&logoColor=white
[PyPI project badge]: https://img.shields.io/pypi/v/wilhelm-graphdb-python?logo=pypi&logoColor=white&style=for-the-badge
[PyPI project url]: https://pypi.org/project/wilhelm-graphdb-python/

[Read the Docs badge]: https://img.shields.io/readthedocs/wilhelm-graphdb-python?style=for-the-badge&logo=readthedocs&logoColor=white&label=Read%20the%20Docs&labelColor=8CA1AF
[Read the Docs URL]: https://wilhelm-graphdb-python.qubitpi.org
