# Copyright 2012 VPAC
#
# This file is part of django-tldap.
#
# django-tldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-tldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-tldap  If not, see <http://www.gnu.org/licenses/>.

import tldap.exceptions
import struct

class Field(object):
    def __init__(self, max_instances=1, required=False):
        self._max_instances = max_instances
        self._required = required

    def contribute_to_class(self, cls, name):
        self.name = name
        self._cls = cls
        cls._meta.add_field(self)

    def to_db(self, value):
        "returns field's value prepared for saving into a database."

        # ensure value is valid
        self.validate(value)

        # do we expect a list or just a single value?
        if self._max_instances == 1:
            assert not isinstance(value, list)
            if value is None:
                value = [ ]
            else:
                value = [ self.value_to_db(value) ]
        else:
            assert isinstance(value, list)
            value = list(value)
            for i,v in enumerate(value):
                value[i] = self.value_to_db(v)

        # return result
        assert isinstance(value, list)
        return value

    def to_python(self, value):
        """
        Converts the input value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        assert isinstance(value, list)

        # convert every value in list
        value = list(value)
        for i,v in enumerate(value):
            value[i] = self.value_to_python(v)

        # if we only expect one value, see if we can remove list
        if self._max_instances is not None:
            if self._max_instances == 1:
                if len(value) == 0:
                    value = None
                elif len(value) == 1:
                    value = value[0]

        # return result
        return value

    def validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        # do we expect a list or just a single value?
        if self._max_instances == 1:
            # check object type
            if isinstance(value, list):
                raise tldap.exceptions.ValidationError("%r is a list and max_instances is %s"%(self.name, self._max_instances))
            # check this required value is given
            if self._required:
                if value is None:
                    raise tldap.exceptions.ValidationError("%r is required"%self.name)
            # validate the value
            self.value_validate(value)
        else:
            # check object type
            if not isinstance(value, list):
                raise tldap.exceptions.ValidationError("%r is not a list and max_instances is %s"%(self.name, self._max_instances))
            # check maximum instances
            if self._max_instances is not None and len(value) > self._max_instances:
                raise tldap.exceptions.ValidationError("%r exceeds max_instances of %d"%(self.name, self._max_instances))
            # check this required value is given
            if self._required:
                if len(value) == 0:
                    raise tldap.exceptions.ValidationError("%r is required"%self.name)
            # validate the value
            for i,v in enumerate(value):
                self.value_validate(v)

    def clean(self, value):
        """
        Convert the value's type and run validation. Validation errors from to_python
        and validate are propagated. The correct value is returned if no error is
        raised.
        """
        value = self.to_python(value)
        self.validate(value)
        return value

    def value_to_db(self, value):
        "returns field's single value prepared for saving into a database."
        raise RuntimeError("Not implemented")

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        raise RuntimeError("Not implemented")

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        raise RuntimeError("Not implemented")


class BinaryField(Field):
    def value_to_db(self, value):
        "returns field's single value prepared for saving into a database."
        assert value is None or isinstance(value, str)
        return value

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        if value is not None and not isinstance(value, str):
            raise tldap.exceptions.ValidationError("%r should be a string"%self.name)
        return value

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if value is not None and not isinstance(value, str):
            raise tldap.exceptions.ValidationError("%r should be a string or None"%self.name)


class CharField(Field):
    def value_to_db(self, value):
        "returns field's single value prepared for saving into a database."
        if isinstance(value, unicode):
            value = value.encode("utf_8")
        return value

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        if value is not None and not isinstance(value, str):
            raise tldap.exceptions.ValidationError("%r should be a string"%self.name)
        return value.decode("utf_8")

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if value is not None and not (isinstance(value, str) or isinstance(value, unicode)):
            raise tldap.exceptions.ValidationError("%r should be a string or None"%self.name)


class UnicodeField(Field):
    def value_to_db(self, value):
        "returns field's single value prepared for saving into a database."
        value = value.encode("utf_16le")
        return value

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        if value is not None and not isinstance(value, str):
            raise tldap.exceptions.ValidationError("%r should be a string"%self.name)
        return value.decode("utf_16")

    def value_validate(self, value):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if value is not None and not (isinstance(value, str) or isinstance(value, unicode)):
            raise tldap.exceptions.ValidationError("%r should be a string or None"%self.name)


class IntegerField(Field):
    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        if value is not None and not isinstance(value, str):
            raise tldap.exceptions.ValidationError("%r should be a string"%self.name)
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("%r is invalid integer"%self.name)

    def value_to_db(self, value):
        "returns field's single value prepared for saving into a database."
        try:
            return str(int(value))
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("%r is invalid integer"%self.name)

    def value_validate(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        if value is None:
            return value
        try:
            return str(int(value))
        except (TypeError, ValueError):
            raise tldap.exceptions.ValidationError("%r is invalid integer"%self.name)

class SidField(Field):

    def value_to_python(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        l = len(value) - 8
        if l%4 != 0:
            raise tldap.exceptions.ValidationError("Invalid sid")

        l = l / 4

        array = struct.unpack('<bbbbbbbb' + 'I'*l, value)

        if array[1] != l:
            raise tldap.exceptions.ValidationError("Invalid sid")

        if array[2:7] != (0, 0, 0, 0, 0):
            raise tldap.exceptions.ValidationError("Invalid sid")

        array = ( "S", ) + array[0:1] + array[7:]
        return "-".join([str(i) for i in array])

    def value_to_db(self, value):
        "returns field's single value prepared for saving into a database."

        array = value.split("-")
        l = len(array) - 3

        assert l >= 0
        assert array[0] == 'S'

        array = array[1:2] + [l, 0, 0, 0, 0, 0] + array[2:]
        array = [ int(i) for i in array ]

        return struct.pack('<bbbbbbbb' + 'I'*l, *array)

    def value_validate(self, value):
        """
        Converts the input single value into the expected Python data type, raising
        django.core.exceptions.ValidationError if the data can't be converted.
        Returns the converted value. Subclasses should override this.
        """
        if value is None:
            return value

        array = value.split("-")
        l = len(array) - 3

        if l < 1:
            raise tldap.exceptions.ValidationError("Invalid sid")

        if array.pop(0) != "S":
            raise tldap.exceptions.ValidationError("Invalid sid")

        try:
            [ int(i) for i in array ]
        except TypeError:
            raise tldap.exceptions.ValidationError("Invalid sid")
