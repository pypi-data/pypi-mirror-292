from setuptools import setup, find_packages

setup(
    name='allstarlist',
    version='0.1.0',
    description='A Python package for allstarlist',
    author='Jon Poindexter W5ALC',
    author_email='w5alc@skyhublink.com',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
	'tenacity',
	'rich',
	'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'allstarlist = allstarlist.main:main',
        ],
    },
    python_requires='>=3.6',
)
