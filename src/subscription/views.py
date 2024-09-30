from django.shortcuts import render, redirect
from .models import SubscriptionPlan, Payment, Subscription
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.
@login_required
def create_order(request, plan_id):
    plan = SubscriptionPlan.objects.get(id=plan_id)
    user = request.user

    # Calculate the amount in paise (Razorpay uses paise)
    amount = int(plan.price * 100)

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Store payment info in the database
    payment = Payment.objects.create(
        user=user,
        subscription_plan=plan,
        amount=plan.price,
        razorpay_order_id=razorpay_order['id']
    )

    context = {
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_id': razorpay_order['id'],
        'amount': amount,
        'plan': plan,
        'user': user
    }

    return render(request, 'payment_page.html', context)

# @csrf_exempt
# def verify_payment(request):
#     if request.method == 'POST':
#         razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         params_dict = {
#             'razorpay_order_id': request.POST.get('razorpay_order_id'),
#             'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
#             'razorpay_signature': request.POST.get('razorpay_signature')
#         }

#         # Verify the payment signature
#         try:
#             razorpay_client.utility.verify_payment_signature(params_dict)

#             # If signature is correct, mark payment as successful
#             payment = Payment.objects.get(razorpay_order_id=params_dict['razorpay_order_id'])
#             payment.razorpay_payment_id = params_dict['razorpay_payment_id']
#             payment.razorpay_signature = params_dict['razorpay_signature']
#             payment.paid = True
#             payment.save()

#             # Activate the user's subscription
#             try:
#                 subscription = Subscription.objects.get_or_create(user=request.user)
#                 subscription.add_credit()
#             except:
#                 subscription = Subscription.objects.create(
#                 user=payment.user,
#                 plan=payment.subscription_plan,
#                 credits=payment.subscription_plan.credits,
#                 active=True
#             )

#             return render(request, 'payment_success.html', {'subscription': subscription})

#         except razorpay.errors.SignatureVerificationError:
#             return render(request, 'payment_failed.html')


@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        params_dict = {
            'razorpay_order_id': request.POST.get('razorpay_order_id'),
            'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
            'razorpay_signature': request.POST.get('razorpay_signature')
        }

        try:
            # Verify the payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Mark payment as successful
            payment = Payment.objects.get(razorpay_order_id=params_dict['razorpay_order_id'])
            payment.razorpay_payment_id = params_dict['razorpay_payment_id']
            payment.razorpay_signature = params_dict['razorpay_signature']
            payment.paid = True
            payment.save()

            # Get or create the user's subscription
            subscription, created = Subscription.objects.get_or_create(
                user=payment.user,
                defaults={
                    'plan': payment.subscription_plan,  # You may need to adjust based on your logic
                    'credits': 0,  # Initial credits if a new subscription is created
                    'active': True
                }
            )

            # Calculate the number of credits to add
            num_pics = payment.amount // 99  # Replace <price_per_credit> with your actual price logic

            # If the subscription was created, set the initial credits
            if created:
                subscription.credits += num_pics  # Set credits for new subscription
            else:
                subscription.credits += num_pics  # Increment existing credits
            
            subscription.save()  # Save updated subscription

            return render(request, 'payment_success.html', {'subscription': subscription})

        except razorpay.errors.SignatureVerificationError:
            return render(request, 'payment_failed.html', {'message': 'Payment verification failed.'})
        except Payment.DoesNotExist:
            return render(request, 'payment_failed.html', {'message': 'Payment record not found.'})


def pricing_page(request):
    qs_subscription = SubscriptionPlan.objects.all()
    context = {
        'object_list': qs_subscription
    }

    return render(request, 'pricing.html', context=context)