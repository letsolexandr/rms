# import sys
import subprocess
import re
import os
import requests

__all__ = ['LibreOfficeConverter']


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


class LibreOfficeConverter(object):

    @classmethod
    def convert_to_pdf_old(cls, source, folder, timeout=None):
        args = ['libreoffice', '--headless', '--convert-to',
                'pdf:writer_web_pdf_Export', '--outdir', folder, source]
        process = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        print(process.stdout)
        filename = re.search('-> (.*?) using filter', process.stdout.decode())

        if filename is None:
            raise LibreOfficeError(process.stdout.decode())
        else:
            return filename.group(1)

    @classmethod
    def convert_to_pdf_local(cls, source, output, timeout=None):
        args = ['doc2pdf', '-o', output, source]
        print(' '.join(args))
        process = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        print(process.stdout)

    @classmethod
    def convert_to_pdf(cls, source, output, timeout=None):
        UNOCONV_HOST = os.environ.get('UNOCONV_HOST', 'localhost')
        UNOCONV_PORT = os.environ.get('UNOCONV_PORT', '3000')
        url = f'http://{UNOCONV_HOST}:{UNOCONV_PORT}/unoconv/pdf'
        payload = {}
        name = os.path.basename(source)
        files = [
            ('file', (name, open(source, 'rb'),
             'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
        ]
        headers = {}
        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files, timeout=timeout)
        if response.status_code!=200:
            raise Exception(response.text)
        with open(output, "wb") as f:
            f.write(response.content)
