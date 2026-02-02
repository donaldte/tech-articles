import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from .models import TimeSlotConfiguration, AvailabilityRule, ExceptionDate
from .forms import TimeSlotConfigurationForm, AvailabilityRuleForm, ExceptionDateForm


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin or staff."""
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class AvailabilitySettingsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Manage availability settings with weekly calendar."""
    template_name = "tech-articles/dashboard/pages/appointments/availability.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create the configuration
        config = TimeSlotConfiguration.objects.filter(is_active=True).first()
        if not config:
            config = TimeSlotConfiguration.objects.create()
        
        # Get all availability rules
        availability_rules = AvailabilityRule.objects.filter(is_active=True).order_by('weekday', 'start_time')
        
        # Get all exception dates
        exception_dates = ExceptionDate.objects.filter(is_active=True).order_by('date')
        
        # Forms
        context.update({
            'config': config,
            'config_form': TimeSlotConfigurationForm(instance=config),
            'availability_rules': availability_rules,
            'exception_dates': exception_dates,
            'availability_form': AvailabilityRuleForm(),
            'exception_form': ExceptionDateForm(),
        })
        
        return context


class SaveConfigurationView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API endpoint to save time slot configuration."""
    
    def post(self, request, *args, **kwargs):
        config = TimeSlotConfiguration.objects.filter(is_active=True).first()
        if not config:
            config = TimeSlotConfiguration.objects.create()
        
        form = TimeSlotConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': str(_('Configuration saved successfully'))
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)


class AvailabilityRuleAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API endpoint to manage availability rules."""
    
    def get(self, request, *args, **kwargs):
        rules = AvailabilityRule.objects.filter(is_active=True).order_by('weekday', 'start_time')
        data = [{
            'id': str(rule.id),
            'weekday': rule.weekday,
            'start_time': rule.start_time.strftime('%H:%M'),
            'end_time': rule.end_time.strftime('%H:%M'),
            'is_recurring': rule.is_recurring,
        } for rule in rules]
        return JsonResponse({'rules': data})
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = AvailabilityRuleForm(data)
        if form.is_valid():
            rule = form.save()
            return JsonResponse({
                'success': True,
                'message': str(_('Availability rule added successfully')),
                'rule': {
                    'id': str(rule.id),
                    'weekday': rule.weekday,
                    'start_time': rule.start_time.strftime('%H:%M'),
                    'end_time': rule.end_time.strftime('%H:%M'),
                    'is_recurring': rule.is_recurring,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    def delete(self, request, *args, **kwargs):
        rule_id = request.GET.get('id')
        try:
            rule = get_object_or_404(AvailabilityRule, id=rule_id)
            rule.delete()
            return JsonResponse({
                'success': True,
                'message': str(_('Availability rule deleted successfully'))
            })
        except (ValueError, AvailabilityRule.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class ExceptionDateAPIView(LoginRequiredMixin, AdminRequiredMixin, View):
    """API endpoint to manage exception dates."""
    
    def get(self, request, *args, **kwargs):
        exceptions = ExceptionDate.objects.filter(is_active=True).order_by('date')
        data = [{
            'id': str(exc.id),
            'date': exc.date.strftime('%Y-%m-%d'),
            'reason': exc.reason,
        } for exc in exceptions]
        return JsonResponse({'exceptions': data})
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = ExceptionDateForm(data)
        if form.is_valid():
            exc = form.save()
            return JsonResponse({
                'success': True,
                'message': str(_('Exception date added successfully')),
                'exception': {
                    'id': str(exc.id),
                    'date': exc.date.strftime('%Y-%m-%d'),
                    'reason': exc.reason,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    def delete(self, request, *args, **kwargs):
        exc_id = request.GET.get('id')
        try:
            exc = get_object_or_404(ExceptionDate, id=exc_id)
            exc.delete()
            return JsonResponse({
                'success': True,
                'message': str(_('Exception date deleted successfully'))
            })
        except (ValueError, ExceptionDate.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
