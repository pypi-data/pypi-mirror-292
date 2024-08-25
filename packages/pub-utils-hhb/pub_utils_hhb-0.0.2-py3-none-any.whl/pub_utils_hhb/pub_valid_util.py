from pub_utils_hhb.pub_args_util import Arg

__all__ = [
    'validate_kwargs',
]


def validate_kwargs(expected: list[Arg], actual: dict):
    for arg in expected:
        arg_name = arg.get_arg_name()
        if arg_name in actual:
            if not isinstance(actual[arg_name], arg.get_arg_type()):
                raise TypeError(f'{arg_name} must be instance of {arg.get_arg_type()}')
        else:
            if arg.get_required():
                raise ValueError(f'{arg_name} is required')
            else:
                actual[arg_name] = arg.get_default_value()
