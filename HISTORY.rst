Release notes
=============

0.3.0
-----

* Add argument permitting annotation uploads in ZIP format.

0.2.3
-----

* Using the package requests[security] rather than requests to avoid download errors with python versions < 2.7.9
* For the download, passing the timeout and the max_try in parameters. Using shutil.copyfileobj to write file on disk

0.2.2
-----

* When sending a task, queue name must be given.

0.2.1
-----

* Honors a new key value called callback_url which is called at the end of a
  task.

0.2.0
-----

* py3k compatible

0.1
---

* First release
