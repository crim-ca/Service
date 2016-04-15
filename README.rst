This package offers helper modules for services working in a distributed
Service architecture. The work being executed by these services might be an
annotation process or a form of conversion process taking a significant amount
of time thereby benefiting from a distributed processing system with a REST
interface.

Messages are communicated through a `Celery <http://www.celeryproject.org/>`_
distributed processing queue system. Celery can be configured to run with
various backends such as RabbitMQ or Reddis. It is mainly meant to work with
the Vesta `Service Gateway <http://services.vesta.crim.ca/docs/SG/latest/>`_ .

Requirements / installation
---------------------------

This package uses Python version 2.x.x .

Python requirements are in file «requirements.txt» and can be installed with
the following command::

    pip install -r requirements.pip

This package is meant to be used in-place, meaning it does offer an
installation procedure to be used as a standalone distribution. When creating a
new project, simply clone this package in your source tree and refer to the
proper package with the Python *import* statement. Furthermore, care should be
taken to include the requirements into one's installation procedure. e.g.
setup.py .
