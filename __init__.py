"""PytSite uLogin Authentication Driver Plugin
"""

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _register_assetman_resources():
    from plugins import assetman

    if not assetman.is_package_registered(__name__):
        assetman.register_package(__name__)
        assetman.js_module('auth-ulogin-widget', __name__ + '@widget')
        assetman.t_js(__name__)
        assetman.t_less(__name__)

    return assetman


def plugin_install():
    assetman = _register_assetman_resources()
    assetman.build(__name__)
    assetman.build_translations()


def plugin_load():
    from pytsite import lang

    _register_assetman_resources()
    lang.register_package(__name__)


def plugin_load_uwsgi():
    from pytsite import tpl
    from plugins import auth, auth_ui
    from . import _driver

    tpl.register_package(__name__)
    auth.register_auth_driver(_driver.Auth())
    auth_ui.register_driver(_driver.UI())
