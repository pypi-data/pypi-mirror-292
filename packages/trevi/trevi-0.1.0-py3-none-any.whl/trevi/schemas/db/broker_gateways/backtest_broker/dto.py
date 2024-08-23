import abc

from protos.rome.services import broker_gateway_pb2
from schemas.db.broker_gateways.backtest_broker import models


class DtoMapper(metaclass=abc.ABCMeta):
    @abc.abstractstaticmethod
    def from_proto(proto):
        raise NotImplementedError

    @abc.abstractstaticmethod
    def to_proto(obj):
        raise NotImplementedError


class OrderMapper(DtoMapper):
    @staticmethod
    def from_proto(order: broker_gateway_pb2.Order) -> models.Order:
        return models.Order(content=order.SerializeToString())

    @staticmethod
    def to_proto(order: models.Order) -> broker_gateway_pb2.Order:
        proto_order = broker_gateway_pb2.Order()
        proto_order.ParseFromString(order.content)
        return proto_order
