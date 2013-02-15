from __future__ import unicode_literals
from mongoengine import *
from collections import deque

connect('newscoop')

class ItemMeta(EmbeddedDocument):
    """Item Meta
    """
    itemClass = StringField()
    provider = StringField()
    versionCreated = DateTimeField()
    firstCreated = DateTimeField()
    pubStatus = StringField()
    role = StringField()

class ContentMeta(EmbeddedDocument):
    """Content Meta
    """
    urgency = StringField()
    slugline = StringField()
    headline = StringField()
    dateline = StringField()
    byline = StringField()
    creditline = StringField()
    description = StringField()
    language = StringField()

class RemoteContent(EmbeddedDocument):
    """Remote Content
    """
    residref = StringField()
    href = StringField()
    size = IntField()
    rendition = StringField()
    contentType = StringField()
    format = StringField()
    generator = StringField()
    width = IntField()
    height = IntField()

class InlineContent(EmbeddedDocument):
    """Inline Content
    """
    contentType = StringField()
    wordCount = IntField()
    content = StringField()

class ContentSet(EmbeddedDocument):
    """Content Set
    """
    remoteContent = ListField(EmbeddedDocumentField(RemoteContent))
    inlineContent = EmbeddedDocumentField(InlineContent)

class Ref(EmbeddedDocument):
    """Reference
    """
    idRef = StringField()
    residRef = StringField()
    version = StringField()
    contentType = StringField()
    itemClass = StringField()
    provider = StringField()
    versionCreated = DateTimeField()
    pubStatus = StringField()
    slugline = StringField()
    headline = StringField()

    def __unicode__(self):
        return self.residRef

class Group(EmbeddedDocument):
    """Group
    """
    id = StringField(db_field='_id')
    role = StringField()
    mode = StringField()
    refs = ListField(EmbeddedDocumentField(Ref))

    def __unicode__(self):
        return self.id

class GroupSet(EmbeddedDocument):
    """Group Set
    """
    root = StringField()
    groups = ListField(EmbeddedDocumentField(Group))

    def get_refs(self, group_id):
        """Get references for given group id
        """
        for group in self.groups:
            if group.id == group_id:
                return group.refs
        return []

class Item(Document):
    """anyItem
    """
    id = StringField(primary_key=True)
    type = StringField()
    itemMeta = EmbeddedDocumentField(ItemMeta)
    contentMeta = EmbeddedDocumentField(ContentMeta)
    contentSet = EmbeddedDocumentField(ContentSet)
    groupSet = EmbeddedDocumentField(GroupSet)
    meta = {'collection': 'news_item'}

    def get_item_refs(self, group):
        """Get references for items in given group
        """
        items = []
        queue = deque((group,))
        while len(queue):
            group_id = queue.popleft()
            refs = self.groupSet.get_refs(group_id)
            for ref in refs:
                if ref.idRef:
                    queue.append(ref.idRef)
                else:
                    items.append(ref)

        return items

    @property
    def slugline(self):
        return self.contentMeta.slugline

    @property
    def headline(self):
        return self.contentMeta.headline

    @property
    def dateline(self):
        return self.contentMeta.dateline

    @property
    def byline(self):
        return self.contentMeta.byline

    @property
    def creditline(self):
        return self.contentMeta.creditline

    @property
    def description(self):
        return self.contentMeta.description

    @property
    def versionCreated(self):
        return self.itemMeta.versionCreated

    @property
    def urgency(self):
        return self.contentMeta.urgency

