import inspect

class SingletonMetaclass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

def singleton_metaclass():
    class SingletonMetaclass(type):
        _instances = {}

        def __call__(cls, *args, **kwargs):
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]

    return SingletonMetaclass


def var_based_singleton_metaclass():
    class _MClass(type):
        _instances = {}

        def __call__(cls, *args, **kwargs):
            id_key = getattr(cls, "__id__", None)
            if id_key is None:
                raise AttributeError(
                    f"Class {cls.__name__} must have an '__id__' attribute"
                )

            parsedParams = inspect.signature(cls.__init__).bind(cls, *args, **kwargs)
            parsedParams.apply_defaults()

            id_value = parsedParams.arguments.get(id_key, None)
            if not id_value:
                raise AttributeError(
                    f"Class {cls.__name__} must have a parameter named '{id_key}'"
                )

            if id_value not in cls._instances:
                cls._instances[id_value] = super().__call__(*args, **kwargs)
            return cls._instances[id_value]

    return type(
        "SingletonMetaclass",
        (_MClass,),
        {
            "_instances": {},
        },
    )
