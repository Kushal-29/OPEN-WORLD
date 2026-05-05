from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

ALLOWED_CHAT_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx'}

def allowed_chat_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CHAT_EXTENSIONS

@api_bp.route('/upload-chat-file', methods=['POST'])
@login_required
def upload_chat_file():
    """Upload image or document to chat"""
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_chat_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Create upload folder if it doesn't exist
        os.makedirs('static/uploads/chat', exist_ok=True)
        
        # Generate secure filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}.{ext}")
        filepath = os.path.join('static/uploads/chat', filename)
        
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/static/uploads/chat/{filename}'
        })
    
    except Exception as e:
        print(f"upload_chat_file error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_info(user_id):
    """Get user info via API"""
    try:
        from models.models import User
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'profile_pic': user.profile_pic,
            'is_friend': current_user.is_friend_with(user)
        })
    except Exception as e:
        print(f"get_user_info error: {e}")
        return jsonify({'error': 'Failed to get user info'}), 500

@api_bp.route('/friends-count', methods=['GET'])
@login_required
def get_friends_count():
    """Get count of friends"""
    try:
        count = current_user.friends.count()
        return jsonify({'count': count})
    except Exception as e:
        print(f"get_friends_count error: {e}")
        return jsonify({'error': 'Failed to get friends count'}), 500

@api_bp.route('/delete-chat/<int:friend_id>', methods=['DELETE'])
@login_required
def delete_chat(friend_id):
    """Delete all messages between current user and friend"""
    try:
        from models.models import db, Message
        from sqlalchemy import or_
        
        Message.query.filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.receiver_id == friend_id),
                (Message.sender_id == friend_id) & (Message.receiver_id == current_user.id)
            )
        ).delete()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Chat deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"delete_chat error: {e}")
        return jsonify({'error': 'Failed to delete chat'}), 500

@api_bp.route('/delete-friend/<int:friend_id>', methods=['DELETE'])
@login_required
def delete_friend(friend_id):
    """Remove friend association"""
    try:
        from models.models import db, User
        
        friend = User.query.get(friend_id)
        if not friend:
            return jsonify({'error': 'User not found'}), 404
            
        current_user.remove_friend(friend)
        
        # Also delete chat when deleting friend? WhatsApp doesn't necessarily do this,
        # but often users expect it. For now, just remove friendship.
        
        return jsonify({'success': True, 'message': 'Friend removed successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"delete_friend error: {e}")
        return jsonify({'error': 'Failed to delete friend'}), 500