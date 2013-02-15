from __future__ import unicode_literals
from django.shortcuts import render_to_response
from django.http import Http404
from models import Item

def home(request):
    return render_to_response('index.html')

def item(request, item_id):
    try: 
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        raise Http404
    return render_to_response(['item_%s.html' % item.type, 'item.html'], {'item': item})
