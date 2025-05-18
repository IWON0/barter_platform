from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class BarterPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='StrongPass123')
        self.user2 = User.objects.create_user(username='user2', password='StrongPass123')

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Велосипед',
            description='Почти новый велосипед',
            category='Транспорт',
            condition='used'
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Смартфон',
            description='Новый смартфон в коробке',
            category='Электроника',
            condition='new'
        )

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'SuperPass123',
            'password2': 'SuperPass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_ad(self):
        self.client.login(username='user1', password='StrongPass123')
        response = self.client.post(reverse('ad_create'), {
            'title': 'Книга',
            'description': 'Интересная книга',
            'category': 'Книги',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='Книга').exists())

    def test_edit_ad(self):
        self.client.login(username='user1', password='StrongPass123')
        response = self.client.post(reverse('ad_edit', args=[self.ad1.id]), {
            'title': 'Велосипед обновлён',
            'description': 'Обновлённое описание',
            'category': 'Транспорт',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 302)
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, 'Велосипед обновлён')

    def test_delete_ad(self):
        self.client.login(username='user1', password='StrongPass123')
        response = self.client.post(reverse('ad_delete', args=[self.ad1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(id=self.ad1.id).exists())

    def test_search_ad(self):
        self.client.login(username='user1', password='StrongPass123')
        response = self.client.get(reverse('ad_list'), {'q': 'Смартфон'})
        self.assertContains(response, 'Смартфон')

    def test_create_exchange_proposal(self):
        self.client.login(username='user1', password='StrongPass123')
        response = self.client.post(reverse('exchange_proposal_create', args=[self.ad2.id]), {
            'ad_sender': self.ad1.id,
            'comment': 'Обмен велосипед на смартфон'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExchangeProposal.objects.filter(comment__icontains='велосипед').exists())

    def test_reject_exchange_proposal(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Обмен?'
        )
        self.client.login(username='user2', password='StrongPass123')
        response = self.client.post(reverse('exchange_proposal_reject', args=[proposal.id]))
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'rejected')

    def test_accept_exchange_proposal(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Обмен?'
        )
        self.client.login(username='user2', password='StrongPass123')
        response = self.client.post(reverse('exchange_proposal_accept', args=[proposal.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(id=self.ad1.id).exists())
        self.assertFalse(Ad.objects.filter(id=self.ad2.id).exists())
