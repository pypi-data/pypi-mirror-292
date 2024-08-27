import dataclasses
from typing import Optional

from portone_server_sdk._api import ApiRequest, ApiErrorResponse
from portone_server_sdk import _errors
from portone_server_sdk._sync import ApiClient
from portone_server_sdk._openapi._schemas._already_paid_error import AlreadyPaidError
from portone_server_sdk._openapi._schemas._currency import Currency
from portone_server_sdk._openapi._schemas._forbidden_error import ForbiddenError
from portone_server_sdk._openapi._schemas._invalid_request_error import InvalidRequestError
from portone_server_sdk._openapi._schemas._pre_register_payment_body import PreRegisterPaymentBody
from portone_server_sdk._openapi._schemas._pre_register_payment_error import PreRegisterPaymentError
from portone_server_sdk._openapi._schemas._pre_register_payment_response import PreRegisterPaymentResponse
from portone_server_sdk._openapi._schemas._unauthorized_error import UnauthorizedError

@dataclasses.dataclass
class PreRegisterPaymentParam:
    paymentId: str
    """결제 건 아이디"""

@dataclasses.dataclass
class PreRegisterPaymentQuery:
    pass

@dataclasses.dataclass
class PreRegisterPaymentRequest(ApiRequest[PreRegisterPaymentResponse, PreRegisterPaymentError, PreRegisterPaymentParam, PreRegisterPaymentQuery, PreRegisterPaymentBody]):
    method = "post"
    path = "/payments/{paymentId}/pre-register"

@dataclasses.dataclass
class PreRegisterPayment(ApiClient):
    def pre_register_payment(
        self,
        paymentId: str,
        totalAmount: Optional[int],
        taxFreeAmount: Optional[int],
        currency: Optional[Currency],
    ) -> None:
        """결제 정보 사전 등록
        
        결제 정보를 사전 등록합니다.
        
        Args:
            paymentId (str): 결제 건 아이디.
            totalAmount (Optional[int]): 결제 총 금액.
            taxFreeAmount (Optional[int]): 결제 면세 금액.
            currency (Optional[Currency]): 통화 단위.
        
        Raises:
            _errors.AlreadyPaidError: 결제가 이미 완료된 경우
            _errors.ForbiddenError: 요청이 거절된 경우
            _errors.InvalidRequestError: 요청된 입력 정보가 유효하지 않은 경우
            _errors.UnauthorizedError: 인증 정보가 올바르지 않은 경우
        """
        param_ = PreRegisterPaymentParam(
            paymentId=paymentId,
        )
        query_ = PreRegisterPaymentQuery()
        body_ = PreRegisterPaymentBody(
            storeId=self.store_id,
            totalAmount=totalAmount,
            taxFreeAmount=taxFreeAmount,
            currency=currency,
        )
        response_ = self.send(
            PreRegisterPaymentRequest(param_, query_, body_),
            PreRegisterPaymentResponse,
            PreRegisterPaymentError,
        )
        if isinstance(response_, ApiErrorResponse):
            error_ = response_.data
            if isinstance(error_, AlreadyPaidError):
                raise _errors.AlreadyPaidError(error_)
            elif isinstance(error_, ForbiddenError):
                raise _errors.ForbiddenError(error_)
            elif isinstance(error_, InvalidRequestError):
                raise _errors.InvalidRequestError(error_)
            else:
                raise _errors.UnauthorizedError(error_)
