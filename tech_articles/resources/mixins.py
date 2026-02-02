"""
Shared mixins for resources app views.
"""
from django.contrib.auth.mixins import UserPassesTestMixin


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
