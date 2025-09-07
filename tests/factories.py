# airbnb-clone-project/tests/factories.py

import datetime as dt
import random

import factory
from factory import Faker
from factory.django import DjangoModelFactory

from accounts.models import User
from amenities.models import Amenity
from bookings.models import Booking
from payments.models import Payment
from properties.models import Property
from reviews.models import Review


class UserFactory(DjangoModelFactory):
    """Factory for the custom User model (email as username)."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    user_type = factory.Iterator(["guest", "host"])  # rotate between roles
    # Generate Ghanaian-style phone numbers within 20 chars (e.g., +233XXXXXXXXX)
    phone_number = factory.LazyFunction(
        lambda: f"+233{random.randint(200000000, 599999999)}"
    )

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pwd = extracted or "pass1234"
        self.set_password(pwd)
        if create:
            self.save()


class AmenityFactory(DjangoModelFactory):
    class Meta:
        model = Amenity

    name = factory.Sequence(lambda n: f"Amenity {n}")
    description = Faker("sentence")


class PropertyFactory(DjangoModelFactory):
    class Meta:
        model = Property

    host = factory.SubFactory(UserFactory, user_type="host")
    title = factory.Sequence(lambda n: f"Stylish apartment #{n}")
    description = Faker("sentence")
    price_per_night = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, positive=True
    )
    bedrooms = factory.Iterator([1, 2, 3, 4])
    city = factory.Iterator(
        ["Accra", "Kumasi", "Takoradi", "Tamale"]
    )  # Ghanaian cities
    country = "Ghana"

    @factory.post_generation
    def amenities(self, create, extracted, **kwargs):
        if not create:
            return
        # If amenities provided, use them; else create a couple
        if extracted:
            for amenity in extracted:
                self.amenities.add(amenity)
        else:
            self.amenities.add(AmenityFactory(name="WiFi"))
            self.amenities.add(AmenityFactory(name="Parking"))


class BookingFactory(DjangoModelFactory):
    class Meta:
        model = Booking

    property = factory.SubFactory(PropertyFactory)
    guest = factory.SubFactory(UserFactory, user_type="guest")
    check_in_date = factory.LazyFunction(
        lambda: dt.date.today() + dt.timedelta(days=10)
    )
    check_out_date = factory.LazyAttribute(
        lambda o: o.check_in_date + dt.timedelta(days=3)
    )
    total_price = factory.Faker(
        "pydecimal", left_digits=4, right_digits=2, positive=True
    )
    status = factory.Iterator(["pending", "confirmed"])


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    booking = factory.SubFactory(BookingFactory)
    amount = factory.LazyAttribute(lambda o: o.booking.total_price)
    payment_method = factory.Iterator(["momo", "card"])  # include Mobile Money
    transaction_id = factory.Sequence(lambda n: f"MTN-{n:04d}")
    status = "succeeded"


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    booking = factory.SubFactory(BookingFactory)
    author = factory.LazyAttribute(lambda o: o.booking.guest)
    rating = factory.Iterator([3, 4, 5])
    comment = Faker("sentence")
