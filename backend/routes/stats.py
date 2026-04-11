"""
统计路由模块
处理所有统计相关的 API
"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Customer, Deal, FollowUp, User
from datetime import datetime, timedelta
from sqlalchemy import func

stats_bp = Blueprint('stats', __name__)


def _get_date_range(range_type):
    """根据范围类型获取起止日期"""
    now = datetime.utcnow()
    
    if range_type == 'custom':
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            return start_date
        return now - timedelta(days=30)
    elif range_type == 'month':
        return now - timedelta(days=30)
    elif range_type == 'quarter':
        return now - timedelta(days=90)
    elif range_type == 'year':
        return now - timedelta(days=365)
    else:
        return datetime(2000, 1, 1)


@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取首页统计数据（含趋势）"""
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    
    total_customers = Customer.query.count()
    total_deals = Deal.query.count()
    total_amount = sum(deal.amount for deal in Deal.query.filter_by(deal_status='closed').all())
    total_follow_ups = FollowUp.query.count()
    
    current_new_customers = Customer.query.filter(Customer.created_at >= thirty_days_ago).count()
    prev_new_customers = Customer.query.filter(
        Customer.created_at >= sixty_days_ago,
        Customer.created_at < thirty_days_ago
    ).count()
    
    current_new_deals = Deal.query.filter(Deal.created_at >= thirty_days_ago).count()
    prev_new_deals = Deal.query.filter(
        Deal.created_at >= sixty_days_ago,
        Deal.created_at < thirty_days_ago
    ).count()
    
    current_new_amount = sum(deal.amount for deal in Deal.query.filter(
        Deal.created_at >= thirty_days_ago,
        Deal.deal_status == 'closed'
    ).all())
    prev_new_amount = sum(deal.amount for deal in Deal.query.filter(
        Deal.created_at >= sixty_days_ago,
        Deal.created_at < thirty_days_ago,
        Deal.deal_status == 'closed'
    ).all())
    
    current_new_follow_ups = FollowUp.query.filter(FollowUp.created_at >= thirty_days_ago).count()
    prev_new_follow_ups = FollowUp.query.filter(
        FollowUp.created_at >= sixty_days_ago,
        FollowUp.created_at < thirty_days_ago
    ).count()
    
    def calculate_growth(current, last):
        if last == 0:
            return 100 if current > 0 else 0
        return round(((current - last) / last) * 100, 2)
    
    return jsonify({
        'total_customers': total_customers,
        'total_deals': total_deals,
        'total_amount': total_amount,
        'total_follow_ups': total_follow_ups,
        'customer_trend': calculate_growth(current_new_customers, prev_new_customers),
        'deal_trend': calculate_growth(current_new_deals, prev_new_deals),
        'amount_trend': calculate_growth(current_new_amount, prev_new_amount),
        'follow_up_trend': calculate_growth(current_new_follow_ups, prev_new_follow_ups)
    })


@stats_bp.route('/stats/kpi', methods=['GET'])
def get_kpi_stats():
    """获取KPI统计数据"""
    range_type = request.args.get('range', 'month')
    
    now = datetime.utcnow()
    
    if range_type == 'custom':
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            days_diff = (end_date - start_date).days
            prev_end_date = start_date
            prev_start_date = prev_end_date - timedelta(days=days_diff)
        else:
            start_date = now - timedelta(days=30)
            prev_start_date = now - timedelta(days=60)
    elif range_type == 'month':
        start_date = now - timedelta(days=30)
        prev_start_date = now - timedelta(days=60)
    elif range_type == 'quarter':
        start_date = now - timedelta(days=90)
        prev_start_date = now - timedelta(days=180)
    elif range_type == 'year':
        start_date = now - timedelta(days=365)
        prev_start_date = now - timedelta(days=730)
    else:  # all
        start_date = datetime(2000, 1, 1)
        prev_start_date = datetime(2000, 1, 1)
    
    current_customers = Customer.query.filter(Customer.created_at >= start_date).count()
    current_deals = Deal.query.filter(Deal.created_at >= start_date).count()
    current_amount = sum(deal.amount for deal in Deal.query.filter(
        Deal.created_at >= start_date,
        Deal.deal_status == 'closed'
    ).all())
    current_follow_ups = FollowUp.query.filter(FollowUp.created_at >= start_date).count()
    
    prev_customers = Customer.query.filter(
        Customer.created_at >= prev_start_date,
        Customer.created_at < start_date
    ).count()
    prev_deals = Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date
    ).count()
    prev_amount = sum(deal.amount for deal in Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date,
        Deal.deal_status == 'closed'
    ).all())
    prev_follow_ups = FollowUp.query.filter(
        FollowUp.created_at >= prev_start_date,
        FollowUp.created_at < start_date
    ).count()
    
    total_deals_current = Deal.query.filter(Deal.created_at >= start_date).count()
    closed_deals_current = Deal.query.filter(
        Deal.created_at >= start_date,
        Deal.deal_status == 'closed'
    ).count()
    conversion_rate = round((closed_deals_current / total_deals_current * 100), 2) if total_deals_current > 0 else 0
    
    total_deals_prev = Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date
    ).count()
    closed_deals_prev = Deal.query.filter(
        Deal.created_at >= prev_start_date,
        Deal.created_at < start_date,
        Deal.deal_status == 'closed'
    ).count()
    prev_conversion_rate = round((closed_deals_prev / total_deals_prev * 100), 2) if total_deals_prev > 0 else 0
    
    def calculate_growth(current, last):
        if last == 0:
            return 100 if current > 0 else 0
        return round(((current - last) / last) * 100, 2)
    
    return jsonify({
        'customers': current_customers,
        'deals': current_deals,
        'amount': current_amount,
        'follow_ups': current_follow_ups,
        'conversionRate': conversion_rate,
        'customerTrend': calculate_growth(current_customers, prev_customers),
        'dealTrend': calculate_growth(current_deals, prev_deals),
        'amountTrend': calculate_growth(current_amount, prev_amount),
        'followUpTrend': calculate_growth(current_follow_ups, prev_follow_ups),
        'conversionTrend': calculate_growth(conversion_rate, prev_conversion_rate)
    })


@stats_bp.route('/stats/trend', methods=['GET'])
def get_trend_stats():
    """获取趋势统计数据"""
    range_type = request.args.get('range', 'month')
    
    now = datetime.utcnow()
    data = []
    
    if range_type == 'custom':
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            days_diff = (end_date - start_date).days
            
            if days_diff <= 31:
                current_date = start_date
                while current_date <= end_date:
                    next_date = current_date + timedelta(days=1)
                    
                    new_customers = Customer.query.filter(
                        Customer.created_at >= current_date,
                        Customer.created_at < next_date
                    ).count()
                    
                    new_deals = Deal.query.filter(
                        Deal.created_at >= current_date,
                        Deal.created_at < next_date
                    ).count()
                    
                    closed_amount = sum(deal.amount for deal in Deal.query.filter(
                        Deal.created_at >= current_date,
                        Deal.created_at < next_date,
                        Deal.deal_status == 'closed'
                    ).all())
                    
                    follow_ups = FollowUp.query.filter(
                        FollowUp.created_at >= current_date,
                        FollowUp.created_at < next_date
                    ).count()
                    
                    conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
                    
                    data.append({
                        'period': current_date.strftime('%m-%d'),
                        'newCustomers': new_customers,
                        'newDeals': new_deals,
                        'closedAmount': closed_amount,
                        'followUps': follow_ups,
                        'conversionRate': conversion_rate
                    })
                    
                    current_date = next_date
            else:
                current_date = start_date
                while current_date <= end_date:
                    month_end = min(
                        datetime(current_date.year, current_date.month, 1) + timedelta(days=32),
                        end_date + timedelta(days=1)
                    )
                    month_end = month_end.replace(day=1) - timedelta(days=1) + timedelta(days=1)
                    if month_end > end_date + timedelta(days=1):
                        month_end = end_date + timedelta(days=1)
                    
                    new_customers = Customer.query.filter(
                        Customer.created_at >= current_date,
                        Customer.created_at < month_end
                    ).count()
                    
                    new_deals = Deal.query.filter(
                        Deal.created_at >= current_date,
                        Deal.created_at < month_end
                    ).count()
                    
                    closed_amount = sum(deal.amount for deal in Deal.query.filter(
                        Deal.created_at >= current_date,
                        Deal.created_at < month_end,
                        Deal.deal_status == 'closed'
                    ).all())
                    
                    follow_ups = FollowUp.query.filter(
                        FollowUp.created_at >= current_date,
                        FollowUp.created_at < month_end
                    ).count()
                    
                    conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
                    
                    data.append({
                        'period': current_date.strftime('%Y-%m'),
                        'newCustomers': new_customers,
                        'newDeals': new_deals,
                        'closedAmount': closed_amount,
                        'followUps': follow_ups,
                        'conversionRate': conversion_rate
                    })
                    
                    next_month = current_date.replace(day=1) + timedelta(days=32)
                    current_date = next_month.replace(day=1)
        else:
            range_type = 'month'
    
    if range_type in ('month', 'all'):
        current_year = now.year
        current_month = now.month
        
        from calendar import monthrange
        _, last_day = monthrange(current_year, current_month)
        
        for day in range(1, last_day + 1):
            date = datetime(current_year, current_month, day)
            next_date = date + timedelta(days=1)
            
            if date > now:
                data.append({
                    'period': f'{current_month:02d}-{day:02d}',
                    'newCustomers': 0,
                    'newDeals': 0,
                    'closedAmount': 0,
                    'followUps': 0,
                    'conversionRate': 0
                })
                continue
            
            new_customers = Customer.query.filter(
                Customer.created_at >= date,
                Customer.created_at < next_date
            ).count()
            
            new_deals = Deal.query.filter(
                Deal.created_at >= date,
                Deal.created_at < next_date
            ).count()
            
            closed_amount = sum(deal.amount for deal in Deal.query.filter(
                Deal.created_at >= date,
                Deal.created_at < next_date,
                Deal.deal_status == 'closed'
            ).all())
            
            follow_ups = FollowUp.query.filter(
                FollowUp.created_at >= date,
                FollowUp.created_at < next_date
            ).count()
            
            conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
            
            data.append({
                'period': f'{current_month:02d}-{day:02d}',
                'newCustomers': new_customers,
                'newDeals': new_deals,
                'closedAmount': closed_amount,
                'followUps': follow_ups,
                'conversionRate': conversion_rate
            })
    
    elif range_type in ('year', 'quarter'):
        current_year = now.year
        current_month = now.month
        
        if range_type == 'quarter':
            start_month = max(1, current_month - 2)
        else:
            start_month = 1
        
        for month in range(start_month, current_month + 1):
            new_customers = Customer.query.filter(
                db.extract('year', Customer.created_at) == current_year,
                db.extract('month', Customer.created_at) == month
            ).count()
            
            new_deals = Deal.query.filter(
                db.extract('year', Deal.created_at) == current_year,
                db.extract('month', Deal.created_at) == month
            ).count()
            
            closed_amount = sum(deal.amount for deal in Deal.query.filter(
                db.extract('year', Deal.created_at) == current_year,
                db.extract('month', Deal.created_at) == month,
                Deal.deal_status == 'closed'
            ).all())
            
            follow_ups = FollowUp.query.filter(
                db.extract('year', FollowUp.created_at) == current_year,
                db.extract('month', FollowUp.created_at) == month
            ).count()
            
            conversion_rate = round((new_deals / new_customers * 100), 2) if new_customers > 0 else 0
            
            data.append({
                'period': f'{current_year}-{month:02d}',
                'newCustomers': new_customers,
                'newDeals': new_deals,
                'closedAmount': closed_amount,
                'followUps': follow_ups,
                'conversionRate': conversion_rate
            })
    
    return jsonify(data)


@stats_bp.route('/stats/status', methods=['GET'])
def get_status_stats():
    """获取状态分布统计"""
    potential = Customer.query.filter_by(status='potential').count()
    active = Customer.query.filter_by(status='active').count()
    lost = Customer.query.filter_by(status='lost').count()
    
    negotiating = Deal.query.filter_by(deal_status='negotiating').count()
    closed = Deal.query.filter_by(deal_status='closed').count()
    failed = Deal.query.filter_by(deal_status='failed').count()
    
    return jsonify({
        'customers': {
            'potential': potential,
            'active': active,
            'lost': lost
        },
        'deals': {
            'negotiating': negotiating,
            'closed': closed,
            'failed': failed
        }
    })


@stats_bp.route('/stats/industry', methods=['GET'])
def get_industry_stats():
    """获取行业分布统计"""
    industry_stats = db.session.query(
        Customer.industry,
        func.count(Customer.id)
    ).filter(Customer.industry != None, Customer.industry != '').group_by(Customer.industry).all()
    
    result = {}
    for industry, count in industry_stats:
        result[industry] = count
    
    return jsonify(result)


@stats_bp.route('/stats/sales-funnel', methods=['GET'])
def get_sales_funnel():
    """获取销售漏斗分析数据"""
    range_type = request.args.get('range', 'month')
    start_date = _get_date_range(range_type)
    
    total_customers = Customer.query.filter(Customer.created_at >= start_date).count()
    
    potential_customers = Customer.query.filter(
        Customer.created_at >= start_date,
        Customer.status == 'potential'
    ).count()
    
    customers_with_followup = db.session.query(Customer.id).join(
        FollowUp, Customer.id == FollowUp.customer_id
    ).filter(
        Customer.created_at >= start_date
    ).distinct().count()
    
    customers_with_deals = db.session.query(Customer.id).join(
        Deal, Customer.id == Deal.customer_id
    ).filter(
        Deal.created_at >= start_date,
        Deal.deal_status == 'closed'
    ).distinct().count()
    
    potential_to_intent = round((customers_with_followup / potential_customers * 100), 2) if potential_customers > 0 else 0
    intent_to_deal = round((customers_with_deals / customers_with_followup * 100), 2) if customers_with_followup > 0 else 0
    overall = round((customers_with_deals / potential_customers * 100), 2) if potential_customers > 0 else 0
    
    return jsonify({
        'stages': [
            {
                'name': '潜在客户',
                'count': potential_customers,
                'conversion_rate': 100.0
            },
            {
                'name': '意向客户',
                'count': customers_with_followup,
                'conversion_rate': potential_to_intent
            },
            {
                'name': '成交客户',
                'count': customers_with_deals,
                'conversion_rate': intent_to_deal
            }
        ],
        'summary': {
            'total_conversion_rate': overall,
            'closed_customers': customers_with_deals,
            'potential_customers': potential_customers,
            'intent_customers': customers_with_followup
        }
    })


@stats_bp.route('/stats/customer-value', methods=['GET'])
def get_customer_value_analysis():
    """获取客户价值分析数据（综合评分模型）"""
    range_type = request.args.get('range', 'month')
    start_date = _get_date_range(range_type)
    
    customers = Customer.query.filter(Customer.created_at >= start_date).all()
    
    customer_deal_stats = {}
    deal_stats = db.session.query(
        Deal.customer_id,
        func.sum(Deal.amount).label('total_amount'),
        func.count(Deal.id).label('deal_count')
    ).filter(
        Deal.created_at >= start_date
    ).group_by(Deal.customer_id).all()
    
    for customer_id, total_amount, deal_count in deal_stats:
        customer_deal_stats[customer_id] = {
            'total_amount': float(total_amount) if total_amount else 0,
            'deal_count': deal_count
        }
    
    high_customers = []
    medium_customers = []
    low_customers = []
    
    for c in customers:
        stats = customer_deal_stats.get(c.id, {'total_amount': 0, 'deal_count': 0})
        total_amount = stats['total_amount']
        deal_count = stats['deal_count']
        
        score_rating = c.value_score if c.value_score else 3
        
        amount_score = 0
        if total_amount > 100000:
            amount_score = 100
        elif total_amount > 50000:
            amount_score = 70
        elif total_amount > 10000:
            amount_score = 40
        elif total_amount > 0:
            amount_score = 20
        
        rating_score = (score_rating / 5) * 100
        
        composite_score = round(amount_score * 0.4 + rating_score * 0.6, 2)
        
        avg_amount = (total_amount / deal_count) if deal_count > 0 else 0
        
        customer_data = {
            'id': c.id,
            'name': c.name,
            'company': c.company,
            'value_score': score_rating,
            'total_amount': total_amount,
            'deal_count': deal_count,
            'avg_amount': float(avg_amount),
            'composite_score': composite_score,
            'amount_score': amount_score,
            'rating_score': rating_score
        }
        
        if composite_score >= 60:
            high_customers.append(customer_data)
        elif composite_score >= 30:
            medium_customers.append(customer_data)
        else:
            low_customers.append(customer_data)
    
    high_customers.sort(key=lambda x: x['composite_score'], reverse=True)
    medium_customers.sort(key=lambda x: x['composite_score'], reverse=True)
    low_customers.sort(key=lambda x: x['composite_score'], reverse=True)
    
    high_total_amount = sum(c['total_amount'] for c in high_customers)
    medium_total_amount = sum(c['total_amount'] for c in medium_customers)
    low_total_amount = sum(c['total_amount'] for c in low_customers)
    
    return jsonify({
        'distribution': {
            'high': {
                'count': len(high_customers),
                'total_amount': float(high_total_amount),
                'customers': high_customers[:10]
            },
            'medium': {
                'count': len(medium_customers),
                'total_amount': float(medium_total_amount),
                'customers': medium_customers[:5]
            },
            'low': {
                'count': len(low_customers),
                'total_amount': float(low_total_amount)
            }
        },
        'thresholds': {
            'high': 60,
            'medium': 30,
            'low': 0,
            'description': '综合评分 = 交易金额分(40%) + 价值评分(60%)'
        }
    })


@stats_bp.route('/stats/sales-performance', methods=['GET'])
def get_sales_performance():
    """获取销售人员业绩统计"""
    range_type = request.args.get('range', 'month')
    start_date = _get_date_range(range_type)
    
    user_all_deals = db.session.query(
        User.id,
        User.username,
        func.count(Deal.id).label('deal_count'),
        func.sum(Deal.amount).label('total_amount')
    ).join(
        Deal, User.id == Deal.created_by
    ).filter(
        Deal.created_at >= start_date
    ).group_by(User.id).all()
    
    user_closed_deals = db.session.query(
        User.id,
        func.count(Deal.id).label('closed_count'),
        func.sum(Deal.amount).label('closed_amount')
    ).join(
        Deal, User.id == Deal.created_by
    ).filter(
        Deal.created_at >= start_date,
        Deal.deal_status == 'closed'
    ).group_by(User.id).all()
    
    closed_map = {}
    for uid, closed_count, closed_amt in user_closed_deals:
        closed_map[uid] = {
            'closed_count': closed_count,
            'closed_amount': float(closed_amt) if closed_amt else 0
        }
    
    by_person = []
    for uid, username, deal_count, total_amount in user_all_deals:
        closed_info = closed_map.get(uid, {'closed_count': 0, 'closed_amount': 0})
        conversion_rate = round((closed_info['closed_count'] / deal_count * 100), 2) if deal_count > 0 else 0
        by_person.append({
            'id': uid,
            'name': username,
            'deal_count': deal_count,
            'total_amount': float(total_amount) if total_amount else 0,
            'closed_amount': closed_info['closed_amount'],
            'conversion_rate': conversion_rate
        })
    
    by_person.sort(key=lambda x: x['closed_amount'], reverse=True)
    
    total_sales = len(by_person)
    total_closed_amount = sum(p['closed_amount'] for p in by_person)
    avg_per_person = round(total_closed_amount / total_sales, 2) if total_sales > 0 else 0
    
    by_industry = db.session.query(
        Customer.industry,
        func.count(Deal.id).label('deal_count'),
        func.sum(Deal.amount).label('total_amount')
    ).join(
        Customer, Deal.customer_id == Customer.id
    ).filter(
        Deal.created_at >= start_date,
        Customer.industry != None,
        Customer.industry != ''
    ).group_by(Customer.industry).all()
    
    industry_list = []
    for industry, deal_count, total_amount in by_industry:
        industry_list.append({
            'industry': industry,
            'deal_count': deal_count,
            'total_amount': float(total_amount) if total_amount else 0
        })
    industry_list.sort(key=lambda x: x['total_amount'], reverse=True)
    
    ranking = {
        'champion': by_person[0] if len(by_person) > 0 else None,
        'runner_up': by_person[1] if len(by_person) > 1 else None,
        'third_place': by_person[2] if len(by_person) > 2 else None
    }
    
    return jsonify({
        'by_person': by_person,
        'by_industry': industry_list,
        'summary': {
            'total_sales': total_sales,
            'total_deals': sum(p['deal_count'] for p in by_person),
            'total_amount': total_closed_amount,
            'avg_per_person': avg_per_person
        },
        'ranking': ranking
    })


@stats_bp.route('/stats/recent-customers', methods=['GET'])
def get_recent_customers():
    """获取最近新增的客户"""
    limit = request.args.get('limit', 5, type=int)
    
    recent_customers = Customer.query.order_by(
        Customer.created_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'company': c.company,
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in recent_customers])


@stats_bp.route('/stats/recent-follow-ups', methods=['GET'])
def get_recent_follow_ups():
    """获取最近的跟进记录"""
    limit = request.args.get('limit', 5, type=int)
    
    recent_followups = FollowUp.query.order_by(
        FollowUp.created_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        'id': f.id,
        'customer_name': f.customer.name if f.customer else None,
        'content': f.content,
        'created_at': f.created_at.isoformat() if f.created_at else None
    } for f in recent_followups])


@stats_bp.route('/stats/monthly-summary', methods=['GET'])
def get_monthly_summary():
    """获取月度汇总数据"""
    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month
    monthly_data = []
    
    for month in range(1, current_month + 1):
        month_str = f'{current_year}-{month:02d}'
        
        new_customers = Customer.query.filter(
            db.extract('year', Customer.created_at) == current_year,
            db.extract('month', Customer.created_at) == month
        ).count()
        
        new_deals = Deal.query.filter(
            db.extract('year', Deal.created_at) == current_year,
            db.extract('month', Deal.created_at) == month
        ).count()
        
        month_deals = Deal.query.filter(
            db.extract('year', Deal.created_at) == current_year,
            db.extract('month', Deal.created_at) == month,
            Deal.deal_status == 'closed'
        ).all()
        
        closed_amount = sum(deal.amount for deal in month_deals)
        
        follow_ups = FollowUp.query.filter(
            db.extract('year', FollowUp.created_at) == current_year,
            db.extract('month', FollowUp.created_at) == month
        ).count()
        
        conversion_rate = round((len(month_deals) / new_customers * 100), 2) if new_customers > 0 else 0
        
        monthly_data.append({
            'month': month_str,
            'newCustomers': new_customers,
            'newDeals': new_deals,
            'closedAmount': closed_amount,
            'followUps': follow_ups,
            'conversionRate': conversion_rate
        })
    
    return jsonify(monthly_data)
