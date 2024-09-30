from django.shortcuts import render
from subscription.models import Subscription, SubscriptionPlan, Payment
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required

import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def home_page(request):
    return render(request, 'home.html')


def pricing(request):
    return render(request, 'pricing.html')

@login_required
def dashboard(request):
    user = request.user
    try:
        subscription = Subscription.objects.get(user=user)
    except Subscription.DoesNotExist:
        return redirect('pricing')

    context = {
        'subscription': subscription,
        'credits': subscription.credits if subscription else 0,
    }

    return render(request, 'dashboard.html', context=context)

def calculate_total_price(num_pics):
    return num_pics * 99


@login_required
def buy_credits(request):
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        return redirect('pricing')
    
    if request.method == 'POST':
        num_pics = int(request.POST.get('num_pics'))
        total_amount = calculate_total_price(num_pics)
        plan = subscription.plan

        razorpay_order = razorpay_client.order.create({
            'amount': total_amount * 100,
            'currency': 'INR',
            'payment_capture': '1',
        })

        payment = Payment.objects.create(
            user=request.user,
            razorpay_order_id=razorpay_order['id'],
            amount=total_amount
        )

        context = {
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': razorpay_order['id'],
            'amount': total_amount,
            'plan': plan,
            'user': request.user
        }

        # subscription.add_credit(num_pics)
        return render(request, 'payment_page.html', context)
        
        # return redirect('dashboard')

    return render(request, 'buy_credits.html')