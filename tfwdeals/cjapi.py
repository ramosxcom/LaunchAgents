"""
a wrapper for the CJ REST API

contains methods for look up and search API
Only includes what I needed for my project
improve and extend whn required
documentation here: https://developers.cj.com/docs/rest-apis/overview
"""

import json
import os
import os.path
import xmltodict
import requests


class CjRestApi(object):
  """
  class to wrap rest calls to CJ API
  """
  def get_cjapikey(self):
    key_path = '/Users/ramos/dev/script/keys/cjapi.key'
    api_key = None
    if os.path.exists(key_path):
      api_keyfn = open(key_path, "r")
      api_key = api_keyfn.read()#.decode('utf8')
      api_keyfn.close()
    return api_key

  def advertiser_lookup(self):
    """
    lookup a the list of joined CJ advertisers for my account
    :return:
    """
    url = "https://advertiser-lookup.api.cj.com/v2/advertiser-lookup"
    request_params = {
        'requestor-cid': '4342599',
        'advertiser-ids': 'joined',
        'advertiser-name': '',
        'keywords': '',
        'page-number': '',
        'records-per-page': '100',
        'mobile-tracking-certified': ''
        }
    request_params = {k: v for k, v in request_params.items() if
                      v}  # remove keys with values that equal empty string

    headers = {}
    headers['authorization'] = self.get_cjapikey()
    response = requests.get(url, headers=headers, params=request_params)
    advertisers = xmltodict.parse(response.content)
    return advertisers

  def link_search(self, advertiser_ids, website_id):
    """
     search for a the current list links for a specified advertisers
    """
    url = "https://link-search.api.cj.com/v2/link-search"
    records_per_page = '100'
    request_params = {
        'website-id': website_id,
        'advertiser-ids': advertiser_ids,
        'keywords': '',
        'category': '',
        'link-type': '',
        'promotion-type': '',
        'promotion-start-date': '',
        'promotion-end-date': '',
        'page-number': '',
        'records-per-page': records_per_page,
        'language': ''
        }

    request_params = {k: v for k, v in request_params.items() if
                      v}  # remove keys with values that equal empty string

    links = {}
    headers = {}
    headers['authorization'] = self.get_cjapikey()
    response = requests.get(url, headers=headers, params=request_params)
    links = xmltodict.parse(response.content)
    return links

  def save_results_as_json(self, pathname, results):
    f = open(pathname, 'w')
    doc = json.dumps(results, indent=2)
    f.write(doc)
    f.close()
    return
