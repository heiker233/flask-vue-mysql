"""
数据导入导出路由模块
处理数据的导入和导出功能
"""
from flask import Blueprint, request, jsonify, send_file
from extensions import db
from models import Customer, Deal, FollowUp, Product
from datetime import datetime
import io
import csv
import json

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

import_export_bp = Blueprint('import_export', __name__)


@import_export_bp.route('/export', methods=['POST'])
def export_data():
    """通用数据导出接口"""
    data = request.json
    
    data_type = data.get('data_type')
    export_format = data.get('format', 'csv')
    export_range = data.get('range', 'all')
    fields = data.get('fields', [])
    filters = data.get('filters', {})
    selected_ids = data.get('selected_ids', [])
    filename = data.get('filename', f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    encoding = data.get('encoding', 'utf-8')
    include_header = data.get('include_header', True)
    
    if not data_type:
        return jsonify({'error': '缺少数据类型参数'}), 400
    
    if not fields:
        return jsonify({'error': '缺少导出字段参数'}), 400
    
    try:
        # 根据数据类型查询数据
        query = None
        if data_type == 'customers':
            query = Customer.query
            # 应用筛选条件
            if filters.get('keyword'):
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    db.or_(
                        Customer.name.ilike(keyword),
                        Customer.phone.ilike(keyword),
                        Customer.company.ilike(keyword)
                    )
                )
        elif data_type == 'deals':
            query = Deal.query
        elif data_type == 'follow-ups':
            query = FollowUp.query
        elif data_type == 'products':
            query = Product.query
        else:
            return jsonify({'error': '不支持的数据类型'}), 400
        
        # 应用选中ID筛选
        if export_range == 'selected' and selected_ids:
            query = query.filter(getattr(query.column_descriptions[0]['type'], 'id').in_(selected_ids))
        
        # 获取数据
        records = query.all()
        
        # 生成数据
        export_data_list = []
        for record in records:
            row = {}
            for field in fields:
                value = getattr(record, field, '')
                if value is None:
                    value = ''
                elif hasattr(value, 'isoformat'):
                    value = value.isoformat()
                row[field] = value
            export_data_list.append(row)
        
        # 根据格式生成文件
        if export_format == 'csv':
            output = io.StringIO()
            if encoding == 'utf-8':
                output.write('\ufeff')  # UTF-8 BOM
            
            if export_data_list:
                headers = fields
                writer = csv.DictWriter(output, fieldnames=headers)
                if include_header:
                    writer.writeheader()
                writer.writerows(export_data_list)
            
            output.seek(0)
            
            if encoding == 'gbk':
                content = output.getvalue().encode('gbk', errors='ignore')
            else:
                content = output.getvalue().encode('utf-8')
            
            return send_file(
                io.BytesIO(content),
                mimetype='text/csv;charset=' + encoding,
                as_attachment=True,
                download_name=f'{filename}.csv'
            )
            
        elif export_format == 'excel':
            if not PANDAS_AVAILABLE:
                return jsonify({'error': 'Excel导出需要安装pandas和openpyxl'}), 500
            
            df = pd.DataFrame(export_data_list)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='数据')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{filename}.xlsx'
            )
                    
        elif export_format == 'json':
            output = io.BytesIO()
            json_content = json.dumps({
                'export_info': {
                    'data_type': data_type,
                    'export_time': datetime.now().isoformat(),
                    'record_count': len(export_data_list),
                    'fields': fields
                },
                'data': export_data_list
            }, ensure_ascii=False, indent=2)
            output.write(json_content.encode('utf-8'))
            output.seek(0)
            return send_file(
                output,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'{filename}.json'
            )
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
            
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


@import_export_bp.route('/import/customers', methods=['POST'])
def import_customers():
    """导入客户数据"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    try:
        # 根据文件类型读取数据
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'message': '不支持的文件格式'}), 400
        
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                customer = Customer(
                    name=str(row.get('name', '')),
                    phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                    email=str(row.get('email', '')) if pd.notna(row.get('email')) else None,
                    company=str(row.get('company', '')) if pd.notna(row.get('company')) else None,
                    industry=str(row.get('industry', '')) if pd.notna(row.get('industry')) else None,
                    status=str(row.get('status', 'potential')),
                    created_by=1
                )
                db.session.add(customer)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f'第{index + 2}行: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'导入完成：成功{success_count}条，失败{error_count}条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # 只返回前10个错误
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500


@import_export_bp.route('/import/deals', methods=['POST'])
def import_deals():
    """导入交易数据"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'success': False, 'message': '不支持的文件格式'}), 400
        
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                deal = Deal(
                    customer_id=int(row.get('customer_id', 0)),
                    amount=float(row.get('amount', 0)),
                    deal_status=str(row.get('deal_status', 'negotiating')),
                    product_name=str(row.get('product_name', '')) if pd.notna(row.get('product_name')) else None,
                    created_by=1
                )
                db.session.add(deal)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f'第{index + 2}行: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'导入完成：成功{success_count}条，失败{error_count}条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'}), 500
