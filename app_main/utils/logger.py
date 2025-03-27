import logging
import os

# Criar diretorio de logs se nao existir
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'app.log')
#logger global
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("app_main")

def log_error(message: str, exception: Exception = None):
    """Registrar mensagens de erro."""
    if exception:
        logger.error(f"{message}: {exception}")
    else:
        logger.error(message)
