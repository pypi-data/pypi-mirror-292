import os, json
import setuptools
import pkg_resources

def get_install_requires():
    try:
        # Check if pandas is already installed
        pkg_resources.get_distribution('pandas')
        return []  # Don't require pandas if it's already installed
    except pkg_resources.DistributionNotFound:
        return ['pandas==1.5.3']  # Install pandas 1.5.3 if it's not installed

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spartaqube", # Replace with your own username
    version='0.1.20',
    author="Spartacus",
    author_email="spartaqube@gmail.com",
    description="SpartaQube is a plug and play solution to visualize your data and build web components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://spartaqube.com",
    packages=setuptools.find_packages(),
    scripts=['installer/spartaqube.sh', 'installer/spartaqube.bat', 'installer/spartaqube_launcher.py'],
    package_data={
        'spartaqube': [
            '**/*'
        ]
    },  # Include all files in all directories
    include_package_data=True,
    install_requires=[
        'aerospike',
        'arctic',
        'arcticdb',
        'cassandra-driver',
        'channels==3.0.4',
        'clickhouse_connect',
        'cloudpickle',
        'couchdb',
        'cx_Oracle',
        'django>=4.0,<5.0',
        'django-async',
        'django-async-orm',
        'django-channels',
        'django-cors-headers',
        'django_debug_toolbar',
        'django-picklefield',
        'django-prometheus',
        'djangorestframework',
        'duckdb',
        'gunicorn',
        'influxdb_client',
        'ipython==8.17.2',
        'ipykernel==6.29.4',
        'jupyter_client',
        'jupyter_core',
        'jupyterlab',
        'mysql-connector-python',
        'numpy',
        'openpyxl',
        *get_install_requires(),  # Conditionally add pandas
        'Pillow',
        'psycopg2-binary',
        'pymongo==3.11.0',
        'pymssql',
        'PyMySQL',
        'pyodbc',
        'python-dateutil',
        'pytz',
        'quantstats',
        'questdb',
        'redis',
        'requests',
        'requests-oauthlib',
        'SQLAlchemy',
        'tinykernel',
        'tqdm',
        'typer',
        'waitress',
        'whitenoise',
        # Add any other dependencies your project requires
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)