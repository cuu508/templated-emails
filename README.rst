================
templated-emails
================

This is a fork of https://github.com/philippWassibauer/templated-emails.
It removes multi-language and Celery support.

This app abstracts the sending of emails in a way so that it is possible to
switch from plain text emails to html emails, even if you are using third party apps.
It does this by using a very similar mechanism as django-notifications.

Each email gets a folder. In this folder one can put:

* short.txt (for the subject)
* email.txt (for the plain text email)
* email.html (optional, if an HTML email should also be sent)

A good practice is to put all emails in an emails/ folder within your templates folder,
so it is easy to see what emails are being sent by your system.

Recipients can either be an array of emails (as strings) or users.
If you pass users it will also try to find the users stored language
(accounts.Account.language in pinax) and send it using it.

Sending an emails works like this::

    from templated_emails.utils import send_templated_email
    send_templated_email(["philipp@gidsy.com"], "emails/invite_friends", {"my_variable":"blafoo"})

or

::

    user = User.objects.get(pk=1)
    # this will try to switch to the correct language of the user
    send_templated_email([user], "emails/invite_friends", {"my_variable":"blafoo"})

The system will add current_site (the Site object of the Django Project)
and STATIC_URL (for linking in static content) to the context of your templates.


Inline CSS Rules
================

Inline CSS Rules are annoying and tedious, but a neccessity if you want to support all email clients.
Since 0.3 pynliner is included that will take the CSS from the HEAD and put it into each element that matches the rule

There is a toggle you can set in settings.py to turn this feature on or off:
TEMPLATEDEMAILS_USE_PYNLINER = False is the default value.


Install
=======

::

    pip install -e http://github.com/cuu508/templated-emails.git#egg=templated-emails



Dependencies
============
* pynliner
* cssutils

Follow Original Author
======================

* http://github.com/philippWassibauer
* http://twitter.com/__philw__
* http://philippw.tumblr.com
* https://bitbucket.org/philippwassibauer
