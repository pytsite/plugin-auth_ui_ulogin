"""PytSite uLogin Authentication Driver Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import json as _json
from time import strptime as _strptime
from datetime import datetime as _datetime
from urllib.request import urlopen as _urlopen
from pytsite import tpl as _tpl, lang as _lang, router as _router, html as _html, http as _http
from plugins import widget as _widget, auth as _auth, auth_ui as _auth_ui, file as _file, form as _form


class _LoginWidget(_widget.Abstract):
    """uLogin Widget
    """

    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, **kwargs)

        self._css += 'widget-ulogin'

    def _get_element(self, **kwargs) -> _html.Element:
        return _html.TagLessElement(_tpl.render('auth_ui_ulogin@widget', {'widget': self}))


class _LoginForm(_form.Form):
    """uLogin Login Form
    """

    def _on_setup_widgets(self):
        """_setup() hook.
        """
        self.add_widget(_widget.input.Hidden(
            uid=self.uid + '-widget-ulogin-token',  # It is important ID format fo JS code. Don't change!
            form_area='hidden',
        ))

        # uLogin widget
        self.add_widget(_LoginWidget(
            uid=self.uid + '-widget-ulogin',  # It is important ID format fo JS code. Don't change!
        ))

        # Submit button is not necessary, form submit performs by JS code
        self.remove_widget('action_submit')


class Auth(_auth.driver.Authentication):
    """ULogin Auth Driver
    """

    def get_name(self) -> str:
        """Get name of the driver
        """
        return 'ulogin'

    def get_description(self) -> str:
        """Get description of the driver
        """
        return 'uLogin'

    def sign_up(self, data: dict) -> _auth.model.AbstractUser:
        # Searching for token in input data
        token = data.get('token')
        if not token:
            for k, v in data.items():
                if k.endswith('token'):
                    token = v
                    break

        if not token:
            raise ValueError('No uLogin token received')

        # Getting user's data from uLogin
        response = _urlopen('http://ulogin.ru/token.php?token={}&host={}'.format(token, _router.request().host))
        if response.status != 200:
            raise _auth.error.AuthenticationError("Bad response status code from uLogin: {}.".format(response.status))
        ulogin_data = _json.loads(response.read().decode('utf-8'))
        if 'error' in ulogin_data:
            raise _auth.error.AuthenticationError("Bad response from uLogin: '{}'.".format(ulogin_data['error']))
        if 'email' not in ulogin_data or ulogin_data['verified_email'] != '1':
            raise _auth.error.AuthenticationError("Email '{}' is not verified by uLogin.".format(ulogin_data['email']))

        email = ulogin_data['email']

        try:
            user = _auth.get_user(email)
            is_new_user = False

        except _auth.error.UserNotFound:
            # User is not exists and its creation is not allowed
            if not _auth.is_sign_up_enabled():
                raise _auth.error.AuthenticationError(_lang.t('auth_ui_ulogin@signup_is_disabled'))
            else:
                # New users can be created only by system user
                _auth.switch_user_to_system()

                # Create new user
                user = _auth.create_user(email)
                is_new_user = True

        # As soon as user created or loaded, set it as current
        _auth.switch_user(user)

        # Picture
        if is_new_user:
            current_pic = user.picture
            picture_url = ulogin_data.get('photo_big')
            if not picture_url:
                picture_url = ulogin_data.get('photo')

            # Replace existing picture with provided by uLogin
            if picture_url:
                user.picture = _file.create(picture_url)
                current_pic.delete()

        # Name
        if not user.first_name:
            user.first_name = ulogin_data.get('first_name')
        if not user.last_name:
            user.last_name = ulogin_data.get('last_name')

        # Alter nickname
        if is_new_user:
            user.nickname = user.first_last_name

        # Gender
        if user.gender not in ('m', 'f') and 'sex' in ulogin_data:
            user.gender = 'f' if int(ulogin_data['sex']) == 1 else 'm'

        # Birth date
        if 'bdate' in ulogin_data:
            try:
                b_date = _strptime(ulogin_data['bdate'], '%d.%m.%Y')
                user.birth_date = _datetime(*b_date[0:5])
            except ValueError:
                # Yes, sometimes uLogin provides strange data here :(
                pass

        # Link to profile
        if 'profile' in ulogin_data and ulogin_data['profile']:
            user.urls = user.urls + (ulogin_data['profile'],)

        # Options
        options = dict(user.options)
        options['ulogin'] = ulogin_data
        user.options = options

        user.save()

        return user

    def sign_in(self, data: dict) -> _auth.model.AbstractUser:
        """Authenticate user.
        """
        return self.sign_up(data)

    def sign_out(self, user: _auth.model.AbstractUser):
        """Sign out user
        """
        pass


class UI(_auth_ui.Driver):
    def get_name(self) -> str:
        """Get name of the driver
        """
        return 'ulogin'

    def get_description(self) -> str:
        """Get description of the driver
        """
        return 'uLogin'

    def get_sign_up_form(self, request: _http.Request, **kwargs) -> _form.Form:
        """Get the sign up form form.
        """
        return _LoginForm(request, **kwargs)

    def get_sign_in_form(self, request: _http.Request, **kwargs) -> _form.Form:
        """Get the sign in form form.
        """
        return self.get_sign_up_form(**kwargs)

    def get_restore_account_form(self, request: _http.Request, **kwargs):
        """Get account restoration form
        """
        raise NotImplementedError('uLogin does not support account restoration')
