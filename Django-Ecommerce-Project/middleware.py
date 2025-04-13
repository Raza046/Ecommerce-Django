import time
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import auth
from datetime import datetime
from django.utils import timezone
from django.conf import settings

class SimpleMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        now = timezone.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')

        # print(request.session.__dict__)
        if request.user.is_authenticated:
            expire_time = request.session.get('login_session', None)
            if expire_time:
                if now_str > expire_time[f"login_{request.user.id}"]:
                    auth.logout(request)
                    del request.session
                    return redirect("loginpage")

        request.Hello = "test requests"

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # print("Into Process Request")
        response = self.get_response(request)
        # print("Receiving Response")

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
    # def process_view(self, request):
    #     response['X-Custom-Header'] = 'Hello World'
    #     # print("RESPONSE EDITED")
    #     return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        ip = request.META.get('REMOTE_ADDR')
        # view_kwargs['new_args']= 'Keyword arguments testing'
        # This code is executed just before the view is called
        # if request.user.is_authenticated:
        #     return HttpResponse("Inside the process_request")
        # print("Into Process View")


    def process_exception(self, request, exception):
        # This code is executed if an exception is raised
        print("INTO PROCESS EXCEPTION")
        # pass
        # return HttpResponse(404)

    def process_template_response(self, request, response):
        print("Template response called")
        # response.context_data['custom_message'] = 'This is a custom message added by middleware!'
        return response
