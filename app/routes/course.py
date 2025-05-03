from flask import Blueprint, request, jsonify
from app.models.course import Course, Review
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone

bp = Blueprint('course', __name__, url_prefix='/courses')

@bp.route('', methods=['GET'])
def get_courses():
    """Get list of courses with optional filtering"""
    department = request.args.get('department')
    search = request.args.get('search')
    
    query = Course.query
    
    if department:
        query = query.filter_by(department=department)
        
    if search:
        query = query.filter(
            Course.title.ilike(f'%{search}%') | 
            Course.course_code.ilike(f'%{search}%')
        )
    
    courses = query.all()
    return jsonify([course.to_dict() for course in courses]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_course():
    """Create a new course"""
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['title', 'course_code', 'department', 'credits']):
        return jsonify({"error": "Missing required fields"}), 400
        
    # Create course
    course = Course(
        title=data['title'],
        content=data.get('content', ''),
        course_code=data['course_code'],
        department=data['department'],
        credits=data['credits'],
        user_id=get_jwt_identity()
    )
    
    db.session.add(course)
    db.session.commit()
    
    return jsonify(course.to_dict()), 201

@bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get a single course with reviews"""
    course = Course.query.get_or_404(course_id)
    return jsonify(course.to_dict(include_reviews=True)), 200

@bp.route('/<int:course_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(course_id):
    """Create a review for a course"""
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['rating', 'content']):
        return jsonify({"error": "Missing required fields"}), 400
        
    # Create review
    review = Review(
        course_id=course_id,
        user_id=get_jwt_identity(),
        rating=data['rating'],
        difficulty=data.get('difficulty'),
        workload=data.get('workload'),
        content=data['content']
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify(review.to_dict()), 201

@bp.route('/<int:course_id>/reviews', methods=['GET'])
def get_reviews(course_id):
    """Get reviews for a course"""
    course = Course.query.get_or_404(course_id)
    reviews = course.reviews.order_by(Review.created_at.desc()).all()
    return jsonify([review.to_dict() for review in reviews]), 200

@bp.route('/<int:course_id>/tags', methods=['GET'])
def get_course_tags(course_id):
    """Get tags for a course"""
    course = Course.query.get_or_404(course_id)
    return jsonify([tag.to_dict() for tag in course.tags]), 200

@bp.route('/<int:course_id>/tags', methods=['POST'])
@jwt_required()
def add_course_tags(course_id):
    """Add tags to a course"""
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    if not data.get('tag_ids'):
        return jsonify({"error": "tag_ids is required"}), 400
        
    # Verify current user owns the course
    if course.user_id != get_jwt_identity():
        return jsonify({"error": "Unauthorized"}), 403
        
    # Add tags logic here (similar to post tags)
    # ...
    
    return jsonify([tag.to_dict() for tag in course.tags]), 200
