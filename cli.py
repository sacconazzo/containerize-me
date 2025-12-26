#!/usr/bin/env python3
"""
Container Manager CLI - Dynamic management of Docker containers with docker-compose
"""
import os
import sys
from pathlib import Path
import yaml
from questionary import select, text, password, Style
from services import SERVICES_CATALOG, generate_compose_config


# Custom style for the menu
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#2196f3 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#2196f3'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])


def ensure_directories():
    """Create necessary directories if they don't exist"""
    base_dir = Path.cwd()
    volumes_dir = base_dir / "volumes"
    compose_dir = base_dir / "compose-files"
    
    volumes_dir.mkdir(exist_ok=True)
    compose_dir.mkdir(exist_ok=True)
    
    return volumes_dir, compose_dir


def select_category():
    """Allows the user to choose a service category"""
    categories = list(SERVICES_CATALOG.keys())
    
    category = select(
        "Select a category:",
        choices=categories,
        style=custom_style
    ).ask()
    
    return category


def select_service(category):
    """Allows the user to choose a service from the category"""
    services = list(SERVICES_CATALOG[category].keys())
    
    service = select(
        f"Select a service from {category}:",
        choices=services,
        style=custom_style
    ).ask()
    
    return service


def get_service_config(category, service):
    """Gets the configuration for the selected service"""
    service_info = SERVICES_CATALOG[category][service]
    
    print(f"\n🚀 Configuration for {service}")
    print("=" * 50)
    
    config = {}
    
    # Username (skip for MySQL which only uses root)
    if service != "MySQL":
        default_user = service_info.get('default_user', 'admin')
        username = text(
            f"Username (default: {default_user}):",
            style=custom_style
        ).ask()
        config['username'] = username if username else default_user
    else:
        config['username'] = 'root'
    
    # Password
    default_pass = service_info.get('default_password', 'password123')
    user_password = password(
        f"Password (default: {default_pass}):",
        style=custom_style
    ).ask()
    config['password'] = user_password if user_password else default_pass
    
    # Database name (if applicable)
    if service_info.get('has_database', False):
        default_db = service_info.get('default_database', 'mydb')
        db_name = text(
            f"Database name (default: {default_db}):",
            style=custom_style
        ).ask()
        config['database'] = db_name if db_name else default_db
    
    # Port
    default_port = service_info.get('default_port', 8080)
    port = text(
        f"Port (default: {default_port}):",
        style=custom_style
    ).ask()
    config['port'] = port if port else default_port
    
    return config


def create_compose_file(category, service, config, volumes_dir, compose_dir):
    """Creates the docker-compose.yml file for the service"""
    service_name = f"{service.lower()}"
    volume_path = volumes_dir / service_name
    volume_path.mkdir(exist_ok=True)
    
    compose_config = generate_compose_config(
        category, 
        service, 
        service_name,
        config,
        str(volume_path.absolute())
    )
    
    # Save the docker-compose file
    compose_file = compose_dir / f"{service_name}-compose.yml"
    with open(compose_file, 'w') as f:
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    return compose_file, service_name


def start_container(compose_file):
    """Starts the container using docker compose"""
    choice = select(
        "\nDo you want to start the container now?",
        choices=["Yes", "No"],
        style=custom_style
    ).ask()
    
    if choice == "Yes":
        print(f"\n🚀 Starting container...")
        os.system(f"docker compose -f {compose_file} up -d")
        print(f"\n✅ Container started successfully!")
        print(f"📄 Compose file saved in: {compose_file}")
    else:
        print(f"\n📄 Compose file saved in: {compose_file}")
        print(f"To start the container manually, run:")
        print(f"  docker compose -f {compose_file} up -d")


def list_and_start_containers(compose_dir):
    """Lists and allows starting already configured containers"""
    compose_files = list(compose_dir.glob("*-compose.yml"))
    
    if not compose_files:
        print("\n⚠️  No docker-compose files found!")
        print("Configure a service first.")
        return
    
    # List of available services
    service_names = [f.stem.replace('-compose', '') for f in compose_files]
    
    choice = select(
        "\nSelect which service to manage:",
        choices=service_names,
        style=custom_style
    ).ask()
    
    if not choice:
        return
    
    # Find the corresponding compose file
    compose_file = compose_dir / f"{choice}-compose.yml"
    
    action = select(
        f"\nWhat do you want to do with {choice}?",
        choices=[
            "▶️  Start (up -d)",
            "⏹️  Stop (down)",
            "🔄 Restart",
            "📊 Show logs"
        ],
        style=custom_style
    ).ask()
    
    if not action:
        return
    
    print()
    if action == "▶️  Start (up -d)":
        print(f"🚀 Starting {choice}...")
        os.system(f"docker compose -f {compose_file} up -d")
        print(f"✅ {choice} started successfully!")
    elif action == "⏹️  Stop (down)":
        print(f"⏹️  Stopping {choice}...")
        os.system(f"docker compose -f {compose_file} down")
        print(f"✅ {choice} stopped successfully!")
    elif action == "🔄 Restart":
        print(f"🔄 Restarting {choice}...")
        os.system(f"docker compose -f {compose_file} restart")
        print(f"✅ {choice} restarted successfully!")
    elif action == "📊 Show logs":
        print(f"📊 Logs for {choice}:")
        os.system(f"docker compose -f {compose_file} logs --tail=50")


def main():
    """Main CLI function"""
    print("=" * 50)
    print("🐳  Container Manager CLI")
    print("=" * 50)
    print()
    
    # Ensure directories exist
    volumes_dir, compose_dir = ensure_directories()
    
    # Main menu
    action = select(
        "What do you want to do?",
        choices=[
            "➕ Configure new service",
            "▶️  Manage existing services"
        ],
        style=custom_style
    ).ask()
    
    if not action:
        return
    
    if action == "▶️  Manage existing services":
        list_and_start_containers(compose_dir)
        
        # Option to return to menu
        another = select(
            "\nDo you want to do something else?",
            choices=["Yes", "No"],
            style=custom_style
        ).ask()
        
        if another == "Yes":
            print("\n" + "=" * 50 + "\n")
            main()
        return
    
    # Category selection
    category = select_category()
    if not category:
        print("Operation cancelled.")
        return
    
    # Service selection
    service = select_service(category)
    if not service:
        print("Operation cancelled.")
        return
    
    # Service configuration
    config = get_service_config(category, service)
    
    # Create docker-compose file
    compose_file, service_name = create_compose_file(
        category, service, config, volumes_dir, compose_dir
    )
    
    print(f"\n✅ Configuration completed!")
    print(f"📦 Service name: {service_name}")
    print(f"💾 Persistent volumes: {volumes_dir / service_name}")
    
    # Start container
    start_container(compose_file)
    
    # Option to configure another service
    another = select(
        "\nDo you want to configure another service?",
        choices=["Yes", "No"],
        style=custom_style
    ).ask()
    
    if another == "Yes":
        print("\n" + "=" * 50 + "\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
