# File: users/pipeline.py

def get_profile_data(backend, user, response, *args, **kwargs):
    """
    Custom pipeline to extract additional profile data from social auth
    """
    if backend.name == 'google-oauth2':
        if response.get('given_name'):
            user.first_name = response['given_name']

        if response.get('family_name'):
            user.last_name = response['family_name']

        # Set email as verified since Google already verifies emails
        user.is_email_verified = True
        user.save()

    elif backend.name == 'github':
        # GitHub doesn't provide first/last name directly
        if response.get('name'):
            names = response['name'].split(' ', 1)
            if len(names) >= 1:
                user.first_name = names[0]
            if len(names) >= 2:
                user.last_name = names[1]

        user.is_email_verified = True
        user.save()

    return {'user': user}
