#! /bin/sh
""":" .

exec python "$0" ${1+"$@"}
"""
# -*- coding: utf-8 -*-
from dropbox_token import TOKEN

import sys
import os
import dropbox
from dropbox.files import WriteMode

LOCALFILE = sys.argv[1]
REMOTEFILE = "/" + os.path.basename(LOCALFILE)

if __name__ == "__main__":
    dbx = dropbox.Dropbox(TOKEN)
    with open(LOCALFILE, 'rb') as f:
        dbx.files_upload(f, REMOTEFILE, mode=WriteMode("overwrite"))

