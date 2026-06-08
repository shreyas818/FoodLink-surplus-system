from django.apps import AppConfig


class FoodlinkappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodlinkApp'

    def ready(self):
        import os
        from django.db import connection
        
        # Ensure database tables exist before querying
        if 'foodlinkApp_customuser' in connection.introspection.table_names():
            from .models import CustomUser
            if not CustomUser.objects.filter(username='shreyas').exists():
                password = os.environ.get('SUPERUSER_PASSWORD', 'NewPassword123')
                CustomUser.objects.create_superuser(
                    username='shreyas',
                    email='admin@foodlink.org',
                    password=password
                )
