from setuptools import setup

# from https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
from pathlib import Path
this_directory = Path(__file__).parent
readme = (this_directory/"README.md").read_text()

setup(
    name='densired',
    version='1.0.0',
    description='A generator for density-based data',
    url='https://github.com/PhilJahn/DENSIRED',
    author='Philipp Jahn',
    author_email='jahn@dbs.ifi.lmu.de',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=['densired'],
    install_requires=['matplotlib',
                      'numpy>=2.0.1',
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.9',
    ],
)
