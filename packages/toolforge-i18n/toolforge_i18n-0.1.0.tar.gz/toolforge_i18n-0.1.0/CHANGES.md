# Changelog

## 0.1.0 (2024-08-25)

Documentation improvements,
and a fix for tools that don’t use Flask and don’t have MarkupSafe installed.

There are no major changes in this release,
and no migration is necessary by tools when upgrading to this version,
but the 0.1.0 version number signifies that the library may now be used by others –
it’s no longer considered “early work in progress”, and using it is no longer discouraged.
(But it’s not 1.0.0 yet, so some rough edges should still be expected.)

## Pre-0.1.0 phase

Prior to the 0.1.0 release, toolforge_i18n was not ready for general use yet.
The following notes only give an overview of what changed,
and there are no migration instructions,
as nobody other than the author should have been using these versions of the library.

### 0.0.9 (2024-08-10)

Improve Read the Docs setup.
(Starting with this release, the documentation was successfully published on Read the Docs.)

### 0.0.8 (2024-08-10)

Add Sphinx-built docs.
(They were meant to be published on Read the Docs, but didn’t work yet.)

### 0.0.7 (2024-08-05)

Move Flask-related dependencies to `Flask` extra (which most tools should use).

### 0.0.6 (2024-07-31)

Re-export all members from `toolforge_i18n` (i.e. `__init__.py`)
and make all other modules internal.

### 0.0.5 (2024-07-21)

Republish of 0.0.3 / 0.0.4 with no user-visible changes.

### 0.0.4 (2024-07-21)

Republish of 0.0.3 with no user-visible changes.
Failed to publish to PyPI.

### 0.0.3 (2024-07-21)

Check translations on load by default,
rather than relying on tool developers always running `pytest`.
Failed to publish to PyPI.

### 0.0.2 (2024-07-07)

Improved translation tests,
automatically registering them with a pytest plugin
and showing nicer assertion messages.

### 0.0.1 (2024-06-04)

Initial release.
