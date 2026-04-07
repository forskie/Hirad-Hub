from django.contrib.auth.decorators import user_passes_test



teacher_required = user_passes_test(
    lambda u: (
        u.is_authenticated
        and u.role in ['teacher', 'admin', 'director']
        and hasattr(u, 'teacher_profile')
        and u.teacher_profile.is_verified
    )
)