"""
跟进记录路由模块
处理跟进记录的增删改查
"""

from flask import Blueprint, request, jsonify
from services.follow_up_service import FollowUpService
from utils import token_required

follow_ups_bp = Blueprint('follow_ups', __name__)

@follow_ups_bp.route('/follow-ups', methods=['GET'])
@token_required
def get_follow_ups():
    """获取跟进记录列表"""
    customer_id = request.args.get('customer_id', type=int)
    deal_id = request.args.get('deal_id', type=int)
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    result = FollowUpService.get_follow_ups(customer_id, deal_id, keyword, page, page_size)
    return jsonify(result)

@follow_ups_bp.route('/follow-ups', methods=['POST'])
@token_required
def add_follow_up():
    """添加跟进记录"""
    data = request.json
    # Pass data and user_id separately to match refined Service signature
    result, status = FollowUpService.add_follow_up(data, request.current_user.id)
    return jsonify(result), status

@follow_ups_bp.route('/follow-ups/<int:id>', methods=['PUT'])
@token_required
def update_follow_up(id):
    """更新跟进记录"""
    data = request.json
    result, status = FollowUpService.update_follow_up(id, data)
    return jsonify(result), status

@follow_ups_bp.route('/follow-ups/<int:id>', methods=['DELETE'])
@token_required
def delete_follow_up(id):
    """删除跟进记录"""
    result, status = FollowUpService.delete_follow_up(id)
    return jsonify(result), status
