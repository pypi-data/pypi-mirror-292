from setuptools import Extension, setup

ext = Extension(
    name='cudart',
    sources=['cudart.c'],
)

long_description = '''
# cudart

Tricks your system to use the most powerful GPU

> For any application without an existing application profile, there is a set of libraries
which, when statically linked to a given application executable, will direct the Optimus
driver to render the application using High Performance Graphics.
'''

setup(
    name='cudart',
    version='1.0.1',
    ext_modules=[ext],
    license='MIT',
    platforms=['windows'],
    description='Tricks your system to use the most powerful GPU',
    long_description=long_description.strip(),
    long_description_content_type='text/markdown',
    author='Szabolcs Dombi',
    author_email='szabolcs@szabolcsdombi.com',
    url='https://github.com/szabolcsdombi/cudart/',
    keywords=['gpu'],
)
