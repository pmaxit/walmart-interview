import unittest
from io import BytesIO
from unittest.mock import patch, mock_open
from flask import Flask
from app import  app
import os


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        app.config['DOWNLOADS_PATH'] = 'downloads'
        app.config['TEMPLATES'] = 'templates'
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_download_endpoint(self):
        # simulate a request to the file download checkpoint
        response = self.client.get('/csv')
        # get the url from self.client
        
        filepath="interview.csv"

        # check if the response has the expected status code
        self.assertEqual(response.status_code, 200)

        # check if the response contains the correct content type header
        self.assertEqual(response.headers['Content-Type'], 'text/csv; charset=utf-8')

        # Check if the response contains the correct content disposition header
        self.assertEqual(response.headers['Content-Disposition'], f'attachment; filename={filepath}')

        # Check if file is saved in current directory
        self.assertTrue(os.path.exists(filepath))

if __name__ == '__main__':
    unittest.main()