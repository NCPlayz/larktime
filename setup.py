from setuptools import setup
import re

requirements = ['lark-parser']

with open('larktime/__init__.py', 'r') as f:
    version = re.search(r"__version__ = '(.+)'\n", f.read()).group(1)

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    name='larktime',
    url='https://github.com/NCPlayz/larktime',
    project_urls = {
        'Issue Tracker': 'https://github.com/NCPlayz/larktime/issues'
    },
    version=version,
    packages=['larktime'],
    license='MIT',
    description='Simple parser for date times using Lark.',
    long_description=readme,
    long_description_content_type='text/x-md',
    install_requires=requirements,
)