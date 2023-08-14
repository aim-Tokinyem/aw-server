from aw_core.config import load_config_toml

default_config = """
[server]
host = "localhost"
port = "5600"
storage = "postgrey"
cors_origins = ""
protocol = "https"

[server.custom_static]

[server-testing]
host = "localhost"
port = "5666"
storage = "postgrey"
cors_origins = ""
protocol = "https"

[server-testing.custom_static]
""".strip()

config = load_config_toml("aw-server", default_config)

def load_config():
    return load_config_toml("aw-server", default_config)
