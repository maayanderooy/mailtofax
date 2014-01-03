# mailtofax settings file

# This is where the attachments will be temporarily stored. /tmp is probably
# a good spot.
TMP = '/tmp'

# List of mime types to be interpreted as faxes.
FAX_MIME_TYPES = ['application/pdf']

# Default sender, if email sender can't be determined.
DEFAULT_SENDER = 'postmaster@localhost'

# sendfax command. Add all options here.
# Refer to the sendfax man page for more info.
#
# Replacements:
# %(sender)s : Sender email address (can contain spaces!)
# %(destination)s : Recipient's fax number
# %(file)s : Temporary file to be faxed (email attachment)
SENDFAX = 'sendfax -mnD -f "%(sender)s" -d %(destination)s %(file)s'

# Load local settings, if they exist.
try:
    from settings_local import *
except ImportError:
    pass
