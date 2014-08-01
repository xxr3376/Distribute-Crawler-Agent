#!encoding=utf-8
import os
import simplejson as json
import tempfile
from gzip import GzipFile
from StringIO import StringIO
import hashlib

class SubmitJob(object):
    def __init__(self, query_id, answer):
        self.query_id = query_id
        answer_string = json.dumps(answer)
        out = StringIO()
        gzip_obj = GzipFile(mode='w', fileobj = out)
        gzip_obj.write(answer_string)
        gzip_obj.close()

        fd, path = tempfile.mkstemp()

        self.zip_file_path = path

        zip_file = os.fdopen(fd, 'w')
        zip_file.write(out.getvalue())
        zip_file.close()

        md5 = hashlib.md5()
        md5.update(out.getvalue())
        self.md5_checksum = md5.hexdigest()

        sha1 = hashlib.sha1()
        sha1.update(out.getvalue())
        self.sha1_checksum = sha1.hexdigest()

        out.close()

    def __del__(self):
        if self.zip_file_path:
            os.remove(self.zip_file_path)
        return

    @property
    def meta(self):
        return {
            "id": self.query_id,
            "md5_checksum": self.md5_checksum,
            "sha1_checksum": self.sha1_checksum,
        }
