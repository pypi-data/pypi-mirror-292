# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AccountHolderDocument", "RequiredDocumentUpload"]


class RequiredDocumentUpload(BaseModel):
    token: Optional[str] = None
    """Globally unique identifier for the document upload."""

    image_type: Optional[Literal["back", "front"]] = None
    """Type of image to upload."""

    status: Optional[Literal["COMPLETED", "FAILED", "PENDING_UPLOAD", "UPLOADED"]] = None
    """Status of document image upload."""

    status_reasons: Optional[
        List[
            Literal[
                "BACK_IMAGE_BLURRY",
                "FILE_SIZE_TOO_LARGE",
                "FRONT_IMAGE_BLURRY",
                "FRONT_IMAGE_GLARE",
                "INVALID_FILE_TYPE",
                "UNKNOWN_ERROR",
            ]
        ]
    ] = None

    upload_url: Optional[str] = None
    """URL to upload document image to.

    Note that the upload URLs expire after 7 days. If an upload URL expires, you can
    refresh the URLs by retrieving the document upload from
    `GET /account_holders/{account_holder_token}/documents`.
    """


class AccountHolderDocument(BaseModel):
    token: Optional[str] = None
    """Globally unique identifier for the document."""

    account_holder_token: Optional[str] = None
    """Globally unique identifier for the account holder."""

    document_type: Optional[
        Literal[
            "EIN_LETTER",
            "TAX_RETURN",
            "OPERATING_AGREEMENT",
            "CERTIFICATE_OF_FORMATION",
            "DRIVERS_LICENSE",
            "PASSPORT",
            "PASSPORT_CARD",
            "CERTIFICATE_OF_GOOD_STANDING",
            "ARTICLES_OF_INCORPORATION",
            "ARTICLES_OF_ORGANIZATION",
            "BYLAWS",
            "GOVERNMENT_BUSINESS_LICENSE",
            "PARTNERSHIP_AGREEMENT",
            "SS4_FORM",
            "BANK_STATEMENT",
            "UTILITY_BILL_STATEMENT",
            "SSN_CARD",
            "ITIN_LETTER",
        ]
    ] = None
    """Type of documentation to be submitted for verification."""

    entity_token: Optional[str] = None
    """Globally unique identifier for the entity."""

    required_document_uploads: Optional[List[RequiredDocumentUpload]] = None
