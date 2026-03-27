from django.contrib.auth.decorators import user_passes_test

teacher_required = user_passes_test(lambda u:u.is_authenticated and u.role in ['teacher', 'admin'])