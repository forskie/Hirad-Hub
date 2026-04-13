from django.contrib.auth.decorators import user_passes_test


teacher_required = user_passes_test(
    lambda u: (
        u.is_authenticated
        and (
            u.role in ['admin', 'director']
            or (
                u.role == 'teacher'
                and hasattr(u, 'teacher_profile')
                and u.teacher_profile.is_verified
            )
        )
    )
)