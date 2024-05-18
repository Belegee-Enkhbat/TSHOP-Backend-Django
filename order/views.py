import stripe

from django.conf import settings
from django.http import HttpRequest

from rest_framework import status, authentication, permissions
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer, MyOrderSerializer


@api_view(["POST"])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def checkout(request) -> Response:
    # Deserialize the request data to validate and save the order
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Calculate the total amount to be paid
        paid_amount = sum(
            item.get("quantity") * item.get("product").price
            for item in serializer.validated_data["items"]
        )

        try:
            # Create a Stripe charge
            stripe.Charge.create(
                amount=int(paid_amount * 100),  # Stripe requires amount in cents
                currency="USD",
                description="Charge from Glee",
                source=serializer.validated_data["stripe_token"],
            )

            # Save the order with the user and paid amount information
            serializer.save(user=request.user, paid_amount=paid_amount)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            # Handle Stripe errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Return validation errors if the serializer is not valid
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersList(APIView):
    # Хэрэглэгчийн танилтыг TokenAuthentication ашиглан хийдэг
    authentication_classes = [authentication.TokenAuthentication]
    # Хэрэглэгчийн эрхийг шалгахдаа IsAuthenticated ашигладаг
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        # Хэрэглэгчийн захиалгуудыг шүүх
        orders = Order.objects.filter(user=request.user)
        # Захиалгуудыг сериалчилж JSON форматад хөрвүүлэх
        serializer = MyOrderSerializer(orders, many=True)
        # Сериалчилсан өгөгдлийг хариу болгон буцаах
        return Response(serializer.data)
