#para ejecutar en el azure en el despliegue
pip install -r requirements.txt
python manage.py migrate
gunicorn  config.wsgi