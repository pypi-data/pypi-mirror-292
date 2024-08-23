import json
from datetime import datetime
from http import HTTPStatus
from typing import List

import requests
from python_sdk_remote.utilities import our_get_env
from logger_local.MetaLogger import MetaLogger
from message_local.MessageLocal import MessageLocal
from message_local.Recipient import Recipient
from python_sdk_remote.http_response import create_authorization_http_headers

from .WhatsAppLocalConstants import (WHATSAPP_API_URL,
                                     WHATSAPP_MESSAGE_INFORU_API_TYPE_ID,
                                     get_logger_object)

# TODO Change the environment name to start with "IS_"
# TODO Shall we combine both into our_get_env in case it starts with "IS_"
REALLY_SEND_WHATSAPP = our_get_env("REALLY_SEND_WHATSAPP", "false")
REALLY_SEND_WHATSAPP = REALLY_SEND_WHATSAPP and REALLY_SEND_WHATSAPP.lower() in ("1", "true")

# TODO We should get the Auth Token from user_external of effective_profile_id
INFORU_AUTH_TOKEN = our_get_env("INFORU_AUTH_TOKEN", raise_if_not_found=REALLY_SEND_WHATSAPP)


class WhatsAppMessageInforuLocal(MessageLocal, metaclass=MetaLogger, object=get_logger_object()):
    """Assuming the usage is as follows:
    message_local = MessageLocal(...)
    message_local.__class__ = WhatsAppMessageInforuLocal
    message_local.__init__()  # calling the "init" of WhatsAppMessageInforuLocal
    message_local.send(...)  # calling the "send" of WhatsAppMessageInforuLocal
    """

    def __init__(self, **kwargs) -> None:  # noqa
        # Don't call super().__init__(), we already have the message_local object
        self._api_type_id = WHATSAPP_MESSAGE_INFORU_API_TYPE_ID  # used by MessageLocal

    def send(self, body: str = None, compound_message_dict: dict = None,
             recipients: List[Recipient] = None, cc: List[Recipient] = None, bcc: List[Recipient] = None,
             scheduled_timestamp_start: datetime = None,
             scheduled_timestamp_end: datetime = None, **kwargs) -> dict:  # TODO: return ids
        recipients = recipients or self.get_recipients()
        # Can also add: "FirstName", "LastName", "CouponCode", "MessageMedia"
        recipients_details = [{"Phone": recipient.get_phone_number_full_normalized()}
                              for recipient in recipients]
        # TODO: should we POST for each recipient or can we use the same message for all of them?
        # self.get_body_after_text_template(...)
        message_media = kwargs.get("message_media")
        payload = {
            "Data": {
                "Message": body,
                "Recipients": recipients_details
            }
        }
        if message_media:
            payload["Data"]["messageMedia"] = message_media
        url = WHATSAPP_API_URL

        payload_json = json.dumps(payload)
        if (REALLY_SEND_WHATSAPP and
                self.can_send(api_data=payload, outgoing_body=payload)):
            headers = create_authorization_http_headers(INFORU_AUTH_TOKEN)
            # TODO Can we change the requests.post with a call to api_management direct via message-local?
            response = requests.post(url, headers=headers, json=payload_json)
            self.after_send_attempt(outgoing_body=payload,
                                    incoming_message=response.json(),
                                    http_status_code=response.status_code,
                                    response_body=response.text)
        else:
            print("Supposed to send the following payload to InforU: " + payload_json)
            return {"status": "success", "message": "Message sent successfully"}

        # Check the response using HTTPStatus.OK from the http library.
        if response.status_code == HTTPStatus.OK:
            self.logger.info("Request Payload: " + json.dumps(payload))
            self.logger.info("Request Headers: " + str(headers))
            self.logger.info("Response Status Code: " + str(response.status_code))
            self.logger.info("Response Content: " + response.text)
            self.logger.info(f"WhatsApp sent successfully to {recipients_details}.")
            self.logger.info("Response: " + response.text)
        else:
            self.logger.error(
                f"SMS sending failed to {recipients_details} with status code: {response.status_code}")

        # Assuming the function returns a dictionary with some data
        return {"status": "success", "message": "Message sent successfully"}
