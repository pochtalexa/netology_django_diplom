import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)
from rest_framework.test import APIClient
from e_shop.models import Product, ProductCollection
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class TestProductCollectionViewSet:
    def set_up(self):
        pass

    @pytest.mark.django_db
    def test_collection_create_unauthorized(self):
        self.collection_payload = {
            'title': 'Коллекция 1',
            'description': 'Описание коллекции 1'
        }

        self.client = APIClient()
        self.url = reverse('product_collections-list')
        self.r = self.client.post(self.url, data=self.collection_payload)
        assert self.r.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_collection_create_admin(self):
        self.user_admin = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=False)
        self.user_token = Token.objects.create(user=self.user_admin)

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)

        self.collection_payload = {
            'title': 'Коллекция 1',
            'description': 'Описание коллекции 1',
            'selection': self.product.id
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_collections-list')
        self.r = self.client.post(self.url, data=self.collection_payload)
        assert self.r.status_code == HTTP_201_CREATED

    @pytest.mark.django_db
    def test_collection_update_admin(self):
        self.user_admin = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=False)
        self.user_token = Token.objects.create(user=self.user_admin)

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)

        self.collection = ProductCollection.objects.create(title='Коллекция 1', description='Описание коллекции 1')
        # self.collection.selection.set(self.product)
        self.collection.selection.add(self.product)

        self.collection_payload = {
            'title': 'Коллекция 2',
            'description': 'Описание коллекции 2',
            'selection': self.product.id
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_collections-detail', args=[self.collection.id])
        self.r = self.client.patch(self.url, data=self.collection_payload)
        assert self.r.status_code == HTTP_200_OK

        self.collection_description = list(ProductCollection.objects.filter(title='Коллекция 2'))[0].description
        assert str(self.collection_description) == 'Описание коллекции 2'

    @pytest.mark.django_db
    def test_collection_list(self):
        self.collections = ProductCollection.objects.bulk_create([
            ProductCollection(title='Коллекция 1', description='Описание коллекции 1'),
            ProductCollection(title='Коллекция 2', description='Описание коллекции 2'),
            ProductCollection(title='Коллекция 3', description='Описание коллекции 3')
        ])

        self.client = APIClient()
        self.url = f"{reverse('product_collections-list')}"
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert len(self.r_json) == 3

    @pytest.mark.django_db
    def test_collection_retrieve(self):
        self.collections = ProductCollection.objects.bulk_create([
            ProductCollection(title='Коллекция 1', description='Описание коллекции 1'),
            ProductCollection(title='Коллекция 2', description='Описание коллекции 2'),
            ProductCollection(title='Коллекция 3', description='Описание коллекции 3')
        ])

        self.client = APIClient()
        self.url = reverse('product_collections-detail', args=[self.collections[0].id])
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

    @pytest.mark.django_db
    def test_collection_destroy_not_admin(self):
        self.collections = ProductCollection.objects.bulk_create([
            ProductCollection(title='Коллекция 1', description='Описание коллекции 1'),
            ProductCollection(title='Коллекция 2', description='Описание коллекции 2'),
            ProductCollection(title='Коллекция 3', description='Описание коллекции 3')
        ])

        self.client = APIClient()
        self.url = reverse('product_collections-detail', args=[self.collections[0].id])
        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_collection_destroy_admin(self):
        self.user_admin = User.objects.create(username='admin', is_staff=True, is_active=True, is_superuser=False)
        self.user_token = Token.objects.create(user=self.user_admin)

        self.collections = ProductCollection.objects.bulk_create([
            ProductCollection(title='Коллекция 1', description='Описание коллекции 1'),
            ProductCollection(title='Коллекция 2', description='Описание коллекции 2'),
            ProductCollection(title='Коллекция 3', description='Описание коллекции 3')
        ])

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_collections-detail', args=[self.collections[0].id])
        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_204_NO_CONTENT
