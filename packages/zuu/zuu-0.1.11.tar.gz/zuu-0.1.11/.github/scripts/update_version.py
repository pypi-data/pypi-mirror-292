import toml

def increment_version(version: str) -> str:
    # Split the version into parts
    parts = version.split('.')
    
    # Check if the version is a beta version
    if 'b' in parts[-1]:
        # Increment the beta number
        main_version, beta_version = parts[-1].split('b')
        new_beta_version = f"{main_version}b{int(beta_version) + 1}"
        parts[-1] = new_beta_version
    else:
        # Increment the patch version and add beta suffix
        parts.append('1b1')

    return '.'.join(parts)

# Load the pyproject.toml file
with open('pyproject.toml', 'r') as file:
    data = toml.load(file)

# Update the version
current_version = data['project']['version']
new_version = increment_version(current_version)
data['project']['version'] = new_version

# Save the changes back to the pyproject.toml file
with open('pyproject.toml', 'w') as file:
    toml.dump(data, file)

print(f"Updated version from {current_version} to {new_version}")