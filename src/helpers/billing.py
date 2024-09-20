import stripe
from decouple import config

DEBUG=config("DEBUG", default=False, cast=bool)
STRIPE_SECRET_KEY=config("STRIPE_SECRET_KEY", default="", cast=str)

if "sk_test" in STRIPE_SECRET_KEY and not DEBUG:
    raise ValueError("Invalid stripe key")

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(name="", metadata={}, email="", raw=False):
    resposnse = stripe.Customer.create(name=name, metadata=metadata, email=email)
    if raw:
        return resposnse
    stripe_id = resposnse.id
    return stripe_id


def create_product(name="", metadata={}, raw=False):
    resposnse = stripe.Product.create(name=name, metadata=metadata)
    if raw:
        return resposnse
    stripe_id = resposnse.id
    return stripe_id

def create_price(currency="usd", unit_amount="9999", interval="month", product=None, metadata={}, raw=False):
    if product is None:
        return None
    response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        recurring={"interval": interval},
        product=product,
        metadata=metadata
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id