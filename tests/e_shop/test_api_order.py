import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND)
from rest_framework.test import APIClient
from e_shop.models import Product, Order
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class TestOrderViewSet:
    def set_up(self):
        pass

    def create_user(self, user_name, is_admin):
        self.user = User.objects.create(username=user_name, is_staff=is_admin, is_active=True, is_superuser=False)
        self.token = Token.objects.create(user=self.user)

        return self.user, self.token


    @pytest.mark.django_db
    def test_order_create_unauthorized(self):
        self.user_user, self.user_token = self.create_user('user1', False)
        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)

        self.order_payload = {
            'positions': [
                {'product': self.product, 'quantity': 2}
            ]
        }

        self.client = APIClient()
        self.url = reverse('orders-list')
        self.r = self.client.post(self.url, data=self.order_payload)
        assert self.r.status_code == HTTP_401_UNAUTHORIZED

    # TODO: не работает
    @pytest.mark.django_db
    def test_order_create_authorized(self):
        self.user_user, self.user_token = self.create_user('user1', False)
        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)

        self.order_payload = {
            "positions": [
                {"product": self.product, "quantity": 1}
            ]
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('orders-list')
        self.r = self.client.post(self.url, data=self.order_payload)
        assert self.r.status_code == HTTP_201_CREATED

    @pytest.mark.django_db
    def test_order_update_user(self):
        self.user_user, self.user_token = self.create_user('user1', False)
        self.order = Order.objects.create(user=self.user_user, sum=334455)

        self.order_payload = {
            'status': 'IN_PROGRESS',
            'sum': 445566.88
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse("orders-detail", args=[self.order.id])
        self.r = self.client.patch(self.url, data=self.order_payload)
        assert self.r.status_code == HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_order_update_admin(self):
        self.user_admin, self.admin_token = self.create_user('admin', True)
        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.order = Order.objects.create(user=self.user_admin, status='NEW', sum=2)
        self.order.positions.product = self.product
        self.order.positions.oreder = self.order
        self.order.positions.quantity = 2

        self.order_payload = {
            'status': 'IN_PROGRESS',
            'positions': [
                {'product': self.product, 'quantity': 2}

            ]
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse("orders-detail", args=[self.order.id])
        self.r = self.client.patch(self.url, data=self.order_payload)
        assert self.r.status_code == HTTP_200_OK

        self.order_sum = Order.objects.filter(status='IN_PROGRESS')[0].sum
        assert str(self.order_sum) == '2.00'

    @pytest.mark.django_db
    def test_order_list_not_admin(self):
        self.user_user, self.user_token = self.create_user('user1', False)
        self.id_author = self.user_user.id
        self.order = Order.objects.create(user=self.user_user, sum=334455)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = f"{reverse('orders-list')}"
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

    @pytest.mark.django_db
    def test_order_list_admin(self):
        self.user_admin, self.admin_token = self.create_user('admin', True)
        self.order = Order.objects.create(user=self.user_admin, sum=334455)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = f"{reverse('orders-list')}"
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

    @pytest.mark.django_db
    def test_order_retrieve_not_self(self):
        self.user_user1, self.user1_token = self.create_user('user1', False)
        self.id_author1 = self.user_user1.id
        self.order1 = Order.objects.create(user=self.user_user1, sum=111)

        self.user_user2, self.user2_token = self.create_user('user2', False)
        self.id_author2 = self.user_user2.id
        self.order2 = Order.objects.create(user=self.user_user2, sum=222)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user1_token.key}')
        self.url = {reverse('orders-list')}
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_order_retrieve_self(self):
        self.user_user1, self.user1_token = self.create_user('user1', False)
        self.id_author1 = self.user_user1.id
        self.order1 = Order.objects.create(user=self.user_user1, sum=111)

        self.user_user2, self.user2_token = self.create_user('user2', False)
        self.id_author2 = self.user_user2.id
        self.order2 = Order.objects.create(user=self.user_user2, sum=222)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user1_token.key}')
        self.url = reverse("orders-detail", args=[self.order1.id])
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

    @pytest.mark.django_db
    def test_order_filter_admin(self):
        self.user_admin, self.admin_token = self.create_user('admin', True)
        self.order1 = Order.objects.create(user=self.user_admin, sum=111)

        self.user_user, self.user_token = self.create_user('user', False)
        self.order2 = Order.objects.create(user=self.user_user, status='IN_PROGRESS', sum=222)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = f'{reverse("orders-list")}'
        self.r = self.client.get(self.url, {'status': 'IN_PROGRESS'}, format='json')
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert self.r_json[0].get('sum') == 222

    @pytest.mark.django_db
    def test_order_destroy_not_self(self):
        self.user_user1, self.user1_token = self.create_user('user1', False)
        self.order1 = Order.objects.create(user=self.user_user1, sum=111)

        self.user_user2, self.user2_token = self.create_user('user2', False)
        self.order2 = Order.objects.create(user=self.user_user2, status='IN_PROGRESS', sum=222)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user1_token.key}')
        self.url = reverse("orders-detail", args=[self.order2.id])
        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_order_destroy_self(self):
        self.user_admin, self.admin_token = self.create_user('user1', True)
        self.order1 = Order.objects.create(user=self.user_admin, sum=111)

        self.user_user, self.user_token = self.create_user('user2', False)
        self.order2 = Order.objects.create(user=self.user_user, status='IN_PROGRESS', sum=222)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse("orders-detail", args=[self.order1.id])
        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_204_NO_CONTENT









