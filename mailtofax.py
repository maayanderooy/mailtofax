#!/usr/bin/env python

import email
import mimetypes
from optparse import OptionParser
import re
from subprocess import call
import sys
import tempfile

import settings


class MailToFax:
    sender = '' # email sender to receive success or error messages
    options = None # options from argument parser
    args = None # arguments from argument parser

    class InputError(Exception):
        """A general error for all the things we can't handle"""
        pass

    def main(self):
        parser = OptionParser()
        usage = "usage: %prog [options] file"
        parser = OptionParser(usage)
        parser.add_option('-c', '--stdin', dest='stdin', action="store_true",
                          help='read data from stdin, not the file argument')
        parser.add_option('-n', '--dry-run', dest='noexec', action="store_true",
                          help='Test mode: Do not execute command, just display ' \
                               'what would be run')
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
        """process email message: fetch attachments to be sent by fax"""
        # grab email sender
        self.sender = msg.get('reply-to', msg.get('from', settings.DEFAULT_SENDER))
        #print "Sender: %s" % self.sender

        if not msg.is_multipart():
            raise InputError('Input needs to be a multipart message!')

        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type not in settings.FAX_MIME_TYPES: continue

            # prepare destination
            dest_match = re.search(r'(\d+)', part.get_filename())
            if not dest_match:
                raise InputError("Attachment file name must contain the " \
                                 "recipient's fax number!")
            destination = dest_match.group(1)
            #print "Destination: %s" % destination

            # prepare file
            suffix = mimetypes.guess_extension(content_type)
            if not suffix:
                suffix = '.bin'
            tmp = tempfile.NamedTemporaryFile(dir=settings.TMP, suffix=suffix)
            tmp.write(part.get_payload(decode=True))
            tmp.flush() # make sure it's not buffered
            self.sendfax(tmp, destination)
            tmp.close()

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

