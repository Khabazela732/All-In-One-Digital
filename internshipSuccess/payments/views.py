from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Payment
# Create your views here.

class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class PaymentListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = sum(p.amount for p in context['payments'])
        return context

class PaymentCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Payment
    fields = ['expense_type', 'amount', 'description']
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payment_list')

class PaymentUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Payment
    fields = ['expense_type', 'amount', 'description']
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payment_list')

class PaymentDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView): 
    model = Payment
    template_name = 'payments/payment_confirm_delete.html'
    success_url = reverse_lazy('administration/pages/payments/payment_list')