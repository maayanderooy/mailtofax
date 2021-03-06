mailtofax
=========

mailtofax is a simple script that parses email messages, extracts PDF
attachments, and sends them on to the Hylafax [sendfax][sendfax-man] command.

The recipient fax number can be in one of two places:

* in the subject (only the number, with no other surrounding cruft)
* as part of the PDF file name, e.g., `0123456789.pdf`.

If there is a number in both places, the *subject* takes precedence.

In the `procmail` directory, there are two example files that show how you can
use the [procmail][procmail] mail processing tool to funnel emails to a
dedicated mailtofax user on your mail server into the mailtofax tool.

[sendfax-man]: http://linux.die.net/man/1/sendfax
[procmail]: http://www.procmail.org/

Authors
-------
* Frederic Wenzel (fwenzel@mozilla.com)
* Jean Pierre Wenzel (jpwenzel@gmx.net)

License
-------
This software is licensed under the [CC-GNU LGPL][LGPL] version 2.1 or later.

[LGPL]: http://creativecommons.org/licenses/LGPL/2.1/

