"""Temporary stub views for missing HTMX endpoints"""
from django.http import HttpResponse

def dashboard_stats_cards(request):
    return HttpResponse("Not implemented", status=501)

def dashboard_metrics(request):
    return HttpResponse("Not implemented", status=501)

def dashboard_activity(request):
    return HttpResponse("Not implemented", status=501)

def dashboard_alerts(request):
    return HttpResponse("Not implemented", status=501)

def mana_stats_cards(request):
    return HttpResponse("Not implemented", status=501)

def recommendations_stats_cards(request):
    return HttpResponse("Not implemented", status=501)
