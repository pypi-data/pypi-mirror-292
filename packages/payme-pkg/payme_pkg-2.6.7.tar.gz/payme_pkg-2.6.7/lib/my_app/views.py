# Create your views here.
from payme.views import MerchantAPIView


class PaymeCallBackAPIView(MerchantAPIView):
    """
    the cancel transition.
    """
    def create_transaction(self, order_id, action) -> None:
        print(f"create_transaction for order_id: {order_id}, response: {action}")  # noqa

    def perform_transaction(self, order_id, action) -> None:
        print(f"perform_transaction for order_id: {order_id}, response: {action}") # noqa

    def cancel_transaction(self, order_id, action) -> None:
        print(f"cancel_transaction for order_id: {order_id}, response: {action}") # noqa
