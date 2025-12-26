"""
Catalogo dei servizi disponibili e generazione configurazioni docker-compose
"""

# Catalogo dei servizi organizzato per categoria
SERVICES_CATALOG = {
    "Database": {
        "MongoDB": {
            "image": "mongo:latest",
            "default_user": "admin",
            "default_password": "password123",
            "default_database": "mydb",
            "default_port": 27017,
            "has_database": True,
            "env_vars": {
                "MONGO_INITDB_ROOT_USERNAME": "username",
                "MONGO_INITDB_ROOT_PASSWORD": "password",
                "MONGO_INITDB_DATABASE": "database"
            },
            "volume_path": "/data/db"
        },
        "PostgreSQL": {
            "image": "postgres:15",
            "default_user": "postgres",
            "default_password": "postgres",
            "default_database": "mydb",
            "default_port": 5432,
            "has_database": True,
            "env_vars": {
                "POSTGRES_USER": "username",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "database"
            },
            "volume_path": "/var/lib/postgresql/data"
        },
        "MySQL": {
            "image": "mysql:latest",
            "default_user": "root",
            "default_password": "root",
            "default_database": "mydb",
            "default_port": 3306,
            "has_database": True,
            "env_vars": {
                "MYSQL_ROOT_PASSWORD": "password",
                "MYSQL_DATABASE": "database",
                "MYSQL_USER": "username",
                "MYSQL_PASSWORD": "password"
            },
            "volume_path": "/var/lib/mysql"
        },
        "Redis": {
            "image": "redis:latest",
            "default_user": "",
            "default_password": "redis",
            "default_database": "",
            "default_port": 6379,
            "has_database": False,
            "env_vars": {},
            "volume_path": "/data",
            "command": "redis-server --requirepass {password}"
        },
        "MariaDB": {
            "image": "mariadb:latest",
            "default_user": "root",
            "default_password": "root",
            "default_database": "mydb",
            "default_port": 3306,
            "has_database": True,
            "env_vars": {
                "MARIADB_ROOT_PASSWORD": "password",
                "MARIADB_DATABASE": "database",
                "MARIADB_USER": "username",
                "MARIADB_PASSWORD": "password"
            },
            "volume_path": "/var/lib/mysql"
        },
        "MSSQL": {
            "image": "mcr.microsoft.com/mssql/server:2022-latest",
            "default_user": "sa",
            "default_password": "YourStrong@Passw0rd",
            "default_database": "mydb",
            "default_port": 1433,
            "has_database": True,
            "env_vars": {
                "ACCEPT_EULA": "Y",
                "SA_PASSWORD": "password",
                "MSSQL_PID": "Developer"
            },
            "volume_path": "/var/opt/mssql"
        }
    },
    "Cache": {
        "Redis": {
            "image": "redis:latest",
            "default_user": "",
            "default_password": "redis",
            "default_port": 6379,
            "has_database": False,
            "env_vars": {},
            "volume_path": "/data",
            "command": "redis-server --requirepass {password}"
        },
        "Memcached": {
            "image": "memcached:latest",
            "default_user": "",
            "default_password": "",
            "default_port": 11211,
            "has_database": False,
            "env_vars": {},
            "volume_path": None
        }
    },
    "Message Queue": {
        "RabbitMQ": {
            "image": "rabbitmq:management",
            "default_user": "admin",
            "default_password": "admin",
            "default_port": 5672,
            "has_database": False,
            "env_vars": {
                "RABBITMQ_DEFAULT_USER": "username",
                "RABBITMQ_DEFAULT_PASS": "password"
            },
            "volume_path": "/var/lib/rabbitmq",
            "additional_ports": [15672]  # Management UI
        },
        "Apache Kafka": {
            "image": "confluentinc/cp-kafka:latest",
            "default_user": "",
            "default_password": "",
            "default_port": 9092,
            "has_database": False,
            "env_vars": {
                "KAFKA_ZOOKEEPER_CONNECT": "zookeeper:2181",
                "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://localhost:9092",
                "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1"
            },
            "volume_path": "/var/lib/kafka/data",
            "requires_zookeeper": True
        }
    },
    "Search Engine": {
        "Elasticsearch": {
            "image": "elasticsearch:8.11.0",
            "default_user": "elastic",
            "default_password": "elastic",
            "default_port": 9200,
            "has_database": False,
            "env_vars": {
                "discovery.type": "single-node",
                "ELASTIC_PASSWORD": "password",
                "xpack.security.enabled": "true"
            },
            "volume_path": "/usr/share/elasticsearch/data",
            "additional_ports": [9300]
        }
    },
    "Web Server": {
        "Nginx": {
            "image": "nginx:latest",
            "default_user": "",
            "default_password": "",
            "default_port": 80,
            "has_database": False,
            "env_vars": {},
            "volume_path": "/usr/share/nginx/html",
            "additional_volumes": {
                "/etc/nginx/conf.d": "config"
            }
        },
        "Apache": {
            "image": "httpd:latest",
            "default_user": "",
            "default_password": "",
            "default_port": 80,
            "has_database": False,
            "env_vars": {},
            "volume_path": "/usr/local/apache2/htdocs"
        }
    }
}


def generate_compose_config(category, service, service_name, config, volume_path):
    """Genera la configurazione docker-compose per il servizio selezionato"""
    service_info = SERVICES_CATALOG[category][service]
    
    compose_config = {
        "name": "containerize-me",
        "services": {
            service_name: {
                "image": service_info["image"],
                "container_name": service_name,
                "restart": "unless-stopped",
                "ports": [
                    f"{config['port']}:{service_info['default_port']}"
                ]
            }
        }
    }
    
    service_config = compose_config["services"][service_name]
    
    # Aggiungi variabili d'ambiente
    if service_info.get("env_vars"):
        env = {}
        for key, value_key in service_info["env_vars"].items():
            if value_key in config:
                env[key] = config[value_key]
            elif isinstance(value_key, str) and not value_key.startswith("{"):
                env[key] = value_key
        
        if env:
            service_config["environment"] = env
    
    # Aggiungi comando personalizzato (per Redis)
    if service_info.get("command"):
        cmd = service_info["command"].format(**config)
        service_config["command"] = cmd
    
    # Aggiungi volumi
    if service_info.get("volume_path"):
        service_config["volumes"] = [
            f"{volume_path}:{service_info['volume_path']}"
        ]
        
        # Aggiungi volumi addizionali
        if service_info.get("additional_volumes"):
            for container_path, subdir in service_info["additional_volumes"].items():
                host_path = f"{volume_path}/{subdir}"
                service_config["volumes"].append(f"{host_path}:{container_path}")
    
    # Aggiungi porte addizionali
    if service_info.get("additional_ports"):
        for port in service_info["additional_ports"]:
            service_config["ports"].append(f"{port}:{port}")
    
    # Gestione servizi con dipendenze (es. Kafka con Zookeeper)
    if service_info.get("requires_zookeeper"):
        compose_config["services"]["zookeeper"] = {
            "image": "confluentinc/cp-zookeeper:latest",
            "container_name": f"{service_name}-zookeeper",
            "restart": "unless-stopped",
            "environment": {
                "ZOOKEEPER_CLIENT_PORT": 2181,
                "ZOOKEEPER_TICK_TIME": 2000
            },
            "ports": ["2181:2181"],
            "volumes": [f"{volume_path}/zookeeper:/var/lib/zookeeper/data"]
        }
        service_config["depends_on"] = ["zookeeper"]
    
    return compose_config
