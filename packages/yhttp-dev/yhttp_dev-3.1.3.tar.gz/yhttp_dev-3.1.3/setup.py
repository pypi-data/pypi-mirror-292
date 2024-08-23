import re
from os.path import join, dirname

from setuptools import setup, find_namespace_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'yhttp/dev', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


dependencies = []


setup(
    name='yhttp-dev',
    version=package_version,
    install_requires=dependencies,
    url='https://github.com/yhttp/yhttp-dev',
    author='pylover',
    author_email='vahid.mardani@gmail.com',
    description='yhttp development utilities',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important!
    packages=find_namespace_packages(
        where='.',
        include=['yhttp.dev'],
        exclude=['tests'],
    )
)
