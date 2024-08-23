from google.protobuf.message import Message

from google.protobuf.descriptor_pb2 import FileDescriptorSet, FileDescriptorProto
from google.protobuf.descriptor import FileDescriptor

from google.protobuf.message import Message
from google.protobuf.json_format import ParseDict
import yaml


class ProtoUtils:

    @staticmethod
    def serialize(x):
        return x.SerializeToString()

    @staticmethod
    def deserialize(t, x):
        t.ParseFromString(x)
        return t

    @staticmethod
    def read_conf(filepath, conf):
        with open(filepath, "r") as yaml_in:
            ParseDict(yaml.safe_load(yaml_in), conf)
            return conf

    @staticmethod
    def create_file_descriptor_proto(msg: Message):
        fdsProto = FileDescriptorSet()

        descriptor = msg.DESCRIPTOR
        fds = set([])

        def generate_ds(fd: FileDescriptor):
            proto = FileDescriptorProto()
            fd.CopyToProto(proto)
            fdsProto.file.append(proto)
            for dep in fd.public_dependencies:
                if dep not in fds:
                    fds.add(dep)
                    generate_ds(dep)

            for dep in fd.dependencies:
                if dep not in fds:
                    fds.add(dep)
                    generate_ds(dep)

        generate_ds(descriptor.file)

        return fdsProto