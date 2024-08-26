import os, json
import setuptools

# TODO SPARTAQUBE: Add quantstats dependencies

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spartaqube", # Replace with your own username
    version='0.1.18',
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
        'pandas',
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