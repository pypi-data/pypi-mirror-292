from dig_ass_ep_protos.DigitalAssistantEntryPoint_pb2_grpc import (
    DigitalAssistantEntryPointStub,
)
from dig_ass_ep_protos.DigitalAssistantEntryPoint_pb2 import (
    DigitalAssistantEntryPointRequest,
    DigitalAssistantEntryPointResponse,
    OuterContextItem,
)

from agi_med_protos.abstract_client import AbstractClient


class EntryPointClient(AbstractClient):
    def __init__(self, address) -> None:
        super().__init__(address)
        self._stub = DigitalAssistantEntryPointStub(self._channel)

    def __call__(self, text: str, outer_context: dict, image=None, pdf=None):
        request = self.request2item(text, outer_context, image, pdf)
        response: DigitalAssistantEntryPointResponse = (
            self._stub.GetTextResponse(request)
        )
        return response.Text

    def get_json_response(self, text: str, outer_context: dict, image=None, pdf=None):
        request = self.request2item(text, outer_context, image, pdf)
        response: DigitalAssistantEntryPointResponse = (
            self._stub.GetTextResponse(request)
        )
        return self.response2dict(response)
    
    @staticmethod 
    def response2dict(response: DigitalAssistantEntryPointResponse) -> dict:
        return {
            'Text': response.Text,
            'Results': [{
                'Diagnosis': result.Diagnosis, 
                'Doctors': result.Doctors,
            } for result in response.Results]
        }

    @staticmethod
    def request2item(text: str, outer_context: dict, image=None, pdf=None) -> DigitalAssistantEntryPointRequest:
        outer_context_item = OuterContextItem(
                Sex=outer_context['Sex'],
                Age=outer_context['Age'],
                UserId=outer_context['UserId'],
                SessionId=outer_context['SessionId'],
                ClientId=outer_context['ClientId'],
                TrackId=outer_context.get('TrackId', '')
            )
        return DigitalAssistantEntryPointRequest(
                Text=text,
                OuterContext=outer_context_item,
                Image=image,
                PDF=pdf,
            )
