Usage
=================

Upon the first start a copy of a pristine application and logging configuration are created in the user's home directory ``~/.AdNITC/``. From this point on configuration files are read from this location. See see :ref:`configuration` section for more information.


This script downloads the specified calendars and parses all events in them. For each event, it will try to create a corresponding ITC entry. In order to do so, the calendar items need to be enhanced with some special information, targeted specially to the ITC system of AdNovum.

* The *Title* of an event automatically gets copied to the **comment** section of the corresponding ITC entry.
* The *Comment* of an event can be used as  normally but should contain somewhere the following block::

    ################
    itctag:UBS STMP.Wave_25:dev
    ticket:STMPPLAT-16969
    jira:true
    zimbra:false
    ################

* not all information is mandatory:

 * ``itctag`` is mandatory.
 * ``ticket`` is optional, if not specified nothing will be written to the ticket field of the ITC system.
 * ``jira`` is optional and defaults to false
 * ``zimbra`` is optional and defaults to false

* It does not matter how many ``#######`` you use, but you need to put at least 3 of them. Before and after this section you can put wathever text you want.


.. _configuration:

Configuration
--------------
Upon the first launch, the script creates the ``~/.AdNITC/`` directory containing:
* logging.conf where the logger is configured
* adnitc.conf where the general configuration is stored. Adapt at least the ``<calendars>``, ``<calendarurl>`` of the specified calendar, ``<itcurl>`` and ``<user>`` properties to get started. The script will interactively ask for passwords when the ``<user>`` tag is set for the *ITC* section or for a *Calendar* section.

The example below shows what such a file could look like::

    [Config]
    # Comma-separated list of calendars to parse for ITC events
    calendars: cal1
    # Shall we first try to do bulk updates (this is the preferred method)
    usebulk: true
    # Verify SSL certificates
    verifyssl: true

    [cal1]
    # Replace XXX with your username
    url: http://adnzimzh.zh.adnovum.ch:8080/home/XXX@zimbra.adnovum.ch/Calendar

    [cal2]
    # If a resource requires authentication (basic auth) you can specify
    # the crendentials with user and pass.
    # if you omit the password, then adnitc will ask for it interactively.
    url: https://example.com/my_hard_work.ics
    user: XXX
    pass: ZZZ

    [ITC]
    # adnitc will aks for the password interactively.
    url: https://aww.adnovum.ch/itc
    user: XXX

The config file has 3 sections *Config* where general options sit, *cal1* contains url and credentials for the first calendar and *ITC* specifies url and credentials for the ITC system.

.. _debugging_and_logging:

Debugging and Logging
---------------------
As the script is run, this folder will also host a ``adnitc.log`` file, containing the log of the *last* run.
