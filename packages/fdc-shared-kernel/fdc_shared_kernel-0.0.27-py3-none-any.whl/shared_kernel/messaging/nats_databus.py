import json
import logging
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig, ConsumerConfig, DeliverPolicy
from typing import Callable, Any, List, Union, Dict
from shared_kernel.interfaces import DataBus

logging.getLogger().setLevel(logging.INFO)


class NATSDataBus(DataBus):
    """
    A NATS interface class to handle both standard NATS and JetStream operations.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NATSDataBus, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict = None):
        """
        Initialize the NATSDataBus.

        Args:
            config (Dict): A dictionary containing the NATS configuration.
        """
        if not hasattr(self, "initialized"):  # Prevent reinitialization
            super().__init__()
            self.nc = NATS()
            self.servers = config.get('servers')
            self.user = config.get('user')
            self.password = config.get('password')
            self.connected = False
            self.js = None  # JetStream context
            self.initialized = True
            self.stream_name = config.get('stream_name', '')
            self.event_names = config.get('event_names', [])

            if self.stream_name and self.event_names:
                self.create_stream(self.stream_name, self.event_names)

    async def make_connection(self):
        """
        Connect to the NATS server.
        """
        if not self.connected:
            await self.nc.connect(
                servers=self.servers,
                user=self.user,
                password=self.password
            )
            self.js = self.nc.jetstream(timeout=10)
            self.connected = True

    async def close_connection(self):
        """
        Close the connection to the NATS server.
        """
        if self.connected:
            try:
                await self.nc.close()
                self.connected = False
            except Exception as e:
                raise e

    async def create_stream(self, stream_name: str, event_names: List[Any]):
        """
        Create a stream for event names to persist the messages.

        Args:
            stream_name (str): The name of the stream.
            event_names (List[Any]): The subjects whose messages will be persisted.
        """
        try:
            self.stream_name = stream_name
            # Check if the stream already exists
            await self.js.stream_info(stream_name)
            logging.info(f"Stream '{stream_name}' already exists.")
        except Exception:
            # Stream does not exist, so create it
            stream_config = StreamConfig(
                name=stream_name,
                subjects=event_names,
                max_age=600  # Retain messages for 10 minutes
            )
            await self.js.add_stream(stream_config)
            logging.info(f"Stream '{stream_name}' created.")

    async def publish_event(
            self, event_name: str, event_payload: dict
    ) -> Union[bool, Exception]:
        """
        Publish a message to a JetStream subject.

        Args:
            event_name (str): The subject to publish the message to.
            event_payload (dict): The message to be published.

        Returns:
            bool: True if the event was published successfully.
        """
        ack = await self.js.publish(
            event_name, json.dumps(event_payload).encode("utf-8")
        )
        logging.info(
            f"Published event '{event_payload.get('event_name')}' to subject '{event_name}', ack: {ack}"
        )
        return True

    async def request_event(
            self, event_name: str, event_payload: dict, timeout: float = 10.0
    ) -> Union[dict, Exception]:
        """
        Send a request and wait for a response.

        Args:
            event_name (str): The subject to publish the message to.
            event_payload (dict): The message to be published.
            timeout (float): The timeout for the request.

        Returns:
            dict: The response message.
        """
        response = await self.nc.request(
            event_name, json.dumps(event_payload).encode("utf-8"), timeout=timeout
        )
        return json.loads(response.data.decode("utf-8"))

    async def subscribe_async_event(
            self, event_name: str, callback: Callable[[Any], None], durable_name: str
    ):
        """
        Subscribe to a JetStream subject with a durable consumer and process messages asynchronously.

        Args:
            event_name (str): The subject to subscribe to.
            callback (Callable[[Any], None]): A callback function to handle received messages.
            durable_name (str): The name of the durable consumer.
        """
        try:
            # Check if the consumer already exists
            await self.js.consumer_info(stream=self.stream_name, name=durable_name)
            logging.info(f"Consumer '{durable_name}' already exists.")
        except Exception:
            # Consumer does not exist, so create it
            self.consumer_config = ConsumerConfig(
                name=durable_name,
                durable_name=durable_name,
                deliver_policy=DeliverPolicy.ALL,
                deliver_subject=durable_name,
                max_deliver=1
            )
            await self.js.add_consumer(stream=self.stream_name, config=self.consumer_config)
            logging.info(f"Consumer '{durable_name}' created.")

        await self.js.subscribe_bind(
            stream=self.stream_name, cb=callback, config=self.consumer_config,
            consumer=durable_name
        )
        logging.info(f"Subscribed to async event on subject '{event_name}'")

    async def subscribe_sync_event(self, event_name: str, callback: Callable[[Any], None]):
        """
        Subscribe to a NATS subject and process the message synchronously.

        Args:
            event_name (str): The subject to subscribe to.
            callback (Callable[[Any], None]): A callback function to handle received messages.
        """
        await self.nc.subscribe(event_name, cb=callback)
        logging.info(f"Subscribed to sync event on subject '{event_name}'")

    def delete_message(self, receipt_handle: str):
        pass
