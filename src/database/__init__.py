"""Database module."""

from .models import (
    Base,
    Product,
    Price,
    ProductVariation,
    ProductSpecification,
    ProductImage,
    ScrapingLog,
    DuplicateProduct,
    DataQualityLog,
)
from .connection import (
    DatabaseManager,
    get_db_session,
    init_database,
    close_database,
    check_database_health,
    db_manager,
)

__all__ = [
    "Base",
    "Product",
    "Price",
    "ProductVariation",
    "ProductSpecification",
    "ProductImage",
    "ScrapingLog",
    "DuplicateProduct",
    "DataQualityLog",
    "DatabaseManager",
    "get_db_session",
    "init_database",
    "close_database",
    "check_database_health",
    "db_manager",
]

