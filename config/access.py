from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


BUSINESS_ROLES = ('chargeur', 'transporteur')


def company_for(user):
    company = getattr(user, 'entreprise', None)
    if company and company.type_entreprise == user.role:
        return company
    return None


class BusinessRoleMixin(LoginRequiredMixin):
    http_method_names = ['get', 'head', 'post', 'options']
    roles = BUSINESS_ROLES
    require_company = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in self.roles:
            raise PermissionDenied
        self.company = company_for(request.user)
        if self.require_company and not self.company:
            if request.method in ('GET', 'HEAD') and not hasattr(request.user, 'entreprise'):
                return redirect('entreprise_create')
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
