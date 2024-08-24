"""QBUS Discovery."""
from __future__ import annotations
import json
import logging

_LOGGER = logging.getLogger(__name__)

KEY_DEVICES = "devices"

KEY_DEVICE_FUNCTIONBLOCKS = "functionBlocks"
KEY_DEVICE_ID = "id"
KEY_DEVICE_IP = "ip"
KEY_DEVICE_MAC = "mac"
KEY_DEVICE_NAME = "name"
KEY_DEVICE_SERIAL_NR = "serialNr"
KEY_DEVICE_TYPE = "type"

KEY_OUTPUT_ID = "id"
KEY_OUTPUT_TYPE = "type"
KEY_OUTPUT_NAME = "name"
KEY_OUTPUT_REF_ID = "ref_id"
KEY_OUTPUT_PROPERTIES = "properties"
KEY_OUTPUT_ACTIONS = "actions"

KEY_CONTROLLER_CONNECTABLE = "connectable"
KEY_CONTROLLER_CONNECTED = "connected"
KEY_CONTROLLER_ID = "id"
KEY_CONTROLLER_STATE_PROPERTIES = "properties"


class QbusMqttOutput:
    """Class for parsing MQTT discovered outputs for Qbus Home Automation."""
    
    def __init__(self, dict: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self._dict = dict

    @property
    def id(self) -> str:
        """Return the id."""
        return self._dict.get(KEY_OUTPUT_ID) or ""

    @property
    def type(self) -> str:
        """Return the type."""
        return self._dict.get(KEY_OUTPUT_TYPE) or ""

    @property
    def name(self) -> str:
        """Return the name."""
        return self._dict.get(KEY_OUTPUT_NAME) or ""

    @property
    def ref_id(self) -> str:
        """Return the ref id."""
        return self._dict.get(KEY_OUTPUT_REF_ID) or ""

    @property
    def properties(self) -> dict:
        """Return the properties."""
        return self._dict.get(KEY_OUTPUT_PROPERTIES) or {}

    @property
    def actions(self) -> dict:
        """Return the actions."""
        return self._dict.get(KEY_OUTPUT_ACTIONS) or {}

class QbusMqttDevice:
    """Class for parsing MQTT discovered devices for Qbus Home Automation."""
    
    def __init__(self, dict: dict) -> None:
        self._dict = dict
        self._outputs: list[QbusMqttOutput] = []
        self._connection_state: bool
        
    @property
    def id(self) -> str:
        """Return the id."""
        return self._dict.get(KEY_DEVICE_ID) or ""
    
    @property
    def ip(self) -> str:
        """Return the ip address."""
        return self._dict.get(KEY_DEVICE_IP) or ""
    
    @property
    def mac(self) -> str:
        """Return the ip address."""
        return self._dict.get(KEY_DEVICE_MAC) or ""
    
    @property
    def name(self) -> str:
        """Return the ip address."""
        return self._dict.get(KEY_DEVICE_NAME) or ""

    @property
    def serial_number(self) -> str:
        """Return the serial number."""
        return self._dict.get(KEY_DEVICE_SERIAL_NR) or ""

    @property
    def type(self) -> str:
        """Return the mac address."""
        return self._dict.get(KEY_DEVICE_TYPE) or ""
    
    @property
    def outputs(self) -> list[QbusMqttOutput]:
        """Return the outputs."""

        outputs: list[QbusMqttOutput] = []

        if self._dict.get(KEY_DEVICE_FUNCTIONBLOCKS):
            outputs = [QbusMqttOutput(x) for x in self._dict[KEY_DEVICE_FUNCTIONBLOCKS]]

        self._outputs = outputs
        return self._outputs

class QbusMqttControllerStateProperties:
    """MQTT representation a Qbus controller its state properties."""

    def __init__(self, dict: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self._dict = dict

    @property
    def connectable(self) -> bool | None:
        """Return True if the controller is connectable."""
        return self._dict.get(KEY_CONTROLLER_CONNECTABLE, None)

    @property
    def connected(self) -> bool | None:
        """Return True if the controller is connected."""
        return self._dict.get(KEY_CONTROLLER_CONNECTED, None)
   
class QbusMqttControllerState:
    """MQTT representation a Qbus controller state."""

    def __init__(self, dict: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self._dict = dict
        self._properties: QbusMqttControllerStateProperties | None = None

    @property
    def id(self) -> str | None:
        """Return the id."""
        return self._dict.get(KEY_CONTROLLER_ID)

    @property
    def properties(self) -> QbusMqttControllerStateProperties | None:
        """Return the properties."""

        if self._properties is not None:
            return self._properties

        properties: QbusMqttControllerStateProperties | None = None

        if self._dict.get(KEY_CONTROLLER_STATE_PROPERTIES):
            properties = QbusMqttControllerStateProperties(self._dict[KEY_CONTROLLER_STATE_PROPERTIES])

        self._properties = properties

        return self._properties   
    
class QbusMqttOutputState:
    """MQTT representation a Qbus output state."""

    def __init__(self, dict: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self._dict = dict

    @property
    def id(self) -> str:
        """Return the id."""
        return self._dict.get(KEY_OUTPUT_ID) or ""

    @property
    def type(self) -> str:
        """Return the type."""
        return self._dict.get(KEY_OUTPUT_TYPE) or ""

    @property
    def properties(self) -> dict | None:
        """Return the properties."""
        return self._dict.get(KEY_OUTPUT_PROPERTIES)
    
class QbusDiscovery:
    """Class for parsing MQTT discovery messages for Qbus Home Automation."""

    def __init__(self, config: dict) -> None:
        """Initialize."""
        self._config = config
        self._devices: list[QbusMqttDevice] = []
        self._hub_id = ""
        self._device_id = ""
        self._device_type = ""
        self._device_desc = ""
        self._name = ""
        self._owner_id = ""
        self._data_topic = ""
        self._command_topic = ""
           
    async def parse_discovery(self, discovery_topic: str, payload: str | bytes) -> bool:
        """Parse an MQTT discovery message and return True if successful."""
        try:
            json_data = json.loads(payload)
        except ValueError:
            _LOGGER.error(
                "Invalid DROP MQTT discovery payload on %s: %s",
                discovery_topic,
                payload,
            )
            return False
        
        # Extract the DROP hub ID and DROP device ID from the MQTT topic.
        topic_elements = discovery_topic.split("/")
        if not (
            topic_elements[2] == "config"
        ):
            return False
        
        # Discovery data must include the Qbus device type and name.
        if (
            KEY_DEVICES in json_data
        ):
            self._devices = json_data[KEY_DEVICES]
        else:
            _LOGGER.error(
                "Incomplete MQTT discovery payload on %s: %s", discovery_topic, payload
            )
            return False
        
        self._name = json_data["app"]
        return True
           
               
    @property
    def devices(self) -> list[QbusMqttDevice]:
        """Return the devices."""

        return self._devices    

    @property
    def name(self):
        """Return device name."""
        return self._name
     
    def get_device(self, serial: str) -> QbusMqttDevice | None:
        """Get the device by serial number."""
        for dev in self._devices:
            print(dev.serial_number)
        return next((x for x in self._devices if x.serial_number == serial), None)

    
    def get_state_topic(self, device_id: str) -> str:
        return "cloudapp/QBUSMQTTGW/" + device_id + "/state"