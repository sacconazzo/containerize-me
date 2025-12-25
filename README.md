# 🐳 Container Manager CLI

Interactive CLI to generate and manage Docker containers with docker-compose dynamically.

## ✨ Features

- 📋 **Interactive menu** - Simple navigation with menu selection
- 🗂️ **Organized categories** - Services organized by category (Database, Cache, Message Queue, etc.)
- ⚙️ **Guided configuration** - Username, password, and ports with default values
- 💾 **Automatic persistent volumes** - Local data storage without manual configuration
- 🚀 **Quick start** - Option to start the container immediately after configuration
- 📦 **Reusable compose files** - Generated docker-compose.yml files saved for future use

## 🛠️ Supported Services

### Database

- MongoDB
- PostgreSQL
- MySQL
- MariaDB
- Redis

### Cache

- Redis
- Memcached

### Message Queue

- RabbitMQ (with Management UI)
- Apache Kafka (with Zookeeper)

### Search Engine

- Elasticsearch

### Web Server

- Nginx
- Apache

## 📦 Installation

1. Clone the repository or download the files

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure you have Docker and docker compose installed:

```bash
docker --version
docker compose version
```

## 🚀 Usage

Run the CLI:

```bash
python cli.py
```

### Workflow

1. **Select category** - Choose from Database, Cache, Message Queue, etc.
2. **Select service** - Choose the specific service (e.g., MongoDB, PostgreSQL)
3. **Configure parameters**:
   - Username (with suggested default)
   - Password (with suggested default)
   - Database name (if applicable)
   - Port (with suggested default)
4. **Automatic start** - Choose whether to start the container immediately or later

### Example

```
==================================================
🐳  Container Manager CLI
==================================================

? Select a category: Database
? Select a service from Database: PostgreSQL

🚀 Configuration for PostgreSQL
==================================================
? Username (default: postgres): myuser
? Password (default: postgres): ********
? Database name (default: mydb): production_db
? Port (default: 5432): 5432

✅ Configuration completed!
📦 Service name: postgresql
💾 Persistent volumes: /path/to/volumes/postgresql

? Do you want to start the container now? Yes

🚀 Starting container...
✅ Container started successfully!
📄 Compose file saved at: /path/to/compose-files/postgresql-compose.yml
```

## 📁 Directory Structure

After first use, the following will be created automatically:

```
.
├── cli.py
├── services.py
├── requirements.txt
├── volumes/                    # Persistent volumes (created automatically)
│   ├── mongodb/
│   ├── postgresql/
│   └── ...
└── compose-files/              # Generated docker-compose files (created automatically)
    ├── mongodb-compose.yml
    ├── postgresql-compose.yml
    └── ...
```

## 🎯 Container Management

### Start a container

```bash
docker compose -f compose-files/SERVICE-NAME-compose.yml up -d
```

### Stop a container

```bash
docker compose -f compose-files/SERVICE-NAME-compose.yml down
```

### View logs

```bash
docker compose -f compose-files/SERVICE-NAME-compose.yml logs -f
```

### Restart a container

```bash
docker compose -f compose-files/SERVICE-NAME-compose.yml restart
```

## 💡 Tips

- **Persistent volumes** are saved locally in the `volumes/` folder
- **Docker-compose files** are saved in `compose-files/` and can be reused
- **Ports** can be customized to avoid conflicts
- You can **configure multiple instances** of the same service with different ports

## 🔧 Customization

To add new services, edit the [services.py](services.py) file and add the configuration to the `SERVICES_CATALOG` dictionary.

Example:

```python
"Database": {
    "NewService": {
        "image": "image:tag",
        "default_user": "admin",
        "default_password": "password",
        "default_database": "mydb",
        "default_port": 1234,
        "has_database": True,
        "env_vars": {
            "ENV_VAR": "username"
        },
        "volume_path": "/data"
    }
}
```

## 📝 License

MIT License - Feel free to use and modify as you wish!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
