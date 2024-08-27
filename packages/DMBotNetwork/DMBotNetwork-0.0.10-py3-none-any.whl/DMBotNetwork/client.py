import asyncio
import inspect
import logging
from asyncio import StreamReader, StreamWriter
from pathlib import Path
from typing import Any, Dict, Optional

import msgpack

logger = logging.getLogger("DMBotNetwork Client")

class Client:
    _net_methods: Dict[str, Any] = {}
    _host: Optional[str] = None
    _port: Optional[int] = None
    _login: Optional[str] = None
    _password: Optional[str] = None
    _server_file_path: Optional[Path] = None
    _reader: Optional[StreamReader] = None
    _writer: Optional[StreamWriter] = None
    _cur_server_name: Optional[str] = None
    _is_connected: bool = False
    _listen_task: Optional[asyncio.Task] = None

    def __init_subclass__(cls, **kwargs):
        """Автоматически регистрирует методы, начинающиеся с 'net_', как сетевые методы.

        Args:
            **kwargs: Дополнительные аргументы.
        """
        super().__init_subclass__(**kwargs)
        for method in dir(cls):
            if callable(getattr(cls, method)) and method.startswith("net_"):
                cls._net_methods[method[4:]] = getattr(cls, method)

    # Сеттеры и геттеры
    @classmethod
    def set_host(cls, host: str) -> None:
        cls._host = host

    @classmethod
    def get_host(cls) -> Optional[str]:
        return cls._host

    @classmethod
    def set_port(cls, port: int) -> None:
        cls._port = port

    @classmethod
    def get_port(cls) -> Optional[int]:
        return cls._port

    @classmethod
    def set_login(cls, login: str) -> None:
        cls._login = login

    @classmethod
    def get_login(cls) -> Optional[str]:
        return cls._login

    @classmethod
    def set_password(cls, password: str) -> None:
        cls._password = password

    @classmethod
    def get_password(cls) -> Optional[str]:
        return cls._password

    @classmethod
    def set_server_file_path(cls, path: Path) -> None:
        cls._server_file_path = path

    @classmethod
    def get_server_file_path(cls) -> Optional[Path]:
        return cls._server_file_path

    # Основные методы взаимодействия с сервером
    @classmethod
    async def connect(cls) -> None:
        """Устанавливает соединение с сервером."""
        if not cls._host or not cls._port:
            logger.error("Host and port must be set before connecting.")
            return

        try:
            cls._listen_task = asyncio.create_task(cls._connect_and_listen())
        
        except Exception as e:
            logger.error(f"Error creating connect task: {e}")

    @classmethod
    async def request_method(cls, spec_type: str, **kwargs) -> None:
        """Запрашивает выполнение метода на сервере.

        Args:
            spec_type (str): Указание метода, который нужно вызвать.

        Raises:
            ConnectionError: Если соединение с сервером не установлено.
        """
        if not cls._writer:
            raise ConnectionError("Not connected to server")

        request_data = {
            "action": "net",
            "type": spec_type,
            **kwargs
        }

        try:
            await cls._send_data(request_data)
        
        except Exception as e:
            logger.error(f"Error requesting method 'net.{spec_type}'. kwargs: '{kwargs}'. Error: {e}")

    @classmethod
    async def close_connection(cls) -> None:
        """Закрывает соединение с сервером."""
        await cls._close()

    # Вспомогательные методы работы с соединением
    @classmethod
    async def _connect_and_listen(cls) -> None:
        """Управляет процессом подключения и прослушивания сообщений в фоне."""
        try:
            cls._reader, cls._writer = await asyncio.open_connection(cls._host, cls._port)
            cls._is_connected = True
            
            await cls.listen_for_messages()
        
        except Exception as e:
            logger.error(f"Error in connection and listening: {e}")
            cls._is_connected = False
            await cls._close()

    @classmethod
    async def _send_data(cls, data: Any) -> None:
        """Отправляет данные на сервер.

        Args:
            data (Any): Данные для отправки.

        Raises:
            ConnectionError: Если соединение с сервером не установлено.
        """
        if not cls._writer:
            raise ConnectionError("Not connected to server")

        try:
            packed_data = msgpack.packb(data)
            cls._writer.write(len(packed_data).to_bytes(4, byteorder='big'))
            await cls._writer.drain()

            cls._writer.write(packed_data)
            await cls._writer.drain()
        
        except Exception as e:
            logger.error(f"Error sending data: {e}")

    @classmethod
    async def _receive_data(cls) -> Any:
        """Получает данные с сервера.

        Raises:
            ConnectionError: Если соединение с сервером не установлено.

        Returns:
            Any: Распакованные данные или None в случае ошибки.
        """
        if not cls._reader:
            raise ConnectionError("Not connected to server")

        try:
            data_size_bytes = await cls._reader.readexactly(4)
            data_size = int.from_bytes(data_size_bytes, 'big')

            packed_data = await cls._reader.readexactly(data_size)

            return msgpack.unpackb(packed_data)
        
        except asyncio.IncompleteReadError as e:
            logger.error(f"Connection closed while receiving data: {e}")
            await cls._close()
            return None

        except ConnectionResetError as e:
            logger.error(f"Connection reset by server: {e}")
            await cls._close()
            return None

        except Exception as e:
            logger.error(f"Unexpected error receiving data: {e}")
            await cls._close()
            return None

    @classmethod
    async def _close(cls) -> None:
        """Закрывает соединение с сервером."""
        if not cls._is_connected:
            logger.warning("Attempted to close connection, but no connection was established.")
            return
        
        cls._is_connected = False

        if cls._writer:
            try:
                cls._writer.close()
                await cls._writer.wait_closed()
            
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        if cls._listen_task:
            cls._listen_task.cancel()
            try:
                await cls._listen_task
            except asyncio.CancelledError:
                pass

    # Обработка сообщений от сервера
    @classmethod
    async def listen_for_messages(cls) -> None:
        """Слушает входящие сообщения от сервера и обрабатывает их."""
        while cls._is_connected:
            try:
                server_data = await cls._receive_data()
                if isinstance(server_data, dict):
                    processors = {
                        'action': cls._action_processor,
                        'req': cls._req_processor
                    }
                    
                    for key, processor in processors.items():
                        data_type = server_data.get(key, None)
                        if data_type:
                            await processor(data_type, server_data)
                            break
            
            except Exception as e:
                logger.error(f"Error in listen_for_messages: {e}")
                await cls._close()

    @classmethod
    async def _req_processor(cls, req_type, server_data: dict) -> None:
        if req_type == "auth":
            await cls._authenticate()

        else:
            logger.warning(f"Unexpected action type from server: {req_type}")

    @classmethod
    async def _action_processor(cls, action_type, server_data: dict) -> None:
        if action_type == 'log':
            cls.log_processor(server_data)
        
        elif action_type == 'net':
            await cls._call_method(cls._net_methods, server_data.get('type'), **server_data)
        
        else:
            logger.warning(f"Unexpected action type from server: {action_type}")

    @classmethod
    async def _call_method(cls, metods_dict: Dict[str, Any], method_name: str, **kwargs) -> Any:
        """Вызывает зарегистрированный метод по его имени.

        Args:
            metods_dict (Dict[str, Any]): Словарь, из которого будут вызываться методы.
            method_name (str): Имя метода для вызова.

        Returns:
            Any: Результат выполнения метода, если найден, иначе None.
        """
        method = metods_dict.get(method_name)
        if method is None:
            logger.error(f"Net method {method_name} not found.")
            return None

        sig = inspect.signature(method)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

        try:
            if inspect.iscoroutinefunction(method):
                return await method(cls, **valid_kwargs)
            else:
                return method(cls, **valid_kwargs)
        
        except Exception as e:
            logger.error(f"Error calling method {method_name}: {e}")
            return None

    @classmethod
    async def _authenticate(cls) -> None:
        """Аутентифицирует клиента на сервере.
        """
        try:
            await cls._send_data({
                "login": cls._login,
                "password": cls._password
            })
        
        except Exception as e:
            logger.error(f"Error during authentication: {e}")

    # Логирование
    @classmethod
    def log_processor(cls, server_data: dict) -> None:
        log_methods = {
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
            "debug": logger.debug,
            "critical": logger.critical,
        }
        log_type = server_data.get('log_type', 'not_set')
        log_method = log_methods.get(log_type)
        msg = server_data.get('msg', "empty")
        
        if log_method:
            log_method(msg)
        
        else:
            logger.warning(f"Unknown log_type: {log_type}. Message: {msg}")
