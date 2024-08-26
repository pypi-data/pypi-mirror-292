#!/usr/bin/python

from setuptools import setup
from version import VERSION
# Disable version normalization performed by setuptools.setup()
try:
    # Try the approach of using sic(), added in setuptools 46.1.0
    from setuptools import sic
except ImportError:
    # Try the approach of replacing packaging.version.Version
    sic = lambda v: v
    try:
        # setuptools >=39.0.0 uses packaging from setuptools.extern
        from setuptools.extern import packaging
    except ImportError:
        # setuptools <39.0.0 uses packaging from pkg_resources.extern
        from pkg_resources.extern import packaging
    packaging.version.Version = packaging.version.LegacyVersion

if __name__ == '__main__':
	setup(
		name="pmcc",
		version=sic(VERSION),
		packages = ['_pmcc'],
		package_dir = {'_pmcc': ''},
		entry_points = {'console_scripts': ['pmcc = _pmcc.pmcc:main']},
		python_requires='>=2.7',
		zip_safe=False,
	)
