import os
import dotenv

from django.core.wsgi import get_wsgi_application
dotenv.load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barter_platform.settings')

application = get_wsgi_application()
