import os
import inspect
from importlib import import_module

from cdf.core.streams.base import StreamDefBase


class Feature(object):

    @classmethod
    def get_features(cls,):
        if hasattr(cls, 'FEATURES'):
            return cls.FEATURES

        cls.FEATURES = []
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../features')
        for n in os.listdir(path):
            if os.path.isdir(os.path.join(path, n)):
                mod = import_module('cdf.features.{}.settings'.format(n))
                feature = Feature(
                    identifier=n,
                    name=getattr(mod, "NAME", None),
                    description=getattr(mod, "DESCRIPTION", None),
                    groups=getattr(mod, "GROUPS", []),
                    order=getattr(mod, "ORDER", None)
                )
                cls.FEATURES.append(feature)
        # Sort features by order
        cls.FEATURES = sorted(cls.FEATURES, key=lambda f: f.order)
        return cls.FEATURES

    def __init__(self, identifier, name, description, groups, order=None):
        """
        :param identifier : Identifier of the feature (ex : amin)
        :param name: Verbose name of the feature
        :param description : Description of the feature
        :param groups : a list of dict. ex : [{"id": "metrics", "name": "Main metrics"}, ..]
        :param priority : Worth of the feature (smaller is better).
                          When generating concatenated groups/fields from a crawl,
                          it will iterate on features sorted by priority
        """
        self.identifier = identifier
        self.name = name
        self.description = description
        self.groups = groups
        self.order = order

    def __unicode__(self):
        return unicode(self.identifier)

    def get_streams_def(self):
        """
        Return streams definition from the current feature
        """
        obj = []
        streams = import_module('cdf.features.{}.streams'.format(self.identifier))
        methods = inspect.getmembers(streams, predicate=inspect.isclass)
        for method_name, klass in methods:
            if issubclass(klass, StreamDefBase) and klass != StreamDefBase:
                obj.append(klass())
        return obj

    def get_streams_def_processing_document(self):
        """
        Return all streams needed to compute urls documents
        """
        obj = []
        for s in self.get_streams_def():
            if hasattr(s, 'process_document'):
                obj.append(s)
        return obj