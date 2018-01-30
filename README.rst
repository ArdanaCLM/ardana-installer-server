..
 (c) Copyright 2018 SUSE LLC

==============================
Ardana Installer Server
==============================

REST server for Ardana cloud installer

---------------
Getting Started
---------------

Start the service using::

   Use 'tox -e runserver' to start the server (on port 8081)

---
API
---

All REST endpoints begin with ``/api/v1``.  The following endpoints are
supported:

  ``/api/v1/progress`` (``GET`` or ``POST``)
       Data to track the progress of the installer.

  ``/api/v1/server`` (``GET``,``POST``,``PUT``,``DELETE``)
       Scratch space for general server details

  ``/api/v1/sm/servers`` (``GET``)
       Retrieves a list of servers from SUSE Manager

  ``/api/v1/sm/servers/{id}`` (``GET``)
       Retrieves the details of the given server from SUSE Manager

  ``/api/v1/ov/servers`` (``GET``)
       Retrieves a list of servers from HPE OneView

  ``/api/v1/ov/servers/{id}`` (``GET``)
       Retrieves the details of the given server from HPE OneView

  ``/api/v1/clm/...``
       Requests to this URL are forwarded to the corresponding
       endpoint under ``/api/v2`` in the Ardana Service
