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

    @mock.patch('hexagonit.testing.mime.hashlib')
    def test_create_boundary(self, hashlib):
        from hexagonit.testing.mime import create_boundary
        hashlib.md5().hexdigest.return_value = 'boundary'
        self.assertEqual(create_boundary('boundary_line'), 'boundary')

    def test_files(self):
        from hexagonit.testing.mime import SUBBOUNDARY
        from hexagonit.testing.mime import files
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
        from hexagonit.testing.mime import BOUNDARY
        from hexagonit.testing.mime import SUBBOUNDARY
        from hexagonit.testing.mime import multifile
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

    def test_multipart_formdata__non_file_single_field(self):
        from hexagonit.testing.mime import BOUNDARY
        from hexagonit.testing.mime import multipart_formdata
        data = [('username', 'Some Name')]
        res = (
            '--{0}\r\nContent-Disposition: form-data; name=username\r\nContent-Length: 9\r\n\r\nSome Name\r\n--{0}--\r\n'.format(BOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY)
        )
        self.assertEquals(res, multipart_formdata(data))

    def test_multipart_formdata__none_file_multi_fields(self):
        from hexagonit.testing.mime import BOUNDARY
        from hexagonit.testing.mime import multipart_formdata
        data = [
            ('username', 'Some Name'),
            ('userpass', 'Some Pass'),
        ]
        res = (
            '--{0}\r\nContent-Disposition: form-data; name=username\r\nContent-Length: 9\r\n\r\nSome Name\r\n--{0}\r\nContent-Disposition: form-data; name=userpass\r\nContent-Length: 9\r\n\r\nSome Pass\r\n--{0}--\r\n'.format(BOUNDARY),
             'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, multipart_formdata(data))

    def test_multipart_formdata__single_file(self):
        from hexagonit.testing.mime import BOUNDARY
        from hexagonit.testing.mime import multipart_formdata
        data = [
            (
                'files', {
                    'data': StringIO.StringIO('text_file'),
                    'content-type': 'text/plain',
                    'filename': 'filename.txt'
                }
            )
        ]
        res = (
            '--{0}\r\nContent-Disposition: form-data; name=files; filename=filename.txt\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--{0}--\r\n'.format(BOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, multipart_formdata(data))

    def test_multipart_formdata__multiple_file(self):
        from hexagonit.testing.mime import BOUNDARY
        from hexagonit.testing.mime import SUBBOUNDARY
        from hexagonit.testing.mime import multipart_formdata
        data = [
            (
                'files', [
                    {
                        'data': StringIO.StringIO('text_file'),
                        'content-type': 'text/plain',
                        'filename': 'filename.txt'},
                    {
                        'data': StringIO.StringIO('image_file'),
                        'content-type': 'image/gif',
                        'filename': 'filename.png'}
                ]
            )
        ]
        res = (
            '--{0}\r\nContent-Disposition: form-data; name="files"\r\nContent-Type: multipart/mixed; boundary={1}\r\n\r\n--{1}\r\nContent-Disposition: file; filename="filename.txt"\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--{1}\r\nContent-Disposition: file; filename="filename.png"\r\nContent-Type: image/gif\r\n\r\nimage_file\r\n--{1}--\r\n--{0}--\r\n'.format(BOUNDARY, SUBBOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, multipart_formdata(data))

    def test_multipart_formdata__non_file_field_single_file_field_and_multiple_file_field_together(self):
        from hexagonit.testing.mime import BOUNDARY
        from hexagonit.testing.mime import SUBBOUNDARY
        from hexagonit.testing.mime import multipart_formdata
        data = [
            (
                'multiple_files',
                    [
                    {
                        'data': StringIO.StringIO('text_file'),
                        'content-type': 'text/plain',
                        'filename': 'filename.txt'
                    },
                    {
                        'data': StringIO.StringIO('image_file'),
                        'content-type': 'image/gif',
                        'filename': 'filename.png'
                    }
                ]
            ),
            (
                'single_file',
                {
                    'data': StringIO.StringIO('single_text_file'),
                    'content-type': 'text/plain',
                    'filename': 'single_filename.txt'
                }
            ),
            (
                'username',
                'Some Name'
            ),
        ]
        res = (
            '--{0}\r\nContent-Disposition: form-data; name="multiple_files"\r\nContent-Type: multipart/mixed; boundary={1}\r\n\r\n--{1}\r\nContent-Disposition: file; filename="filename.txt"\r\nContent-Type: text/plain\r\n\r\ntext_file\r\n--{1}\r\nContent-Disposition: file; filename="filename.png"\r\nContent-Type: image/gif\r\n\r\nimage_file\r\n--{1}--\r\n--{0}\r\nContent-Disposition: form-data; name=single_file; filename=single_filename.txt\r\nContent-Type: text/plain\r\n\r\nsingle_text_file\r\n--{0}\r\nContent-Disposition: form-data; name=username\r\nContent-Length: 9\r\n\r\nSome Name\r\n--{0}--\r\n'.format(BOUNDARY, SUBBOUNDARY),
            'multipart/form-data; boundary={0}'.format(BOUNDARY))
        self.assertEquals(res, multipart_formdata(data))
