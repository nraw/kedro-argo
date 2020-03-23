==========
Kedro-Argo
==========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov| |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/kedro-argo/badge/?style=flat
    :target: https://readthedocs.org/projects/kedro-argo
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/nraw/kedro-argo.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/nraw/kedro-argo

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/nraw/kedro-argo?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/nraw/kedro-argo

.. |requires| image:: https://requires.io/github/nraw/kedro-argo/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/nraw/kedro-argo/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/nraw/kedro-argo/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/nraw/kedro-argo

.. |coveralls| image:: https://coveralls.io/repos/github/nraw/argokedro/badge.svg?branch=master
   :alt: Coveralls Status
   :target: https://coveralls.io/github/nraw/argokedro?branch=master


.. |version| image:: https://img.shields.io/pypi/v/kedro-argo.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/kedro-argo

.. |wheel| image:: https://img.shields.io/pypi/wheel/kedro-argo.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/kedro-argo

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/kedro-argo.svg
    :alt: Supported versions
    :target: https://pypi.org/project/kedro-argo

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/kedro-argo.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/kedro-argo

.. |commits-since| image:: https://img.shields.io/github/commits-since/nraw/kedro-argo/v0.0.7.svg
    :alt: Commits since latest release
    :target: https://github.com/nraw/kedro-argo/compare/v0.0.7...master



.. end-badges

Converting kedro pipelines to argo pipelines.

* Free software: BSD 3-Clause License

Installation
============

::

    pip install kedro-argo

You can also install the in-development version with::

    pip install https://github.com/nraw/kedro-argo/archive/master.zip

Requirements
============

To be used with Kedro, so it's assumed this package is used with a Kedro project.
An image name is needed. You can generate one with Kedro-docker.
Argo CLI is needed for the deployment step.
As the workflow will be in Argo, all datasets should be somehow passed between containers or else the pipeline will fail.


Usage
============

When installed, argo should be visible under your kedro commands
::

    kedro

Get the kedro.yaml and the template file by running
::

   kedro argo IMAGE_NAME


You can now run:
::

   ytt -f templates > argo.yaml

or if you prefer in Docker:
::

   docker run --rm -it --name ytt -v $(pwd)/templates:/templates gerritk/ytt:latest -f /templates > argo.yaml

and finally
::

   argo submit --watch argo.yaml

Documentation
=============


https://kedro-argo.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
