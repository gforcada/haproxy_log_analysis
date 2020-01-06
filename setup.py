# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '4.1.1.dev0'

description = "Haproxy log analyzer that tries to gives an insight of what's going on"

long_description = """{0}
{1}
""".format(
    open('README.rst').read(), open('CHANGES.rst').read()
)

setup(
    name='haproxy_log_analysis',
    version=version,
    description=description,
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: Log Analysis',
    ],
    keywords='haproxy log analysis report',
    author='Gil Forcada',
    author_email='gil.gnome@gmail.com',
    url='https://github.com/gforcada/haproxy_log_analysis',
    license='GPL v3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': ['haproxy_log_analysis = haproxy.main:console_script']
    },
)
