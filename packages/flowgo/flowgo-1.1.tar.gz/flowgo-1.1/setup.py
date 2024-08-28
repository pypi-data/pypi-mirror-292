from distutils.core import setup

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(name='flowgo',
      packages=['flowgo'],
      version='1.1',
      description='This module for creating and working with individual threads in the local memory of each.',
      author = 'YesthisI',
      author_email='teiwaz-h@mail.ru',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url = 'https://github.com/YesthisI/flow/',
      keywords = ['stack','local','threaded'],
      classifiers = ["Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
                     ])
