"""JupyterLab server extension that adds a display name field to the login page."""

from __future__ import annotations
from typing import Any
import os
from tornado.web import RequestHandler
from jupyter_server import DEFAULT_TEMPLATE_PATH_LIST
from jupyter_server.serverapp import ServerApp
from jupyter_server.auth.identity import PasswordIdentityProvider, User


# Sets the module that defines _load_jupyter_server_extension()
def _jupyter_server_extension_points() -> list[dict[str, Any]]:
    return [{"module": "jupyterlab_display_name"}]


# Called when the JupyterLab server extension is loaded. Even though we perform actions
# in the import phase, this function is required for the server extension to work.
def _load_jupyter_server_extension(_server_app: ServerApp) -> None:
    pass


TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")
"""Path to the page templates provided by JupyerLab Display Names."""


class DisplayNamePasswordIdentityProvider(PasswordIdentityProvider):
    """Password identity provider that also accepts a display name to use."""

    def process_login_form(self, handler: RequestHandler) -> User | None:
        user = super().process_login_form(handler)
        display_name = handler.get_argument("display_name", default=None)
        if user is not None and display_name is not None:
            user.name = display_name
            user.display_name = display_name
            user.initials = "".join([n[0] for n in display_name.split(" ")])
        return user


# Add the path to a directory containing the modified login template
DEFAULT_TEMPLATE_PATH_LIST.insert(0, TEMPLATE_PATH)

# Change the default login provider to our custom display name provider
ServerApp.identity_provider_class.default_value = DisplayNamePasswordIdentityProvider
