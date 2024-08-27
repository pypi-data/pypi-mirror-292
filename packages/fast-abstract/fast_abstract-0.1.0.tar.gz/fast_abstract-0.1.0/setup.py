from setuptools import setup, find_packages

setup(
    name='fast_abstract',
    version='0.1.0',
    description='A high-performance abstract base class implementation for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Michael Avina',
    author_email='a.v.i.na.m@gm-ail.com',
    url='https://github.com/mavin2009/fast_abstract',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
