#!encoding=utf-8
import os
import simplejson as json
import tempfile
import zlib
import hashlib

class SubmitJob(object):
    def __init__(self, query_id, answer):
        self.query_id = query_id
        answer_string = json.dumps(answer)
        compress_string = zlib.compress(answer_string)
        fd, path = tempfile.mkstemp()

        self.zip_file_path = path

        zip_file = os.fdopen(fd, 'w')
        zip_file.write(compress_string)

        zip_file.close()

        md5 = hashlib.md5()
        md5.update(compress_string)
        self.md5_checksum = md5.hexdigest()

        sha1 = hashlib.sha1()
        sha1.update(compress_string)
        self.sha1_checksum = sha1.hexdigest()

    def __del__(self):
        print 'file already  delete!!!!!!!!!! %s' % self.query_id
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
