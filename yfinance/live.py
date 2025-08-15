import asyncio
import base64
import json
from typing import List, Optional, Callable, Union

from websockets.sync.client import connect as sync_connect
from websockets.asyncio.client import connect as async_connect

from yfinance import utils
from yfinance.pricing_pb2 import PricingData
from google.protobuf.json_format import MessageToDict


class BaseWebSocket:
    """WebSocket客户端的基类。"""
    def __init__(self, url: str = "wss://streamer.finance.yahoo.com/?version=2", verbose=True):
        self.url = url
        self.verbose = verbose
        self.logger = utils.get_yf_logger()
        self._ws = None
        self._subscriptions = set()
        self._subscription_interval = 15  # seconds

    def _decode_message(self, base64_message: str) -> dict:
        """解码base64编码的消息。"""
        try:
            decoded_bytes = base64.b64decode(base64_message)
            pricing_data = PricingData()
            pricing_data.ParseFromString(decoded_bytes)
            return MessageToDict(pricing_data, preserving_proto_field_name=True)
        except Exception as e:
            self.logger.error("Failed to decode message: %s", e, exc_info=True)
            if self.verbose:
                print("Failed to decode message: %s", e)
            return {
                'error': str(e),
                'raw_base64': base64_message
            }


class AsyncWebSocket(BaseWebSocket):
    """
    用于流式传输实时定价数据的异步WebSocket客户端。
    """

    def __init__(self, url: str = "wss://streamer.finance.yahoo.com/?version=2", verbose=True):
        """
        初始化AsyncWebSocket客户端。

        参数:
            url (str): WebSocket服务器URL。默认为Yahoo Finance的WebSocket URL。
            verbose (bool): 是否启用或禁用打印语句的标志。默认为True。
        """
        super().__init__(url, verbose)
        self._message_handler = None  # 用于处理消息的可调用对象
        self._heartbeat_task = None  # 用于发送心跳订阅的任务

    async def _connect(self):
        """连接到WebSocket服务器。"""
        try:
            if self._ws is None:
                self._ws = await async_connect(self.url)
                self.logger.info("Connected to WebSocket.")
                if self.verbose:
                    print("Connected to WebSocket.")
        except Exception as e:
            self.logger.error("Failed to connect to WebSocket: %s", e, exc_info=True)
            if self.verbose:
                print(f"Failed to connect to WebSocket: {e}")
            self._ws = None
            raise

    async def _periodic_subscribe(self):
        """定期发送订阅消息以保持连接活动。"""
        while True:
            try:
                await asyncio.sleep(self._subscription_interval)

                if self._subscriptions:
                    message = {"subscribe": list(self._subscriptions)}
                    await self._ws.send(json.dumps(message))

                    if self.verbose:
                        print(f"Heartbeat subscription sent for symbols: {self._subscriptions}")
            except Exception as e:
                self.logger.error("Error in heartbeat subscription: %s", e, exc_info=True)
                if self.verbose:
                    print(f"Error in heartbeat subscription: {e}")
                break

    async def subscribe(self, symbols: Union[str, List[str]]):
        """
        订阅一个或多个股票代码。

        参数:
            symbols (Union[str, List[str]]): 要订阅的股票代码。
        """
        await self._connect()

        if isinstance(symbols, str):
            symbols = [symbols]

        self._subscriptions.update(symbols)

        message = {"subscribe": list(self._subscriptions)}
        await self._ws.send(json.dumps(message))

        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._periodic_subscribe())

        self.logger.info(f"Subscribed to symbols: {symbols}")
        if self.verbose:
            print(f"Subscribed to symbols: {symbols}")

    async def unsubscribe(self, symbols: Union[str, List[str]]):
        """
        取消订阅一个或多个股票代码。

        参数:
            symbols (Union[str, List[str]]): 要取消订阅的股票代码。
        """
        await self._connect()

        if isinstance(symbols, str):
            symbols = [symbols]

        self._subscriptions.difference_update(symbols)

        message = {"unsubscribe": symbols}
        await self._ws.send(json.dumps(message))

        self.logger.info(f"Unsubscribed from symbols: {symbols}")
        if self.verbose:
            print(f"Unsubscribed from symbols: {symbols}")

    async def listen(self, message_handler=None):
        """
        开始监听来自WebSocket服务器的消息。

        参数:
            message_handler (Optional[Callable[[dict], None]]): 用于处理接收到的消息的可选函数。
        """
        await self._connect()
        self._message_handler = message_handler

        self.logger.info("Listening for messages...")
        if self.verbose:
            print("Listening for messages...")

        if self._heartbeat_task is None:
            self._heartbeat_task = asyncio.create_task(self._periodic_subscribe())

        while True:
            try:
                async for message in self._ws:
                    message_json = json.loads(message)
                    encoded_data = message_json.get("message", "")
                    decoded_message = self._decode_message(encoded_data)

                    if self._message_handler:
                        try:
                            if asyncio.iscoroutinefunction(self._message_handler):
                                await self._message_handler(decoded_message)
                            else:
                                self._message_handler(decoded_message)
                        except Exception as handler_exception:
                            self.logger.error("Error in message handler: %s", handler_exception, exc_info=True)
                            if self.verbose:
                                print("Error in message handler:", handler_exception)
                    else:
                        print(decoded_message)

            except (KeyboardInterrupt, asyncio.CancelledError):
                self.logger.info("WebSocket listening interrupted. Closing connection...")
                if self.verbose:
                    print("WebSocket listening interrupted. Closing connection...")
                await self.close()
                break

            except Exception as e:
                self.logger.error("Error while listening to messages: %s", e, exc_info=True)
                if self.verbose:
                    print("Error while listening to messages: %s", e)

                self.logger.info("Attempting to reconnect...")
                if self.verbose:
                    print("Attempting to reconnect...")
                await asyncio.sleep(3)
                await self._connect()

    async def close(self):
        """关闭WebSocket连接。"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._ws is not None:
            await self._ws.close()
            self.logger.info("WebSocket connection closed.")
            if self.verbose:
                print("WebSocket connection closed.")

    async def __aenter__(self):
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


class WebSocket(BaseWebSocket):
    """
    用于流式传输实时定价数据的同步WebSocket客户端。
    """

    def __init__(self, url: str = "wss://streamer.finance.yahoo.com/?version=2", verbose=True):
        """
        初始化WebSocket客户端。

        参数:
            url (str): WebSocket服务器URL。默认为Yahoo Finance的WebSocket URL。
            verbose (bool): 是否启用或禁用打印语句的标志。默认为True。
        """
        super().__init__(url, verbose)

    def _connect(self):
        """连接到WebSocket服务器。"""
        try:
            if self._ws is None:
                self._ws = sync_connect(self.url)
                self.logger.info("Connected to WebSocket.")
                if self.verbose:
                    print("Connected to WebSocket.")
        except Exception as e:
            self.logger.error("Failed to connect to WebSocket: %s", e, exc_info=True)
            if self.verbose:
                print(f"Failed to connect to WebSocket: {e}")
            self._ws = None
            raise

    def subscribe(self, symbols: Union[str, List[str]]):
        """
        订阅一个或多个股票代码。

        参数:
            symbols (Union[str, List[str]]): 要订阅的股票代码。
        """
        self._connect()

        if isinstance(symbols, str):
            symbols = [symbols]

        self._subscriptions.update(symbols)

        message = {"subscribe": list(self._subscriptions)}
        self._ws.send(json.dumps(message))

        self.logger.info(f"Subscribed to symbols: {symbols}")
        if self.verbose:
            print(f"Subscribed to symbols: {symbols}")

    def unsubscribe(self, symbols: Union[str, List[str]]):
        """
        取消订阅一个或多个股票代码。

        参数:
            symbols (Union[str, List[str]]): 要取消订阅的股票代码。
        """
        self._connect()

        if isinstance(symbols, str):
            symbols = [symbols]

        self._subscriptions.difference_update(symbols)

        message = {"unsubscribe": symbols}
        self._ws.send(json.dumps(message))

        self.logger.info(f"Unsubscribed from symbols: {symbols}")
        if self.verbose:
            print(f"Unsubscribed from symbols: {symbols}")

    def listen(self, message_handler: Optional[Callable[[dict], None]] = None):
        """
        开始监听来自WebSocket服务器的消息。

        参数:
            message_handler (Optional[Callable[[dict], None]]): 用于处理接收到的消息的可选函数。
        """
        self._connect()

        self.logger.info("Listening for messages...")
        if self.verbose:
            print("Listening for messages...")

        while True:
            try:
                message = self._ws.recv()
                message_json = json.loads(message)
                encoded_data = message_json.get("message", "")
                decoded_message = self._decode_message(encoded_data)

                if message_handler:
                    try:
                        message_handler(decoded_message)
                    except Exception as handler_exception:
                        self.logger.error("Error in message handler: %s", handler_exception, exc_info=True)
                        if self.verbose:
                            print("Error in message handler:", handler_exception)
                else:
                    print(decoded_message)

            except KeyboardInterrupt:
                if self.verbose:
                    print("Received keyboard interrupt.")
                self.close()
                break

            except Exception as e:
                self.logger.error("Error while listening to messages: %s", e, exc_info=True)
                if self.verbose:
                    print("Error while listening to messages: %s", e)
                break

    def close(self):
        """关闭WebSocket连接。"""
        if self._ws is not None:
            self._ws.close()
            self.logger.info("WebSocket connection closed.")
            if self.verbose:
                print("WebSocket connection closed.")

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
