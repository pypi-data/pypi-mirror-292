import click
import subprocess
import os

project = os.environ.get('GOOGLE_CLOUD_PROJECT')
zone = os.environ.get('GOOGLE_CLOUD_ZONE')
instance = os.environ.get('GOOGLE_CLOUD_INSTANCE')

@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(name):
  """Greet a person with a hello message"""
  click.echo(f"🔥Hello {name}!🔥")

@click.command()
def start():
    """Start your vm"""
    subprocess.run(f"gcloud compute instance start {instance}", shell=True, check=True)
   
@click.command() 
def stop():
    """Stop your VM"""
    subprocess.run("gcloud compute instance stop", shell=True, check=True)
    print()

if __name__ == '__main__':
    hello()