from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError
import time
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os


@api_view(['GET'])
def db_status(request):
    """Simple view to check database connectivity"""
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row[0] == 1:
                return JsonResponse({"status": "ok", "message": "Database connection successful"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Database connection failed"}, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def db_stats(request):
    """View to get basic database statistics"""
    try:
        stats = {}
        with connections['default'].cursor() as cursor:
            # Get total tables
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            stats['total_tables'] = cursor.fetchone()[0]

        return JsonResponse({"status": "ok", "stats": stats})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def test_static(request):
    """Simple view to test static files"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Static Files Test</title>
        <link rel="stylesheet" type="text/css" href="/static/test/test.css">
    </head>
    <body>
        <h1>Testing Static Files</h1>
        <p>If this page has a red background, static files are working.</p>
    </body>
    </html>
    """)


def test_admin_static(request):
    """Simple view to test admin static files"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Static Files Test</title>
        <link rel="stylesheet" type="text/css" href="/static/admin/css/base.css">
    </head>
    <body>
        <h1>Testing Admin Static Files</h1>
        <p>If this page has admin styling, admin static files are working.</p>
    </body>
    </html>
    """)
