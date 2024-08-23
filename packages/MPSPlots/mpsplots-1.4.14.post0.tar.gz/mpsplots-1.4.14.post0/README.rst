MPSPlots
========


|python|
|docs|
|unittest|
|PyPi|
|PyPi_download|


The library
***********

My personal Matplotlib[2D]/PyVista[3D] wrapper. Its aim is to offer a good compromise between ease-of-use and flexibility. I have started this library in order to uniformise my plots for scientific journal and as of today I continue to update and distribute the code.

----

Testing
*******

To test localy (with cloning the GitHub repository) you'll need to install the dependencies and run the coverage command as

.. code:: console

   >>> git clone https://github.com/MartinPdeS/MPSPlots.git
   >>> cd MPSPlots
   >>> pip install -r requirements/requirements.txt
   >>> coverage run --source=MPSPlots --module pytest --verbose tests
   >>> coverage report --show-missing

----

Contact Information
*******************

As of 2023 the project is still under development if you want to collaborate it would be a pleasure! I encourage you to contact me.

MPSPlots was written by `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdeS>`_  .

Email:`martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=MPSPlots>`_ .


.. |python| image:: https://img.shields.io/pypi/pyversions/mpsplots.svg
   :target: https://www.python.org/

.. |PyPi| image:: https://badge.fury.io/py/MPSPlots.svg
   :alt: PyPi package
   :target: https://pypi.org/project/MPSPlots/

.. |docs| image:: https://readthedocs.org/projects/mpsplots/badge/?
   :target: https://mpsplots.readthedocs.io/en/latest/
   :alt: Documentation Status

.. |unittest| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/MartinPdeS/f0955be398d59efac69042c1b0fbece2/raw/b0469e6a361cc54c19eca1f23662b3ad0b76b1ce/MPSPlotscoverage_badge.json
   :alt: Unittest coverage
   :target: https://github.com/MartinPdeS/MPSPlots/actions

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/MPSPlots.svg
   :target: https://pypistats.org/packages/mpsplots