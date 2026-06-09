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
            
            env_password = os.environ.get('SUPERUSER_PASSWORD')
            if env_password:
                user, created = CustomUser.objects.get_or_create(
                    username='shreyas',
                    defaults={
                        'email': 'admin@foodlink.org',
                        'is_superuser': True,
                        'is_staff': True,
                        'role': 'ADMIN'
                    }
                )
                user.set_password(env_password)
                user.is_superuser = True
                user.is_staff = True
                user.role = 'ADMIN'
                user.save()
            elif not CustomUser.objects.filter(username='shreyas').exists():
                CustomUser.objects.create_superuser(
                    username='shreyas',
                    email='admin@foodlink.org',
                    password='NewPassword123'
                )
