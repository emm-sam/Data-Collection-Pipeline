from gettext import find
from setuptools import setup
from setuptools import find_packages

setup(
    name = 'scraper_example',
    versions = '1.0',
    # description = 'scraper package',
    # author = 'Emma Samouelle',
    # license='MIT',
    packages = find_packages(), 
    install_requires=[
        'pandas',
        'numpy',
        'psycopg2-binary',
        'urllib3',
        'boto3',
        'requests',
        'sqlalchemy',
        'botocore',
        'selenium',
        's3transfer'
        ])