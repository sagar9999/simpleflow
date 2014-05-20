import unittest

from cdf.analysis.urls.generators.documents import UrlDocumentGenerator
from cdf.features.main.streams import IdStreamDef, InfosStreamDef
from cdf.features.ganalytics.streams import VisitsStreamDef


class TestBasicInfoGeneration(unittest.TestCase):
    def setUp(self):
        self.ids = [
            [1, 'http', 'www.site.com', '/path/name1.html', ''],
            [2, 'http', 'www.site.com', '/path/name2.html', ''],
            [3, 'http', 'www.site.com', '/path/name3.html', ''],
        ]
        self.infos = [
            [1, 1, 'text/html', 0, 1, 200, 1200, 303, 456],
            [2, 2, 'text/html', 0, 1, 200, 1200, 303, 456],
            [3, 2, 'text/html', 0, 1, 200, 1200, 303, 456],
        ]

        self.visits = [
            [1, "organic", "google", 10],
            [1, "organic", "bing", 15],
            [3, "organic", "google", 7],
        ]

    def test_url_infos(self):
        gen = UrlDocumentGenerator([
            IdStreamDef.get_stream_from_iterator(iter(self.ids)),
            InfosStreamDef.get_stream_from_iterator(iter(self.infos)),
            VisitsStreamDef.get_stream_from_iterator(iter(self.visits)),
        ])
        documents = [k[1] for k in gen]

        self.assertEquals(
            documents[0]["visits"],
            {
                "organic": {
                    "google": {
                        "nb": 10
                    },
                    "bing": {
                        "nb": 15
                    }
                }
            }
        )

        self.assertEquals(
            documents[1]["visits"],
            {
                "organic": {
                    "google": {
                        "nb": 0
                    },
                    "bing": {
                        "nb": 0
                    }
                }
            }
        )

        self.assertEquals(
            documents[2]["visits"],
            {
                "organic": {
                    "google": {
                        "nb": 7
                    },
                    "bing": {
                        "nb": 0
                    }
                }
            }
        )
