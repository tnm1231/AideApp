from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TaskRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, nullable=False)  # ID của Celery Task
    name = db.Column(db.String(255), nullable=False)  # Tên của task
    check_type = db.Column(db.String(50), nullable=False)  # Loại quét
    specific_file = db.Column(db.String(255), nullable=True)  # Đường dẫn file cụ thể
    custom_config = db.Column(db.String(255), nullable=True)  # Đường dẫn config tùy chỉnh
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Thời gian tạo
    progress = db.Column(db.Integer, nullable=True, default=0)  # Tiến độ quét
    status = db.Column(db.String(50), nullable=True)  # Trạng thái (STARTED, SUCCESS, FAILURE)
    # result = db.Column(db.Text, nullable=True)  # Kết quả quét

    def __repr__(self):
        return f'<TaskRecord {self.id}>'
