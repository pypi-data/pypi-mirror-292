from ..models import (
    ApplePaymentTokenVersion,
    ApplePayPayment,
    MobilePaymentMethodSpecificInput,
    Network,
)


def network_from_string(value: str) -> str:
    for network in Network:
        if value.upper() == network.value:
            return network
    raise TypeError(f"'{value}' can't represent a Network")


def version_from_string(value: str) -> str:
    for version in ApplePaymentTokenVersion:
        if value.upper() == version.value:
            return version
    raise TypeError(f"'{value}' can't represent an ApplePaymentTokenVersion")


def transform_apple_pay_payment_to_mobile_payment_method_specific_input(
    payment: ApplePayPayment,
) -> MobilePaymentMethodSpecificInput:
    token = payment.token or {}
    paymentData = token.get("paymentData", {})
    header = paymentData.get("header", {})
    paymentMethod = token.get("paymentMethod", {})

    return MobilePaymentMethodSpecificInput(
        paymentProductId=302,
        publicKeyHash=header.get("publicKeyHash"),
        ephemeralKey=header.get("ephemeralPublicKey"),
        paymentProduct302SpecificInput={
            "network": network_from_string(paymentMethod.get("network", "")),
            "token": {
                "version": version_from_string(paymentData.get("version", "")),
                "signature": paymentData.get("signature"),
                "header": {
                    "transactionId": header.get("transactionId"),
                    "applicationData": header.get("applicationData"),
                },
            },
        },
    )
