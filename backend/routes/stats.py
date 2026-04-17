"""
统计路由模块
处理所有统计相关的 API
"""

from flask import Blueprint, request, jsonify
from services.stats_service import StatsService
from utils import token_required

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    """获取首页统计数据（含趋势）"""
    result = StatsService.get_stats()
    return jsonify(result)

@stats_bp.route('/stats/kpi', methods=['GET'])
@token_required
def get_kpi_stats():
    """获取KPI统计数据"""
    range_type = request.args.get('range', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    result = StatsService.get_kpi_stats(range_type, start_date_str, end_date_str)
    return jsonify(result)

@stats_bp.route('/stats/trend', methods=['GET'])
@token_required
def get_trend_stats():
    """获取趋势统计数据"""
    range_type = request.args.get('range', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    result = StatsService.get_trend_stats(range_type, start_date_str, end_date_str)
    return jsonify(result)

@stats_bp.route('/stats/status', methods=['GET'])
@token_required
def get_status_stats():
    """获取状态分布统计"""
    result = StatsService.get_status_stats()
    return jsonify(result)

@stats_bp.route('/stats/industry', methods=['GET'])
@token_required
def get_industry_stats():
    """获取行业分布统计"""
    result = StatsService.get_industry_stats()
    return jsonify(result)

@stats_bp.route('/stats/sales-funnel', methods=['GET'])
@token_required
def get_sales_funnel():
    """获取销售漏斗分析数据"""
    range_type = request.args.get('range', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    result = StatsService.get_sales_funnel(range_type, start_date_str, end_date_str)
    return jsonify(result)

@stats_bp.route('/stats/customer-value', methods=['GET'])
@token_required
def get_customer_value_analysis():
    """获取客户价值分析数据（综合评分模型）"""
    range_type = request.args.get('range', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    result = StatsService.get_customer_value_analysis(range_type, start_date_str, end_date_str)
    return jsonify(result)

@stats_bp.route('/stats/sales-performance', methods=['GET'])
@token_required
def get_sales_performance():
    """获取销售人员业绩统计"""
    range_type = request.args.get('range', 'month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    result = StatsService.get_sales_performance(range_type, start_date_str, end_date_str)
    return jsonify(result)

@stats_bp.route('/stats/recent-customers', methods=['GET'])
@token_required
def get_recent_customers():
    """获取最近新增的客户"""
    limit = request.args.get('limit', 5, type=int)
    result = StatsService.get_recent_customers(limit)
    return jsonify(result)

@stats_bp.route('/stats/recent-follow-ups', methods=['GET'])
@token_required
def get_recent_follow_ups():
    """获取最近的跟进记录"""
    limit = request.args.get('limit', 5, type=int)
    result = StatsService.get_recent_follow_ups(limit)
    return jsonify(result)

@stats_bp.route('/stats/monthly-summary', methods=['GET'])
@token_required
def get_monthly_summary():
    """获取月度汇总数据"""
    result = StatsService.get_monthly_summary()
    return jsonify(result)
