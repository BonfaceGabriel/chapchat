from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from orders.models import Order, OrderItem


class AnalyticsOverview(APIView):
    """Return sales analytics for the authenticated seller."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        seller = request.user.seller_profile
        orders = (
            Order.objects.filter(seller=seller)
            .exclude(status=Order.OrderStatus.IN_PROGRESS)
        )

        # Exclude cancelled or failed orders from revenue totals
        revenue_orders = orders.exclude(
            status__in=[Order.OrderStatus.CANCELLED, Order.OrderStatus.FAILED]
        )

        total_sales = revenue_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = orders.count()
        average_order_value = float(total_sales) / total_orders if total_orders else 0

        # Monthly sales for last six months
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        monthly_query = (
            revenue_orders.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )
        monthly_sales = [
            {'month': m['month'].strftime('%Y-%m'), 'total': m['total']}
            for m in monthly_query
        ]

        # Order status distribution
        status_counts = orders.values('status').annotate(count=Count('id'))
        status_distribution = {sc['status']: sc['count'] for sc in status_counts}

        # Top 5 products by quantity sold
        top_products_qs = (
            OrderItem.objects.filter(order__in=revenue_orders)
            .values('product__name')
            .annotate(quantity=Sum('quantity'))
            .order_by('-quantity')[:5]
        )
        top_products = [
            {'name': p['product__name'] or 'Unknown', 'quantity': p['quantity']}
            for p in top_products_qs
        ]

        data = {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_order_value': average_order_value,
            'monthly_sales': monthly_sales,
            'status_distribution': status_distribution,
            'top_products': top_products,
        }
        return Response(data)
