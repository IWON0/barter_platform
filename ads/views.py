from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.permissions import IsAuthenticated
from .forms import AdForm, ExchangeProposalForm
from .models import Ad, ExchangeProposal
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, serializers
from .serializers import AdSerializer, ExchangeProposalSerializer
from .permissions import IsOwner
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        ad_sender = serializer.validated_data['ad_sender']
        if ad_sender.user != self.request.user:
            raise serializers.ValidationError("Вы можете предложить только своё объявление.")
        ad_receiver = serializer.validated_data['ad_receiver']
        if ad_receiver.user == self.request.user:
            raise serializers.ValidationError("Нельзя предлагать обмен на своё объявление.")
        serializer.save()


@login_required
def exchange_proposal_list(request):
    proposals = ExchangeProposal.objects.all()

    sender_username = request.GET.get('sender', '')
    receiver_username = request.GET.get('receiver', '')
    status = request.GET.get('status', '')

    if sender_username:
        proposals = proposals.filter(ad_sender__user__username__icontains=sender_username)
    if receiver_username:
        proposals = proposals.filter(ad_receiver__user__username__icontains=receiver_username)
    if status:
        proposals = proposals.filter(status=status)

    context = {
        'proposals': proposals,
        'filter_sender': sender_username,
        'filter_receiver': receiver_username,
        'filter_status': status,
        'status_choices': ExchangeProposal.STATUS_CHOICES,
    }
    return render(request, 'ads/exchange_proposal_list.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ad_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    return redirect('ad_list')


@require_http_methods(["GET", "POST"])
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def ad_list(request):
    query = request.GET.get("q")
    category = request.GET.get("category")
    condition = request.GET.get("condition")

    ads = Ad.objects.all()

    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if category:
        ads = ads.filter(category=category)

    if condition:
        ads = ads.filter(condition=condition)

    paginator = Paginator(ads, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "ads/ad_list.html", {
        "page_obj": page_obj,
        "categories": Ad.objects.values_list("category", flat=True).distinct(),
        "conditions": Ad.CONDITION_CHOICES,
        "query": query,
        "selected_category": category,
        "selected_condition": condition,
    })


@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/ad_create.html', {'form': form})


@login_required
def ad_edit(request, pk):
    ad = get_object_or_404(Ad, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_list')
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_edit.html', {'form': form})


@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk, user=request.user)
    ad.delete()
    return redirect('ad_list')


def ad_detail(request, pk):
    ad = Ad.objects.get(pk=pk)
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def exchange_proposal_create(request, ad_receiver_id):
    ad_receiver = get_object_or_404(Ad, id=ad_receiver_id)

    if ad_receiver.user == request.user:
        messages.error(request, 'Нельзя предложить обмен своему объявлению.')
        return redirect('ad_list')

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.status = 'pending'
            proposal.save()
            messages.success(request, 'Предложение обмена успешно отправлено!')
            return redirect('exchange_proposal_list')
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(request, 'ads/exchange_proposal_create.html', {'form': form, 'ad_receiver': ad_receiver})


@login_required
def exchange_proposal_accept(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden("Вы не можете принять это предложение.")

    if proposal.status == 'pending':
        proposal.status = 'accepted'
        proposal.save()
        proposal.ad_sender.delete()
        proposal.ad_receiver.delete()

    return redirect('exchange_proposal_list')


@login_required
def exchange_proposal_reject(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if request.user != proposal.ad_receiver.user and request.user != proposal.ad_sender.user:
        messages.error(request, "Вы не имеете доступа к этому предложению.")
        return redirect('exchange_proposal_list')

    if proposal.status != 'pending':
        messages.warning(request, "Это предложение уже обработано.")
        return redirect('exchange_proposal_list')

    proposal.status = 'rejected'
    proposal.save()
    messages.success(request, "Предложение отклонено.")
    return redirect('exchange_proposal_list')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_ads(request):
    ads = Ad.objects.filter(user=request.user)
    serializer = AdSerializer(ads, many=True)
    return Response(serializer.data)
