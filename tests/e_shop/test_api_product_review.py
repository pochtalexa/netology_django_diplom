import pytest
from django.urls import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.test import APIClient
from e_shop.models import Product, ProductReview
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class TestProductReviewViewSet:
    def set_up(self):
        pass

    @pytest.mark.django_db
    def test_product_review_create_unauthorized(self):
        self.user_user = User.objects.create(username='user1', is_staff=False, is_active=True, is_superuser=False)
        self.id_author = self.user_user.id

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.id_product = self.product.id

        self.review_payload = {
            'id_author': self.id_author,
            'id_product': self.id_product,
            'review': 'тестовый отзыв о товаре',
            'mark': 5
        }

        self.client = APIClient()
        self.url = reverse('product_reviews-list')
        self.r = self.client.post(self.url, data=self.review_payload)
        assert self.r.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_product_review_create_authorized(self):
        self.user_user = User.objects.create(username='user1', is_staff=False, is_active=True, is_superuser=False)
        self.id_author = self.user_user.id

        self.user_token = Token.objects.create(user=self.user_user)

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.id_product = self.product.id

        self.review_payload = {
            'author': self.id_author,
            'product': self.id_product,
            'review': 'тестовый отзыв о товаре',
            'mark': 5
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_reviews-list')
        self.r = self.client.post(self.url, data=self.review_payload)
        assert self.r.status_code == HTTP_201_CREATED

    @pytest.mark.django_db
    def test_product_review_create_authorized_invalid_mark(self):
        self.user_user = User.objects.create(username='user1', is_staff=False, is_active=True, is_superuser=False)
        self.id_author = self.user_user.id

        self.user_token = Token.objects.create(user=self.user_user)

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.id_product = self.product.id

        self.review_payload = {
            'id_author': self.id_author,
            'id_product': self.id_product,
            'review': 'тестовый отзыв о товаре',
            'mark': 6
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_reviews-list')
        self.r = self.client.post(self.url, data=self.review_payload)
        assert self.r.status_code == HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_review_update_authorized(self):
        self.user_user = User.objects.create(username='user1', is_staff=False, is_active=True, is_superuser=False)
        self.id_author = self.user_user.id

        self.user_token = Token.objects.create(user=self.user_user)

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.id_product = self.product.id

        self.product_review = ProductReview.objects.create(
            author=self.user_user,
            product=self.product,
            review='тестовый отзыв о товаре',
            mark=1
        )

        self.id_product_review = self.product_review.id

        self.review_payload = {
            'author': self.id_author,
            'product': self.id_product,
            'review': 'тестовый отзыв о товаре 1',
            'mark': 5
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_reviews-detail', args=[self.id_product_review])
        self.r = self.client.patch(self.url, data=self.review_payload)
        assert self.r.status_code == HTTP_200_OK

        self.product_review_mark = list(ProductReview.objects.filter(review='тестовый отзыв о товаре 1'))[0].mark
        assert self.product_review_mark == 5

    @pytest.mark.django_db
    def test_review_partial_update_authorized(self):
        self.user_user = User.objects.create(username='user1', is_staff=False, is_active=True, is_superuser=False)
        self.id_author = self.user_user.id

        self.user_token = Token.objects.create(user=self.user_user)

        self.product = Product.objects.create(title='Огурец', description='Огурцы', price=1)
        self.id_product = self.product.id

        self.product_review = ProductReview.objects.create(
            author=self.user_user,
            product=self.product,
            review='тестовый отзыв о товаре',
            mark=1
        )

        self.id_product_review = self.product_review.id

        self.review_payload = {
            'mark': 5
        }

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse('product_reviews-detail', args=[self.id_product_review])
        self.r = self.client.patch(self.url, data=self.review_payload)
        assert self.r.status_code == HTTP_200_OK

        self.product_review_mark = list(ProductReview.objects.filter(review='тестовый отзыв о товаре'))[0].mark
        assert self.product_review_mark == 5

    @pytest.mark.django_db
    def test_review_list_unauthorized(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.user_user = User.objects.bulk_create([
            User(username='user1', is_staff=False, is_active=True, is_superuser=False),
            User(username='user2', is_staff=False, is_active=True, is_superuser=False),
            User(username='user3', is_staff=False, is_active=True, is_superuser=False)
        ])

        self.product_review = ProductReview.objects.bulk_create([
            ProductReview(author=self.user_user[0], product=self.products[0], review='отзыв 1', mark=1),
            ProductReview(author=self.user_user[1], product=self.products[1], review='отзыв 2', mark=2),
            ProductReview(author=self.user_user[2], product=self.products[2], review='отзыв 3', mark=3)
        ])

        self.client = APIClient()
        self.url = reverse('product_reviews-list')
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert len(self.r_json) == 3

        self.db_ids_set = {el['id'] for el in self.r_json}
        self.expected_ids_set = {el.id for el in self.product_review}

        assert self.db_ids_set == self.expected_ids_set

    @pytest.mark.django_db
    def test_review_retrieve_unauthorized(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.user_user = User.objects.bulk_create([
            User(username='user1', is_staff=False, is_active=True, is_superuser=False),
            User(username='user2', is_staff=False, is_active=True, is_superuser=False),
            User(username='user3', is_staff=False, is_active=True, is_superuser=False)
        ])

        self.product_review = ProductReview.objects.bulk_create([
            ProductReview(author=self.user_user[0], product=self.products[0], review='отзыв 1', mark=1),
            ProductReview(author=self.user_user[1], product=self.products[1], review='отзыв 2', mark=2),
            ProductReview(author=self.user_user[2], product=self.products[2], review='отзыв 3', mark=3)
        ])

        self.client = APIClient()
        self.url = reverse('product_reviews-detail', args=[self.product_review[1].id])
        self.r = self.client.get(self.url)
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert self.r_json['review'] == 'отзыв 2'

    @pytest.mark.django_db
    def test_review_filter_unauthorized(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.user_user = User.objects.bulk_create([
            User(username='user1', is_staff=False, is_active=True, is_superuser=False),
            User(username='user2', is_staff=False, is_active=True, is_superuser=False),
            User(username='user3', is_staff=False, is_active=True, is_superuser=False)
        ])

        self.product_review = ProductReview.objects.bulk_create([
            ProductReview(author=self.user_user[0], product=self.products[0], review='отзыв 1', mark=1),
            ProductReview(author=self.user_user[1], product=self.products[1], review='отзыв 2', mark=2),
            ProductReview(author=self.user_user[2], product=self.products[2], review='отзыв 3', mark=3)
        ])

        self.client = APIClient()
        self.url = f'{reverse("product_reviews-list")}'
        self.r = self.client.get(self.url, {'product': 'Банан'}, format='json')
        assert self.r.status_code == HTTP_200_OK

        self.r_json = self.r.json()
        assert self.r_json[0].get('review') == 'отзыв 3'

    @pytest.mark.django_db
    def test_review_destroy_unauthorized(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.user_user = User.objects.bulk_create([
            User(username='user1', is_staff=False, is_active=True, is_superuser=False),
            User(username='user2', is_staff=False, is_active=True, is_superuser=False),
            User(username='user3', is_staff=False, is_active=True, is_superuser=False)
        ])

        self.product_review = ProductReview.objects.bulk_create([
            ProductReview(author=self.user_user[0], product=self.products[0], review='отзыв 1', mark=1),
            ProductReview(author=self.user_user[1], product=self.products[1], review='отзыв 2', mark=2),
            ProductReview(author=self.user_user[2], product=self.products[2], review='отзыв 3', mark=3)
        ])

        self.client = APIClient()
        self.url = reverse("product_reviews-detail", args=[self.product_review[0].id])
        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_review_destroy_authorized(self):
        self.products = Product.objects.bulk_create([
            Product(title='Огурец', description='Огурцы', price=1),
            Product(title='Помидор', description='Помидоры', price=2),
            Product(title='Банан', description='Бананы', price=3)
        ])

        self.user_user = User.objects.bulk_create([
            User(username='user1', is_staff=False, is_active=True, is_superuser=False),
            User(username='user2', is_staff=False, is_active=True, is_superuser=False),
            User(username='user3', is_staff=False, is_active=True, is_superuser=False)
        ])

        self.product_review = ProductReview.objects.bulk_create([
            ProductReview(author=self.user_user[0], product=self.products[0], review='отзыв 1', mark=1),
            ProductReview(author=self.user_user[1], product=self.products[1], review='отзыв 2', mark=2),
            ProductReview(author=self.user_user[2], product=self.products[2], review='отзыв 3', mark=3)
        ])

        self.user_token = Token.objects.create(user=self.user_user[0])
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        self.url = reverse("product_reviews-detail", args=[self.product_review[0].id])
        self.r = self.client.delete(self.url)
        assert self.r.status_code == HTTP_204_NO_CONTENT
        assert not ProductReview.objects.filter(review='отзыв 1')