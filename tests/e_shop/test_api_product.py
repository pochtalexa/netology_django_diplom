import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.test import APIClient
from e_shop.models import Product
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class TestProductsViewSet:
    def set_up(self):
        pass

    @pytest.mark.django_db
    def test_product_db(self):
        self.product_1 = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.product_2 = Product.objects.create(title='Помидор', description='Помидоры', price=2)
        self.product_3 = Product.objects.create(title='Банан', description='Бананы', price=3)
        assert Product.objects.filter(title='Огурец')
        assert Product.objects.filter(title='Помидор')
        assert Product.objects.filter(title='Банан')

    @pytest.mark.django_db
    def test_product_create_unauthorized(self):
        self.product_payload = {
            'title': 'Огурец',
            'description': 'Огурцы',
            'price': 1
        }

        self.client = APIClient()
        self.url = reverse('products-list')
        self.r = self.client.post(self.url, data=self.product_payload)
        assert self.r.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_product_create_admin(self):
        self.product_payload = {
            'title': 'Огурец',
            'description': 'Огурцы',
            'price': 1
        }
        self.admin_user = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=True)
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse('products-list')
        self.r = self.client.post(self.url, data=self.product_payload)
        assert self.r.status_code == HTTP_201_CREATED

    @pytest.mark.django_db
    def test_product_update_admin(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.product_payload = {
            'title': 'Огурец_1',
            'description': 'Огурцы_1',
            'price': 55
        }
        self.admin_user = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=True)
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse("products-detail", args=[self.products[0].id])
        self.r = self.client.patch(self.url, data=self.product_payload)
        assert self.r.status_code == HTTP_200_OK

        self.product_1_desc = list(Product.objects.filter(title='Огурец_1'))[0].description
        assert self.product_1_desc == 'Огурцы_1'

    @pytest.mark.django_db
    def test_product_partial_update_admin(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.product_payload = {
            'price': 55
        }

        self.admin_user = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=True)
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse("products-detail", args=[self.products[0].id])
        self.r = self.client.patch(self.url, data=self.product_payload)
        assert self.r.status_code == HTTP_200_OK

        self.product_1_desc = list(Product.objects.filter(title='Огурец'))[0].price
        assert self.product_1_desc == 55

    @pytest.mark.django_db
    def test_product_list(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.client = APIClient()
        self.url = reverse('products-list')
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert len(self.r_json) == 3

        self.db_ids_set = {el['id'] for el in self.r_json}
        self.expected_ids_set = {el.id for el in self.products}

        assert self.db_ids_set == self.expected_ids_set

    @pytest.mark.django_db
    def test_product_retrieve(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.client = APIClient()
        self.url = reverse("products-detail", args=[self.products[1].id])

        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert self.r_json['title'] == 'Помидор'

    @pytest.mark.django_db
    def test_product_filter(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.client = APIClient()
        self.url = f'{reverse("products-list")}'
        self.r = self.client.get(self.url, {'title': 'Банан'}, format='json')
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert self.r_json[0].get('title') == 'Банан'

    @pytest.mark.django_db
    def test_product_destroy_admin(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.admin_user = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=True)
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        self.url = reverse("products-detail", args=[self.products[0].id])
        assert Product.objects.filter(title='Огурец')

        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_204_NO_CONTENT
        assert not Product.objects.filter(title='Огурец')
