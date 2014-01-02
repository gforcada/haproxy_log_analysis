# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '0.0.1'

description = 'Haproxy log analyzer that tries to gives an insight of ' \
              'what\'s going on'

long_description = """{0}
{1}


LICENSE
=======

{2}
""".format(
    open('README.rst').read(),
    open('CHANGES.rst').read(),
    open('LICENSE').read(),
)

setup(
    name='haproxy_log_analysis',
    version=version,
    description=description,
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: Log Analysis',
    ],
    keywords='haproxy log analysis report',
    author='Gil Forcada',
    author_email='gforcada@gnome.org',
    url='https://github.com/gforcada/haproxy_log_analysis',
    license='GPL v3',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['haproxy', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    extras_require={
        'test': [
            'nose',
        ],
    },
)
