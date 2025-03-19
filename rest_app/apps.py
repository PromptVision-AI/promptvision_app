from django.apps import AppConfig


class RestAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rest_app"

    def ready(self):
        """
        Initialize services when the app is ready
        """
        # # Import and initialize Cloudinary
        # from rest_app.config.cloudinary_config import initialize_cloudinary
        # initialize_cloudinary()
