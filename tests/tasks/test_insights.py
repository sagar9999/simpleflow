import unittest
import mock
import httpretty
import boto
from moto import mock_s3

from cdf.exceptions import ApiError, ApiFormatError
from cdf.core.features import Feature
from cdf.core.insights import (
    PositiveTrend,
    Insight,
    InsightTrendPoint,
    InsightValue
)
from cdf.metadata.url.es_backend_utils import ElasticSearchBackend
from cdf.query.filter import EqFilter
from cdf.query.query import Query
from cdf.tasks.insights import (
    get_query_agg_result,
    compute_insight_value,
    compute_insight_values,
    compute_insights,
    get_feature_options
)


class TestGetQueryAggResult(unittest.TestCase):
    def test_nominal_case(self):
        query = mock.create_autospec(Query)
        query.aggs = [{"metrics": [5]}]
        self.assertEqual(5, get_query_agg_result(query))

    def test_no_result_case(self):
        query = mock.create_autospec(Query)
        query.aggs = []
        self.assertEqual(0, get_query_agg_result(query))


class TestComputeInsightValue(unittest.TestCase):
    def setUp(self):
        self.feature_name = "feature"
        self.es_location = "http://elasticsearch.com:1234"
        self.es_index = "es_index"
        self.es_doc_type = "urls"

    @mock.patch("cdf.tasks.insights.get_query_agg_result", autospec=True)
    @mock.patch("cdf.tasks.insights.Query", autospec=True)
    def test_nominal_case(self,
                          query_mock,
                          get_query_agg_result_mock):
        #mocking
        get_query_agg_result_mock.return_value = 3.14

        #definition
        insight = Insight(
            "foo",
            "Foo insight",
            PositiveTrend.UP,
            EqFilter("foo_field", 1001)
        )
        crawls = {1001: {"foo"}, 2008: {"bar"}}

        #actual call
        actual_result = compute_insight_value(
            insight,
            self.feature_name,
            crawls,
            self.es_location,
            self.es_index,
            self.es_doc_type
        )

        #check values
        positive_trend = [
            InsightTrendPoint(1001, 3.14),
            InsightTrendPoint(2008, 3.14)
        ]
        expected_result = InsightValue(
            insight, self.feature_name, positive_trend)

        self.assertDictEqual(expected_result.to_dict(), actual_result.to_dict())

        #check the calls to Query.__init__()
        expected_query_calls = [
            mock.call(
                self.es_location, self.es_index, self.es_doc_type,
                1001, insight.query, backend=ElasticSearchBackend({}),
                limit=0, search_type='count'
            ),
            mock.call(
                self.es_location, self.es_index, self.es_doc_type,
                2008, insight.query, backend=ElasticSearchBackend({}),
                limit=0, search_type='count'
            )
        ]
        self.assertEqual(expected_query_calls, query_mock.mock_calls)

    def test_error_query(self):
        insight = Insight(
            "1", "Insight 1",
            PositiveTrend.UP, EqFilter("field", 1)
        )
        crawls = {1: {}}

        result = compute_insight_value(
            insight, "feature", crawls,
            self.es_location, self.es_index,
            self.es_doc_type
        )
        self.assertListEqual(
            map(lambda t: t.to_dict(), result.trend),
            [{'crawl_id': 1, 'score': None}]
        )

    @mock.patch("cdf.tasks.insights.get_query_agg_result", autospec=True)
    @mock.patch("cdf.tasks.insights.Query", autospec=True)
    def test_comparison_case(self,
                             query_mock,
                             get_query_agg_result_mock):
        #mocking
        get_query_agg_result_mock.return_value = 3.14

        #definition
        insight = Insight(
            "foo",
            "Foo insight",
            PositiveTrend.UP,
            EqFilter("foo_field", 1001)
        )
        crawls = {2008: {"comparison": {"options": []}}}

        #actual call
        actual_result = compute_insight_value(
            insight,
            self.feature_name,
            crawls,
            self.es_location,
            self.es_index,
            self.es_doc_type
        )

        #check values
        positive_trend = [
            InsightTrendPoint(2008, 3.14)
        ]
        expected_result = InsightValue(
            insight, self.feature_name, positive_trend)

        self.assertDictEqual(
            expected_result.to_dict(),
            actual_result.to_dict()
        )

        decorated_query = {
            "filters": {
                "and": [
                    {"or": [
                        {"not": {
                            "predicate": "exists",
                            "field": "disappeared"
                        }
                        },
                        {
                            "predicate": "eq",
                            "field": "disappeared",
                            "value": False
                        }
                    ]
                    },
                    {
                        "field": "foo_field",
                        "predicate": "eq",
                        "value": 1001
                    }
                ]
            },
            "aggs": [
                {"metrics": [{"count": "id"}]}
            ]
        }

        query_mock.assert_called_once_with(
            self.es_location,
            self.es_index,
            self.es_doc_type,
            2008,
            decorated_query,
            backend=mock.ANY,
            limit=0,
            search_type='count'
        )


class TestComputeInsightValues(unittest.TestCase):
    @mock.patch.object(Feature, 'get_features')
    @mock.patch("cdf.tasks.insights.compute_insight_value", autospec=True)
    def test_nominal_case(self, compute_insight_value_mock, get_features_mock):

        #we don't really care about the result
        compute_insight_value_mock.return_value = InsightValue(None, "", [])

        insight1 = Insight("1", "Insight 1", PositiveTrend.UP, EqFilter("field", 1))
        insight2 = Insight("2", "Insight 2", PositiveTrend.DOWN, EqFilter("field", 2))
        insight3 = Insight("3", "Insight 3", PositiveTrend.UNKNOWN, EqFilter("field", 3))

        feature1 = mock.create_autospec(Feature)
        feature1.name = "feature1"
        feature1.get_insights.return_value = [insight1]

        feature2 = mock.create_autospec(Feature)
        feature2.name = "feature2"
        feature2.get_insights.return_value = [insight2, insight3]

        get_features_mock.return_value = [feature1, feature2]

        crawls = {1001: {}}
        es_location = "http://elasticsearch.com"
        es_index = "botify"
        es_doc_type = "urls"
        actual_result = compute_insight_values(crawls,
                                               es_location,
                                               es_index,
                                               es_doc_type)
        #check results
        self.assertEqual(3, len(actual_result))
        self.assertTrue(
            all([isinstance(r, InsightValue) for r in actual_result])
        )
        expected_calls = [
            mock.call(insight1, 'feature1', crawls, es_location, es_index, es_doc_type),
            mock.call(insight2, 'feature2', crawls, es_location, es_index, es_doc_type),
            mock.call(insight3, 'feature2', crawls, es_location, es_index, es_doc_type),
        ]

        self.assertEqual(expected_calls, compute_insight_value_mock.mock_calls)


class TestComputeInsights(unittest.TestCase):
    @mock_s3
    @mock.patch("cdf.tasks.insights.get_feature_options", autospec=True)
    @mock.patch("cdf.tasks.insights.compute_insight_values", autospec=True)
    def test_nominal_case(self,
                          compute_insight_values_mock,
                          get_feature_options_mock):
        crawl_configurations = [(1001, "foo", "s3://foo"), (2008, "bar", "s3://bar")]
        get_feature_options_mock.return_value = {1001: {}, 2008: {}}
        es_location = "foo"
        es_index = "bar"
        es_doc_type = "baz"
        s3_uri = "s3://test_bucket"
        s3 = boto.connect_s3()
        s3.create_bucket('test_bucket')

        actual_result = compute_insights(
            crawl_configurations, es_location, es_index, es_doc_type, s3_uri
        )
        compute_insight_values_mock.assert_called_once_with(
            {1001: {}, 2008: {}},  # crawl ids are integers
            es_location,
            es_index,
            es_doc_type)
        expected_result = "s3://test_bucket/precomputation/insights.json"
        self.assertEqual(expected_result, actual_result)
        get_feature_options_mock.assert_called_once_with(crawl_configurations)


@mock.patch("cdf.tasks.insights.get_botify_api_token", autospec=True)
class TestGetFeatureOptions(unittest.TestCase):
    @httpretty.activate
    def test_nominal_case(self, get_botify_api_token_mock):
        #mocking
        get_botify_api_token_mock.return_value = "foo"
        httpretty.register_uri(httpretty.GET,
                               "http://api.foo.com/crawls/1001/config/",
                               body='{"features": {"option1": true}}',
                               content_type="application/json")
        httpretty.register_uri(httpretty.GET,
                               "http://api.foo.com/crawls/2008/config/",
                               body='{"features": {"option1": false}}',
                               content_type="application/json")

        crawl_configurations = [
            [1001, "http://api.foo.com/crawls/1001/config/", None],
            [2008, "http://api.foo.com/crawls/2008/config/", None]
        ]
        actual_result = get_feature_options(crawl_configurations)
        expected_result = {
            1001: {"option1": True},
            2008: {"option1": False}
        }
        self.assertEquals(expected_result, actual_result)

    @httpretty.activate
    def test_api_error(self, get_botify_api_token_mock):
        get_botify_api_token_mock.return_value = "foo"
        httpretty.register_uri(httpretty.GET,
                               "http://api.foo.com/crawls/1001/config/",
                               status=500)
        crawl_configurations = [
            [1001, "http://api.foo.com/crawls/1001/config/", None]
        ]
        self.assertRaises(
            ApiError,
            get_feature_options,
            crawl_configurations
        )

    @httpretty.activate
    def test_missing_features(self, get_botify_api_token_mock):
        get_botify_api_token_mock.return_value = "foo"
        httpretty.register_uri(httpretty.GET,
                               "http://api.foo.com/crawls/1001/config/",
                               body='{}',
                               content_type="application/json")
        crawl_configurations = [
            [1001, "http://api.foo.com/crawls/1001/config/", None]
        ]
        self.assertRaises(
            ApiFormatError,
            get_feature_options,
            crawl_configurations
        )

