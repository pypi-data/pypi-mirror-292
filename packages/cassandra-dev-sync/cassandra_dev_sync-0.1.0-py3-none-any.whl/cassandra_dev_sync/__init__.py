#!/usr/bin/env python3

import csv
import subprocess

import click
import yaml
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import BatchStatement

from tqdm import tqdm

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def run_cqlsh_command(host, port, username, password, command):
    cqlsh_command = [
        "cqlsh",
        "-e", command,
        host,
        str(port),
        "-u", username,
        "-p", password
    ]

    try:
        result = subprocess.run(cqlsh_command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:

        click.echo(f"Error executing command: {e.stdout} {e.stderr} {e}", err=True)
        return None



def connect_to_cassandra(host, port, username, password):
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster([host], port=port, auth_provider=auth_provider)
    return cluster.connect()


def get_keyspace_descriptions(session, keyspace_name):
    query = f"DESCRIBE KEYSPACE {keyspace_name}"
    return session.execute(query).all()




def generate_rebuild_script(statements):
    script = ""
    for statement in statements:
        script += f"{  statement.create_statement};\n\n"

    return script

def generate_config(statements,keyspace,default_limit):
    conf = dict()
    conf['keyspace']=keyspace
    for statement in statements:
        if statement.type=='table':
            conf[statement.name]=dict(limit=default_limit)

    return dict(tables=conf)

def export_table(session, target_session, keyspace, target_keyspace, table, filter_condition=None, limit =None):
    query = f"SELECT * FROM {keyspace}.{table}"
    if filter_condition:
        query += f" WHERE {filter_condition}"
    if limit:
        query += f" LIMIT {limit}"
    else:
        query += f" LIMIT 500"

    rows = session.execute(query)

    if not rows:
        print(f"No data found for table {table}")
        return

    import_table(target_session,target_keyspace,table,rows)

    # filename = f"{table}_export.csv"
    # with open(filename, 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     writer.writerow(rows.column_names)  # Write header
    #     for row in rows:
    #         writer.writerow(row)


def import_table(target_session,target_keyspace,table,rows):
    insert_statement = target_session.prepare(f"INSERT INTO {target_keyspace}.{table} ({' , '.join(rows.column_names)}) VALUES ({' , '.join([ '?' for item in rows.column_names])})")
    batch = BatchStatement()
    counter = 0
    batch_size = 100

    for row in rows:
        batch.add(insert_statement, tuple(row))
        counter += 1

        if counter == batch_size:
            result=target_session.execute(batch)
            batch.clear()
            counter = 0

    if counter > 0:
        result = target_session.execute(batch)


@click.group()
def cli():
    """Cassandra CQL Tool for dumping data and describing keyspace structure."""
    pass

@cli.command()
@click.option('--host', required=True)
@click.option('--port', required=False, default=9042)
@click.option('--user', required=True)
@click.option('--password', required=True)
@click.option('--config', default='export_config.yaml', help='Path to YAML config file')
def describe(host,port,user,password,config):
    try:
        config_data = load_config(config)
    except FileNotFoundError:
        click.echo(f"Config file {config} not found.", err=True)
        return
    except yaml.YAMLError as e:
        click.echo(f"Error parsing config file: {e}", err=True)
        return

    keyspace = config_data['keyspace']
    session = connect_to_cassandra(host, port, user, password)
    description = get_keyspace_descriptions(session, keyspace)

    rebuild_script = generate_rebuild_script(description)

    with open(f"{keyspace}_rebuild.cql", "w") as f:
        f.write(rebuild_script)

    print(
        f"Rebuild script for keyspace '{keyspace}' has been generated and saved to '{keyspace}_rebuild.cql'")

    session.shutdown()


def clean_statement(create_statement):
    return create_statement.strip().split('WITH')[0]


@cli.command()
@click.option('--host', required=True)
@click.option('--port', required=False, default=9042)
@click.option('--user', required=True)
@click.option('--password', required=True)
@click.option('--target-host', required=True)
@click.option('--target-port', required=False, default=9042)
@click.option('--target-user', required=True)
@click.option('--target-password', required=True)
@click.option('--target-keyspace', help='keyspace name', required=True)
@click.option('--config', default='export_config.yaml', help='Path to YAML config file')
def replicate_schema(host,port,user,password,target_host,target_port,target_user,target_password,target_keyspace,config):
    try:
        config_data = load_config(config)
    except FileNotFoundError:
        click.echo(f"Config file {config} not found.", err=True)
        return
    except yaml.YAMLError as e:
        click.echo(f"Error parsing config file: {e}", err=True)
        return

    keyspace = config_data['keyspace']
    session = connect_to_cassandra(host, port, user, password)
    target_session = connect_to_cassandra(target_host, target_port, target_user, target_password)
    description = get_keyspace_descriptions(session, keyspace)
    try:
        target_session.execute("CREATE keyspace "+target_keyspace+"  WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1}")
    except Exception as e:
        print(str(e))
    for item in description:
        if item.type == 'table':
            try:
                statement = clean_statement(item.create_statement)
                target_session.execute(statement)
            except Exception as e:
                print(str(e))



    session.shutdown()

@cli.command()
@click.option('--host', required=True)
@click.option('--port', required=False, default=9042)
@click.option('--user', required=True)
@click.option('--password', required=True)
@click.option('--keyspace', help='keyspace name', required=True)
@click.option('--output', default=None, help='Path to YAML config file', required=False)
@click.option('--default-limit', default=1000, required=False)
def init(host,port,user,password,keyspace,output,default_limit):

    if output is None:
        output = f"{keyspace}.config.yaml"

    session = connect_to_cassandra(host, port, user, password)
    description = get_keyspace_descriptions(session, keyspace)
    config = generate_config(description,keyspace,default_limit)
    with open(output, 'w') as file:
        return yaml.safe_dump(config,file)


@cli.command()
@click.option('--host', required=True)
@click.option('--port', required=False, default=9042)
@click.option('--user', required=True)
@click.option('--password', required=True)
@click.option('--target-host', required=True)
@click.option('--target-port', required=False, default=9042)
@click.option('--target-user', required=True)
@click.option('--target-password', required=True)
@click.option('--target-keyspace', help='keyspace name', required=True)
@click.option('--config', default='export_config.yaml', help='Path to YAML config file')
def dump(host,port,user,password,target_host,target_port,target_user,target_password,target_keyspace,config):
    try:
        config_data = load_config(config)
    except FileNotFoundError:
        click.echo(f"Config file {config} not found.", err=True)
        return
    except yaml.YAMLError as e:
        click.echo(f"Error parsing config file: {e}", err=True)
        return
    session = connect_to_cassandra(host, port, user, password)
    target_session = connect_to_cassandra(target_host, target_port, target_user, target_password)

    pbar = tqdm(config_data['tables'].items())
    for table, table_config in pbar:
        try:
            pbar.set_description("Dumping table %s" % table)
            filter_condition = table_config['filter'] if table_config and 'filter' in table_config else None
            limit = table_config['limit'] if table_config and 'limit' in table_config else None
            export_table(session,target_session, config_data['keyspace'], target_keyspace, table,filter_condition, limit)
        except Exception as e:
            pbar.set_description("Error:" + str(e))

    session.shutdown()

def main():
    cli()


if __name__ == "__main__":
    cli()