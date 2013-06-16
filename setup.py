from setuptools import setup

setup(
	name='vimwiki_tools',
	url='https://github.com/zweifisch/vimwiki-tools',
	version='0.0.2',
	description='tools for vimwiki',
	author='Feng Zhou',
	author_email='zf.pascal@gmail.com',
	packages=['vimwiki_tools'],
	install_requires=['docopt'],
	entry_points={
		'console_scripts': ['vimwiki=vimwiki_tools:main'],
	},
)
