###############
Using in Docker
###############


**********
Installing
**********


Installing from Dockerhub
=========================

By default, we create few tags:

#. ``latest`` - Latest project release.
#. ``dev`` - Latest possible project version.
   Use only for testing, always can have breaking changes.
#. ``x.y.z`` - Project release in `Semantic Versions
   <https://semver.org/>`_ style.

Every of those tags also have duplicates with database suffixes, at now
it is can be ``sqlite``, ``mysql`` and ``postgresql``. As example, for tag
``latest`` also will be available tag ``latest-sqlite``.

Tag without suffix - standard database. At now, it is ``sqlite``.
It means that tag ``latest`` give the same as ``latest-sqlite``.

.. note::
  There are few deprecated tags, which are still available only for history. It is
  :ref:`main <pages/changelog:version 0.1.0>`,
  :ref:`rewrite <pages/changelog:version 0.2.0>` and
  :ref:`newdb <pages/changelog:version 0.3.0>`.

.. warning::
  If you use not ``sqlite``, you need to apply database migrations manually.
  In ``sqlite`` migrations are applied automatically while we compile image.
  See :ref:`index:database migrations` for details.

.. seealso::
  `Our page on Dockerhub with all available tags.
  <https://hub.docker.com/r/perchunpak/pingerbot/tags>`_


Self compilation
================

Also, you can compile images from project's root.

To do this, you just need to run the command:

.. code-block:: bash

  docker build -t perchunpak/pingerbot . --build-arg dialect=sqlite

Where ``--build-arg dialect=sqlite`` - parameter, which defines database,
what you want to use. Instead of ``sqlite`` you can set any supported.

.. warning::
  If you use not ``sqlite``, you need to apply database migrations manually.
  In ``sqlite`` migrations are applied automatically while we compile image.
  See :ref:`index:database migrations` for details.

***
Run
***

To run the bot, in both cases of installation, use this command:

.. code-block:: bash

  docker run --name pingerbot -d perchunpak/pingerbot

.. note::
  If you want to use ``sqlite``, you also need to set
  ``-v YOUR_FOLDER:/app/pinger/data`` option (Where ``YOUR_FOLDER`` it is a
  folder with your database file. I recommend set absolute path.)
  This is needed to save database in case of container restart.

  This parameter **must** be set between ``-d`` flag and ``perchunpak/pingerbot``.

.. warning::
  You also need to set ``-e`` option for every configuration parameter.
  This option just set environment variables, interface will be the same as
  in ``config.yml``, but all parameters keys in upper case.

  They should be used like ``-e KEY=VALUE``, where ``KEY`` upper cased key
  from ``config.yml`` (example ``DISCORD_TOKEN``), and ``VALUE`` is a value.

  Same as ``-v`` option, they **must** be set between ``-d`` flag and
  ``perchunpak/pingerbot``.

.. warning::
  Since version 0.4.0 the container runs in non-root mode, which means that
  if you use the sqlite tag and a ``-v`` option you have to give rights
  to the folder. This can be done with the command ``chown -R 5000:5000 <your folder>``.

  .. note:: Doesn't applies to Windows users.

.. seealso::
  `podman <https://podman.io>`_ as replacement for a Docker.

.. seealso::
  Command

  .. code-block:: bash

    docker run --help

  For full list of arguments and possibilities, upper I wrote only basics.
