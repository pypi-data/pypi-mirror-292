def abstractmethod(func):
    """Decorator to mark a method as abstract."""
    func.__isabstractmethod__ = True
    return func

def abstractproperty(func):
    """Decorator to mark a property as abstract."""
    return property(abstractmethod(func))

class FastAbstractMeta(type):
    """Metaclass for high-performance abstract base class functionality."""

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace)
        if name == 'FastAbstract':  # Avoid direct reference to FastAbstract
            return cls
        
        # Initialize __abstractmethods__ attribute as a tuple for performance
        abstract_methods = []
        
        # Collect methods explicitly marked as abstract
        for attr_name, value in namespace.items():
            if getattr(value, '__isabstractmethod__', False):
                abstract_methods.append(attr_name)
            
            # Auto-detect abstract methods and properties with naming conventions
            if attr_name.startswith('abstract_') and callable(value):
                abstract_methods.append(attr_name)
            if attr_name.startswith('abstract_') and isinstance(value, property):
                abstract_methods.append(attr_name)

        # Collect abstract methods from base classes
        for base in bases:
            if isinstance(base, FastAbstractMeta):
                abstract_methods.extend(getattr(base, '__abstractmethods__', ()))

        # Convert to tuple to save memory and speed up iteration
        cls.__abstractmethods__ = tuple(set(abstract_methods))

        # Remove methods from __abstractmethods__ if they are implemented in this class
        cls.__abstractmethods__ = tuple(
            method for method in cls.__abstractmethods__
            if method not in namespace or getattr(namespace[method], '__isabstractmethod__', False)
        )

        # Enforcement level directly as an attribute
        cls.enforcement_level = kwargs.get('enforcement_level', 'error')
        return cls

    def __call__(cls, *args, **kwargs):
        if cls.enforcement_level != 'none' and cls.__abstractmethods__:
            raise TypeError(
                f"Can't instantiate abstract class {cls.__name__} with abstract methods: "
                f"{', '.join(cls.__abstractmethods__)}. Missing implementation."
            )
        return super().__call__(*args, **kwargs)


class FastAbstract(metaclass=FastAbstractMeta):
    """Base class for creating high-performance abstract base classes."""
    pass
