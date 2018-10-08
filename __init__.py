"""PytSite uLogin Authentication Driver Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def plugin_load_wsgi():
    from plugins import auth, auth_ui
    from . import _driver

    auth.register_auth_driver(_driver.Auth())
    auth_ui.register_driver(_driver.UI())
