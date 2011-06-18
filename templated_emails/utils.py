import logging

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Context, TemplateDoesNotExist
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.translation import get_language, activate
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User

class LanguageStoreNotAvailable(Exception):
    pass

def send_templated_email(recipients, template_path, context=None,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    fail_silently=False):
    """
        recipients can be either a list of emails or a list of users,
        if it is users the system will change to the language that the
        user has set as theyr mother toungue
    """
    current_language = get_language()
    current_site = Site.objects.get(id=settings.SITE_ID)

    default_context = context or {}
    default_context["current_site"] = current_site
    default_context["STATIC_URL"] = settings.STATIC_URL

    subject_path = "%s/short.txt" % template_path
    text_path = "%s/email.txt" % template_path
    html_path = "%s/email.html" % template_path

    for recipient in recipients:
        # if it is user, get the email and switch the language
        if isinstance(recipient, User):
            email = recipient.email
            try:
                language = get_users_language(recipient)
            except LanguageStoreNotAvailable:
                language = None

            if language is not None:
                # activate the user's language
                activate(language)
        else:
            email = recipient

        # populate per-recipient context
        context = Context(default_context)
        context['recipient'] = recipient
        context['email'] = email

        # load email text and subject
        subject = render_to_string(subject_path, context)
        subject = "".join(subject.splitlines()) # this must be a single line
        text = render_to_string(text_path, context)

        msg = EmailMultiAlternatives(subject, text, from_email, [email])

        # try to attach the html variant
        try:
            body = render_to_string(html_path, context)
            if getattr(settings, "TEMPLATEDEMAILS_USE_PYNLINER", False):
                import pynliner
                body = pynliner.fromString(body)
            msg.attach_alternative(body, "text/html")
            msg.content_subtype = "html"
        except TemplateDoesNotExist:
            logging.info("Email sent without HTML, since %s not found" % html_path)

        msg.send(fail_silently=fail_silently)

        # reset environment to original language
        if isinstance(recipient, User):
            activate(current_language)


def get_users_language(user):
    """
    Returns site-specific language for this user. Raises
    LanguageStoreNotAvailable if this site does not use translated
    notifications.
    """
    if getattr(settings, 'NOTIFICATION_LANGUAGE_MODULE', False):
        try:
            app_label, model_name = settings.NOTIFICATION_LANGUAGE_MODULE.split('.')
            model = models.get_model(app_label, model_name)
            language_model = model._default_manager.get(user__id__exact=user.id)
            if hasattr(language_model, 'language'):
                return language_model.language
        except (ImportError, ImproperlyConfigured, model.DoesNotExist):
            raise LanguageStoreNotAvailable
    raise LanguageStoreNotAvailable
