"""PytSite uLogin Authentication Driver Plugin
"""

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def plugin_load():
    from pytsite import lang
    from plugins import assetman

    lang.register_package(__name__)
    assetman.register_package(__name__)

    assetman.js_module('auth-ulogin-widget', __name__ + '@widget')
    assetman.t_js(__name__)
    assetman.t_less(__name__)


def plugin_load_uwsgi():
    from pytsite import tpl
    from plugins import auth, auth_ui
    from . import _driver

    tpl.register_package(__name__)
    auth.register_auth_driver(_driver.Auth())
    auth_ui.register_driver(_driver.UI())
