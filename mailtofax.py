#!/usr/bin/env python

import email
import json
import mimetypes
import re
import smtplib
import sys
import tempfile
from email.mime.message import MIMEMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from optparse import OptionParser
from subprocess import call

import settings


class InputError(Exception):
    """A general error for all the things we can't handle"""
    pass


_L10N_CACHE = None
def _(key):
    """Poor man's L10n."""
    global _L10N_CACHE

    if _L10N_CACHE is None:
        _L10N_CACHE = json.loads(open('l10n.json').read())

    return _L10N_CACHE[settings.LANG].get(key)


class Bouncer(object):
    """Bounce mail generator."""

    def __init__(self, incoming=None):
        self._msg = MIMEMultipart('alternative')
        # Hold on to incoming mail so we can use its info to generate bounces.
        self._incoming = incoming

    def bounce(self, err='Error!', recipient=None):
        """Generate a bounce message with the given error message."""
        text = _('email_text') % err
        html = _('email_html') % err

        self._msg.attach(MIMEText(text, 'plain'))
        self._msg.attach(MIMEText(html, 'html'))

        # Stick it all in an envelope.
        envelope = MIMEMultipart('mixed')
        envelope.attach(self._msg)

        # If present, attach the entire incoming email.
        if self._incoming is not None:
            inc_msg = MIMEMessage(self._incoming)
            inc_msg.add_header('Content-Disposition', 'attachment',
                               filename='%s.eml' % self._incoming['subject'])
            envelope.attach(inc_msg)

        if recipient is None and self._incoming:
            recipient = self._incoming.get('reply-to',
                                           self._incoming.get('from'))

        recipient = 'fwenzel@mozilla.com'
        envelope['From'] = settings.MAILTOFAX_EMAIL
        envelope['To'] = recipient
        envelope['Subject'] = _('subject') % (self._incoming['subject'] if
                                              self._incoming else '')
        if self._incoming:
            envelope['In-Reply-To'] = self._incoming['message-id']

        #print self._msg.as_string()
        smtp = smtplib.SMTP(settings.SMTP_SERVER['host'],
                            settings.SMTP_SERVER.get('port') or 25)
        if settings.SMTP_SERVER['tls']:
            smtp.starttls()
        if settings.SMTP_SERVER.get('user'):
            smtp.login(settings.SMTP_SERVER['user'],
                       settings.SMTP_SERVER['password'])

        smtp.sendmail(envelope['From'], [envelope['To']],
                      envelope.as_string())
        sys.exit(1)


class MailToFax(object):
    sender = '' # email sender to receive success or error messages
    options = None # options from argument parser
    args = None # arguments from argument parser

    def main(self):
        parser = OptionParser()
        usage = "usage: %prog [options] file"
        parser = OptionParser(usage)
        parser.add_option('-c', '--stdin', dest='stdin', action="store_true",
                          help='read data from stdin, not the file argument')
        parser.add_option('-n', '--dry-run', dest='noexec', action="store_true",
                          help=('Test mode: Do not execute command, just '
                                'display what would be run'))
        (self.options, self.args) = parser.parse_args()

        if self.options.stdin:
            mailfile = sys.stdin
        else:
            try:
                mailfile = open(self.args[0])
            except IndexError:
                print "The file argument is required!"
                sys.exit(1)
            except IOError:
                print "Input file not found!"
                sys.exit(1)
        msg = email.message_from_file(mailfile)
        self.process_email(msg)

    def process_email(self, msg):
        """Process email message: fetch attachments to be sent by fax."""
        if not msg.is_multipart():
            Bouncer(msg).bounce(_('e_noattachment'))

        # Grab email sender.
        self.sender = msg.get('reply-to', msg.get('from', settings.DEFAULT_SENDER))
        #print "Sender: %s" % self.sender

        # A fallback destination can be specified as subject. Each file name
        # can override this.
        subject = msg.get('subject')
        if re.match(r'\d+', subject):
            destination = subject
        else:
            destination = None

        sent = 0  # Number of faxes actually sent.
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type not in settings.FAX_MIME_TYPES: continue

            # Fall back to filename if no number in subject.
            if not destination:
                dest_match = re.search(r'^(\d+)\.', part.get_filename())
                if dest_match:
                    destination = dest_match.group(1)
                else:
                    Bouncer(msg).bounce(_('e_nonumber'))
            #print "Destination: %s" % destination

            # Prepare file
            suffix = mimetypes.guess_extension(content_type)
            if not suffix:
                suffix = '.bin'

            tmp = tempfile.NamedTemporaryFile(dir=settings.TMP, suffix=suffix)
            tmp.write(part.get_payload(decode=True))
            tmp.flush() # make sure it's not buffered

            self.sendfax(tmp, destination)
            sent += 1

            tmp.close()

        # Error handling: No faxes sent?
        if not sent:
            Bouncer(msg).bounce(_('e_noattachment'))

    def sendfax(self, file, destination):
        """send a fax to the given destination."""
        fax_command = settings.SENDFAX.split()
        substitutions = {'sender': self.sender,
                         'destination': destination,
                         'file': file.name,
                        }
        fax_command = [ l % substitutions for l in fax_command ]
        if self.options.noexec:
            fax_command.insert(0, 'echo')
        call(fax_command)

if __name__ == '__main__':
    MailToFax().main()
    # TODO: Report errors back to sender.
