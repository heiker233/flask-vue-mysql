from datetime import datetime

def parse_date(date_str):
    """通用的日期解析函数"""
    if not date_str:
        return None
    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%fZ']:
        try:
            # 处理 ISO 格式中的毫秒和 Z
            clean_date = date_str[:23] if '.' in date_str else date_str
            return datetime.strptime(clean_date, fmt)
        except ValueError:
            continue
    return None

def format_datetime(dt, date_format='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    return dt.strftime(date_format) if dt else None
