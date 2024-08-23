"""
Type annotations for payment-cryptography-data service client.

[Open documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/)

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_payment_cryptography_data.client import PaymentCryptographyDataPlaneClient

    session = get_session()
    async with session.create_client("payment-cryptography-data") as client:
        client: PaymentCryptographyDataPlaneClient
    ```
"""

from typing import Any, Dict, Mapping, Type

from aiobotocore.client import AioBaseClient
from botocore.client import ClientMeta

from .literals import MajorKeyDerivationModeType, PinBlockFormatForPinDataType
from .type_defs import (
    CardGenerationAttributesTypeDef,
    CardVerificationAttributesTypeDef,
    CryptogramAuthResponseTypeDef,
    DecryptDataOutputTypeDef,
    DukptAttributesTypeDef,
    DukptDerivationAttributesTypeDef,
    EncryptDataOutputTypeDef,
    EncryptionDecryptionAttributesTypeDef,
    GenerateCardValidationDataOutputTypeDef,
    GenerateMacOutputTypeDef,
    GeneratePinDataOutputTypeDef,
    MacAttributesTypeDef,
    PinGenerationAttributesTypeDef,
    PinVerificationAttributesTypeDef,
    ReEncryptDataOutputTypeDef,
    ReEncryptionAttributesTypeDef,
    SessionKeyDerivationTypeDef,
    TranslatePinDataOutputTypeDef,
    TranslationIsoFormatsTypeDef,
    VerifyAuthRequestCryptogramOutputTypeDef,
    VerifyCardValidationDataOutputTypeDef,
    VerifyMacOutputTypeDef,
    VerifyPinDataOutputTypeDef,
    WrappedKeyTypeDef,
)

__all__ = ("PaymentCryptographyDataPlaneClient",)

class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str

class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]
    VerificationFailedException: Type[BotocoreClientError]

class PaymentCryptographyDataPlaneClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        PaymentCryptographyDataPlaneClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.exceptions)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.can_paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#can_paginate)
        """

    async def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.close)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#close)
        """

    async def decrypt_data(
        self,
        *,
        KeyIdentifier: str,
        CipherText: str,
        DecryptionAttributes: EncryptionDecryptionAttributesTypeDef,
        WrappedKey: WrappedKeyTypeDef = ...,
    ) -> DecryptDataOutputTypeDef:
        """
        Decrypts ciphertext data to plaintext using a symmetric (TDES, AES), asymmetric
        (RSA), or derived (DUKPT or EMV) encryption key
        scheme.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.decrypt_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#decrypt_data)
        """

    async def encrypt_data(
        self,
        *,
        KeyIdentifier: str,
        PlainText: str,
        EncryptionAttributes: EncryptionDecryptionAttributesTypeDef,
        WrappedKey: WrappedKeyTypeDef = ...,
    ) -> EncryptDataOutputTypeDef:
        """
        Encrypts plaintext data to ciphertext using a symmetric (TDES, AES), asymmetric
        (RSA), or derived (DUKPT or EMV) encryption key
        scheme.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.encrypt_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#encrypt_data)
        """

    async def generate_card_validation_data(
        self,
        *,
        KeyIdentifier: str,
        PrimaryAccountNumber: str,
        GenerationAttributes: CardGenerationAttributesTypeDef,
        ValidationDataLength: int = ...,
    ) -> GenerateCardValidationDataOutputTypeDef:
        """
        Generates card-related validation data using algorithms such as Card
        Verification Values (CVV/CVV2), Dynamic Card Verification Values (dCVV/dCVV2),
        or Card Security Codes
        (CSC).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.generate_card_validation_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#generate_card_validation_data)
        """

    async def generate_mac(
        self,
        *,
        KeyIdentifier: str,
        MessageData: str,
        GenerationAttributes: MacAttributesTypeDef,
        MacLength: int = ...,
    ) -> GenerateMacOutputTypeDef:
        """
        Generates a Message Authentication Code (MAC) cryptogram within Amazon Web
        Services Payment
        Cryptography.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.generate_mac)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#generate_mac)
        """

    async def generate_pin_data(
        self,
        *,
        GenerationKeyIdentifier: str,
        EncryptionKeyIdentifier: str,
        GenerationAttributes: PinGenerationAttributesTypeDef,
        PrimaryAccountNumber: str,
        PinBlockFormat: PinBlockFormatForPinDataType,
        PinDataLength: int = ...,
    ) -> GeneratePinDataOutputTypeDef:
        """
        Generates pin-related data such as PIN, PIN Verification Value (PVV), PIN
        Block, and PIN Offset during new card issuance or
        reissuance.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.generate_pin_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#generate_pin_data)
        """

    async def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.generate_presigned_url)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#generate_presigned_url)
        """

    async def re_encrypt_data(
        self,
        *,
        IncomingKeyIdentifier: str,
        OutgoingKeyIdentifier: str,
        CipherText: str,
        IncomingEncryptionAttributes: ReEncryptionAttributesTypeDef,
        OutgoingEncryptionAttributes: ReEncryptionAttributesTypeDef,
        IncomingWrappedKey: WrappedKeyTypeDef = ...,
        OutgoingWrappedKey: WrappedKeyTypeDef = ...,
    ) -> ReEncryptDataOutputTypeDef:
        """
        Re-encrypt ciphertext using DUKPT or Symmetric data encryption keys.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.re_encrypt_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#re_encrypt_data)
        """

    async def translate_pin_data(
        self,
        *,
        IncomingKeyIdentifier: str,
        OutgoingKeyIdentifier: str,
        IncomingTranslationAttributes: TranslationIsoFormatsTypeDef,
        OutgoingTranslationAttributes: TranslationIsoFormatsTypeDef,
        EncryptedPinBlock: str,
        IncomingDukptAttributes: DukptDerivationAttributesTypeDef = ...,
        OutgoingDukptAttributes: DukptDerivationAttributesTypeDef = ...,
        IncomingWrappedKey: WrappedKeyTypeDef = ...,
        OutgoingWrappedKey: WrappedKeyTypeDef = ...,
    ) -> TranslatePinDataOutputTypeDef:
        """
        Translates encrypted PIN block from and to ISO 9564 formats 0,1,3,4.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.translate_pin_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#translate_pin_data)
        """

    async def verify_auth_request_cryptogram(
        self,
        *,
        KeyIdentifier: str,
        TransactionData: str,
        AuthRequestCryptogram: str,
        MajorKeyDerivationMode: MajorKeyDerivationModeType,
        SessionKeyDerivationAttributes: SessionKeyDerivationTypeDef,
        AuthResponseAttributes: CryptogramAuthResponseTypeDef = ...,
    ) -> VerifyAuthRequestCryptogramOutputTypeDef:
        """
        Verifies Authorization Request Cryptogram (ARQC) for a EMV chip payment card
        authorization.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.verify_auth_request_cryptogram)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#verify_auth_request_cryptogram)
        """

    async def verify_card_validation_data(
        self,
        *,
        KeyIdentifier: str,
        PrimaryAccountNumber: str,
        VerificationAttributes: CardVerificationAttributesTypeDef,
        ValidationData: str,
    ) -> VerifyCardValidationDataOutputTypeDef:
        """
        Verifies card-related validation data using algorithms such as Card
        Verification Values (CVV/CVV2), Dynamic Card Verification Values (dCVV/dCVV2)
        and Card Security Codes
        (CSC).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.verify_card_validation_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#verify_card_validation_data)
        """

    async def verify_mac(
        self,
        *,
        KeyIdentifier: str,
        MessageData: str,
        Mac: str,
        VerificationAttributes: MacAttributesTypeDef,
        MacLength: int = ...,
    ) -> VerifyMacOutputTypeDef:
        """
        Verifies a Message Authentication Code (MAC).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.verify_mac)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#verify_mac)
        """

    async def verify_pin_data(
        self,
        *,
        VerificationKeyIdentifier: str,
        EncryptionKeyIdentifier: str,
        VerificationAttributes: PinVerificationAttributesTypeDef,
        EncryptedPinBlock: str,
        PrimaryAccountNumber: str,
        PinBlockFormat: PinBlockFormatForPinDataType,
        PinDataLength: int = ...,
        DukptAttributes: DukptAttributesTypeDef = ...,
    ) -> VerifyPinDataOutputTypeDef:
        """
        Verifies pin-related data such as PIN and PIN Offset using algorithms including
        VISA PVV and
        IBM3624.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client.verify_pin_data)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/#verify_pin_data)
        """

    async def __aenter__(self) -> "PaymentCryptographyDataPlaneClient":
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/)
        """

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/payment-cryptography-data.html#PaymentCryptographyDataPlane.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_payment_cryptography_data/client/)
        """
