import logging
import click
import click_spinner

from natural_lens.databases.postgres import PostgreSQLDatabase
from natural_lens.databases.trino import TrinoDatabase
from .profile import generate_profiles 
from .query import load_profiles, construct_prompt, query_openai

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

@click.group()
def cli():
    """An AI driven CLI tool for database operations."""
    pass

@cli.command()
@click.option('--dbtype', required=True, type=click.Choice(['postgres', 'trino']), help='Type of database.')
@click.option('--user', required=True, help='Database user.')
@click.option('--port', required=True, help='Database port.') 
@click.option('--host', default='localhost', help='Database host.')
@click.option('--dbname', help='Database name for Postgres.')
@click.option('--password', help='Database password for Postgres.')
@click.option('--catalog', help='Catalog name for Trino.')
@click.option('--schema', help='Schema name for Trino.')
def download(dbtype, user, port, host, dbname, password, catalog, schema):
    """Download the database schema."""
   
    if dbtype == 'postgres':
        if not dbname:
            raise click.BadParameter('The --dbname option is required when using Postgres.')
        if not password:
            raise click.BadParameter('The --password option is required when using Postgres.')            
        db = PostgreSQLDatabase(dbname, user, password, host, port)  # Adjust if needed
    elif dbtype == 'trino':
        if not catalog:
            raise click.BadParameter('The --catalog option is required when using Trino.')
        if not schema:
            raise click.BadParameter('The --schema option is required when using Trino.')
        db = TrinoDatabase(catalog, schema, user, host, port)

    db.connect()
    db.download_schema()
    prompt = db.get_prompt()
    # Save the prompt to a file
    with open("prompt.txt", "w") as f:
        f.write(prompt)
    db.close()

@cli.command()
def profile():
    """Generate database profiles."""
    with open("prompt.txt", "r") as f:
        prompt = f.read()
        generate_profiles(prompt)

@cli.command()
def query():
    """Query the database schemas using the profiles as context."""
    profiles_path = "./profiles/"
    profiles_content = load_profiles(profiles_path)
    if profiles_content is None:
        click.echo("No profiles found. Please generate profiles first.")
        return
    
    click.echo("Welcome to the query interface. Type 'exit' to quit.")

    conversation = []

    with open("prompt.txt", "r") as f:
        prompt = f.read()
        conversation.append({"role": "system", "content": f"You are an expert in data analysis. {prompt}"})
    
    while True:
        # Prompt the user for the query
        query = click.prompt("", prompt_suffix='> ')

        # Check if the user wants to exit
        if query.lower() == 'exit':
            click.echo("Exiting the query interface.")
            break

        prompt = construct_prompt(profiles_content, query)
        with click_spinner.spinner('Querying the database schemas...'):
            response, conversation = query_openai(prompt, conversation)

        if response:
            click.echo(response)

if __name__ == '__main__':
    cli()