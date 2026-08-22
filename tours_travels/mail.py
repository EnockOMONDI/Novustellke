from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def verification_mail(link, user):
    try:
        subject = "Welcome to Novustell Travel"
        message = f'Hi {user.username}, welcome to Novustell Travel.<br>To activate your account, click the link below:<br>{link}<br><br>'

        # Add a new paragraph about the advantages of your travel agency in HTML
        directors_message = """
        <p> <strong> Directors message </strong></p>
        """

        advantages_message = """
        <p>We are delighted to have you as part of the Novustell Travel community. Our goal is simple: We want every trip you take with us to be <strong>affordable</strong> and wonderfully <strong>memorable</strong>. Thats where we come in, we take care of all the little things to ensure your journey is smooth and effortless, creating moments you'll treasure forever.</p>    """

        html_body = message + directors_message + advantages_message
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_body),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_body, "text/html")
        email.send(fail_silently=False)

        print(f"Verification email sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False



