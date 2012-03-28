import os

def pippy_home():
    """Gives the pippy home directory
    
    It is searched for at ~/.pippy or can be specified by the PIPPY_HOME
    environment variable
    """
    return os.environ.get('PIPPY_HOME', os.path.expanduser('~/.pippy'))
