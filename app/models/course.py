from datetime import datetime, timezone
from app.extensions import db
from app.models.post import Post
from sqlalchemy.dialects.postgresql import JSONB

class Course(Post):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    
    # Relationships
    reviews = db.relationship('Review', backref='course', lazy='dynamic', 
                            cascade='all, delete-orphan')
    
    # Polymorphic identity
    __mapper_args__ = {
        'polymorphic_identity': 'course'
    }
    
    def to_dict(self, include_reviews=False):
        data = super().to_dict()
        data.update({
            "course_code": self.course_code,
            "department": self.department,
            "credits": self.credits
        })
        
        if include_reviews:
            data["reviews"] = [review.to_dict() for review in self.reviews]
            
        return data


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    difficulty = db.Column(db.Integer)  # 1-5 scale
    workload = db.Column(db.Integer)  # Hours per week
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), 
                         default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "difficulty": self.difficulty,
            "workload": self.workload,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
