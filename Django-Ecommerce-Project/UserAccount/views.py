from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from Cart.models import Cart
from django.utils import timezone
from UserAccount.forms import LoginForm, RegistrationForm
from UserAccount.models import Users
# from django_ratelimit.decorators import ratelimit
from django.template.response import TemplateResponse
from django.views.generic import View, FormView


def UserAccount(request):

    user_acc = Users.objects.get(user=request.user)
    context = {"user":user_acc}
    return render(request,"user-acount.html",context)

class RegistrationView(FormView):

    template_name = "user-register.html"
    form_class = RegistrationForm
    success_url = "login"

    def form_valid(self, form):

        form_data = form.cleaned_data
        user_obj = User.objects.create_user(
            username=form_data['username'],email=form_data['email'],password=form_data['password']
            )
        registration_form = form.save(commit=False)
        registration_form.user = user_obj
        registration_form.save()
        return super().form_valid(form)

# @ratelimit(key='ip', rate='5/h', method=['GET'], block=False)
class LoginView(FormView):

    form_class = LoginForm
    template_name = "user-login.html"
    success_url = "home"

    def form_valid(self, form):
        form = form.cleaned_data
        user = authenticate(username = form['username'], password = form['password'])
        auth.login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        print("INVALID FORM")
        print(form.errors)
        return super().form_invalid(form)
        # expire_time = timezone.now() + timezone.timedelta(seconds=2005)
        # expire_time = expire_time.strftime('%Y-%m-%d %H:%M:%S')
        # # print(expire_time)
        # request.session['login_session'] = {f"login_{request.user.id}":expire_time}
        # request.session.save()

def Logout(request):

    auth.logout(request)
    return redirect("login")
