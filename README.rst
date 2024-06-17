ShowCase Browser - v3
#####################


.. image:: https://raw.githubusercontent.com/srccircumflex/docs/main/showcase-logo.png
    :align: left
    :width: 120px
    :target: https://github.com/srccircumflex/ShowCase-Browser

This minimalistic program turns any website or other document into a stand-alone application.

Coded with the PyQt6_ package (The QtGroup_) and powered by chromium_.

.. image:: https://raw.githubusercontent.com/srccircumflex/docs/main/sep.png
    :align: center

Install and Run
***************

Use the module ``pip`` to install the ``showcase_browser`` package:

::

    python -m pip install showcase-browser --upgrade

This installs all the required packages and creates the shell command

::

    showcase

and you can execute:

::

    showcase github.com

..

  See also Troubleshooting_


Features
********

All optional features are deactivated by default.

For an overview of the command line parameters execute:

::

    showcase --help


Examples
========

Add Browser Basis Widgets
-------------------------

::

    showcase github.com --wg-url --wg-back --wg-forward --wg-refresh --wg-stop --wg-home --home-url google.com

Add Browser Tabs
----------------

::

    showcase github.com --wg-tabs --wg-tabs-close --wg-tabs-add --tabs-default-url google.com --tabs-dynamic-labels --tabs-keep-last


Communicator
------------

For the possibility to use ``showcase`` dynamically in scripts, a socket is
installed with the flag ``--com`` which enables remote control from another process.

::

    showcase github.com --com --window-title "my app" --window-maxsize

Now some commands can be executed from another process (Shell/Terminal/Cmd) to control the ``showcase``.

::

    showcase https://pypi.org/ --com-try

Troubleshooting
***************

Under Linux, the following error may occur during execution::

    qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
    qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
    This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

    Available platform plugins are: wayland-egl, xcb, vkkhrdisplay, wayland, vnc, linuxfb, offscreen, eglfs, minimal, minimalegl.

Fix it by installing the required packages::

    sudo apt-get install -y libxcb-cursor-dev





.. _PyQt6: https://pypi.org/project/PyQt6/
.. _QtGroup: https://www.qt.io/
.. _chromium: https://www.chromium.org/Home/

