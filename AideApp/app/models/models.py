from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TaskRecord(db.Model):

    __tablename__ = 'task_record'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, nullable=False)  # ID của Celery Task redis server
    name = db.Column(db.String(255), nullable=False)  # Tên của task
    check_type = db.Column(db.String(50), nullable=False)  # Loại quét
    specific_file = db.Column(db.String(255), nullable=True)  # Đường dẫn file cụ thể
    custom_config = db.Column(db.String(255), nullable=True)  # Đường dẫn config tùy chỉnh
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Thời gian tạo
    progress = db.Column(db.Integer, nullable=True, default=0)  # Tiến độ quét
    status = db.Column(db.String(50), nullable=True)  # Trạng thái (Completed, Resumed, Paused)
    pid = db.Column(db.Integer, nullable=True) 


    # result = db.Column(db.Text, nullable=True)  # Kết quả quét

    results = db.relationship('ResultScan', backref='task_record', lazy=True, cascade="all, delete-orphan")
    
    @property
    def mapping_check_type(self):
        mapping = {
            "fullSystem" : "Full System",
            "specificFile" : "Specific File",
            "detailCheck": "Detail Check",
            "customConfig": "Custom Config",
            "customConfigAndFile": "Custom Config And File"

        }
        return mapping.get(self.check_type, self.check_type)

    def __repr__(self):
        return f'<TaskRecord {self.id}>'

class ResultScan(db.Model):
    __tablename__ = 'result_scan'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(50), db.ForeignKey('task_record.task_id'), nullable=False)
    total_entries = db.Column(db.Integer, nullable=True)
    added_entries = db.Column(db.Integer, nullable=True)
    removed_entries = db.Column(db.Integer, nullable=True)
    changed_entries = db.Column(db.Integer, nullable=True)
    added_files = db.Column(db.Integer, nullable=True)
    added_directories = db.Column(db.Text, nullable=True)
    removed_files = db.Column(db.Text, nullable=True)
    changed_files = db.Column(db.Text, nullable=True)
    algorithm = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.String(100), nullable=True )


    def __repr__(self):
        return f'<ResultScan {self.id}>'

