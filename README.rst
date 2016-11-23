Build status: https://travis-ci.org/crim-ca/Service.svg?branch=master

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

This package can be used in-place, by simply cloning this package in your
source tree and refering to the proper package with the Python *import*
statement.

Python requirements are in file «requirements.txt» and can be installed with
the following command::

    pip install -r requirements.txt

Furthermore, care should be taken to include the requirements into one's
installation procedure. e.g. setup.py .

Alternatively, one can simply use this package's installation procedure such
as::

   pip install git+https://github.com/crim-ca/Service

Which should install all requirements such as Celery.
