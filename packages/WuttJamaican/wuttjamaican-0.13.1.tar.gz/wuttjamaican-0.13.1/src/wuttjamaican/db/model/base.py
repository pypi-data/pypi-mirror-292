# -*- coding: utf-8; -*-
################################################################################
#
#  WuttJamaican -- Base package for Wutta Framework
#  Copyright © 2023-2024 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Base Models

.. class:: Base

   This is the base class for all data models.
"""

import sqlalchemy as sa
from sqlalchemy import orm

from wuttjamaican.util import make_uuid


# nb. this convention comes from upstream docs
# https://docs.sqlalchemy.org/en/14/core/constraints.html#constraint-naming-conventions
naming_convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}

metadata = sa.MetaData(naming_convention=naming_convention)


class ModelBase:
    """ """

    def __iter__(self):
        # nb. we override this to allow for `dict(self)`
        state = sa.inspect(self)
        fields = [attr.key for attr in state.attrs]
        return iter([(field, getattr(self, field))
                     for field in fields])

    def __getitem__(self, key):
        # nb. we override this to allow for `x = self['field']`
        state = sa.inspect(self)
        if hasattr(state.attrs, key):
            return getattr(self, key)


Base = orm.declarative_base(metadata=metadata, cls=ModelBase)


def uuid_column(*args, **kwargs):
    """
    Returns a UUID column for use as a table's primary key.
    """
    kwargs.setdefault('primary_key', True)
    kwargs.setdefault('nullable', False)
    kwargs.setdefault('default', make_uuid)
    return sa.Column(sa.String(length=32), *args, **kwargs)


def uuid_fk_column(target_column, *args, **kwargs):
    """
    Returns a UUID column for use as a foreign key to another table.

    :param target_column: Name of the table column on the remote side,
       e.g. ``'user.uuid'``.
    """
    return sa.Column(sa.String(length=32), sa.ForeignKey(target_column), *args, **kwargs)


class Setting(Base):
    """
    Represents a :term:`config setting`.
    """
    __tablename__ = 'setting'

    name = sa.Column(sa.String(length=255), primary_key=True, nullable=False, doc="""
    Unique name for the setting.
    """)

    value = sa.Column(sa.Text(), nullable=True, doc="""
    String value for the setting.
    """)

    def __str__(self):
        return self.name or ""


class Person(Base):
    """
    Represents a person.

    The use for this table in the base framework, is to associate with
    a :class:`~wuttjamaican.db.model.auth.User` to provide first and
    last name etc.  (However a user does not have to be associated
    with any person.)

    But this table could also be used as a basis for a Customer or
    Employee relationship etc.
    """
    __tablename__ = 'person'

    uuid = uuid_column()

    full_name = sa.Column(sa.String(length=100), nullable=False, doc="""
    Full name for the person.  Note that this is *required*.
    """)

    first_name = sa.Column(sa.String(length=50), nullable=True, doc="""
    The person's first name.
    """)

    middle_name = sa.Column(sa.String(length=50), nullable=True, doc="""
    The person's middle name or initial.
    """)

    last_name = sa.Column(sa.String(length=50), nullable=True, doc="""
    The person's last name.
    """)

    users = orm.relationship(
        'User',
        back_populates='person',
        cascade_backrefs=False,
        doc="""
        List of :class:`~wuttjamaican.db.model.auth.User` accounts for
        the person.  Typically there is only one user account per
        person, but technically multiple are supported.
        """)

    def __str__(self):
        return self.full_name or ""

    @property
    def user(self):
        """
        Reference to the "first"
        :class:`~wuttjamaican.db.model.auth.User` account for the
        person, or ``None``.

        .. warning::

           Note that the database schema supports multiple users per
           person, but this property logic ignores that and will only
           ever return "one or none".  That might be fine in 99% of
           cases, but if multiple accounts exist for a person, the one
           returned is indeterminate.

           See :attr:`users` to access the full list.
        """

        # TODO: i'm not crazy about the ambiguity here re: number of
        # user accounts a person may have.  in particular it's not
        # clear *which* user account would be returned, as there is no
        # sequence ordinal defined etc.  a better approach might be to
        # force callers to assume the possibility of multiple
        # user accounts per person? (if so, remove this property)

        if self.users:
            return self.users[0]
