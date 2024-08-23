import click
import subprocess
import os 

project = os.environ["PROJECT"]
zone = os.environ["ZONE"]
vm = os.environ["VM"]

@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(name):
    """Greet a person with a hello message"""
    click.echo(f"🔥Hello {name}!🔥")

@click.command()
def start():
    """Start your vm"""
    subprocess.run(['gcloud', 'compute', 'instances', 'start', vm, '--project', project, '--zone', zone])
    click.echo(f'Started VM {vm} in project {project} and zone {zone}')
   
@click.command() 
def stop():
    """Stop your vm"""
    subprocess.run(['gcloud', 'compute', 'instances', 'stop', vm, '--project', project, '--zone', zone])
    click.echo(f'Stopped VM {vm} in project {project} and zone {zone}')

@click.command()
# Connect to the VM using VS Code Remote SSH
@click.pass_context
def connect(context):
    """ Connect to your vm"""
    context.invoke(start)
    subprocess.run(
        [
            "code",
            "--folder-uri",
            "vscode-remote://ssh-remote+aloys.bernard@34.163.33.233//home/aloys.bernard/code/aloys-bernard-artefact",
        ]
    )

if __name__ == '__main__':
    hello()