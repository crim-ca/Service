Service development guide for Vesta infrastructure
==================================================

This section is intended to help a developer wanting to add a new service to an existing Vesta infrastructure.

Essentially a service can be seen as a program which can process input data and produce output and exist in a semi-standalone deployment and stateless form. In the context of the Vesta infrastructure, input is generally defined as a multimedia document referenced by a URL and the output is a series of annotations produced by the given program conforming to an arbitrary annotations schema. It receives it's commands to process documents from a `Service Gateway <http://services.vesta.crim.ca/docs/sg/latest/>`_ which acts as a unified interface by a pub-sub messenging scheme implemented on AMQP and using the `Celery <http://www.celeryproject.org/>`_ library. To facilitate development of a new service type, we offer this package, which is essentially a wrapper which normalises input from the Celery library.

Celery is a Python library. The only current implementation of Celery is in fact in Python. This currently limits the development of Vesta Services to the Python language. Nonetheless, Python can be integrated to a number of other languages through foreign interface calls such as `CFFI <https://cffi.readthedocs.org/en/latest/>`_ or more native approaches such as `ctypes <https://docs.python.org/2/library/ctypes.html>`_ for C and C++ calls, `swig <http://www.swig.org/>`_ wrappers for multi-language bindings, `Jython <http://www.jython.org/>`_ for Java code, `IronPython <http://ironpython.net/>`_ for .NET programs and so forth. Another valid approach is simply by forking subprocesses and wrapping an existing program. With this in mind one can seek integration mechanisms to expose one's existing code base in another language to the Python Vesta and Celery wrapper without many challenges.

The Vesta Service wrapper package is available online on github at the following address: https://github.com/crim-ca/Service .  This wrapper is a Python package which can be used as a standalone deployment (using the setup.py file) or can be simply used by cloning this package in a code base which will use relative imports to access the functionality provided by this package. If this second option is chosen, one should use whichever method one desires to package and distribute the resulting application (Python *.whl* file, Docker image, etc.)

.. note:: The resulting name of the package containing the source will depend on the method used to install this source. If you simply clone this package using version control using default values, the package will be cloned as "Service" whereas if you ask pip to install this package the resulting package name will be named "VestaService". This is because there was a prior package with the name "Service" on the Python Packaging Index and declaring a dependency on a package hosted on github with the same name and version as a package existing on PyPi unnecessarily complexified the installation process of any new package with a dependency on this source. A method which could be used to use a uniform name might be to specify a clone destination with the name "VestaService". (See git documentation).

Using and starting the service is done through the `Celery application interface <http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#application>`_ for which the Vesta infrastructures sets a certain number of norms. These are the following:

* The name of the Celery task is arbitrary but should be the same as is defined in the configuration of the Service Gateway so that calls to the Service Gateway result in a call to the Celery Task. Furthermore, it is customary to prepend to the name of the service the string "worker." to denote the fact that this is a worker for a service. Again, this is defined in the configuration of the Service Gateway.
* Parameters which were given to the Service Gateway are passed along to the Service Celery Task in a pre-defined structure and is meant to be parsed by the Service package module. It's values are then accessible through a wrapper object. The class is named Service.Request and uses the arguments passed along by the Service Gateway to the Celery Task method. Useful fields are:

   :process_version: Can be set to reflect the version of the process of the service which is being run. Generally used to double-check the resulting data's process version with the declared one in the Gateway's configuration.
   :set_progress: Callback method which is provided to give the Gateway information on task advancement and progress.
   :document: An object giving information on the document to process. Contains the following fields:

      :local_document: A local file name which contains a local copy of the document.
      :url: The original URL from which the copy was obtained.

* Use of the Python logging interface is highly recommended so that distributed instances can produce logs to a centralised instance (Syslog for instance). Furthermore, Celery provides a task logger which injects contextual information for the task execution in the log messages. This is also highly recommended.
* Resulting annotations in the context of the Vesta infrastructure uses `JSON-LD <http://json-ld.org/>`_ annotations format. Typically one can save the annotations to a `JASS : JSON-LD Annotations Storage System <http://services.vesta.crim.ca/docs/jass/latest/>`_ which might be deployed in the context of a given infrastructure. Care must be taken to define a valid JSON-LD schema and place a copy of that schema in a public HTTP repository and include a link to that schema within the produced annotations.

Consider the following example:

.. code-block:: python

   #!/usr/bin/env python
   # coding:utf-8

   """
   Service worker module example code
   """

   # --Project specific----------------------------------------------------------
   from .my_module import my_function
   from VestaService.request import Request  # Use Vesta Service wrapper

   # --3rd party modules----------------------------------------------------------
   from celery.utils.log import get_task_logger  # Obtain task logger from Celery
   from celery import Celery, current_task  # Use Celery and get handle on task

   # --Configuration-------------------------------------------------------------
   PROCESS_NAME = 'worker.my_process'  # Set Celery task name
   APP = Celery(PROCESS_NAME)  # Instantiate Celery Application.


   @APP.task(name=PROCESS_NAME)
   def process(body):
       """
       Function that serves the actual functionality through a Celery
       task.

       :param body: Body of request message as defined by Service Gateway.
       :returns: List of annotations.
       """
       # Hook our packages / modules into the task logger hierarchy
       logger = get_task_logger('.my_module')

       logger.info("Starting work")
       request = Request(body, current_task)  # Parse arguments.

       request.process_version = '0.1.2'  # Inject version number.

       # Launch the processing on downloaded local copy of document.
	   annotations = my_function(request.document, request.set_progress)

       # Optional : Send annotations to a JASS.
       request.store_annotations(annotations)

       return annotations

This example, which might be a fully functional service in a file named *my_package/my_worker.py*, would be associated with a Service Gateway configuration entry in which we might find the following directives:

.. code-block:: python


   WORKER_SERVICES = {
    'my_service': {
        # Keyword used in the rest api to access this service
        # (ex.: http://server/<route_keyword>/info)
        # Set to '.' to access this service without keyword
        # (ex.: http://server/info)
        'route_keyword': 'my_service',

        # The celery task name.
        # Must match the task in the worker app name : <proj_name>.<task_name>
        # (ex.: worker.matching)
        'celery_task_name': 'my_process',

        # The celery queue name.
        # Must match the queue name specified when starting the worker
        # (by the -Q switch)
        # Kept separate from production
        'celery_queue_name': 'my_process',

        # Following parameters are required by the CANARIE API (info request)
        'name': 'my service',
        'synopsis': "RESTful service providing glory, joy and thrill.",
        'version': "0.1.2",  # Expected version - will check.
        'institution': 'My Institution',
        'releaseTime': '2015-01-01T00:00:00Z',
        'supportEmail': 'me@my.institution',
        'category': "Data Manipulation",
        'researchSubject': "Joy generation",
        'tags': "joy, thrill, glory, data",

        # The following parameters are used to respond to some CANARIE API
        # request.
        #
        # They must be one of the following:
        #  - A valid URL to perform a redirection
        #  - A relative template file that will be used to generate the HTML
        #    page (relative to the templates directory)
        #  - A response string and the html status separated by a comma that
        #    will be used  to make a response to the requested element. Ex.:
        #    'Not available,404'
        'home': "http://my.institution/blah.html",
        'doc': "http://my.institution/blah.html",
        'releasenotes': "http://my.institution/blah.html",
        'support': "http://my.institution/blah.html",

        # If the source are not provided, CANARIE requires a 204 (No content)
        # response
        'source': ",204",
        'tryme': "http://my.institution/blah.html",
        'licence': "http://my.institution/blah.html",
        'provenance': "http://my.institution/blah.html",
    },
   }

The service Gateway configuration can contain many entries for multiple service types and can contain many other directives. See documentation of the Service Gateway for more information.

Will the previous two code elements, a service worker instance could be linked to a given instance of a service Gateway and hence accessible through the Gateway. This of course requires that an instance of AMQP (RabbitMQ) be shared by the two. Celery can use a configuration file to specify which AMQP server to use (see Celery documentation). A bare bones example of a configuration file might be the following:

.. code-block:: python

   """
   Configuration values for worker processes.
   """

   # Broker settings ------------------------------------------------------------
   BROKER_URL = 'amqp://localhost//'
   CELERY_RESULT_BACKEND = 'amqp://'
   CELERY_TASK_RESULT_EXPIRES = 7200  # 2 hours.

   # Result backend settings ----------------------------------------------------
   CELERY_TASK_SERIALIZER = 'json'
   CELERY_RESULT_SERIALIZER = 'json'
   CELERY_ACCEPT_CONTENT = ['json']

   # Worker settings ------------------------------------------------------------
   CELERY_SEND_EVENTS = True
   CELERYD_CONCURRENCY = 2
   CELERYD_PREFETCH_MULTIPLIER = 1

   # Logging settings -----------------------------------------------------------
   CELERYD_TASK_LOG_FORMAT = ("[%(asctime)s: %(levelname)s/%(processName)s] "
                              "[%(task_name)s(%(task_id)s)] - %(name)s - "
                              "%(message)s")

   CELERYD_LOG_FORMAT = ("[%(asctime)s: %(levelname)s/%(processName)s] "
                         "- %(name)s - %(message)s")

Saved in a document named as *celeryconfig.py*, one could start the Service through Celery such as :

.. code-block:: bash

   celery worker -A my_package.my_worker -l INFO -c 1 -E --config=celeryconfig -Q my_process

This would start up the worker and listen for incoming tasks through Celery. See Celery documentation for more options. When calling the Service Gateway with an associated document, the Request class constructor would download the document and the resulting annotations would be sent back to the Gateway through Celery which could be accessed by the HTTP caller or fetched on the optional JASS backend.


