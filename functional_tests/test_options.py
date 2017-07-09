# TODO: re-add when more stable

# import os
# import unittest
# import pytest
# import requests
# from stable_world.client import Client
#
# STABLE_WORLD_URL = os.getenv('STABLE_WORLD_URL', 'http://stable.world')
# url_templates = list(Client.url_templates().items())
#
#
# @pytest.mark.parametrize("url_template, test_method", url_templates)
# def test_client_urls(url_template, test_method):
#     res = requests.request(test_method, STABLE_WORLD_URL + url_template)
#     assert res.status_code == 200
#
#
# if __name__ == "__main__":
#     unittest.main()
