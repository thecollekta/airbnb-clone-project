from __future__ import annotations

import random
import string
from datetime import date, timedelta
from typing import Iterable

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from accounts.models import User
from amenities.models import Amenity
from bookings.models import Booking
from payments.models import Payment
from properties.models import Property
from reviews.models import Review


class Command(BaseCommand):
    """Seed the database with Ghanaian-flavored demo data.

    This command populates:
    - amenities
    - users (hosts and guests)
    - properties
    - bookings
    - payments
    - reviews

    It is safe to run multiple times; it attempts to avoid duplicates where reasonable.
    Use --wipe to clear all related data before seeding.
    """

    help = "Seed the database with Ghanaian-flavored demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete existing data in related tables before seeding.",
        )
        parser.add_argument(
            "--amenities",
            type=int,
            default=15,
            help="Number of amenities to create (if > fixed list, random filler used).",
        )
        parser.add_argument(
            "--hosts", type=int, default=5, help="Number of host users to create."
        )
        parser.add_argument(
            "--guests", type=int, default=15, help="Number of guest users to create."
        )
        parser.add_argument(
            "--properties", type=int, default=20, help="Number of properties to create."
        )
        parser.add_argument(
            "--bookings", type=int, default=25, help="Number of bookings to create."
        )
        parser.add_argument(
            "--payments",
            action="store_true",
            help="Also create payments for confirmed bookings.",
        )
        parser.add_argument(
            "--reviews",
            action="store_true",
            help="Also create reviews for completed bookings.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Try Ghana locale, fallback to English if not available
        try:
            fake = Faker("en_GH")
            fake.localized_phone()  # Test if locale is available
        except (AttributeError, ImportError):
            self.stdout.write(
                self.style.WARNING(
                    "Ghana locale not found. Falling back to generic English.\n"
                    "Install Ghanaian locale with: pip install 'faker[ghana]'"
                )
            )
            fake = Faker("en_US")  # Fallback to US English

        random.seed(42)
        Faker.seed(42)

        if options["wipe"]:
            self._wipe()

        amenities = self._seed_amenities(options["amenities"])
        hosts = self._seed_users(role="host", count=options["hosts"], fake=fake)
        guests = self._seed_users(role="guest", count=options["guests"], fake=fake)
        properties = self._seed_properties(
            count=options["properties"], hosts=hosts, amenities=amenities, fake=fake
        )
        bookings = self._seed_bookings(
            count=options["bookings"], properties=properties, guests=guests, fake=fake
        )

        if options["payments"]:
            self._seed_payments(bookings)

        if options["reviews"]:
            self._seed_reviews(bookings, fake=fake)

        self.stdout.write(self.style.SUCCESS("Seeding complete."))

    # ---- helpers ----

    def _wipe(self):
        """Delete data in reverse dependency order to satisfy FK constraints."""
        self.stdout.write(
            "Wiping existing data (reviews, payments, bookings, properties, amenities, users[non-staff])..."
        )
        Review.objects.all().delete()
        Payment.objects.all().delete()
        Booking.objects.all().delete()
        # properties has M2M to amenities; clear through deletion
        Property.objects.all().delete()
        Amenity.objects.all().delete()
        # Keep superusers and staff accounts; wipe demo non-staff we likely created
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS("Wipe complete."))

    def _seed_amenities(self, target_count: int) -> list[Amenity]:
        """Create a set of common Ghanaian amenities.

        Returns the Amenity queryset list.
        """
        base = [
            ("24/7 Light (ECG)", "Reliable electricity supply"),
            ("Running Water", "Constant water supply"),
            ("Standby Generator", "Backup power for outages"),
            ("Air Conditioning", "Cooling for the Ghanaian heat"),
            ("Ceiling Fans", "Energy-efficient cooling"),
            ("Wi-Fi (Fibre)", "High-speed internet"),
            ("DSTV", "Satellite TV package"),
            ("Netflix", "Streaming entertainment"),
            ("Fully Fitted Kitchen", "With fridge, microwave, cooker"),
            ("Security (24/7)", "Gated community security"),
            ("CCTV", "Security cameras"),
            ("Parking", "On-premise parking space"),
            ("Swimming Pool", "Shared or private pool"),
            ("Gym", "Fitness centre"),
            ("Borehole", "Alternative water source"),
            ("Inverter System", "Solar/inverter backup"),
            ("Laundry", "Washer/Dryer available"),
            ("Housekeeping", "Cleaning services available"),
        ]

        created: list[Amenity] = []
        for name, desc in base[: max(0, min(target_count, len(base)))]:
            amenity, _ = Amenity.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            created.append(amenity)

        # If caller wants more than base, fill with generic names
        for i in range(len(created), target_count):
            filler_name = f"Amenity {i + 1}"
            amenity, _ = Amenity.objects.get_or_create(
                name=filler_name, defaults={"description": "Extra amenity"}
            )
            created.append(amenity)

        self.stdout.write(self.style.SUCCESS(f"Amenities ready: {len(created)}"))
        return created

    def _random_ghana_phone(self) -> str:
        prefix = random.choice(["024", "054", "055", "059", "020", "050", "027", "026"])
        rest = "".join(random.choices(string.digits, k=7))
        return f"+233{prefix[1:]}{rest}"

    def _seed_users(self, role: str, count: int, fake: Faker) -> list[User]:
        assert role in {"host", "guest"}
        users: list[User] = []
        default_password = "Password123!"  # Dev-only sample password

        for _ in range(count):
            first = fake.first_name()
            last = fake.last_name()
            email = f"{first}.{last}.{random.randint(100, 999)}@example.com".lower()

            # Generate a phone number based on available locale
            try:
                phone = fake.phone_number()
                if not phone.startswith("+"):
                    # Ensure international format
                    phone = (
                        f"+233{phone.lstrip('0')}"
                        if phone.startswith("0")
                        else f"+{phone}"
                    )
            except:
                # Fallback to random Ghanaian number
                prefix = random.choice(["24", "54", "55", "59", "20", "50", "27", "26"])
                phone = f"+233{prefix}{''.join(random.choices('0123456789', k=7))}"

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "user_type": role,
                    "phone_number": phone,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(default_password)
                user.save()
            users.append(user)

        self.stdout.write(
            self.style.SUCCESS(f"Users created for role={role}: {len(users)}")
        )
        return users

    def _seed_properties(
        self, count: int, hosts: Iterable[User], amenities: list[Amenity], fake: Faker
    ) -> list[Property]:
        cities = [
            "Accra",
            "Kumasi",
            "Takoradi",
            "Tamale",
            "Cape Coast",
            "Tema",
            "Koforidua",
            "Ho",
            "Sunyani",
            "Bolgatanga",
        ]
        props: list[Property] = []
        hosts = list(hosts) or [self._create_placeholder_host()]

        for _ in range(count):
            host = random.choice(hosts)
            title = f"{random.choice(['Chic', 'Cozy', 'Modern', 'Spacious', 'Serene'])} Apartment in {random.choice(cities)}"
            prop = Property.objects.create(
                host=host,
                title=title,
                description=fake.paragraph(nb_sentences=5),
                price_per_night=round(random.uniform(150, 1500), 2),
                bedrooms=random.randint(1, 5),
                city=random.choice(cities),
                country="Ghana",
            )
            # Add some random amenities
            if amenities:
                sample = random.sample(
                    amenities, k=random.randint(2, min(7, len(amenities)))
                )
                prop.amenities.add(*sample)
            props.append(prop)

        self.stdout.write(self.style.SUCCESS(f"Properties created: {len(props)}"))
        return props

    def _create_placeholder_host(self) -> User:
        user = User.objects.create_user(
            email="placeholder.host@example.com",
            password="Password123!",
            first_name="Kofi",
            last_name="Mensah",
            user_type="host",
            phone_number=self._random_ghana_phone(),
        )
        return user

    def _seed_bookings(
        self,
        count: int,
        properties: Iterable[Property],
        guests: Iterable[User],
        fake: Faker,
    ) -> list[Booking]:
        bookings: list[Booking] = []
        properties = list(properties)
        guests = [g for g in guests if g.user_type == "guest"]
        if not properties or not guests:
            self.stdout.write(
                self.style.WARNING("Skipping bookings: need properties and guests.")
            )
            return bookings

        today = date.today()
        for _ in range(count):
            prop = random.choice(properties)
            guest = random.choice(guests)

            # Randomly choose past or future stay
            is_past = random.random() < 0.6
            start_offset = random.randint(2, 60)
            length = random.randint(2, 10)
            if is_past:
                check_in = today - timedelta(days=start_offset)
            else:
                check_in = today + timedelta(days=start_offset)
            check_out = check_in + timedelta(days=length)

            total_price = prop.price_per_night * length

            status = random.choices(
                ["pending", "confirmed", "cancelled"], weights=[0.2, 0.7, 0.1]
            )[0]

            # Try a few times to avoid overlap (model clean() will enforce)
            for attempt in range(5):
                try:
                    booking = Booking(
                        property=prop,
                        guest=guest,
                        check_in_date=check_in,
                        check_out_date=check_out,
                        total_price=total_price,
                        status=status,
                    )
                    booking.full_clean()
                    booking.save()
                    bookings.append(booking)
                    break
                except Exception:
                    # Adjust dates slightly and retry
                    check_in = check_in + timedelta(days=random.randint(1, 5))
                    check_out = check_in + timedelta(days=length)

        self.stdout.write(self.style.SUCCESS(f"Bookings created: {len(bookings)}"))
        return bookings

    def _seed_payments(self, bookings: Iterable[Booking]):
        created = 0
        for b in bookings:
            if b.status != "confirmed":
                continue
            if hasattr(b, "payment"):
                continue
            txn = f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            Payment.objects.create(
                booking=b,
                amount=b.total_price,
                payment_method=random.choice(["momo", "card"]),
                transaction_id=txn,
                status=random.choice(["succeeded", "failed"]),
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Payments created: {created}"))

    def _seed_reviews(self, bookings: Iterable[Booking], fake: Faker):
        created = 0
        today = date.today()
        gh_phrases = [
            "Chale, place be nice paa!",
            "Cool breeze and serene environment.",
            "Very close to waakye joint, I loved it!",
            "Host was very responsive, medaase.",
            "Small small issues with water pressure, but overall fine.",
            "Top top place, will come again.",
            "Great location near the market.",
        ]
        for b in bookings:
            # Only for completed stays, ensure author is the guest
            if b.check_out_date >= today:
                continue
            if hasattr(b, "review"):
                continue
            rating = random.randint(3, 5)
            Review.objects.create(
                booking=b,
                author=b.guest,
                rating=rating,
                comment=random.choice(gh_phrases),
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Reviews created: {created}"))
