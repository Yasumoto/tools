"""Distribution Definition for tools module"""

from setuptools import find_packages, setup


MOCK_VERSION = '2.0.0'
NOSE_VERSION = '1.3.7'
PYDOCSTYLE_VERSION = '1.0.0'
PYLINT_VERSION = '1.5.5'


setup(name='tools',
      version='0.0.1',
      description='Automation for Operations and Reliability',
      long_description='Tools and Services built to run the things that run our company',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: System Administrators',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Distributed Computing',
          'Topic :: System :: Systems Administration'
      ],
      keywords='Configuration Management',
      url='https://github.com/Yasumoto/tools',
      author='Joe Smith',
      author_email='yasumoto7@gmail.com',
      packages=find_packages('lib'),
      package_dir={'': 'lib'},
      entry_points={
          'console_scripts': [
              'yapf=yapf:run_main',
          ],
      },
      install_requires=[
          'boto3==1.3.1',
          'botocore==1.4.25',
          'fabric==1.11.1',
          'flask==0.11.1',
          'requests==2.10.0',
          'pex==1.1.10',
          'pychef==0.3.0',
          'python-consul==0.6.1',
          'yapf==0.14',
          'mock==%s' % MOCK_VERSION,
          'nose==%s' % NOSE_VERSION,
          'pydocstyle==%s' % PYDOCSTYLE_VERSION,
          'pylint==%s' % PYLINT_VERSION,
      ],
      test_suite='nose.collector',
      tests_require=[
          'mock==%s' % MOCK_VERSION,
          'nose==%s' % NOSE_VERSION,
          'pydocstyle==%s' % PYDOCSTYLE_VERSION,
          'pylint==%s' % PYLINT_VERSION,
      ],
      include_package_data=True,
      zip_safe=True)
