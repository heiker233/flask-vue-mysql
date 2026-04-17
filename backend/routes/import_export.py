"""
数据导入导出路由模块
处理数据的导入和导出功能
"""

from flask import Blueprint, request, jsonify, send_file
from services.import_export_service import ImportExportService
from utils import token_required

import_export_bp = Blueprint('import_export', __name__)

@import_export_bp.route('/export', methods=['POST'])
@token_required
def export_data():
    """通用数据导出接口"""
    data = request.json
    result, status, file_info = ImportExportService.export_data(data)
    
    if file_info:
        return send_file(
            file_info['content'],
            mimetype=file_info['mimetype'],
            as_attachment=True,
            download_name=file_info['download_name']
        )
    return jsonify(result), status

@import_export_bp.route('/import/customers', methods=['POST'])
@token_required
def import_customers():
    """导入客户数据"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    result, status = ImportExportService.import_customers(file, request.current_user.id)
    return jsonify(result), status

@import_export_bp.route('/import/deals', methods=['POST'])
@token_required
def import_deals():
    """导入交易数据"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    result, status = ImportExportService.import_deals(file, request.current_user.id)
    return jsonify(result), status
