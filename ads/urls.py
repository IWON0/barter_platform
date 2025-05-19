from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from rest_framework.routers import DefaultRouter
from .views import AdViewSet, ExchangeProposalViewSet

urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('create/', views.ad_create, name='ad_create'),
    path('edit/<int:pk>/', views.ad_edit, name='ad_edit'),
    path('ad/<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('proposals/', views.exchange_proposal_list, name='exchange_proposal_list'),
    path('proposals/<int:proposal_id>/accept/', views.exchange_proposal_accept, name='exchange_proposal_accept'),
    path('proposals/<int:proposal_id>/reject/', views.exchange_proposal_reject, name='exchange_proposal_reject'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('propose/<int:ad_receiver_id>/', views.exchange_proposal_create, name='exchange_proposal_create'),

]

router = DefaultRouter()
router.register(r'api/ads', AdViewSet, basename='ad')
router.register(r'api/proposals', ExchangeProposalViewSet, basename='exchangeproposal')

urlpatterns += router.urls
