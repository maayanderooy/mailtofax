# mailtofax settings file

# this is where the attachments will be temporarily stored. /tmp is probably
# a good spot.
TMP = '/tmp'

# list of mime types to be interpreted as faxes
FAX_MIME_TYPES = ['application/pdf']

# default sender, if email sender can't be determined
DEFAULT_SENDER = 'postmaster@localhost'

# sendfax command. Add all options here.
#
# refer to the sendfax man page for more info:
# http://linux.die.net/man/1/sendfax
#
# replacements:
# %(sender)s : sender email address
# %(destination)s : recipient's fax number
# %(file)s : temporary file to be faxed (email attachment)
SENDFAX = 'sendfax -mnD -$ %(sender)s -d %(destination)s %(file)s'

