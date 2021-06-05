import re
from urllib import parse
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

# describe_url() expects a string that is a URL
# describe_url() returns a description of the webpage based solely on the URL
# (unless it's a youtube video, in which case the description is just the whole URL)
@register.filter(is_safe=True)
@stringfilter
def describe_url(url):
	site_name = ""
	site_page = ""
	if 'genshin-impact.fandom' in url:
		# expecting a valid URL for a specific page on genshin-impact.fandom.com
		# page name is after "wiki/"
		site_name = "Genshin Impact Wiki"
		with_underscores = parse.unquote(url[url.find("wiki")+5:])
		site_page = with_underscores.replace("_", " ")
	elif ('youtube.com' in url) or ('youtu.be' in url):
		# forget describing it haha
		return url
	else:
		# from Python's regex how-to:
		# "The syntax for a named group is one of the Python-specific extensions: (?P<name>...)."
		domain_re = re.compile("(?P<domain>(?:\w+\.)*\w+\.(?:com|co|org|net))")
		site_name = domain_re.search(url).group('domain')
		page_re = re.compile("(?:\w\.(?:com|co|org|net)/(?P<page>.*))")
		site_page = page_re.search(url).group('page')
	return "{page} ({site})".format(page=site_page, site=site_name)