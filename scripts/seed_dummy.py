import os
import sys

import django

sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from domains.features.supplements.models import MFDSHealthFood


def seed():
    # Create or Get dummy product
    p, _created = MFDSHealthFood.objects.get_or_create(
        license_number="TEST-2026-001",
        defaults={
            "report_number": "2026002",
            "product_name": "Centrum Silver Men",
            "company_name": "Centrum",
            "raw_materials": "Calcium Carbonate (Calcium 300mg), Vitamin D3 (20mcg)",
            "functionality": "Vitamin D, Calcium",
            "intake_method": "1일 1정",
            "expiry_period": "2028-01-01",
            "appearance": "Tablet",
            "cautions": "None",
            "shape": "Tablet",
            "standard": "Standard",
            "product_form": "Tablet",
        },
    )
    print(f"Seeded Product ID: {p.id}")


if __name__ == "__main__":
    seed()
