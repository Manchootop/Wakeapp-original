from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from WakeApp.account.forms import CreateProfileForm, EditProfileForm
from WakeApp.account.models import WakeAppUser, Profile


class UserRegistrationView(CreateView):
    # template_name = 'account/profile_registration.html'
    form_class = CreateProfileForm
    template_name = 'account/profile_register.html'

    success_url = reverse_lazy('dashboard')


class UserLoginView(LoginView):
    template_name = 'account/login_page.html'
    success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return super().get_success_url()


def account_view(request, *args, **kwargs):
    context = {}
    user_id = kwargs.get('user_id')
    try:
        account = WakeAppUser.objects.get(pk=user_id)
        u = Profile.objects.get(pk=user_id)
    except WakeAppUser.DoesNotExist:
        return HttpResponse('Error')

    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = u.email
        # context['profile_picture'] = u.picture.url

    is_self = True
    is_friend = False
    user = request.user
    if user.is_authenticated and user != account:
        is_self = False
    elif not user.is_authenticated:
        is_self = False

    context['is_self'] = is_self
    context['is_friend'] = is_friend
    # context['BASE_URL'] = settings.BASE_URl

    return render(request, 'account/account.html', context)


from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from django.contrib.auth import login, authenticate, logout
# from django.conf import settings
#
# from django.core.files.storage import default_storage
# from django.core.files.storage import FileSystemStorage
# import os
# import cv2
# import json
# import base64
# import requests
# from django.core import files
#
# from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
# from account.models import Account
# from friend.utils import get_friend_request_or_false
# from friend.friend_request_status import FriendRequestStatus
# from friend.models import FriendList, FriendRequest
from WakeApp.account.models import Profile

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


# This is basically almost exactly the same as friends/friend_list_view
def account_search_view(request, *args, **kwargs):
    context = {}
    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            search_results = Profile.user.objects.filter(email__icontains=search_query).filter(
                username__icontains=search_query).distinct()
            # user = request.user
            accounts = []  # [(account1, True), (account2, False), ...]
            # if user.is_authenticated:
            #     get the authenticated users friend list
            #     auth_user_friend_list = FriendList.objects.get(user=user)
            for account in search_results:
                accounts.append((account, False))
            context['account'] = accounts
            # else:
            #     for account in search_results:
            #         account.append((account, False))
            #     context['account'] = account

        return render(request, "account/search_results.html", context)


def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    account = Profile.objects.get(pk=user_id)
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone else's profile.")
    context = {}
    if request.POST:
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:view", user_id=account.pk)
        else:
            form = EditProfileForm(
                request.POST,
                instance=request.user,
                initial={
                    'id': account.pk,
                    'email': account.email,
                    'username': account.user.username,
                    'first_name': account.first_name,
                    'last_name': account.last_name,
                    'profile_image': account.profile_image,
                    'description': account.description,
                    'gender': account.gender,
                }
            )
            # initial={"id": account.pk,"email": account.email, "username": account.username, "profile_image": account.profile_image,}

            context['form'] = form
    else:
        form = EditProfileForm(
            initial={
                'id': account.pk,
                'email': account.email,
                'username': account.user.username,
                'first_name': account.first_name,
                'last_name': account.last_name,
                'profile_image': account.profile_image,
                'description': account.description,
                'gender': account.gender,
            }
        )
        context['form'] = form
    # context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "account/edit_account.html", context)


DEBUG = True


def home_screen_view(request):
    context = {}
    context['debug_mode'] = settings.DEBUG
    context['debug'] = DEBUG
    context['room_id'] = "1"
    return render(request, "chat/home.html", context)
