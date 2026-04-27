import csv
import io
import json
import os
from datetime import date, datetime

from extensions import db
from date_utils import parse_date_end_exclusive, parse_date_start
from models import Customer, Deal, FollowUp, Product
from openpyxl import Workbook

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False


class ImportExportService:
    PREVIEW_LIMIT = 5
    SUPPORTED_IMPORT_EXTENSIONS = {'.csv', '.xlsx'}
    CUSTOMER_STATUS_VALUES = {'potential', 'active', 'lost'}
    DEAL_STATUS_VALUES = {'negotiating', 'closed', 'cancelled'}
    PAYMENT_STATUS_VALUES = {'unpaid', 'partial', 'paid'}

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
                if filters.get('keyword'):
                    keyword = f"%{filters['keyword']}%"
                    query = query.join(Customer).outerjoin(Product, Deal.product_id == Product.id).filter(
                        db.or_(
                            Customer.name.ilike(keyword),
                            Customer.company.ilike(keyword),
                            Deal.product_name.ilike(keyword),
                            Product.name.ilike(keyword)
                        )
                    )
                if filters.get('status'):
                    query = query.filter(Deal.deal_status == filters['status'])
                if filters.get('start_date'):
                    try:
                        query = query.filter(Deal.created_at >= parse_date_start(filters['start_date']))
                    except ValueError:
                        pass
                if filters.get('end_date'):
                    try:
                        query = query.filter(Deal.created_at < parse_date_end_exclusive(filters['end_date']))
                    except ValueError:
                        pass
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
                    writer = csv.DictWriter(output, fieldnames=fields)
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

            if export_format == 'excel':
                if not PANDAS_AVAILABLE:
                    return {'error': 'Excel导出需要安装 pandas 和 openpyxl'}, 500, None

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

            if export_format == 'json':
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

            return {'error': '不支持的导出格式'}, 400, None
        except Exception as exc:
            return {'error': f'导出失败: {str(exc)}'}, 500, None

    @staticmethod
    def preview_import(file):
        try:
            df = ImportExportService._load_dataframe(file)
        except ValueError as exc:
            return {'success': False, 'message': str(exc)}, 400
        except Exception as exc:
            return {'success': False, 'message': f'解析预览失败: {str(exc)}'}, 500

        if df.empty:
            return {'success': False, 'message': '导入文件为空'}, 400

        return {
            'success': True,
            'columns': list(df.columns),
            'preview_data': ImportExportService._dataframe_preview(df),
            'total_rows': int(len(df.index))
        }, 200

    @staticmethod
    def download_template(template_type):
        if template_type == 'customers':
            headers = ['name', 'phone', 'email', 'company', 'industry', 'status']
            sample_row = ['张三', '13800000000', 'zhangsan@example.com', '示例科技', 'IT', 'potential']
            download_name = 'customer_import_template.xlsx'
        elif template_type == 'deals':
            headers = ['customer_id', 'amount', 'product_name', 'deal_status', 'expected_close_date']
            sample_row = [1, 5000, 'CRM系统', 'negotiating', '2026-05-01']
            download_name = 'deal_import_template.xlsx'
        else:
            return {'success': False, 'message': '不支持的模板类型'}, 400, None

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'template'
        worksheet.append(headers)
        worksheet.append(sample_row)

        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        return None, 200, {
            'content': output,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'download_name': download_name
        }

    @staticmethod
    def import_customers(file, current_user_id=1):
        try:
            df = ImportExportService._load_dataframe(file)
        except ValueError as exc:
            return {'success': False, 'message': str(exc)}, 400
        except Exception as exc:
            return {'success': False, 'message': f'导入失败: {str(exc)}'}, 500

        if df.empty:
            return {'success': False, 'message': '导入文件为空'}, 400

        rows = df.to_dict(orient='records')
        existing_keys = ImportExportService._existing_customer_keys(rows)
        file_keys = set()
        success_count = 0
        errors = []

        for index, row in enumerate(rows, start=2):
            customer, error = ImportExportService._build_customer(row, index, current_user_id, existing_keys, file_keys)
            if error:
                errors.append(error)
                continue

            try:
                with db.session.begin_nested():
                    db.session.add(customer)
                    db.session.flush()
                success_count += 1
            except Exception as exc:
                errors.append(f'第{index}行: {str(exc)}')

        return ImportExportService._finalize_import_result(success_count, errors)

    @staticmethod
    def import_deals(file, current_user_id=1):
        try:
            df = ImportExportService._load_dataframe(file)
        except ValueError as exc:
            return {'success': False, 'message': str(exc)}, 400
        except Exception as exc:
            return {'success': False, 'message': f'导入失败: {str(exc)}'}, 500

        if df.empty:
            return {'success': False, 'message': '导入文件为空'}, 400

        rows = df.to_dict(orient='records')
        existing_customer_ids = ImportExportService._existing_customer_ids(rows)
        success_count = 0
        errors = []

        for index, row in enumerate(rows, start=2):
            deal, error = ImportExportService._build_deal(row, index, current_user_id, existing_customer_ids)
            if error:
                errors.append(error)
                continue

            try:
                with db.session.begin_nested():
                    db.session.add(deal)
                    db.session.flush()
                success_count += 1
            except Exception as exc:
                errors.append(f'第{index}行: {str(exc)}')

        return ImportExportService._finalize_import_result(success_count, errors)

    @staticmethod
    def _finalize_import_result(success_count, errors):
        error_count = len(errors)

        try:
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            return {'success': False, 'message': f'导入失败: {str(exc)}'}, 500

        success = success_count > 0
        status = 200 if success else 400
        return {
            'success': success,
            'message': f'导入完成：成功{success_count}条，失败{error_count}条',
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]
        }, status

    @staticmethod
    def _load_dataframe(file):
        if not PANDAS_AVAILABLE:
            raise ValueError('当前环境未安装 pandas，无法处理导入文件')

        ext = ImportExportService._get_extension(file.filename)
        if ext not in ImportExportService.SUPPORTED_IMPORT_EXTENSIONS:
            raise ValueError('仅支持 .xlsx 和 .csv 格式文件')

        raw_bytes = file.read()
        file.seek(0)
        if not raw_bytes:
            raise ValueError('导入文件为空')

        if ext == '.csv':
            last_error = None
            for encoding in ('utf-8-sig', 'utf-8', 'gbk'):
                try:
                    df = pd.read_csv(io.BytesIO(raw_bytes), encoding=encoding)
                    break
                except UnicodeDecodeError as exc:
                    last_error = exc
            else:
                raise ValueError(f'CSV 文件编码无法识别: {str(last_error)}')
        else:
            df = pd.read_excel(io.BytesIO(raw_bytes), engine='openpyxl')

        df.columns = [str(column).strip() for column in df.columns]
        return df

    @staticmethod
    def _dataframe_preview(df):
        preview_rows = []
        preview_df = df.head(ImportExportService.PREVIEW_LIMIT)
        for _, row in preview_df.iterrows():
            item = {}
            for column, value in row.items():
                item[column] = ImportExportService._serialize_preview_value(value)
            preview_rows.append(item)
        return preview_rows

    @staticmethod
    def _serialize_preview_value(value):
        if value is None or (PANDAS_AVAILABLE and pd.isna(value)):
            return ''
        if isinstance(value, datetime):
            return value.isoformat(sep=' ')
        if isinstance(value, date):
            return value.isoformat()
        if hasattr(value, 'isoformat'):
            try:
                return value.isoformat()
            except TypeError:
                pass
        return value

    @staticmethod
    def _build_customer(row, index, current_user_id, existing_keys, file_keys):
        name = ImportExportService._clean_string(row.get('name'))
        if not name:
            return None, f'第{index}行: name 为必填项'

        phone = ImportExportService._clean_string(row.get('phone'))
        email = ImportExportService._clean_string(row.get('email'))
        company = ImportExportService._clean_string(row.get('company'))
        industry = ImportExportService._clean_string(row.get('industry'))
        status = (ImportExportService._clean_string(row.get('status')) or 'potential').lower()

        if status not in ImportExportService.CUSTOMER_STATUS_VALUES:
            return None, f'第{index}行: status 仅支持 potential、active、lost'

        duplicate_key = None
        if phone:
            duplicate_key = (name.lower(), phone)
            if duplicate_key in existing_keys or duplicate_key in file_keys:
                return None, f'第{index}行: 客户姓名和电话重复'

        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            company=company,
            industry=industry,
            status=status,
            created_by=current_user_id
        )

        if duplicate_key:
            file_keys.add(duplicate_key)

        return customer, None

    @staticmethod
    def _build_deal(row, index, current_user_id, existing_customer_ids):
        customer_id, error = ImportExportService._parse_int_value(row.get('customer_id'), 'customer_id', required=True)
        if error:
            return None, f'第{index}行: {error}'
        if customer_id not in existing_customer_ids:
            return None, f'第{index}行: customer_id 对应的客户不存在'

        amount, error = ImportExportService._parse_float_value(row.get('amount'), 'amount', required=True)
        if error:
            return None, f'第{index}行: {error}'

        quantity, error = ImportExportService._parse_int_value(row.get('quantity'), 'quantity', default=1)
        if error:
            return None, f'第{index}行: {error}'

        unit_price, error = ImportExportService._parse_float_value(row.get('unit_price'), 'unit_price', default=0)
        if error:
            return None, f'第{index}行: {error}'

        paid_amount, error = ImportExportService._parse_float_value(row.get('paid_amount'), 'paid_amount', default=0)
        if error:
            return None, f'第{index}行: {error}'

        deal_status = (ImportExportService._clean_string(row.get('deal_status')) or 'negotiating').lower()
        if deal_status not in ImportExportService.DEAL_STATUS_VALUES:
            return None, f'第{index}行: deal_status 仅支持 negotiating、closed、cancelled'

        payment_status = (ImportExportService._clean_string(row.get('payment_status')) or 'unpaid').lower()
        if payment_status not in ImportExportService.PAYMENT_STATUS_VALUES:
            return None, f'第{index}行: payment_status 仅支持 unpaid、partial、paid'

        expected_close_date, error = ImportExportService._parse_date_value(row.get('expected_close_date'), 'expected_close_date')
        if error:
            return None, f'第{index}行: {error}'

        product_name = ImportExportService._clean_string(row.get('product_name')) or ImportExportService._clean_string(row.get('product'))
        notes = ImportExportService._clean_string(row.get('notes'))

        deal = Deal(
            customer_id=customer_id,
            amount=amount,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            deal_status=deal_status,
            payment_status=payment_status,
            paid_amount=paid_amount,
            expected_close_date=expected_close_date,
            notes=notes,
            created_by=current_user_id
        )
        return deal, None

    @staticmethod
    def _existing_customer_keys(rows):
        phones = []
        for row in rows:
            phone = ImportExportService._clean_string(row.get('phone'))
            if phone:
                phones.append(phone)

        if not phones:
            return set()

        existing_customers = Customer.query.filter(Customer.phone.in_(set(phones))).all()
        return {
            (customer.name.strip().lower(), customer.phone.strip())
            for customer in existing_customers
            if customer.name and customer.phone
        }

    @staticmethod
    def _existing_customer_ids(rows):
        customer_ids = []
        for row in rows:
            customer_id, error = ImportExportService._parse_int_value(row.get('customer_id'), 'customer_id')
            if customer_id is not None and not error:
                customer_ids.append(customer_id)

        if not customer_ids:
            return set()

        return {
            customer.id
            for customer in Customer.query.filter(Customer.id.in_(set(customer_ids))).all()
        }

    @staticmethod
    def _parse_int_value(raw_value, field_name, required=False, default=None):
        if ImportExportService._is_empty_value(raw_value):
            if required:
                return None, f'{field_name} 为必填项'
            return default, None

        if isinstance(raw_value, int):
            return raw_value, None

        if isinstance(raw_value, float):
            if raw_value.is_integer():
                return int(raw_value), None
            return None, f'{field_name} 必须为整数'

        text = str(raw_value).strip()
        try:
            if '.' in text:
                number = float(text)
                if not number.is_integer():
                    return None, f'{field_name} 必须为整数'
                return int(number), None
            return int(text), None
        except ValueError:
            return None, f'{field_name} 格式不正确'

    @staticmethod
    def _parse_float_value(raw_value, field_name, required=False, default=None):
        if ImportExportService._is_empty_value(raw_value):
            if required:
                return None, f'{field_name} 为必填项'
            return default, None

        try:
            return float(str(raw_value).strip()), None
        except ValueError:
            return None, f'{field_name} 必须为数字'

    @staticmethod
    def _parse_date_value(raw_value, field_name):
        if ImportExportService._is_empty_value(raw_value):
            return None, None

        if isinstance(raw_value, datetime):
            return raw_value.date(), None
        if isinstance(raw_value, date):
            return raw_value, None

        text = str(raw_value).strip()
        try:
            return datetime.strptime(text, '%Y-%m-%d').date(), None
        except ValueError:
            return None, f'{field_name} 日期格式应为 YYYY-MM-DD'

    @staticmethod
    def _clean_string(value):
        if ImportExportService._is_empty_value(value):
            return None
        return str(value).strip()

    @staticmethod
    def _is_empty_value(value):
        if value is None:
            return True
        if PANDAS_AVAILABLE and pd.isna(value):
            return True
        return str(value).strip() == ''

    @staticmethod
    def _get_extension(filename):
        return os.path.splitext((filename or '').lower())[1]
