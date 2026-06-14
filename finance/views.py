from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms

from .models import CashFlow


class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = ['category', 'amount', 'description']

        widgets = {
            'category': forms.Select(
                attrs={
                    'class': 'w-full rounded-xl border border-slate-300 px-4 py-3'
                }
            ),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'w-full rounded-xl border border-slate-300 px-4 py-3',
                    'step': '0.01'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'w-full rounded-xl border border-slate-300 px-4 py-3',
                    'rows': 4
                }
            ),
        }


def ledger_list(request):
    transactions = CashFlow.objects.all().order_by('-date')

    context = {
        'transactions': transactions,
        'global_balance': CashFlow.get_global_balance(),
    }

    return render(
        request,
        'finance/ledger_list.html',
        context
    )


def cashflow_create(request):

    if request.method == 'POST':
        form = CashFlowForm(request.POST)

        if form.is_valid():
            flow = form.save()

            messages.success(
                request,
                f"{flow.get_category_display()} recorded successfully (${flow.amount:.2f})"
            )

            return redirect('ledger_list')

    else:
        form = CashFlowForm()

    return render(
        request,
        'finance/cashflow_form.html',
        {
            'form': form
        }
    )