from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

LEVELS = [
    (1000,   1, 'Newcomer'),   
    (5000,   2, 'Reader'),
    (10000,  3, 'Curious'),
    (20000,  4, 'Connoisseur'),
    (35000,  5, 'Researcher'),
    (45000,  6, 'Analyst'),
    (55000,  7, 'Erudite'),
    (70000,  8, 'Intellectual'),
    (85000,  9, 'Thinker'),
    (100000, 10, 'Hiradcore'),
]
@receiver(post_save, sender=CustomUser)
def update_level_and_title(sender, instance, **kwargs):
    
    score = instance.score or 0

    new_level = 1
    new_title = 'Newcomer'
    
    for points, level, title in LEVELS:
        if score >= points:
            new_level = level
            new_title = title
        else:
            break
    if instance.level != new_level or instance.title != new_title:
        instance.level = new_level
        instance.title = new_title
        instance.save(update_fields=['level', 'title'])


"""
This is the first variant, but its looks unoptimized, then i use another (just for optimization)
"""
# @receiver(post_save, sender=CustomUser)
# def update_level_and_title(sender, instance, **kwargs):
#     # title & level 
#     score = instance.score
#     if score >= 100000:
#         level = 10
#         title = 'Hiradcore'
#     elif score >= 85000:
#         level = 9
#         title = 'Thinker'
#     elif score >= 70000:
#         level = 8
#         title = 'Intellectual'
#     elif score >= 55000:
#         level = 7
#         title = 'Erudite'
#     elif score >= 45000:
#         level = 6
#         title = 'Analyst'
#     elif score >= 35000:
#         level = 5
#         title = 'Researcher'
#     elif score >= 20000:
#         level = 4
#         title = 'Connoisseur'
#     elif score >= 10000:
#         level = 3
#         title = 'Curious'
#     elif score >= 5000:
#         level = 2
#         title = 'Reader'
#     elif score >= 1000:
#         level = 1
#         title = 'Newcomer'
# if instance.level != new_level or instance.title != new_title:
#         instance.level = new_level
#         instance.title = new_title
#         instance.save(update_fields=['level', 'title'])