from flask import Flask
from app.routes import routes_blueprint  # Import directly from the file
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
    
    # Cấu hình Celery
    app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379/0',  # Thay bằng cấu hình của bạn
        CELERY_RESULT_BACKEND='redis://localhost:6379/0',  # Thay bằng cấu hình của bạn
        CELERY_ACCEPT_CONTENT=['json'],  # Content types for task communication
        CELERY_TASK_SERIALIZER='json',  # How tasks are serialized
        CELERY_RESULT_SERIALIZER='json',  # How task results are serialized
        CELERY_TIMEZONE='UTC',    # Set the timezone for Celery
        task_track_started=True,
        CELERYD_PREFETCH_MULTIPLIER=1
    )
    
    # Khởi tạo Celery
    celery = make_celery(app)

    # Đăng ký Blueprint
    app.register_blueprint(routes_blueprint)

    return app, celery  