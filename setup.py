from setuptools import setup, find_packages


# Workaround for issue
# https://bugs.python.org/issue15881
try:
	import multiprocessing
except ImportError:
	pass

setup(name = 'o3d3xx',
      version = '0.1',
      description = 'A Python library for ifm O3D3xx devices',
      url = '',
      author = 'Christoph Freundl',
      author_email = 'Christoph.Freundl@ifm.com',
      license = 'MIT',
      packages = ['o3d3xx', 'o3d3xx.rpc', 'o3d3xx.pcic'],
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      zip_safe = False)
