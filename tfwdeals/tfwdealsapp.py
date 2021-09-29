#!/usr/bin/python
"""
tfwdeals app

retrieves the current CJ promotional links for the TFW brands
generates an HTML page using a filtered list of links
posts the page of links to smartphonematters if the list of links
has changed since last run


"""
import collections
import cjapi
import os
import time
from datetime import datetime
import wprestapi
import pytz
import filecmp
import smtplib
from email.mime.text import MIMEText
import pickle
import jinja2


class TfwDealsApp(object):
  """
  class for TfwDeals main app
  """
  _publisher_cid = '4342599'
  _spm_website_id = '7601551'
  _spm_website_name = 'smartphonematters.com'
  _tfwbrands = {
      'tfw': {'post_id': '12251', 'cj_id': u'1038777'},
      # 'tw': {'post_id': '12230', 'cj_id': u'4499568'},
      # 'sm': {'post_id': '12283', 'cj_id': u'4078821'},
      # 'ntw': {'post_id': '12305', 'cj_id': u'1554194'},
      # 'stw': {'post_id': '12300', 'cj_id': u'2757954'},
      }

  def send_email_update_notification(self, body):
    """
    sends an email that pages where uploaded.
    """
    title = "Updated pages on {:s}".format(self._spm_website_name)

    to_address = 'chrisr@actonnetworks.com'
    from_address = to_address
    mail_username = from_address
    mail_password = "747Fastmailme747!"
    outgoing_smtp_name = 'mail.gandi.net'
    outgoing_smtp_port = 587

    msg = MIMEText(body)
    msg['Subject'] = title
    msg['From'] = from_address
    msg['To'] = to_address
    message = msg.as_string()

    smtp_server = smtplib.SMTP(outgoing_smtp_name, port=outgoing_smtp_port)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login(mail_username, mail_password)
    smtp_server.sendmail(from_address, to_address, message)

    return

  def save_html_files(self, pathname, b):
    """
      saves a normalized HTML file with a time index suffix appended to the end
      b is the Html file of links being posted to the site
      before saving, the domains for the links are normalized
      per each link search call, CJ changes the domains but the links are
      otherwise identical

      the links are normalized so that the current run can be comparied to the
      previous to detect if the links have
      changed

    """
    # save the original html file
    # save a copy with the link and image URLs normalized
    # this is so the files can be compared to check for differences
    hrefs = {
        'www.anrdoezrs.net': 'www.jdoqocy.com',
        'www.dpbolvw.net': 'www.jdoqocy.com',
        'www.kqzyfj.com': 'www.jdoqocy.com',
        'www.tkqlhce.com': 'www.jdoqocy.com',
        'www.awltovhc.com': 'www.lduhtrp.net',
        'www.ftjcfx.com': 'www.lduhtrp.net',
        'www.tqlkg.com': 'www.lduhtrp.net',
        }
    norm_buffer = b
    for k, v in hrefs.items():
      norm_buffer = norm_buffer.replace(k, v)

    norm_pathname = pathname + time.strftime("-%Y-%m-%d-%H%M%S")
    norm_file = open(norm_pathname, 'w')
    norm_file.write(norm_buffer)
    norm_file.close()

    return

  def generate_deals_page(self, links):
    """

    :param links: a list of links as returned from the CJ REST API
    :return:

    Extracts appropriate text links from list and generate
    HTML snippet using JINJA templating.

    """
    text_links = []
    coupon_links = []
    phone_brands = ['iPhone', 'Samsung', 'LG', 'Motorola', "BLU"]
    ordered_brand_links = collections.OrderedDict()
    for b in phone_brands:
      ordered_brand_links[b] = []
    for link in links:
      if u'Banner' not in link['link-type']:
        if link['coupon-code'] and link['coupon-code'].find('no code') == -1:
          coupon_links.append(link)
        else:
          text_links.append(link)
    codes = {}
    for c in coupon_links:
      code = c['coupon-code']
      if code not in codes:
        codes[code] = [c]
      else:
          codes[code].append(c)


    # print "there are {:d} total links in links".format(len(links))
    # print "there are {:d} text links in text_links".format(len(text_links))
    #print ("there are {:d} coupon links "
    #       "in coupon_links").format(len(coupon_links))

    # group the text links by phone brands or other
    for link in text_links:
      link_code_html = link['link-code-html']#.encode('ascii', 'ignore')

      for brand in phone_brands:
        link_code_html = link['link-code-html']#.encode('ascii', 'ignore')
        # if link_code_html.find(brand) != -1:
        if brand in link_code_html:
          #print "brand = {:s}".format(brand)
          ordered_brand_links[brand].append(link)
          break  # no need to continue
      else:  # **** this else executes when the for loop doesn't break
        brand = 'Other'
        #        print "brand = {:s}".format(brand)
        if brand not in ordered_brand_links:
          ordered_brand_links[brand] = []
        ordered_brand_links[brand].append(link)

    # # print 'links ordered by brand'
    # for k, v in ordered_brand_links.iteritems():
    #   print k, len(v)
    # for i in ordered_brand_links['Other']:
    #   print i

    data = {}
    data["text_links"] = text_links
    data["coupon_links"] = coupon_links
    if coupon_links:
      cl = coupon_links[0]
      data['coupon_code'] = cl["coupon-code"]
      #data['discount'] = cl["description"][0:3]

      #fixme - this is a really janky wat to find the percent discounted
      index = cl['link-code-html'].find('%')
      data['discount'] = cl["link-code-html"][index-2:index+1]


      # CJ date format  "2020-12-31 21:00:00.0",

      data['startdate'] = datetime.strptime(cl["promotion-start-date"],
                                            "%Y-%m-%d %H:%M:%S.%f")
      data['startdate'] = data['startdate'].strftime('%B %d,%Y')
      data['enddate'] = datetime.strptime(cl["promotion-end-date"],
                                          "%Y-%m-%d %H:%M:%S.%f")
      data['enddate'] = data['enddate'].strftime('%B %d,%Y')

    data["phone_brands"] = phone_brands
    data["phone_brands"].append("Other")
    data["ordered_brand_links"] = ordered_brand_links
    data["coupon_links"] = coupon_links
    data["advertiser_name"] = text_links[0]["advertiser-name"]

    my_path = os.path.dirname(__file__)  # path to where this script is located
    my_loader = jinja2.FileSystemLoader(my_path)
    env = jinja2.Environment(loader=my_loader, trim_blocks=True)
    #print os.path.join(my_path, 'tfw_template.html')
    #print os.path.join(my_path, 'tfw_template.html')
    template = env.get_template('tfw_template.html')

    rendered = template.render(mydata=data)
    return rendered

  def get_pathname(self, base, ext):
    """
    creates a pathname for the html filw
    uses a basename and appends the current working directory
    :param base:
    :param ext:
    :return:
    """
    pathname = os.path.dirname(__file__)
    filename = base + '.' + ext
    pathname = os.path.join(pathname, filename)
    return pathname

  def create_post_title(self, current_post):
    """
    changes the month and year in the current post title.

    This updates the month and year in the post tile
    should generate the whole title though
    if the post title is accidently changed on the site this doesn't fix it
    :param current_post:
    :return:
    """
    title = None
    if 'title' in current_post and \
        'rendered' in current_post['title']:
      title = current_post['title']['rendered']
      title = title.split("for", 1)
      title = title[0]
      title = title + time.strftime("for %B %Y")

    return title

  def html_file_cleanup(self, pathname, brands):
    """
    deletes html files older than the last 5 runs
    :param pathname:
    :param brands:
    :return:
    """
    for basename in brands:
      if os.path.isdir(pathname):
        filename = basename + '.html-'
        filenames = os.listdir(pathname)
        filtered_filenames = [os.path.join(pathname, f)
                              for f in filenames if f.startswith(filename)]
        filtered_filenames.sort(reverse=True)

        keep = 5
        filtered_filenames = filtered_filenames[keep:]
        if filtered_filenames:
          for fn in filtered_filenames:
            try:
              print('5 os.remove(%s)' % fn)
              os.remove(fn)
            except OSError as error:
              print(error)
    return

  def html_changed(self, pathname):
    """
    compares two normalized HTML files to check if the links have changed
    :param pathname:
    :return:
    """
    changed = True
    pn, fn = os.path.split(pathname) #files are stored where script resides

    filenames = os.listdir(pn)
    filtered = [f for f in filenames if fn + '-' in f]
    filtered.sort(reverse=True)

    if len(filtered) >= 2:
      p1 = os.path.join(pn, filtered[0])
      p2 = os.path.join(pn, filtered[1])
      changed = not filecmp.cmp(p1, p2)
      print(changed, p1, p2)

    return changed

  def run(self):
    """
    the main function for the app.
    I should change it to main
    :return:
    """
    print('running tfwdeals.py...')

    cjrestapi = cjapi.CjRestApi()
    posts = wprestapi.Post()
    posts.set_authentication("bob", "123web127me456")
    update_email_message = None

    for index, (brand_key, brand_dict) in enumerate(self._tfwbrands.items()): #pylint: disable=unused-variable,line-too-long
      post_id = brand_dict['post_id']
      cj_id = brand_dict['cj_id']
      # get the links for the brand
      results = cjrestapi.link_search(cj_id, self._spm_website_id)
      links = results['cj-api']['links']['link']

      date = datetime.now(pytz.utc).isoformat()
      # time.strftime("%Y-%M-%d-%H:%M:%S")

      current_post = posts.retrieve('smartphonematters.com', post_id)
      title = self.create_post_title(current_post)
      html_path = self.get_pathname(brand_key, 'html')
      r = self.generate_deals_page(links)
      self.save_html_files(html_path, r)
      if self.html_changed(html_path):
        # create the HTML page for the brand
        print(html_path)
        f = open(html_path, 'w')
        f.write(r)
        f.close()

        content = r
        status = 'publish'
        x = posts.update('smartphonematters.com', post_id, date, date,
                         content, title=title, status=status, author='2')
        # update the post on the smartphonematters.com
        # print('%s - changes found,'
        #        'updating %s') % (html_path, 'smartphonematters.com')

        if not update_email_message:
          update_email_message = ("The following pages were updated today"
                                  " on %s\n") % self._spm_website_name
        update_email_message = update_email_message + x + '\n'

      else:
        print('%s - No changes %s' % (html_path, 'smartphonematters.com'))

    self.html_file_cleanup(os.path.dirname(__file__), self._tfwbrands.keys())
    if update_email_message:
      self.send_email_update_notification(update_email_message)
    print ('tfwdeals.py completed.')
    return

  def debug(self):
    print('debug')
    cjrestapi = cjapi.CjRestApi()
    results = cjrestapi.link_search(u'1038777', self._spm_website_id)
    links = results['cj-api']['links']['link']
    print(links)
    d = pickle.dumps(links)
    with open('links.pickle', 'wb') as f:
      f.write(d)
    return


app = TfwDealsApp()
#app.debug()
app.run()
