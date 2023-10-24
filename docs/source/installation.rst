Installation
============

.. admonition:: using herakoi on Windows
  :class: warning

  We tested ``herakoi`` only on macOS or some linux distributions. We know, however, that ``herakoi`` has been successfully installed on Windows machines too, but we can not guarantee that it will work properly. If you encounter any issues with the installation or with making `herakoi` run, please contact us.

``herakoi`` runs on python 3. To check whether you have already a working python build, you can try typing ``python3 --version``. If you get a message like ``Python 3.XX.YY`` (with ``XX`` and ``YY`` on the specific version), then you are ready to go!

The stable release of ``herakoi`` can be installed through `pip <https://pip.pypa.io/en/stable/>`_ simply as

.. code-block:: bash

  python -m pip install herakoi

This will install the main ``herakoi`` library, as well as all the dependencies required to let you sonify your favorite images.

From source
-----------

If you feel adventurous, you can instead give a try to the pre-release version. Since the source files of ``herakoi`` are hosted on `GitHub <https://github.com/lucadimascolo/herakoi>`_, you can directly clone the repository and install it from there:

.. code-block:: bash

  git clone https://github.com/lucadimascolo/herakoi.git
  cd herakoi
  python -m pip install -e . 

Please note that, in this case, many features might still be in an experimental stage, and might not work properly. If you find any bug, though, feel free to contact us by email or by commenting on the `GitHub issue tracker <https://github.com/lucadimascolo/herakoi/issues>`_.

