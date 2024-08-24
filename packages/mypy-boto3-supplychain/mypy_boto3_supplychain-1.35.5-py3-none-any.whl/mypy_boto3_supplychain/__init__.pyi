"""
Main interface for supplychain service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_supplychain import (
        Client,
        SupplyChainClient,
    )

    session = Session()
    client: SupplyChainClient = session.client("supplychain")
    ```
"""

from .client import SupplyChainClient

Client = SupplyChainClient

__all__ = ("Client", "SupplyChainClient")
