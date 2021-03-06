# coding: utf-8

from flask import current_app
from flask.ext.wtf import TextField, PasswordField, BooleanField
from flask.ext.wtf import TextAreaField
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf import Required, Email, Length, Regexp, Optional
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm
from ..models import Account


__all__ = [
    'SignupForm', 'SigninForm', 'SettingForm',
    'FindForm', 'ResetForm',
]


RESERVED_WORDS = [
    'root', 'admin', 'bot', 'robot', 'master', 'webmaster',
    'account', 'people', 'user', 'users', 'project', 'projects',
    'search', 'action', 'favorite', 'like', 'love',
    'team', 'teams', 'group', 'groups', 'organization',
    'organizations', 'package', 'packages', 'org', 'com', 'net',
    'help', 'doc', 'docs', 'document', 'documentation', 'blog',
    'bbs', 'forum', 'forums', 'static', 'assets', 'repository',

    'public', 'private',
    'mac', 'windows', 'ios', 'lab',
]


class SignupForm(BaseForm):
    username = TextField(
        _('Username'), validators=[
            Required(), Length(min=3, max=20),
            Regexp(r'^[a-z0-9A-Z]+$')
        ], description=_('English Characters Only.'),
    )
    email = EmailField(
        _('Email'), validators=[Required(), Email()]
    )
    password = PasswordField(
        _('Password'), validators=[Required()]
    )

    def validate_username(self, field):
        data = field.data.lower()
        if data in RESERVED_WORDS:
            raise ValueError(_('This name is a reserved name.'))
        if data in current_app.config.get('RESERVED_WORDS', []):
            raise ValueError(_('This name is a reserved name.'))
        if Account.query.filter_by(username=data).count():
            raise ValueError(_('This name has been registered.'))

    def validate_email(self, field):
        if Account.query.filter_by(email=field.data.lower()).count():
            raise ValueError(_('This email has been registered.'))

    def save(self):
        user = Account(**self.data)
        user.save()
        return user


class SigninForm(BaseForm):
    account = TextField(
        _('Account'), validators=[Required(), Length(min=3, max=20)]
    )
    password = PasswordField(
        _('Password'), validators=[Required()]
    )
    permanent = BooleanField(_('Remember me for a month.'))

    def validate_password(self, field):
        account = self.account.data
        if '@' in account:
            user = Account.query.filter_by(email=account).first()
        else:
            user = Account.query.filter_by(username=account).first()

        if not user:
            raise ValueError(_('Wrong account or password'))
        if user.check_password(field.data):
            self.user = user
            return user
        raise ValueError(_('Wrong account or password'))


class SettingForm(BaseForm):
    screen_name = TextField(_('Display Name'), validators=[Length(max=80)])
    description = TextAreaField(
        _('Description'), validators=[Optional(), Length(max=400)],
        description=_('Markdown is supported.')
    )


class FindForm(BaseForm):
    account = TextField(
        _('Account'), validators=[Required(), Length(min=3, max=20)],
        description=_('Username or email address')
    )

    def validate_account(self, field):
        account = field.data
        if '@' in account:
            user = Account.query.filter_by(email=account).first()
        else:
            user = Account.query.filter_by(username=account).first()
        if not user:
            raise ValueError(_('This account does not exist.'))
        self.user = user


class ResetForm(BaseForm):
    password = PasswordField(
        _('Password'), validators=[Required()],
        description=_('Remember your password')
    )
