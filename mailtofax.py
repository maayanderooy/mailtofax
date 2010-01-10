#!/usr/bin/env python

import email
from optparse import OptionParser
import sys

import settings

SENDER='' # email sender to receive success or error messages


class InputError(Exception):
    """A general error for all the things we can't handle"""
    pass

def main():
    parser = OptionParser()
    usage = "usage: %prog [options] file"
    parser = OptionParser(usage)
    parser.add_option('-c', '--stdin', dest='stdin', action="store_true",
                      help='read data from stdin, not the file argument')
    (options, args) = parser.parse_args()

    if options.stdin:
        mailfile = sys.stdin
    else:
        try:
            mailfile = open(args[0])
        except IndexError:
            print "The file argument is required!"
            sys.exit(1)
        except IOError:
            print "Input file not found!"
            sys.exit(1)
    msg = email.message_from_file(mailfile)
    process_email(msg)

def process_email(msg):
    """process email message: fetch attachments to be sent by fax"""
    if not msg.is_multipart():
        raise InputError('Input needs to be a multipart message!')
    for part in msg.walk():
        if part.get_content_type() not in settings.FAX_MIME_TYPES: continue
        print part.get_content_type()

if __name__ == '__main__':
    main()

