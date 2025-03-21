# this context will be available in all templates
def user_context(request):
    """Add user information to template context"""
    if request.session.get("user_id"):
        return {
            'is_authenticated': True,
            'user_email': request.session.get("user_email"),
            'user_id': request.session.get("user_id"),
        }
    return {
        'is_authenticated': False,
    } 