import hashlib


MULTIPART_TEXT_TMPL = '\r\n'.join([
'--{0[boundary]}',
'Content-Disposition: form-data; name={0[name]}',
'Content-Length: {0[length]}',
'',
'{0[value]}',
''])


MULTIPART_ONE_FILE_TMPL = '\r\n'.join([
'--{0[boundary]}',
'Content-Disposition: form-data; name={0[name]}; filename={0[filename]}',
'Content-Type: {0[content-type]}',
'',
'{0[value]}',
''])


def create_boundary(boundary):
    """Create boundary for post submission.

    :param boundary: boundary will be converted into hexdigest.
    :type boundary: str

    """
    return hashlib.md5(boundary).hexdigest()


BOUNDARY = create_boundary('OuterBoundary')
SUBBOUNDARY = create_boundary('InnerBoundary')


def files(value):
    """Construct multipart/mixed part for post submission::

        --InnerBoundary
        Content-Disposition: file; filename="file1.txt"
        Content-Type: text/plain

        Some text comes here.
        --InnerBoundary
        Content-Disposition: file; filename="file2.png"
        Content-Type: image/gif
        Content-Transfer-Encoding: binary

        Binary gif file.
        --InnerBoundary--


    :param value: List of file data.
    :type value: list

    Example of value:

    .. code-block:: python

        [
            {
                'content-type': 'text/plain',
                'data': <StringIO.StringIO instance at 0x37d3320>,
                'filename': 'file1.txt'},
            {
                'content-type': 'image/gif',
                'data': <StringIO.StringIO instance at 0x37d3368>,
                'filename': 'file2.png'}]
    """

    body = []
    for val in value:
        data = val['data']
        data.seek(0)
        parts = [
            '--{0}'.format(SUBBOUNDARY),
            'Content-Disposition: file; filename="{0}"'.format(val['filename']),
            'Content-Type: {0}'.format(val['content-type']),
            '',
            '{0}'.format(data.read())]
        body.append('\r\n'.join(parts))
    body = '\r\n'.join(body) + '\r\n--{0}--'.format(SUBBOUNDARY)
    return body


def multifile(key, value, boundary):
    """Construct multipart/form-data part for post submission::

        Content-Type: multipart/form-data; boundary=OuterBoundary

        --OuterBoundary
        Content-Disposition: form-data; name="some_name"
        Content-Type: multipart/mixed; boundary=InnerBorder
        ...
        --OuterBoundary--

    :param key: The name of multipart/mixed file field name. In this case, it is some_name.
    :type url: str

    :param value: List of file data. Values created by files function will be used between --OuterBoundary and --OuterBoundary--
    :type url: list

    :param boundary: Boundary string.
    :type url: str
    """

    values = files(value)
    parts = [
        '--{0}'.format(boundary),
        'Content-Disposition: form-data; name="{0}"'.format(key),
        'Content-Type: multipart/mixed; boundary={0}'.format(SUBBOUNDARY),
        '',
        values,
        '']
    return parts


def multipart_formdata(data):
    """Given an iterable of (key, value) field parameters, returns the HTTP request
    body and the content_type (which includes the boundary string), to be used with an
    httplib-like call.

    This function is adapted from

       http://urllib3.googlecode.com/svn/trunk/urllib3/filepost.py

    :param data: Data which is list of tuples.
    :type data: list
    """

    body = []
#    for key, value in sorted(fields.items()):
    for key, value in data:
        if isinstance(value, dict):
            body.append(MULTIPART_ONE_FILE_TMPL.format({
                'boundary': BOUNDARY,
                'name': key,
                'filename': value['filename'],
                'content-type': value['content-type'],
                'value': value['data'].read(),
            }))
        elif isinstance(value, list):
            body.append('\r\n'.join(multifile(key, value, BOUNDARY)))
        else:
            body.append(MULTIPART_TEXT_TMPL.format({
                'boundary': BOUNDARY,
                'name': key,
                'value': value,
                'length': len(value),
            }))
    body.append('--{0}--\r\n'.format(BOUNDARY))
    content_type = 'multipart/form-data; boundary={0}'.format(BOUNDARY)

    return ''.join(body), content_type
