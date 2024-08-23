from typing import Any

from pydantic import Field, field_validator
from typing_extensions import override

from lion_core.communication.base_mail import BaseMail
from lion_core.communication.package import Package, PackageCategory
from lion_core.exceptions import LionValueError


class Mail(BaseMail):
    """
    A mail component with sender, recipient, and package.

    The `Mail` class represents a communication component that includes the
    sender, recipient, and the package to be delivered. It extends the
    `BaseMail` class, adding a `package` field and methods for validating
    sender and recipient information.

    Attributes:
        sender (str): The ID of the sender node. Valid values include 'system',
            'user', or 'assistant'.
        recipient (str): The ID of the recipient node. Valid values include
            'system', 'user', or 'assistant'.
        package (Package): The package to be delivered, which includes the
            content and metadata.

    Properties:
        category (PackageCategory): The category of the package.

    Methods:
        _validate_sender_recipient(cls, value: Any) -> str: Validates the
            sender and recipient fields to ensure they are not 'N/A'.
    """

    sender: str = Field(
        ...,
        title="Sender",
        description="The ID of the sender node, or 'system', 'user', "
        "or 'assistant'.",
    )

    recipient: str = Field(
        ...,
        title="Recipient",
        description="The ID of the recipient node, or 'system', 'user', "
        "or 'assistant'.",
    )

    package: Package = Field(
        ...,
        title="Package",
        description="The package to be delivered.",
    )

    @property
    def category(self) -> PackageCategory:
        """
        Returns the category of the package.

        The `category` property extracts and returns the `PackageCategory`
        associated with the `package`.

        Returns:
            PackageCategory: The category of the package.
        """
        return self.package.category

    @override
    @field_validator("sender", "recipient", mode="before")
    @classmethod
    def _validate_sender_recipient(cls, value: Any) -> str:
        """
        Validates the sender and recipient fields.

        This method overrides the base validation to ensure that the sender
        and recipient are valid and not 'N/A'. It relies on the parent
        validation logic and adds an additional check.

        Args:
            value (Any): The value to validate, typically a string representing
            a node ID or a predefined value like 'system'.

        Returns:
            str: The validated sender or recipient value.

        Raises:
            LionValueError: If the value is 'N/A', indicating an invalid sender
            or recipient for `Mail`.
        """
        value = super()._validate_sender_recipient(value)
        if value == "N/A":
            raise LionValueError(f"Invalid sender or recipient for Mail")
        return value


# File: lion_core/communication/mail.py
