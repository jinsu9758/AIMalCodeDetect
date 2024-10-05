from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import UserForm, CustomLoginForm, ChangePassword
# Create your views here.


@csrf_exempt
def sign_up(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            #messages.success(request, '회원가입이 성공적으로 완료되었습니다.')
            return redirect('/')
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' 필드가 email로 대체되었음
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
@csrf_exempt
def change_pw(request):
    if request.method == 'POST':
        form = ChangePassword(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('/changepw')
    else:
        form = ChangePassword(request.user)
    return render(request, 'changepw.html', {'form': form})