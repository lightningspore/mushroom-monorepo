import os
from jinja2 import Environment, FileSystemLoader

# Get the environment variables
targets_list = os.environ.get('TARGETS_LIST', '').split(',')
username = os.environ.get('USERNAME', '')
password = os.environ.get('PASSWORD', '')

# Create the Jinja2 environment
env = Environment(loader=FileSystemLoader('/app'))

# Load the template
template = env.get_template('grafana-agent.yaml.jinja')

# Render the template
rendered = template.render(targets_list=targets_list, username=username, password=password)

# Print the rendered template
print(rendered)

with open('agent-config.yaml', 'w') as f:
    f.write(rendered)