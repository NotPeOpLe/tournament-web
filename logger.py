import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="DEBUG", 
    format="%(message)s", 
    datefmt="[%X]", 
    handlers=[RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True
        )]
)

log = logging.getLogger(__name__)