.. image:: https://travis-ci.org/crim-ca/Service.svg?branch=master

This package offers helper modules for Vesta services working in a distributed
Service architecture. The work being executed by these services might be an
annotation process or a form of conversion process taking a significant amount
of time thereby benefiting from a distributed processing system with a REST
interface.

Messages are communicated through a `Celery <http://www.celeryproject.org/>`_
distributed processing queue system. Celery can be configured to run with
various backends such as RabbitMQ or Reddis. It is mainly meant to work with
the Vesta `Service Gateway <http://services.vesta.crim.ca/docs/sg/latest/>`_ .

Requirements / installation
---------------------------

This package uses Python version 2.x.x but should be compatible with Py3K. 
Tox tests are run regurlarly through the TravisCI on github. See the tox.ini
configuration file.

You can install the package from the Python package index such as::

   pip install VestaService
   
Alternatively one can install this package from source such as::

   pip install git+https://github.com/crim-ca/Service

Which should install all requirements such as Celery.

You can also install from a cloned version.

See the documentation for pip for more installation use cases.

Contribution
------------

Pull requests are most welcome. Please ensure you follow pep8 for any 
modifications.
