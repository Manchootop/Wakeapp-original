from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from WakeApp.account.forms import CreateProfileForm, EditProfileForm
from WakeApp.account.models import WakeAppUser, Profile
from WakeApp.friend.friend_request_status import FriendRequestStatus
from WakeApp.friend.models import FriendList, FriendRequest
from WakeApp.friend.utils import get_friend_request_or_false

UserModel = get_user_model()


class UserRegistrationView(CreateView):
    # template_name = 'account/profile_registration.html'
    form_class = CreateProfileForm
    template_name = 'account/profile_register.html'

    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        request = self.request
        messages.success(request, 'Your profile is successfully created!')
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'account/login.html'
    success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return super().get_success_url()

    def form_valid(self, form):
        request = self.request
        messages.success(request, 'You have succesfully logged in!')
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    pass


def account_view(request, *args, **kwargs):
    context = {}

    user_id = kwargs.get('user_id')

    account = WakeAppUser.objects.get(pk=user_id)
    u = Profile.objects.get(pk=user_id)

    if account:
        context['id'] = account.pk
        context['username'] = account.username
        context['email'] = u.email
        # context['profile_picture'] = u.profile_image.url

    is_self = True
    is_friend = False
    user = request.user
    if user.is_authenticated and user != account:
        is_self = False
    elif not user.is_authenticated:
        is_self = False

    try:
        friend_list = FriendList.objects.get(user=account)
    except FriendList.DoesNotExist:
        friend_list = FriendList(user=account)
        friend_list.save()
    friends = friend_list.friends.all()
    context['friends'] = friends

    # Define template variables
    is_self = True
    is_friend = False
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value  # range: ENUM -> friend/friend_request_status.FriendRequestStatus
    friend_requests = None
    user = request.user
    if user.is_authenticated and user != account:
        is_self = False
        if friends.filter(pk=user.id):
            is_friend = True
        else:
            is_friend = False
            # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
            if get_friend_request_or_false(sender=account, receiver=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
            # CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
            elif get_friend_request_or_false(sender=user, receiver=account) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
            # CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

    elif not user.is_authenticated:
        is_self = False
    else:
        try:
            friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
        except:
            pass

    # Set the template variables to the values
    context['is_self'] = is_self
    context['is_friend'] = is_friend
    context['request_sent'] = request_sent
    context['friend_requests'] = friend_requests
    context['BASE_URL'] = settings.BASE_URL

    return render(request, 'account/account.html', context)


from django.shortcuts import render, redirect
from django.http import HttpResponse
# from django.contrib.auth import login, authenticate, logout
from django.conf import settings
#
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64

from django.core import files

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
            search_results = WakeAppUser.objects.filter(
                username__icontains=search_query)
            user = request.user
            accounts = []  # [(account1, True), (account2, False), ...]
            if user.is_authenticated:
                # get the authenticated users friend list
                auth_user_friend_list = FriendList.objects.get(user=user)
                for account in search_results:
                    accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
                context['accounts'] = accounts
            else:
                for account in search_results:
                    accounts.append((account, False))
                context['accounts'] = accounts

    return render(request, "account/search_results.html", context)


class EditProfileView(UpdateView):
    model = UserModel
    template_name = 'account/edit_account.html'
    form_class = EditProfileForm

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = EditProfileForm(instance=self.request.user)
        return context

DEBUG = True
# def edit_account_view(request, *args, **kwargs):
#     if not request.user.is_authenticated:
#         return redirect("login")
#     user_id = kwargs.get("user_id")
#     account = Profile.objects.get(pk=user_id)
#     if account.pk != request.user.pk:
#         return HttpResponse("You cannot edit someone else's profile.")
#     context = {}
#     if request.POST:
#         form = EditProfileForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect("account:view", user_id=account.pk)
#         else:
#             form = EditProfileForm(
#                 request.POST,
#                 instance=request.user,
#                 initial={
#                     'id': account.pk,
#                     'email': account.email,
#                     'username': account.user.username,
#                     'first_name': account.first_name,
#                     'last_name': account.last_name,
#                     'profile_image': account.profile_image,
#                     'description': account.description,
#                     'gender': account.gender,
#                 }
#             )
#             # initial={"id": account.pk,"email": account.email, "username": account.username, "profile_image": account.profile_image,}
#
#             context['form'] = form
#     else:
#         form = EditProfileForm(
#             initial={
#                 'id': account.pk,
#                 'email': account.email,
#                 'username': account.user.username,
#                 'first_name': account.first_name,
#                 'last_name': account.last_name,
#                 'profile_image': account.profile_image,
#                 'description': account.description,
#                 'gender': account.gender,
#             }
#         )
#         context['form'] = form
#     # context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
#     return render(request, "account/edit_account.html", context)
#
#
# DEBUG = True


def home_screen_view(request):
    context = {}
    context['debug_mode'] = settings.DEBUG
    context['debug'] = DEBUG
    return render(request, "chat/home.html", context)


def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" + str(user.pk), TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imageString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        print("exception: " + str(e))
        # workaround for an issue I found
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imageString += "=" * ((4 - len(imageString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imageString, user)
    return None


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user
    profile = Profile.objects.get(user.pk)

    if request.POST and user.is_authenticated:
        try:
            imageString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imageString, user)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))
            if cropX < 0:
                cropX = 0
            if cropY < 0:  # There is a bug with cropperjs. y can be negative.
                cropY = 0
            crop_img = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            cv2.imwrite(url, crop_img)

            # delete the old image
            profile.profile_image.delete()

            # Save the cropped image to user model
            profile.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            profile.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = profile.profile_image.url

            # delete temp file
            os.remove(url)

        except Exception as e:
            print("exception: " + str(e))
            payload['result'] = "error"
            payload['exception'] = str(e)
    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required(login_url=reverse_lazy('account:login'))
def edit_account_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")
    user = WakeAppUser.objects.get(pk=user_id)

    account = Profile.objects.get(pk=user_id)
    if user.pk != request.user.pk:
        return HttpResponse("You cannot edit someone elses profile.")
    context = {}
    if request.POST:
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:view", user_id=account.pk)
        else:
            form = EditProfileForm(request.POST, instance=request.user,
                                   initial={
                                       "id": account.pk,
                                       "email": account.email,
                                       "username": user.username,
                                       "profile_image": account.profile_image,
                                   }
                                   )
            context['form'] = form
    else:
        form = EditProfileForm(
            initial={
                "id": account.pk,
                "email": account.email,
                "username": user.username,
                "profile_image": account.profile_image,
            }
        )
        context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, "account/edit_account.html", context)
