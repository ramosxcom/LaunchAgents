"""module to wrap the WordPress Rest API

class Post has methods to create, retrieve, and update wordpress posts.
currently relies on basic authentication, which should only be used
for development, not production. Improve / extend module when needed

"""

import json
import requests

# WP-API doc https://developer.wordpress.org/rest-api/reference/posts/

class Post(object):
  """
  wraps the WordPress REST API for Posts
  """
  authentication = {}

  def set_authentication(self, user, passwd):
    self.authentication['user'] = user
    self.authentication['pass'] = passwd
    return

  def create(self, hostname, date, date_gmt, title, content,
             slug=None, status=None, password=None, author=None,
             excerpt=None, featured_media=None, comment_status=None,
             ping_status=None, format=None, meta=None, sticky=None,#pylint: disable=redefined-builtin
             template=None, categories=None, tags=None):
    """
   Create a new post
    """
    url = "https://%s/wp-json/wp/v2/posts" % hostname
    args = {}

    args['date'] = date  # YYYY-MM-DDTHH:MM:SS
    args['date_gmt'] = date_gmt  # YYYY-MM-DDTHH:MM:SS
    args['slug'] = slug
    args['status'] = status
    args['password'] = password
    args['title'] = title
    args['content'] = content
    args['author'] = author
    args['excerpt'] = excerpt
    args['featured_media'] = featured_media
    args['comment_status'] = comment_status
    args['ping_status'] = ping_status
    args['format'] = format
    args['meta'] = meta
    args['sticky'] = sticky
    args['template'] = template
    args['categories'] = categories
    args['tags'] = tags

    request_params = {}
    args = {k: v for k, v in args.items() if v}
    #remove keys with values that equal empty string

    auth = (self.authentication['user'], self.authentication['pass'])
    headers = {}
    response = requests.post(url, headers=headers, params=request_params,
                             auth=auth, data=args)
    payload = response.content
    print("Post.create")
    return payload

  def update(self, hostname, id, date, date_gmt, content, #pylint: disable=redefined-builtin
             title=None, slug=None, status=None, password=None,
             author=None, excerpt=None, featured_media=None,
             comment_status=None, ping_status=None, format=None, #pylint: disable=redefined-builtin
             meta=None, sticky=None, template=None, categories=None,
             tags=None):
    """
    Update a wordpress post
    """

    url = "https://%s/wp-json/wp/v2/posts/%s" % (hostname, id)
    args = {}
    args['date'] = date  # YYYY-MM-DDTHH:MM:SS
    args['date_gmt'] = date_gmt  # YYYY-MM-DDTHH:MM:SS
    args['slug'] = slug
    args['status'] = status
    args['password'] = password
    args['title'] = title
    args['content'] = content
    args['author'] = author
    args['excerpt'] = excerpt
    args['featured_media'] = featured_media
    args['comment_status'] = comment_status
    args['ping_status'] = ping_status
    args['format'] = format
    args['meta'] = meta
    args['sticky'] = sticky
    args['template'] = template
    args['categories'] = categories
    args['tags'] = tags

    request_params = {}
    args = {k: v for k, v in args.items() if v}
    # remove keys with values that equal empty string

    auth = (self.authentication['user'], self.authentication['pass'])
    headers = {}
    response = requests.post(url, headers=headers, #pylint: disable=unused-variable
                             params=request_params, auth=auth, data=args)
    print("Post.update")
    ret_url = None
    if response.content:
      ret_url = json.loads(response.content)['guid']['rendered']
    return ret_url

  def retrieve(self, hostname, id): #pylint: disable=redefined-builtin
    """
      retreive a workspress post given the site URL ans a wordpress post id
    """
    url = "https://%s/wp-json/wp/v2/posts/%s" % (hostname, id)
    request_params = {}
    auth = (self.authentication['user'], self.authentication['pass'])
    headers = {}
    response = requests.get(url, headers=headers,
                            params=request_params, auth=auth)
    payload = response.content
    payload = json.loads(payload)
    # print payload
    # print ("Post.retrieve")
    return payload

  def delete(self, id): #pylint: disable=redefined-builtin
    print(Post.delete, id)
    return

