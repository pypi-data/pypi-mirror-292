# Fast Abstract

Fast Abstract is a high-performance implementation of abstract base classes for Python, designed with optimized checks and minimal overhead. Created by Michael Avina, this module offers a lightweight solution for developers who want to leverage abstract classes without the additional overhead of Python's built-in `abc` module.

## Why?

I wanted a lightweight, high-performance alternative to Python's `abc` module that still provides the essential functionality of abstract base classes. Fast Abstract is perfect for applications that require speed and minimal overhead while still enforcing interface contracts within your Python code.

## Features

- **Optimized for Performance**: Fast Abstract uses tuples and avoids dynamic checks wherever possible to minimize runtime overhead.
- **Lightweight**: The module is small, simple, and easy to integrate into any Python project.
- **Flexible Enforcement Levels**: Allows you to specify enforcement levels ('error', 'warning', 'none') for abstract method checks.


## Installation

You can install Fast Abstract using `pip`

## Usage

```python
from fast_abstract import FastAbstract, abstractmethod, abstractproperty

class MyBase(FastAbstract):
    @abstractmethod
    def method(self):
        pass
    
    @abstractproperty
    def my_property(self):
        """Abstract property example."""
        pass

    @abstractmethod
    def abstract_another_method(self):
        """Abstract method example with prefix 'abstract_'."""
        pass

class ConcreteClass(MyBase):
    def method(self):
        print("Method implemented in ConcreteClass")

    @property
    def my_property(self):
        return "Property implemented in ConcreteClass"

    def abstract_another_method(self):
        print("Abstract method with prefix implemented")

obj = ConcreteClass()
obj.method()  # This will print: Method implemented in ConcreteClass
print(obj.my_property)  # This will print: Property implemented in ConcreteClass
obj.abstract_another_method()  # This will print: Abstract method with prefix implemented

### 5. `LICENSE` File

The license remains the same:

#### `LICENSE`

```plaintext
MIT License

MIT License

Copyright (c) 2024 Michael Avina

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.