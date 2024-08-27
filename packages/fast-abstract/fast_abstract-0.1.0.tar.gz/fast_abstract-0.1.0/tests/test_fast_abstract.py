import unittest
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
        return "Method implemented in ConcreteClass"

    @property
    def my_property(self):
        return "Property implemented in ConcreteClass"

    def abstract_another_method(self):
        return "Abstract method with prefix implemented"

class TestFastAbstract(unittest.TestCase):

    def test_concrete_class_implementation(self):
        obj = ConcreteClass()
        self.assertEqual(obj.method(), "Method implemented in ConcreteClass")
        self.assertEqual(obj.my_property, "Property implemented in ConcreteClass")
        self.assertEqual(obj.abstract_another_method(), "Abstract method with prefix implemented")

    def test_incomplete_class(self):
        with self.assertRaises(TypeError):
            class IncompleteClass(MyBase):
                pass
            IncompleteClass()

if __name__ == '__main__':
    unittest.main()
