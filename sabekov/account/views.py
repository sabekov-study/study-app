from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect


@login_required
def my_account(request):
    return render(request, 'registration/my_account.html', {
        'active_nav': 'account'
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, _('Your password was changed successfully.'))
            return redirect('my_account')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'active_nav': 'account',
        'form': form
    })
