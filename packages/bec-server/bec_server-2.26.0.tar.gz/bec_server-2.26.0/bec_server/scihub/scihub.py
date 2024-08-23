from bec_lib import messages
from bec_lib.bec_service import BECService
from bec_lib.connector import ConnectorBase
from bec_lib.service_config import ServiceConfig
from bec_server.scihub.scibec import SciBecConnector
from bec_server.scihub.scilog import SciLogConnector
from bec_server.scihub.service_handler.service_handler import ServiceHandler


class SciHub(BECService):
    def __init__(self, config: ServiceConfig, connector_cls: ConnectorBase) -> None:
        super().__init__(config, connector_cls, unique_service=True)
        self.config = config
        self.scibec_connector = None
        self.scilog_connector = None
        self.service_handler = None
        self._start_scibec_connector()
        self._start_scilog_connector()
        self._start_service_handler()
        self.status = messages.BECStatus.RUNNING

    def _start_scibec_connector(self):
        self.wait_for_service("DeviceServer")
        self.scibec_connector = SciBecConnector(self, self.connector)

    def _start_scilog_connector(self):
        self.scilog_connector = SciLogConnector(self, self.connector)

    def _start_service_handler(self):
        self.service_handler = ServiceHandler(self.connector)
        self.service_handler.start()

    def shutdown(self):
        super().shutdown()
        if self.scibec_connector:
            self.scibec_connector.shutdown()
        if self.scilog_connector:
            self.scilog_connector.shutdown()
