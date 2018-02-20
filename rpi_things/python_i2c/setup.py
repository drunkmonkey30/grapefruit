from distutils.core import setup, Extension

module1 = Extension('python_i2c', 
	sources = ['python_i2c.c'],
	include_dirs = ['/usr/include'])

setup (name = 'python_i2c',
	   version = '0.2',
	   description = 'Provides access to i2c interface on RPi',
	   ext_modules = [module1])
