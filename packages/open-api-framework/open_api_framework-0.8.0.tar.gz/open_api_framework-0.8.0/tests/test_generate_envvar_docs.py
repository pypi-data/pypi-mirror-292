from unittest.mock import mock_open, patch

from django.core.management import call_command

EXPECTED_OUTPUT = """\
.. _installation_env_config:

===================================
Environment configuration reference
===================================



Available environment variables
===============================


Required
--------

* ``SECRET_KEY``: Secret key that's used for certain cryptographic utilities. Defaults to: \
``so-secret-i-cant-believe-you-are-looking-at-this``.


Optional
--------

* ``DEBUG``: Only set this to ``True`` on a local development environment. Various other \
security settings are derived from this setting!. Defaults to: ``False``.
* ``IS_HTTPS``: Used to construct absolute URLs and controls a variety of security settings. \
Defaults to the inverse of ``DEBUG``.





Specifying the environment variables
=====================================

There are two strategies to specify the environment variables:

* provide them in a ``.env`` file
* start the component processes (with uwsgi/gunicorn/celery) in a process
  manager that defines the environment variables

Providing a .env file
---------------------

This is the most simple setup and easiest to debug. The ``.env`` file must be
at the root of the project - i.e. on the same level as the ``src`` directory (
NOT *in* the ``src`` directory).

The syntax is key-value:

.. code::

   SOME_VAR=some_value
   OTHER_VAR="quoted_value"


Provide the envvars via the process manager
-------------------------------------------

If you use a process manager (such as supervisor/systemd), use their techniques
to define the envvars. The component will pick them up out of the box.
"""


def test_generate_envvar_docs():
    mock_file = mock_open()
    with patch(
        "open_api_framework.management.commands.generate_envvar_docs.open", mock_file
    ):
        call_command(
            "generate_envvar_docs", file="some/file/path.txt", exclude_group="Excluded"
        )

        mock_file.assert_called_once_with("some/file/path.txt", "w")

        handle = mock_file()

        # Check the entire content written to the mock file
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)

        assert written_content == EXPECTED_OUTPUT
