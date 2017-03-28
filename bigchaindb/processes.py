import logging
import multiprocessing as mp

import bigchaindb
from bigchaindb.pipelines import vote, block, election, stale
from bigchaindb.pipelines.events_consumer_example import events_consumer
from bigchaindb.events import setup_events_queue
from bigchaindb.web import server


logger = logging.getLogger(__name__)

BANNER = """
****************************************************************************
*                                                                          *
*   Initialization complete. BigchainDB Server is ready and waiting.       *
*   You can send HTTP requests via the HTTP API documented in the          *
*   BigchainDB Server docs at:                                             *
*    https://bigchaindb.com/http-api                                       *
*                                                                          *
*   Listening to client connections on: {:<15}                    *
*                                                                          *
****************************************************************************
"""


def start():
    logger.info('Initializing BigchainDB...')

    # Create the events queue
    # The events queue needs to be initialized once and shared between
    # processes. This seems the best way to do it
    # At this point only the election processs and the event consumer require
    # this queue.
    events_queue = setup_events_queue()

    # start the processes
    logger.info('Starting block')
    block.start()

    logger.info('Starting voter')
    vote.start()

    logger.info('Starting stale transaction monitor')
    stale.start()

    logger.info('Starting election')
    election.start(events_queue)

    # start the web api
    app_server = server.create_server(bigchaindb.config['server'])
    p_webapi = mp.Process(name='webapi', target=app_server.run)
    p_webapi.start()

    # start the example events consumer
    logger.info('Starting the events consumer example')
    p_events_consumer = events_consumer(events_queue)
    p_events_consumer.start()

    # start message
    logger.info(BANNER.format(bigchaindb.config['server']['bind']))
