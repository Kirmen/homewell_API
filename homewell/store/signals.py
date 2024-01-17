from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserRating
from django.db.models import Avg, Count


@receiver(post_save, sender=UserRating)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    ratings_for_product = UserRating.objects.filter(product=product)
    total_rating = sum([rating.rating for rating in ratings_for_product])
    product.rating = total_rating / max(len(ratings_for_product), 1)
    product.save()


def update_rating(self, new_rating, rating_id=None):
    if 1 <= new_rating <= 5:
        ratings_aggregate = UserRating.objects.filter(product=self).aggregate(
            total_rating=Avg('rating'),
            total_ratings=Count('rating')
        )

        total_rating = ratings_aggregate['total_rating'] or 0.0
        total_ratings = ratings_aggregate['total_ratings'] or 1

        if rating_id:
            old_rating = UserRating.objects.get(id=rating_id).rating
            total_rating -= old_rating

        self.rating = total_rating / total_ratings
        self.save()
    else:
        raise ValueError("Рейтинг повинен бути від 1 до 5.")
