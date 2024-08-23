from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.event_created_webhook_v0_alpha import EventCreatedWebhookV0Alpha
from ..models.webhook_envelope_app import WebhookEnvelopeApp
from ..models.webhook_envelope_version import WebhookEnvelopeVersion
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebhookEnvelope")


@attr.s(auto_attribs=True, repr=False)
class WebhookEnvelope:
    """  """

    _app: WebhookEnvelopeApp
    _base_url: str
    _message: EventCreatedWebhookV0Alpha
    _tenant_id: str
    _version: WebhookEnvelopeVersion
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("app={}".format(repr(self._app)))
        fields.append("base_url={}".format(repr(self._base_url)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("tenant_id={}".format(repr(self._tenant_id)))
        fields.append("version={}".format(repr(self._version)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WebhookEnvelope({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        app = self._app.to_dict()

        base_url = self._base_url
        message = self._message.to_dict()

        tenant_id = self._tenant_id
        version = self._version.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if app is not UNSET:
            field_dict["app"] = app
        if base_url is not UNSET:
            field_dict["baseURL"] = base_url
        if message is not UNSET:
            field_dict["message"] = message
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_app() -> WebhookEnvelopeApp:
            app = WebhookEnvelopeApp.from_dict(d.pop("app"), strict=False)

            return app

        try:
            app = get_app()
        except KeyError:
            if strict:
                raise
            app = cast(WebhookEnvelopeApp, UNSET)

        def get_base_url() -> str:
            base_url = d.pop("baseURL")
            return base_url

        try:
            base_url = get_base_url()
        except KeyError:
            if strict:
                raise
            base_url = cast(str, UNSET)

        def get_message() -> EventCreatedWebhookV0Alpha:
            message = EventCreatedWebhookV0Alpha.from_dict(d.pop("message"), strict=False)

            return message

        try:
            message = get_message()
        except KeyError:
            if strict:
                raise
            message = cast(EventCreatedWebhookV0Alpha, UNSET)

        def get_tenant_id() -> str:
            tenant_id = d.pop("tenantId")
            return tenant_id

        try:
            tenant_id = get_tenant_id()
        except KeyError:
            if strict:
                raise
            tenant_id = cast(str, UNSET)

        def get_version() -> WebhookEnvelopeVersion:
            _version = d.pop("version")
            try:
                version = WebhookEnvelopeVersion(_version)
            except ValueError:
                version = WebhookEnvelopeVersion.of_unknown(_version)

            return version

        try:
            version = get_version()
        except KeyError:
            if strict:
                raise
            version = cast(WebhookEnvelopeVersion, UNSET)

        webhook_envelope = cls(
            app=app,
            base_url=base_url,
            message=message,
            tenant_id=tenant_id,
            version=version,
        )

        webhook_envelope.additional_properties = d
        return webhook_envelope

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def app(self) -> WebhookEnvelopeApp:
        if isinstance(self._app, Unset):
            raise NotPresentError(self, "app")
        return self._app

    @app.setter
    def app(self, value: WebhookEnvelopeApp) -> None:
        self._app = value

    @property
    def base_url(self) -> str:
        """ Base tenant URL from which the webhook is coming """
        if isinstance(self._base_url, Unset):
            raise NotPresentError(self, "base_url")
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        self._base_url = value

    @property
    def message(self) -> EventCreatedWebhookV0Alpha:
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: EventCreatedWebhookV0Alpha) -> None:
        self._message = value

    @property
    def tenant_id(self) -> str:
        """ Global tenant id from which webhook is coming """
        if isinstance(self._tenant_id, Unset):
            raise NotPresentError(self, "tenant_id")
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, value: str) -> None:
        self._tenant_id = value

    @property
    def version(self) -> WebhookEnvelopeVersion:
        """ Version of the webhook envelope shape. Always 0 for now. """
        if isinstance(self._version, Unset):
            raise NotPresentError(self, "version")
        return self._version

    @version.setter
    def version(self, value: WebhookEnvelopeVersion) -> None:
        self._version = value
