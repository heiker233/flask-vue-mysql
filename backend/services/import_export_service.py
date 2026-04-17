
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

class ImportExportService:
    @staticmethod
    def export_data(data):
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
            return {'error': '缺少数据类型参数'}, 400, None
        
        if not fields:
            return {'error': '缺少导出字段参数'}, 400, None
        
        try:
            query = None
            if data_type == 'customers':
                query = Customer.query
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
                return {'error': '不支持的数据类型'}, 400, None
            
            if export_range == 'selected' and selected_ids:
                query = query.filter(getattr(query.column_descriptions[0]['type'], 'id').in_(selected_ids))
            
            records = query.all()
            
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
            
            if export_format == 'csv':
                output = io.StringIO()
                if encoding == 'utf-8':
                    output.write('\ufeff')
                
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
                
                return None, 200, {
                    'content': io.BytesIO(content),
                    'mimetype': 'text/csv;charset=' + encoding,
                    'download_name': f'{filename}.csv'
                }
                
            elif export_format == 'excel':
                if not PANDAS_AVAILABLE:
                    return {'error': 'Excel导出需要安装pandas和openpyxl'}, 500, None
                
                df = pd.DataFrame(export_data_list)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='数据')
                output.seek(0)
                return None, 200, {
                    'content': output,
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'download_name': f'{filename}.xlsx'
                }
                        
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
                return None, 200, {
                    'content': output,
                    'mimetype': 'application/json',
                    'download_name': f'{filename}.json'
                }
            else:
                return {'error': '不支持的导出格式'}, 400, None
                
        except Exception as e:
            return {'error': f'导出失败: {str(e)}'}, 500, None

    @staticmethod
    def import_customers(file, current_user_id=1):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return {'success': False, 'message': '不支持的文件格式'}, 400
            
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
                        created_by=current_user_id
                    )
                    db.session.add(customer)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f'第{index + 2}行: {str(e)}')
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'导入完成：成功{success_count}条，失败{error_count}条',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'导入失败: {str(e)}'}, 500

    @staticmethod
    def import_deals(file, current_user_id=1):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return {'success': False, 'message': '不支持的文件格式'}, 400
            
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
                        created_by=current_user_id
                    )
                    db.session.add(deal)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f'第{index + 2}行: {str(e)}')
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'导入完成：成功{success_count}条，失败{error_count}条',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'导入失败: {str(e)}'}, 500
