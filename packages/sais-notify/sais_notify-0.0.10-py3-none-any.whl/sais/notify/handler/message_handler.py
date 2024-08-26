import logging

from sais.notify.auth.auth_info import EnvVarCredentialsProvider
from sais.notify.clients.notify_client import NotifyClient
from sais.notify.config import const
from sais.notify.config.const import ENDPOINT, NOTIFY_SERVICE_NOTIFY_TYPE_FEISHU, \
    NOTIFY_SERVICE_NOTIFY_TYPE_FEISHU_GROUP, LOGGER_NAME, NOTIFY_SERVICE_NOTIFY_TYPE_EMAIL, \
    NOTIFY_SERVICE_NOTIFY_TYPE_SMS
from sais.notify.model.message_model import NotificationRequest, MessageModel
from sais.notify.types import NotifyType

logger = logging.getLogger(LOGGER_NAME)
logging.basicConfig(level=logging.INFO)


class MessageHandler(object):
    def __init__(self, auth_provider: EnvVarCredentialsProvider):
        self.auth_provider = auth_provider

    def send_notification(self, notify_type: NotifyType, to: str, message: str, subject: str = None,
                          sign_name: str = None, template_code: str = None) -> bool:
        """
        发送通知的函数。

        参数:
        - notify_type: 通知类型，枚举类型NotifyType指定。
        - to: 接收通知的目标标识，可以是用户或群组的标识。
        - message: 要发送的消息内容。

        返回值:
        - bool: 发送成功返回True，失败返回False。
        """
        logger.info(f'info send notification: {notify_type}, {to}, {message}')
        logger.debug(f'debug send notification: {notify_type}, {to}, {message}')
        request = NotificationRequest(notify_type=notify_type, to=to, message=message)
        request.model_dump()
        if notify_type in (NotifyType.FEISHU_USER_TEXT, NotifyType.FEISHU_USER_RICH_TEXT,
                           NotifyType.FEISHU_GROUP_TEXT, NotifyType.FEISHU_GROUP_MESSAGE_CARD):
            return self.__send_notification_feishu(notify_type, to, message)
        elif notify_type == NotifyType.EMAIL:
            return self.__send_notification_email(to, message, subject)
        elif notify_type == NotifyType.SMS:
            return self.__send_notification_sms(sign_name, template_code, to, message)
        else:
            logger.error(f'not support notify type: {notify_type}')
        return False

    def __send_notification_feishu(self, notify_type: NotifyType, to: str, message: str) -> bool:
        client = NotifyClient(ENDPOINT, self.auth_provider)
        message_model = MessageModel(
            message=message,
            to=to,
            type={
                NotifyType.FEISHU_USER_TEXT: NOTIFY_SERVICE_NOTIFY_TYPE_FEISHU,
                NotifyType.FEISHU_USER_RICH_TEXT: NOTIFY_SERVICE_NOTIFY_TYPE_FEISHU,
                NotifyType.FEISHU_GROUP_TEXT: NOTIFY_SERVICE_NOTIFY_TYPE_FEISHU_GROUP,
                NotifyType.FEISHU_GROUP_MESSAGE_CARD: NOTIFY_SERVICE_NOTIFY_TYPE_FEISHU_GROUP,
            }.get(notify_type, None)
        )

        robot_name = const.SAIS_ROBOT_NAME if notify_type == NotifyType.FEISHU_USER_RICH_TEXT else None
        message_model.robot_name = robot_name

        if message_model.type is None:
            logger.error(f'not support notify type: {notify_type}')
            return False

        return client.send_notification(message_model)

    def __send_notification_email(self, to: str, message: str, subject: str) -> bool:
        client = NotifyClient(ENDPOINT, self.auth_provider)
        message_model = MessageModel(
            subject=subject,
            message=message,
            to=to,
            type=NOTIFY_SERVICE_NOTIFY_TYPE_EMAIL
        )

        return client.send_notification(message_model)

    def __send_notification_sms(self, sign_name: str, template_code: str, to: str, message: str) -> bool:
        client = NotifyClient(ENDPOINT, self.auth_provider)
        message_model = MessageModel(
            message=message,
            to=to,
            type=NOTIFY_SERVICE_NOTIFY_TYPE_SMS
        )
        message_model.sign_name = sign_name
        message_model.template_code = template_code
        return client.send_notification(message_model)
