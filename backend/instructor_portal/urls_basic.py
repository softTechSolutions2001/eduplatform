# Very basic URLs for instructor_portal to allow Django to start
from django.urls import path
from django.http import JsonResponse

app_name = 'instructor_portal'

def basic_debug_view(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'instructor_portal basic endpoint',
        'app': 'instructor_portal'
    })

urlpatterns = [
    path('debug/', basic_debug_view, name='debug'),
]
