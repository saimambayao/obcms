"""
Deprecation dashboard view for monitoring deprecated URL usage.

Provides insights into:
- Total deprecated requests
- Most accessed deprecated URLs
- User impact analysis
- Trend visualization
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings


@staff_member_required
def deprecation_dashboard(request):
    """
    Display deprecation monitoring dashboard.

    Parses deprecation.log file to generate statistics and visualizations.
    """
    # Path to deprecation log
    log_path = os.path.join(settings.BASE_DIR, 'logs', 'deprecation.log')

    # Initialize data structures
    total_requests = 0
    url_counter = Counter()
    user_requests = defaultdict(list)
    daily_requests = defaultdict(int)
    all_entries = []

    # Parse log file if it exists
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    if 'Deprecated URL accessed' in line:
                        total_requests += 1

                        # Parse log entry
                        entry = _parse_log_line(line)
                        if entry:
                            all_entries.append(entry)
                            url_counter[entry['url']] += 1
                            user_requests[entry['user']].append(entry)

                            # Daily stats
                            date_key = entry['timestamp'].date()
                            daily_requests[date_key] += 1
        except Exception as e:
            # Log parsing error (fail gracefully)
            pass

    # Calculate statistics
    unique_users = len([u for u in user_requests.keys() if u != 'Anonymous'])

    # Top deprecated URL
    top_url = None
    top_url_count = 0
    if url_counter:
        top_url, top_url_count = url_counter.most_common(1)[0]

    # Last 24 hours requests
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_24h_requests = sum(
        1 for entry in all_entries
        if entry['timestamp'] >= last_24h
    )

    # Top URLs with details
    top_urls = []
    for url, count in url_counter.most_common(10):
        url_entries = [e for e in all_entries if e['url'] == url]
        unique_users_for_url = len(set(e['user'] for e in url_entries))
        last_accessed = max(e['timestamp'] for e in url_entries)

        top_urls.append({
            'url': url,
            'count': count,
            'unique_users': unique_users_for_url,
            'last_accessed': last_accessed,
        })

    # Affected users analysis
    affected_users = []
    for user, entries in user_requests.items():
        if user != 'Anonymous':
            user_urls = [e['url'] for e in entries]
            url_counter_user = Counter(user_urls)

            affected_users.append({
                'username': user,
                'request_count': len(entries),
                'url_count': len(set(user_urls)),
                'top_url': url_counter_user.most_common(1)[0][0] if url_counter_user else 'N/A',
                'last_access': max(e['timestamp'] for e in entries),
            })

    # Sort by request count
    affected_users.sort(key=lambda x: x['request_count'], reverse=True)

    # Trend data (last 30 days)
    trend_labels, trend_data = _generate_trend_data(daily_requests)

    context = {
        'total_requests': total_requests,
        'unique_users': unique_users,
        'top_url': top_url,
        'top_url_count': top_url_count,
        'last_24h_requests': last_24h_requests,
        'top_urls': top_urls,
        'affected_users': affected_users[:20],  # Top 20 users
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
    }

    return render(request, 'admin/deprecation_dashboard.html', context)


def _parse_log_line(line):
    """
    Parse a deprecation log line into structured data.

    Example line:
    2025-10-05 15:30:00 | WARNING | Deprecated URL accessed | Path: /staff/tasks/ | User: admin (ID: 1) | ...
    """
    try:
        parts = line.split('|')

        # Extract timestamp
        timestamp_str = parts[0].strip()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        timestamp = timezone.make_aware(timestamp)

        # Extract URL
        url = None
        for part in parts:
            if 'Path:' in part:
                url = part.split('Path:')[1].strip()
                break

        # Extract user
        user = 'Anonymous'
        for part in parts:
            if 'User:' in part:
                user_info = part.split('User:')[1].strip()
                # Extract just the username
                if '(ID:' in user_info:
                    user = user_info.split('(ID:')[0].strip()
                else:
                    user = user_info
                break

        if url:
            return {
                'timestamp': timestamp,
                'url': url,
                'user': user,
            }
    except Exception:
        pass

    return None


def _generate_trend_data(daily_requests):
    """
    Generate trend chart data for the last 30 days.

    Returns:
        Tuple of (labels, data) where labels are dates and data are request counts
    """
    if not daily_requests:
        return [], []

    # Get date range (last 30 days)
    today = timezone.now().date()
    date_range = [today - timedelta(days=i) for i in range(29, -1, -1)]

    labels = [date.strftime('%b %d') for date in date_range]
    data = [daily_requests.get(date, 0) for date in date_range]

    return labels, data
