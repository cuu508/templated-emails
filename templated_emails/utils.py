import logging
import threading

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template import Context, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model


pynliner = None
if getattr(settings, 'TEMPLATEDEMAILS_USE_PYNLINER', False):
    import pynliner


def send_templated_email(recipients, template_path, context=None,
                         from_email=settings.DEFAULT_FROM_EMAIL,
                         fail_silently=False, extra_headers=None):
    """
        Each item in the recipients list can be either an user object
        or an email address. For user objects, the system will change to
        user's language.
    """

    kwargs = {
        "recipients": recipients,
        "template_path": template_path,
        "extra_context": context,
        "from_email": from_email,
        "fail_silently": fail_silently,
        "extra_headers": extra_headers
    }

    if getattr(settings, 'TEMPLATEDEMAILS_USE_THREADING', True):
        threading.Thread(target=_send_all, kwargs=kwargs).start()
    else:
        _send_all(**kwargs)


def _send_all(recipients, **kwargs):
    for recipient in recipients:
        _send_single(recipient, **kwargs)


def _send_single(recipient, template_path, extra_context, from_email,
                 fail_silently, extra_headers):

    context = Context()
    context.update(extra_context)
    context["STATIC_URL"] = settings.STATIC_URL
    context["recipient"] = recipient

    subject_path = "%s/short.txt" % template_path
    text_path = "%s/email.txt" % template_path
    html_path = "%s/email.html" % template_path

    if isinstance(recipient, get_user_model()):
        email = recipient.email
    else:
        email = recipient

    context["email"] = email

    # load email subject, strip and remove line breaks
    subject = render_to_string(subject_path, context).strip()
    subject = "".join(subject.splitlines())  # this must be a single line
    text = render_to_string(text_path, context)

    msg = EmailMultiAlternatives(subject, text, from_email, [email],
                                 headers=extra_headers)

    # try to attach the html variant
    try:
        body = render_to_string(html_path, context)
        if pynliner:
            body = pynliner.fromString(body)
        msg.attach_alternative(body, "text/html")
    except TemplateDoesNotExist:
        logging.info("Email sent without HTML, since %s not found" % html_path)

    msg.send(fail_silently=fail_silently)
    return msg
