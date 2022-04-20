from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='sutagent',  
    version='1.37.0rc',
    description='A sutagent python project',
    long_description=long_description,
    author='sutagent developers',
    author_email='chengming.zhao@intel.com',
    license='BSD 3-Clause License',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    install_requires=[
      'pyserial==3.4',
      'wheel>=0.33.4',
      'lxml==4.5.0',
      'WMI==1.4.9',
      'pyzmp',
      'six'
        ],
    package_data={
        'sutagent': [
            'bin/PSTools/psshutdown.exe',
            '*.sh',
            '*.bat',
            '*.ini',
            'lib/globals/logging.conf',
            'lib/configuration/SUT_config.cfg'
        ],
    },
    entry_points={
        'console_scripts': [
            'sutagent=sutagent:main',
        ],
    },
    extras_require={},
)
