from django.apps import AppConfig


class WishlistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domains.features.wishlist"
    label = "wishlist"
    verbose_name = "❤️ Wishlist"
