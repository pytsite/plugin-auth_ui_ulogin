"""PytSite uLogin Authentication Driver Plugin
"""

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _init():
    from pytsite import tpl, lang
    from plugins import assetman, auth
    from ._driver import ULogin

    auth.register_auth_driver(ULogin())
    lang.register_package(__name__)
    tpl.register_package(__name__)

    assetman.register_package(__name__)
    assetman.js_module('pytsite-auth-ulogin-widget', __name__ + '@widget')
    assetman.t_js(__name__ + '@**')
    assetman.t_less(__name__ + '@**')


_init()
