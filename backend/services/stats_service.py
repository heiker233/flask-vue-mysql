
from extensions import db
from models import Customer, Deal, FollowUp, User
from datetime import datetime, timedelta
from sqlalchemy import func
from date_utils import parse_date_start, parse_date_end_exclusive

def _get_date_range(range_type, start_date_str=None, end_date_str=None):
    now = datetime.utcnow()
    
    if range_type == 'custom':
        if start_date_str and end_date_str:
            start_date = parse_date_start(start_date_str)
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


def _get_date_bounds(range_type, start_date_str=None, end_date_str=None):
    if range_type == 'custom' and start_date_str and end_date_str:
        return parse_date_start(start_date_str), parse_date_end_exclusive(end_date_str)

    return _get_date_range(range_type, start_date_str, end_date_str), None

def calculate_growth(current, last):
    if last == 0:
        return 100 if current > 0 else 0
    return round(((current - last) / last) * 100, 2)

class StatsService:
    @staticmethod
    def get_stats():
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
        
        return {
            'total_customers': total_customers,
            'total_deals': total_deals,
            'total_amount': total_amount,
            'total_follow_ups': total_follow_ups,
            'customer_trend': calculate_growth(current_new_customers, prev_new_customers),
            'deal_trend': calculate_growth(current_new_deals, prev_new_deals),
            'amount_trend': calculate_growth(current_new_amount, prev_new_amount),
            'follow_up_trend': calculate_growth(current_new_follow_ups, prev_new_follow_ups)
        }

    @staticmethod
    def get_kpi_stats(range_type='month', start_date_str=None, end_date_str=None):
        now = datetime.utcnow()
        end_date = None
        prev_end_date = None
        
        if range_type == 'custom':
            if start_date_str and end_date_str:
                start_date = parse_date_start(start_date_str)
                end_date = parse_date_end_exclusive(end_date_str)
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

        current_customer_filters = [Customer.created_at >= start_date]
        current_deal_filters = [Deal.created_at >= start_date]
        current_follow_up_filters = [FollowUp.created_at >= start_date]
        if end_date is not None:
            current_customer_filters.append(Customer.created_at < end_date)
            current_deal_filters.append(Deal.created_at < end_date)
            current_follow_up_filters.append(FollowUp.created_at < end_date)

        prev_customer_filters = [
            Customer.created_at >= prev_start_date,
            Customer.created_at < (prev_end_date or start_date)
        ]
        prev_deal_filters = [
            Deal.created_at >= prev_start_date,
            Deal.created_at < (prev_end_date or start_date)
        ]
        prev_follow_up_filters = [
            FollowUp.created_at >= prev_start_date,
            FollowUp.created_at < (prev_end_date or start_date)
        ]

        current_customers = Customer.query.filter(*current_customer_filters).count()
        current_deals = Deal.query.filter(*current_deal_filters).count()
        current_amount = sum(deal.amount for deal in Deal.query.filter(
            *current_deal_filters,
            Deal.deal_status == 'closed'
        ).all())
        current_follow_ups = FollowUp.query.filter(*current_follow_up_filters).count()
        
        prev_customers = Customer.query.filter(*prev_customer_filters).count()
        prev_deals = Deal.query.filter(*prev_deal_filters).count()
        prev_amount = sum(deal.amount for deal in Deal.query.filter(
            *prev_deal_filters,
            Deal.deal_status == 'closed'
        ).all())
        prev_follow_ups = FollowUp.query.filter(*prev_follow_up_filters).count()
        
        total_deals_current = Deal.query.filter(*current_deal_filters).count()
        closed_deals_current = Deal.query.filter(
            *current_deal_filters,
            Deal.deal_status == 'closed'
        ).count()
        conversion_rate = round((closed_deals_current / total_deals_current * 100), 2) if total_deals_current > 0 else 0
        
        total_deals_prev = Deal.query.filter(*prev_deal_filters).count()
        closed_deals_prev = Deal.query.filter(
            *prev_deal_filters,
            Deal.deal_status == 'closed'
        ).count()
        prev_conversion_rate = round((closed_deals_prev / total_deals_prev * 100), 2) if total_deals_prev > 0 else 0
        
        return {
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
        }

    @staticmethod
    def get_trend_stats(range_type='month', start_date_str=None, end_date_str=None):
        now = datetime.utcnow()
        data = []
        
        if range_type == 'custom':
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
        
        return data

    @staticmethod
    def get_status_stats():
        potential = Customer.query.filter_by(status='potential').count()
        active = Customer.query.filter_by(status='active').count()
        lost = Customer.query.filter_by(status='lost').count()
        
        negotiating = Deal.query.filter_by(deal_status='negotiating').count()
        closed = Deal.query.filter_by(deal_status='closed').count()
        failed = Deal.query.filter_by(deal_status='failed').count()
        
        return {
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
        }

    @staticmethod
    def get_industry_stats():
        industry_stats = db.session.query(
            Customer.industry,
            func.count(Customer.id)
        ).filter(Customer.industry != None, Customer.industry != '').group_by(Customer.industry).all()
        
        result = {}
        for industry, count in industry_stats:
            result[industry] = count
        
        return result

    @staticmethod
    def get_sales_funnel(range_type='month', start_date_str=None, end_date_str=None):
        start_date, end_date = _get_date_bounds(range_type, start_date_str, end_date_str)

        customer_filters = [Customer.created_at >= start_date]
        deal_filters = [Deal.created_at >= start_date]
        if end_date is not None:
            customer_filters.append(Customer.created_at < end_date)
            deal_filters.append(Deal.created_at < end_date)

        total_customers = Customer.query.filter(*customer_filters).count()
        
        potential_customers = Customer.query.filter(
            *customer_filters,
            Customer.status == 'potential'
        ).count()
        
        customers_with_followup = db.session.query(Customer.id).join(
            FollowUp, Customer.id == FollowUp.customer_id
        ).filter(
            *customer_filters
        ).distinct().count()
        
        customers_with_deals = db.session.query(Customer.id).join(
            Deal, Customer.id == Deal.customer_id
        ).filter(
            *deal_filters,
            Deal.deal_status == 'closed'
        ).distinct().count()
        
        potential_to_intent = round((customers_with_followup / potential_customers * 100), 2) if potential_customers > 0 else 0
        intent_to_deal = round((customers_with_deals / customers_with_followup * 100), 2) if customers_with_followup > 0 else 0
        overall = round((customers_with_deals / potential_customers * 100), 2) if potential_customers > 0 else 0
        
        return {
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
        }

    @staticmethod
    def get_customer_value_analysis(range_type='month', start_date_str=None, end_date_str=None):
        start_date, end_date = _get_date_bounds(range_type, start_date_str, end_date_str)

        customer_filters = [Customer.created_at >= start_date]
        deal_filters = [Deal.created_at >= start_date]
        if end_date is not None:
            customer_filters.append(Customer.created_at < end_date)
            deal_filters.append(Deal.created_at < end_date)

        customers = Customer.query.filter(*customer_filters).all()
        
        customer_deal_stats = {}
        deal_stats = db.session.query(
            Deal.customer_id,
            func.sum(Deal.amount).label('total_amount'),
            func.count(Deal.id).label('deal_count')
        ).filter(
            *deal_filters
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
            
            score_rating = getattr(c, 'value_score', 3) if hasattr(c, 'value_score') and c.value_score else 3
            
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
        
        return {
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
        }

    @staticmethod
    def get_sales_performance(range_type='month', start_date_str=None, end_date_str=None):
        start_date, end_date = _get_date_bounds(range_type, start_date_str, end_date_str)

        deal_filters = [Deal.created_at >= start_date]
        if end_date is not None:
            deal_filters.append(Deal.created_at < end_date)
        
        user_all_deals = db.session.query(
            User.id,
            User.username,
            func.count(Deal.id).label('deal_count'),
            func.sum(Deal.amount).label('total_amount')
        ).join(
            Deal, User.id == Deal.created_by
        ).filter(
            *deal_filters
        ).group_by(User.id).all()
        
        user_closed_deals = db.session.query(
            User.id,
            func.count(Deal.id).label('closed_count'),
            func.sum(Deal.amount).label('closed_amount')
        ).join(
            Deal, User.id == Deal.created_by
        ).filter(
            *deal_filters,
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
            *deal_filters,
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
        
        return {
            'by_person': by_person,
            'by_industry': industry_list,
            'summary': {
                'total_sales': total_sales,
                'total_deals': sum(p['deal_count'] for p in by_person),
                'total_amount': total_closed_amount,
                'avg_per_person': avg_per_person
            },
            'ranking': ranking
        }

    @staticmethod
    def get_recent_customers(limit=5):
        recent_customers = Customer.query.order_by(
            Customer.created_at.desc()
        ).limit(limit).all()
        
        return [{
            'id': c.id,
            'name': c.name,
            'company': c.company,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in recent_customers]

    @staticmethod
    def get_recent_follow_ups(limit=5):
        recent_followups = FollowUp.query.order_by(
            FollowUp.created_at.desc()
        ).limit(limit).all()
        
        return [{
            'id': f.id,
            'customer_name': f.customer.name if f.customer else None,
            'content': f.content,
            'created_at': f.created_at.isoformat() if f.created_at else None
        } for f in recent_followups]

    @staticmethod
    def get_monthly_summary():
        now = datetime.utcnow()
        current_year = now.year
        current_month = now.month
        
        # 使用 SQLAlchemy func 聚合查询
        new_cust_map = dict(db.session.query(func.extract('month', Customer.created_at), func.count(Customer.id))
                         .filter(func.extract('year', Customer.created_at) == current_year).group_by(func.extract('month', Customer.created_at)).all())
        new_deal_map = dict(db.session.query(func.extract('month', Deal.created_at), func.count(Deal.id))
                         .filter(func.extract('year', Deal.created_at) == current_year).group_by(func.extract('month', Deal.created_at)).all())
        closed_deal_map = dict(db.session.query(func.extract('month', Deal.created_at), func.sum(Deal.amount))
                            .filter(func.extract('year', Deal.created_at) == current_year, Deal.deal_status == 'closed').group_by(func.extract('month', Deal.created_at)).all())
        closed_deal_count_map = dict(db.session.query(func.extract('month', Deal.created_at), func.count(Deal.id))
                            .filter(func.extract('year', Deal.created_at) == current_year, Deal.deal_status == 'closed').group_by(func.extract('month', Deal.created_at)).all())
        follow_up_map = dict(db.session.query(func.extract('month', FollowUp.created_at), func.count(FollowUp.id))
                          .filter(func.extract('year', FollowUp.created_at) == current_year).group_by(func.extract('month', FollowUp.created_at)).all())
        
        monthly_data = []
        for month in range(1, current_month + 1):
            month_str = f'{current_year}-{month:02d}'
            new_customers = new_cust_map.get(month, 0)
            new_deals = new_deal_map.get(month, 0)
            closed_amount = float(closed_deal_map.get(month, 0) or 0)
            month_closed_deals = closed_deal_count_map.get(month, 0)
            follow_ups = follow_up_map.get(month, 0)
            
            conversion_rate = round((month_closed_deals / new_customers * 100), 2) if new_customers > 0 else 0
            
            monthly_data.append({
                'month': month_str,
                'newCustomers': new_customers,
                'newDeals': new_deals,
                'closedAmount': closed_amount,
                'followUps': follow_ups,
                'conversionRate': conversion_rate
            })
        
        return monthly_data
