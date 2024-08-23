from shared_kernel.messaging.nats_databus import NATSDataBus
from shared_kernel.messaging.http_databus import HTTPDataBus
from shared_kernel.interfaces import DataBus


class DataBus:
    data_bus_classes = {"NATS": NATSDataBus, "HTTP": HTTPDataBus}

    @staticmethod
    def create_data_bus(bus_type: str, config: dict) -> DataBus:
        data_bus_class = DataBus.data_bus_classes.get(bus_type)
        if data_bus_class is None:
            raise ValueError(f"Unknown data bus type: {bus_type}")
        return data_bus_class(config)
