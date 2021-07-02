from rest_framework import permissions


# class IsMoreThanOneReview(permissions.BasePermission):
#     def has_permission(self, request, view):
#         self.req_user_id = request.user.id
#         self.req_product_id = request.data.get('product')
#         self.review_qnty = view.queryset.filter(author=self.req_user_id, product=self.req_product_id).count()
#
#         if self.review_qnty >= 1:
#             self.message = "Нельзя создавать более одного отзыва на товар"
#             return False
#
#         return True


class IsSelfReviewOrOrder(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if view.basename == 'product_reviews':
            self.obj_user = obj.author
        else:
            self.obj_user = obj.user

        if request.user != self.obj_user:
            if view.basename == 'product_reviews':
                self.message = 'Нельзя удалять или редактировать отзыв другого пользователя'
            else:
                self.message = 'Нельзя удалить или посмотреть чужой заказ'

            return False

        return True


class DenyAny(permissions.BasePermission):
    def has_permission(self, request, view):
        self.message = 'Метод не определен'
        return False

    def has_object_permission(self, request, view, obj):
        self.message = 'Метод не определен'
        return False
