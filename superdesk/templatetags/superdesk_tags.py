from __future__ import unicode_literals
from hashlib import sha1
from bs4 import BeautifulSoup
from django import template
from django.template.base import NodeList, token_kwargs
from django.utils import six
from ..models import Item

register = template.Library()

@register.filter
def media_url(value):
    """Get media url for given resource
    """
    return "http://localhost:8080/reuters-php/web/media/%s" % sha1(value).hexdigest()

@register.assignment_tag(takes_context=True)
def remote_content(context, rendition, **kwargs):
    """Get item remote content
    """
    try:
        item = kwargs['item']
    except KeyError:
        item = context['item']
    for remote in item.contentSet.remoteContent:
        if remote.rendition == rendition:
            return remote

@register.assignment_tag(takes_context=True)
def inline_content(context, **kwargs):
    """Get item inline content
    """
    try:
        item = kwargs['item']
    except KeyError:
        item = context['item']
    soup = BeautifulSoup(item.contentSet.inlineContent.content)
    return "\n".join([unicode(p) for p in soup.body.find_all('p')])

def get_kwargs(parser, token):
    """helper for parsing token kwargs"""
    kwargs = {}
    bits = token.split_contents()
    bits = bits[1:]
    if len(bits):
        kwargs = token_kwargs(bits, parser)
    return kwargs

@register.tag(name="items")
def do_items(parser, token):
    kwargs = get_kwargs(parser, token)
    nodelist = parser.parse(('/items',))
    parser.delete_first_token()
    return ItemsNode(nodelist, kwargs)

@register.tag(name="package_items")
def do_package_items(parser, token):
    kwargs = get_kwargs(parser, token)
    nodelist = parser.parse(('/package_items',))
    parser.delete_first_token()
    return PackageItemsNode(nodelist, kwargs)

class ItemsNode(template.Node):
    """Items Node
    """

    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def resolve_kwargs(self, context):
        return dict([(key, val.resolve(context)) for key, val in six.iteritems(self.kwargs)])

    def render(self, context):
        context.push();
        kwargs = self.resolve_kwargs(context)
        items = Item.objects(type=kwargs['type']).order_by('-itemMeta.versionCreated')[:kwargs['length']]
        nodelist = NodeList()
        for item in items:
            context['item'] = item
            for node in self.nodelist:
                nodelist.append(node.render(context))
        context.pop()
        return nodelist.render(context)

class PackageItemsNode(ItemsNode):
    def render(self, context):
        context.push()
        items = self.get_items(context)
        nodelist = NodeList()
        context['package'] = context['item']
        first = True
        for item in items:
            context['item'] = item
            context['first'] = first
            for node in self.nodelist:
                nodelist.append(node.render(context))
            first = False
        context.pop()
        return nodelist.render(context)

    def get_items(self, context):
        package = context['item']
        kwargs = self.resolve_kwargs(context)
        refs = package.get_item_refs(kwargs['group'])

        if 'class' in kwargs:
            refs = [r for r in refs if r.itemClass == kwargs['class']]

        if 'length' in kwargs:
            refs = refs[:kwargs['length']]

        items = [Item.objects.get(id=r.residRef) for r in refs]
        return items
