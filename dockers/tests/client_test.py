#coding=utf-8
from __future__ import absolute_import
import unittest
from ..views.client import Client
# from django.test import TestCase

class ClientTest(unittest.TestCase):

    def setUp(self):

        self.client = Client(r'docker22')

    def test__create_hwaddr(self):
        print 1111111111111
        # uri = self.client.get_authorization_code_uri(state="app.state")

        # # Check URI
        # self.assertTrue(uri.startswith('https://grapheffect.com/pyoauth2/auth?'))

        # # Check params
        # params = utils.url_query_params(uri)
        # self.assertEquals('code', params['response_type'])
        # self.assertEquals('some.client', params['client_id'])
        # self.assertEquals('https://example.com/pyoauth2redirect', params['redirect_uri'])
        # self.assertEquals('app.state', params['state'])


