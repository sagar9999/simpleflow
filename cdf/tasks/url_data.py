import os
import gzip
import itertools
import ujson as json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from cdf.log import logger
from cdf.metadata.url import ELASTICSEARCH_BACKEND
from cdf.utils.s3 import fetch_files, push_file
from cdf.core.streams.caster import Caster
from cdf.metadata.raw import STREAMS_HEADERS, STREAMS_FILES
from cdf.analysis.urls.generators.documents import UrlDocumentGenerator
from cdf.core.streams.utils import split_file
from .decorators import TemporaryDirTask as with_temporary_dir
from .constants import DEFAULT_FORCE_FETCH


def prepare_crawl_index(crawl_id, es_location, es_index, es_doc_type='urls',
                        es_nb_shards=10, es_nb_replicas=1, es_refresh='1m'):
    """Prepare an ElasticSearch index

    :param crawl_id: unique id of the user crawl
    :param es_location: ElasticSearch location (ex: http://localhost:9200)
    :param es_index: ElasticSearch index name
    :param es_doc_type: ElasticSearch doc_type, defaults to `urls`
    :param es_nb_shards: shard number of the index to be created
    :param es_nb_replicas: replica number
    :param es_refresh: refresh interval, in minutes
    """
    host, port = es_location[7:].split(':')
    es = Elasticsearch([{'host': host, 'port': int(port)}])

    if es.indices.exists(es_index):
        logger.info("Index {} already exists".format(es_index))
        return

    settings = ELASTICSEARCH_BACKEND.index_settings(
        es_nb_shards, es_nb_replicas, es_refresh)

    try:
        es.indices.create(es_index, body=settings)
    except Exception, e:
        logger.error("{} : {}".format(type(e), str(e)))
    es.indices.put_mapping(es_index, es_doc_type,
                           ELASTICSEARCH_BACKEND.mapping())


@with_temporary_dir
def push_documents_to_elastic_search(s3_uri, part_id,
                                     es_location, es_index, es_doc_type,
                                     tmp_dir=None,
                                     force_fetch=DEFAULT_FORCE_FETCH):
    """Push pre-generated url documents to ElasticSearch

    :param s3_uri: s3 bucket uri for the crawl in processing
    :param part_id: part_id of the crawl, could be a list or an int
    :param es_location: ES location, eg. `http://location_url:9200`
    :param es_index: index name
    :param es_doc_type: doc type in the index
    :param tmp_dir: temporary directory for processing
    """
    host, port = es_location[7:].split(':')
    es = Elasticsearch([{'host': host, 'port': int(port)}])
    docs_uri = os.path.join(s3_uri, 'documents')

    part_ids = part_id if isinstance(part_id, list) else [part_id]
    fetch_regexp = ['url_documents.json.%d.gz' % i for i in part_ids]

    files_fetched = fetch_files(docs_uri, tmp_dir,
                                regexp=fetch_regexp,
                                force_fetch=force_fetch)

    reader = itertools.chain(*[gzip.open(f[0], 'r') for f in files_fetched])

    docs = []
    for i, line in enumerate(reader):
        docs.append(json.loads(line))
        if i % 3000 == 0:
            logger.info('{} items pushed to ES index {} for part {}'.format(
                i, es_index, part_id))
            bulk(es, docs, doc_type=es_doc_type, index=es_index)
            docs = []
    if len(docs) > 0:
        bulk(es, docs, doc_type=es_doc_type, index=es_index)


@with_temporary_dir
def generate_documents(crawl_id, part_id, s3_uri,
                       tmp_dir=None, force_fetch=DEFAULT_FORCE_FETCH):
    """Generate JSON type urls documents from a crawl's `part_id`

    Crawl dataset for this part_id is found by fetching all files finishing
    by .txt.[part_id] in the `s3_uri` called.

    :param part_id : part_id of the crawl
    :param s3_uri : location where raw files are fetched
    :param tmp_dir : temporary directory where the S3 files are fetched to
        compute the task
    :param force_fetch : fetch the S3 files even if they are already in the
        temp directory
    """

    # Fetch locally the files from S3
    files_fetched = fetch_files(s3_uri, tmp_dir,
                                regexp=['url(ids|infos|links|inlinks|contents|' +
                                        'contentsduplicate|_suggested_clusters|' +
                                        'badlinks).txt.%d.gz' % part_id],
                                force_fetch=force_fetch)
    streams = {}

    for path_local, fetched in files_fetched:
        stream_identifier = STREAMS_FILES[os.path.basename(path_local).split('.')[0]]
        cast = Caster(STREAMS_HEADERS[stream_identifier.upper()]).cast

        if stream_identifier == "patterns":
            stream_patterns = cast(split_file(gzip.open(path_local)))
        else:
            streams[stream_identifier] = cast(split_file(gzip.open(path_local)))

    g = UrlDocumentGenerator(stream_patterns, **streams)

    output_name = 'url_documents.json.{}.gz'.format(part_id)
    with gzip.open(os.path.join(tmp_dir, output_name), 'w') as output:
        for i, document in enumerate(g):
            document[1]['crawl_id'] = crawl_id
            document[1]['_id'] = '{}:{}'.format(crawl_id, document[0])
            output.write(json.dumps(document[1]) + '\n')

            if i % 3000 == 0:
                logger.info('Generated {} documents in {}'.format(
                    i, output_name))

    logger.info('Pushing {}'.format(output_name))
    docs_uri = os.path.join(s3_uri, 'documents')
    push_file(
        os.path.join(docs_uri, output_name),
        os.path.join(tmp_dir, output_name),
    )