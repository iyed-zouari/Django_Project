from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .forms import DeleteAccountForm, ProfileForm


@login_required
@never_cache
@require_http_methods(['GET', 'HEAD', 'POST'])
def profile(request):
    form = ProfileForm(request.POST if request.method == 'POST' else None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        if form.has_changed():
            form.instance.save(update_fields=[*form.changed_data, 'updated_at'])
            messages.success(request, 'Votre profil a été mis à jour.')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@never_cache
@require_http_methods(['GET', 'HEAD', 'POST'])
def delete_account(request):
    user = request.user
    form = DeleteAccountForm(request.POST if request.method == 'POST' else None, user=user)
    confirmed = request.method == 'POST' and form.is_valid()
    company = getattr(user, 'entreprise', None)
    active_statuses = ('attribuee', 'en_cours')
    has_active_shipments = bool(company and (
        company.expeditions.filter(statut__in=active_statuses).exists()
        or company.offres.filter(statut='acceptee', expedition__statut__in=active_statuses).exists()
    ))

    if confirmed:
        if has_active_shipments:
            form.add_error(None, 'Terminez ou annulez les expéditions concernées avant de supprimer votre compte.')
        else:
            user.delete()
            logout(request)
            messages.success(request, 'Votre compte a été supprimé.')
            return redirect('home')

    return render(request, 'accounts/delete_account.html', {
        'form': form, 'company': company, 'has_active_shipments': has_active_shipments,
    })
