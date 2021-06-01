.. :changelog:

History
-------

0.0.1 (08-10-2020)
---------------------

* First code creation


0.1.0 (26-03-2021)
------------------

* heavily refactored: created new modules (windows.py, application.py, and logging.py), created new class Effect() in Items.py, updated README, the two main attributes in CanvasFrame() renamed to canvas_landscape and canvas_status.


0.2.0 (30-03-2021)
------------------

* CommandWindow() added which provides an interface for the user to send commands, change_state_menu_bar_entry() method in MainWindow() added for changing state of menu bar entries, and more comments added and docstrings filled out


0.2.1 (11-04-2021)
------------------

* added docstrings for the Adapters() in helpers.py + updated pipfile to point to newer version of powermolelib (3.0.2)


0.2.2 (18-05-2021)
------------------

* Refactor main window code for simplicity and readability


0.2.3 (25-05-2021)
------------------

* Add code to make Agent's movement more accurate, refactor a bunch of public methods into protected ones, add docstrings for all canvas items, remove the creation of the canvas item objects during initialization, and remove the scaling feature


0.2.4 (01-06-2021)
------------------

* Rename status messages in status banner, update documentation, update dependency to latest powermole library package, and add heartbeat interval value
