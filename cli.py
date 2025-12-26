#!/usr/bin/env python3
"""
Container Manager CLI - Gestione dinamica di container Docker con docker-compose
"""
import os
import sys
from pathlib import Path
import yaml
from questionary import select, text, password, Style
from services import SERVICES_CATALOG, generate_compose_config


# Style personalizzato per il menu
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
    """Crea le directory necessarie se non esistono"""
    base_dir = Path.cwd()
    volumes_dir = base_dir / "volumes"
    compose_dir = base_dir / "compose-files"
    
    volumes_dir.mkdir(exist_ok=True)
    compose_dir.mkdir(exist_ok=True)
    
    return volumes_dir, compose_dir


def select_category():
    """Permette all'utente di scegliere una categoria di servizi"""
    categories = list(SERVICES_CATALOG.keys())
    
    category = select(
        "Seleziona una categoria:",
        choices=categories,
        style=custom_style
    ).ask()
    
    return category


def select_service(category):
    """Permette all'utente di scegliere un servizio dalla categoria"""
    services = list(SERVICES_CATALOG[category].keys())
    
    service = select(
        f"Seleziona un servizio da {category}:",
        choices=services,
        style=custom_style
    ).ask()
    
    return service


def get_service_config(category, service):
    """Ottiene la configurazione per il servizio selezionato"""
    service_info = SERVICES_CATALOG[category][service]
    
    print(f"\n🚀 Configurazione per {service}")
    print("=" * 50)
    
    config = {}
    
    # Username (skip per MySQL che usa solo root)
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
    
    # Database name (se applicabile)
    if service_info.get('has_database', False):
        default_db = service_info.get('default_database', 'mydb')
        db_name = text(
            f"Nome database (default: {default_db}):",
            style=custom_style
        ).ask()
        config['database'] = db_name if db_name else default_db
    
    # Port
    default_port = service_info.get('default_port', 8080)
    port = text(
        f"Porta (default: {default_port}):",
        style=custom_style
    ).ask()
    config['port'] = port if port else default_port
    
    return config


def create_compose_file(category, service, config, volumes_dir, compose_dir):
    """Crea il file docker-compose.yml per il servizio"""
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
    
    # Salva il file docker-compose
    compose_file = compose_dir / f"{service_name}-compose.yml"
    with open(compose_file, 'w') as f:
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    return compose_file, service_name


def start_container(compose_file):
    """Avvia il container usando docker compose"""
    choice = select(
        "\nVuoi avviare il container ora?",
        choices=["Sì", "No"],
        style=custom_style
    ).ask()
    
    if choice == "Sì":
        print(f"\n🚀 Avvio container...")
        os.system(f"docker compose -f {compose_file} up -d")
        print(f"\n✅ Container avviato con successo!")
        print(f"📄 File compose salvato in: {compose_file}")
    else:
        print(f"\n📄 File compose salvato in: {compose_file}")
        print(f"Per avviare il container manualmente, esegui:")
        print(f"  docker compose -f {compose_file} up -d")


def list_and_start_containers(compose_dir):
    """Elenca e permette di avviare i container già configurati"""
    compose_files = list(compose_dir.glob("*-compose.yml"))
    
    if not compose_files:
        print("\n⚠️  Nessun file docker-compose trovato!")
        print("Configura prima un servizio.")
        return
    
    # Lista dei servizi disponibili
    service_names = [f.stem.replace('-compose', '') for f in compose_files]
    service_names.append("⬅️  Torna al menu principale")
    
    choice = select(
        "\nSeleziona quale servizio avviare:",
        choices=service_names,
        style=custom_style
    ).ask()
    
    if choice == "⬅️  Torna al menu principale" or not choice:
        return
    
    # Trova il file compose corrispondente
    compose_file = compose_dir / f"{choice}-compose.yml"
    
    action = select(
        f"\nCosa vuoi fare con {choice}?",
        choices=[
            "▶️  Avvia (up -d)",
            "⏹️  Ferma (down)",
            "🔄 Riavvia (restart)",
            "📊 Mostra logs",
            "⬅️  Torna indietro"
        ],
        style=custom_style
    ).ask()
    
    if action == "⬅️  Torna indietro" or not action:
        return
    
    print()
    if action == "▶️  Avvia (up -d)":
        print(f"🚀 Avvio {choice}...")
        os.system(f"docker compose -f {compose_file} up -d")
        print(f"✅ {choice} avviato con successo!")
    elif action == "⏹️  Ferma (down)":
        print(f"⏹️  Fermo {choice}...")
        os.system(f"docker compose -f {compose_file} down")
        print(f"✅ {choice} fermato con successo!")
    elif action == "🔄 Riavvia (restart)":
        print(f"🔄 Riavvio {choice}...")
        os.system(f"docker compose -f {compose_file} restart")
        print(f"✅ {choice} riavviato con successo!")
    elif action == "📊 Mostra logs":
        print(f"📊 Logs di {choice}:")
        os.system(f"docker compose -f {compose_file} logs --tail=50")


def main():
    """Funzione principale della CLI"""
    print("=" * 50)
    print("🐳  Container Manager CLI")
    print("=" * 50)
    print()
    
    # Assicura che le directory esistano
    volumes_dir, compose_dir = ensure_directories()
    
    # Menu principale
    action = select(
        "Cosa vuoi fare?",
        choices=[
            "➕ Configura nuovo servizio",
            "▶️  Gestisci servizi esistenti",
            "❌ Esci"
        ],
        style=custom_style
    ).ask()
    
    if action == "❌ Esci" or not action:
        print("\n👋 Arrivederci!")
        return
    
    if action == "▶️  Gestisci servizi esistenti":
        list_and_start_containers(compose_dir)
        
        # Opzione per tornare al menu
        another = select(
            "\nVuoi fare altro?",
            choices=["Sì", "No"],
            style=custom_style
        ).ask()
        
        if another == "Sì":
            print("\n" + "=" * 50 + "\n")
            main()
        return
    
    # Selezione categoria
    category = select_category()
    if not category:
        print("Operazione annullata.")
        return
    
    # Selezione servizio
    service = select_service(category)
    if not service:
        print("Operazione annullata.")
        return
    
    # Configurazione servizio
    config = get_service_config(category, service)
    
    # Crea il file docker-compose
    compose_file, service_name = create_compose_file(
        category, service, config, volumes_dir, compose_dir
    )
    
    print(f"\n✅ Configurazione completata!")
    print(f"📦 Nome servizio: {service_name}")
    print(f"💾 Volumi persistenti: {volumes_dir / service_name}")
    
    # Avvia il container
    start_container(compose_file)
    
    # Opzione per configurare un altro servizio
    another = select(
        "\nVuoi configurare un altro servizio?",
        choices=["Sì", "No"],
        style=custom_style
    ).ask()
    
    if another == "Sì":
        print("\n" + "=" * 50 + "\n")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Arrivederci!")
        sys.exit(0)
