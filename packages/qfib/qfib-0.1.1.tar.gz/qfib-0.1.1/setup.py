from setuptools import setup, find_packages

setup(
    name='qfib',
    version='0.1.1',
    author='Freek van Keulen',
    author_email='freek@quidome.nl',
    description='Fibonacci number generator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
#    url='https://github.com/yourusername/my_package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
