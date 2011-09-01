import StringIO
import mock
import unittest2 as unittest


VALUE = [
    {
        'data': StringIO.StringIO('text_file'),
        'content-type': 'text/plain',
        'filename': 'filename.txt',
    },
    {
        'data': StringIO.StringIO('image_file'),
        'content-type': 'image/gif',
        'filename': 'filename.png',
    },
]


class TestMime(unittest.TestCase):

    @mock.patch('leo.testing.mime.hashlib')
    def test_create_boundary(self, hashlib):
        from leo.testing.mime import create_boundary
        hashlib.md5().hexdigest.return_value = 'boundary'
        self.assertEqual(create_boundary('boundary_line'), 'boundary')

    def test_files(self):
        from leo.testing.mime import SUBBOUNDARY
        from leo.testing.mime import files
        value = VALUE
        parts = '\r\n'.join([
            '--{0}'.format(SUBBOUNDARY),
            'Content-Disposition: file; filename="filename.txt"',
            'Content-Type: text/plain',
            '',
            'text_file',
            '--{0}'.format(SUBBOUNDARY),
            'Content-Disposition: file; filename="filename.png"',
            'Content-Type: image/gif',
            '',
            'image_file',
            '--{0}--'.format(SUBBOUNDARY)])
        self.assertEquals(parts, files(value))

    def test_multifile(self):
        from leo.testing.mime import BOUNDARY
        from leo.testing.mime import SUBBOUNDARY
        from leo.testing.mime import multifile
        key = 'files'
        boundary = BOUNDARY
        value = VALUE
        res = [
            '--{0}'.format(BOUNDARY),
            'Content-Disposition: form-data; name="files"',
            'Content-Type: multipart/mixed; boundary={0}'.format(SUBBOUNDARY),
            '',
            '--{0}\r\nContent-Disposition: file; filename="filename.txt"\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--{0}\r\nContent-Disposition: file; filename="filename.png"\r\nContent-Type: image/gif\r\n\r\nimage_file\r\n--{0}--'.format(SUBBOUNDARY),
            '']
        self.assertEquals(res, multifile(key, value, boundary))
