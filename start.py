#!/usr/local/bin/python3

import os
import sqlite3
import subprocess
import sys
import time
from sqlite3 import Cursor
from urllib.request import Request, urlopen

import jinja2

database_path = '/automx2_db.sqlite'
template_path = '/etc/automx2.template.conf'
configuration_path = '/etc/automx2.conf'
custom_sql_path = '/data/custom.sql'


def check_required_env():
    """
    Checks if the required environment variables are set
    """
    # If a SQL file is provided, not all environment variables are required
    if os.path.isfile(custom_sql_path):
        required_env_variables = ['PROXY_COUNT', 'PROVIDER_NAME', 'PROVIDER_SHORTNAME', 'DOMAINS']
    else:
        required_env_variables = ['PROXY_COUNT', 'PROVIDER_NAME', 'PROVIDER_SHORTNAME', 'DOMAINS']

    missing_env_variables = [v for v in required_env_variables if os.getenv(v) is None]
    if len(missing_env_variables) > 0:
        print(f'Error: The environment variables {missing_env_variables} must be set')
        sys.exit(1)


def create_configuration():
    """
    Creates the configuration file for automx2 by applying the environment variables to the template.

    check_required_env() must be called beforehand.
    """
    with open(template_path, 'r') as template_file:
        template = template_file.read()

    result = jinja2.Template(template).render({'proxy_count': os.getenv('PROXY_COUNT')})

    with open(configuration_path, 'w') as configuration_file:
        configuration_file.write(result)


def create_database():
    """
    Creates a SQLite database at the given path and populates with the default tables and entries.

    create_configuration() must be called beforehand.
    """
    # Deletes the database file if it already exists
    if os.path.isfile(database_path):
        os.remove(database_path)

    # Runs automx2 with gunicorn as the application server as a subprocess to populate the database
    # https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#gunicorn
    # https://docs.python.org/3.10/library/subprocess.html#subprocess.Popen
    process = subprocess.Popen(['/usr/local/bin/gunicorn', '-b 127.0.0.1:80', 'automx2.server:app'])

    # Send a request to the /initdb/ endpoint to generate the database schema
    # https://rseichter.github.io/automx2/#_testing_standalone_automx2
    initdb_request = Request('http://127.0.0.1/initdb/')
    time.sleep(1)
    with urlopen(initdb_request) as response:
        if response.status != 200:
            print('Unable to create the database schema')
            sys.exit(1)

    # Once the database schema is created, we'll stop automx2 to edit the database
    process.terminate()


def populate_database():
    """
    Decides which method to use for database population.

    create_database() must be called beforehand.

    See: https://docs.python.org/3/library/sqlite3.html
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    remove_database_defaults(cursor)
    if os.path.isfile(custom_sql_path):
        populate_database_file(cursor)
    else:
        populate_database_env(cursor)

    cursor.close()
    connection.commit()
    connection.close()


def remove_database_defaults(cursor: Cursor):
    """
    Removes the default contents of the database.

    See: https://github.com/rseichter/automx2/blob/master/automx2/model.py
    """
    cursor.execute('DELETE FROM provider')
    cursor.execute('DELETE FROM ldapserver')
    cursor.execute('DELETE FROM davserver')
    cursor.execute('DELETE FROM server')
    cursor.execute('DELETE FROM domain')
    cursor.execute('DELETE FROM server_domain')


def populate_database_file(cursor: Cursor):
    """
    Inserts data based on a user-provided SQL script.
    """
    with open(custom_sql_path, 'r') as custom_sql_file:
        custom_sql = custom_sql_file.read()
    cursor.executescript(custom_sql)


def populate_database_env(cursor: Cursor):
    """
    Inserts data based on the environment variables.

    See: https://github.com/rseichter/automx2/blob/master/contrib/sqlite-generate.sh
    """

    # Table: provider
    provider_id = 0
    provider_name = os.getenv('PROVIDER_NAME', 'Default name')
    provider_shortname = os.getenv('PROVIDER_SHORTNAME', 'Default')

    cursor.execute(
        'INSERT INTO provider(id, name, short_name) VALUES(?, ?, ?)',
        (0, provider_name, provider_shortname)
    )

    # Table: server
    def server_from_env(identifier: int, server_type: str) -> list[tuple]:
        host = os.getenv(f'{server_type.upper()}_HOST')
        port = os.getenv(f'{server_type.upper()}_PORT')
        socket = os.getenv(f'{server_type.upper()}_SOCKET')
        if not host:
            return []

        return [(identifier, 10, port, server_type, host, socket, '%EMAILADDRESS%', 'plain')]

    servers = []

    servers += server_from_env(0, 'imap')
    servers += server_from_env(1, 'pop')
    servers += server_from_env(2, 'smtp')

    cursor.executemany(
        'INSERT INTO server(id, prio, port, type, name, socket_type, user_name, authentication) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        servers
    )

    if len(servers) == 0:
        print('Warning: No server configured')

    # Table: domain

    domains = []
    domain_strings = os.getenv('DOMAINS').split(',')
    for index, domain_string in enumerate(domain_strings):
        domains += [(index, domain_string, provider_id, None)]

    cursor.executemany('INSERT INTO domain(id, name, provider_id, ldapserver_id) VALUES (?, ?, ?, ?)', domains)

    # Table: server_domain

    server_domains = []
    for domain in domains:
        for server in servers:
            server_domains += [(server[0], domain[0])]

    cursor.executemany('INSERT INTO server_domain(server_id, domain_id) VALUES(?, ?)', server_domains)


def replace_with_app():
    """
    Replaces this process with actual automx2 application running with the gunicorn application server.

    populate_database() must be called beforehand.
    """
    # Replace this process with the flask application server
    os.execv('/usr/local/bin/gunicorn', ['gunicorn', '-b 0.0.0.0:80', 'automx2.server:app'])


check_required_env()
create_configuration()
create_database()
populate_database()
replace_with_app()
