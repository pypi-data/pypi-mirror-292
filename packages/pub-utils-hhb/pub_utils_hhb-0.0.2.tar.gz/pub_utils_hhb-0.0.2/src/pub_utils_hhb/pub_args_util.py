__all__ = [
    'Arg',
]


class Arg:
    def __init__(self,
                 arg_name: str = '',
                 arg_type: type = object,
                 required: bool = False,
                 default_value=None):

        self._arg_name = ''
        self._arg_type = object
        self._required = False
        self._default_value = None

        self.set_arg_name(arg_name)
        self.set_arg_type(arg_type)
        self.set_required(required)
        self.set_default_value(default_value)

    def get_arg_name(self):
        return self._arg_name

    def get_arg_type(self):
        return self._arg_name

    def get_required(self):
        return self._required

    def get_default_value(self):
        return self._default_value

    def set_arg_name(self, arg_name: str):
        if not isinstance(arg_name, str):
            raise TypeError('arg_name must be a non-empty string')
        if not arg_name:
            raise ValueError('arg_name must be a non-empty string')

        self._arg_name = arg_name
        return self

    def set_arg_type(self, arg_type: type):
        if not isinstance(arg_type, type):
            raise TypeError('arg_type must be one of built-in type')

        self._arg_type = arg_type
        return self

    def set_required(self, required: bool):
        if not isinstance(required, bool):
            raise TypeError('required must be boolean')

        self._required = required
        return self

    def set_default_value(self, default_value=None):
        self._default_value = default_value
        return self
