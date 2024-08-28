#!/usr/bin/env python3
import base64
import gzip
import os
import sys
import tempfile
from dataclasses import dataclass
from google.protobuf.descriptor import Descriptor, FileDescriptor
from google.protobuf.descriptor_pb2 import (
    FileDescriptorProto,
    FileDescriptorSet,
)
from grpc_tools import protoc as grpc_tools_protoc
from importlib import resources
from resemble.cli import terminal
from resemble.cli.directories import chdir
from resemble.protoc_gen_resemble_generic import (
    BaseFile,
    BaseMethod,
    BaseMethodOptions,
    BaseService,
    BaseServiceOptions,
    PluginSpecificData,
    ProtoType,
    UserProtoError,
)
from resemble.protoc_gen_resemble_python import (
    PythonResembleProtocPlugin,
    PythonType,
)
from resemble.protoc_gen_resemble_typescript import (
    TypescriptResembleProtocPlugin,
)
from typing import Optional, Sequence


def protoc(file: FileDescriptor) -> tuple[str, str]:
    """Helper for generating *_pb2.py and *_pb2_grpc.py files that we
    embed within the *_rsm.ts generated files.
    """
    protoc_args: list[str] = ["grpc_tool.protoc"]

    # We want to find the Python `site-packages`/`dist-packages` directories
    # that contain a 'resemble/v1alpha1' directory, which is where we'll
    # find our protos. We can look for the 'resemble' folder via the
    # `resources` module; the resulting path is a `MultiplexedPath`, since
    # there may be multiple. Such a path doesn't contain a `parent`
    # attribute, since there isn't one answer. Instead we use `iterdir()` to
    # get all of the children of all 'resemble' folders, and then
    # deduplicate the parents-of-the-parents-of-those-children (via the
    # `set`), which gives us the `resemble` folders' parents' paths.
    resemble_parent_paths: set[str] = set()
    for resource in resources.files('resemble').iterdir():
        with resources.as_file(resource) as path:
            resemble_parent_paths.add(str(path.parent.parent))

    if len(resemble_parent_paths) == 0:
        raise FileNotFoundError(
            "Failed to find 'resemble' resource path. "
            "Please report this bug to the maintainers."
        )

    # Now add these to '--proto_path', so that users don't need to provide
    # their own Resemble protos.
    for resemble_parent_path in resemble_parent_paths:
        protoc_args.append(f"--proto_path={resemble_parent_path}")

    # User protos may rely on `google.protobuf.*` protos. We
    # conveniently have those files packaged in our Python
    # package; make them available to users, so that users don't
    # need to provide them.
    protoc_args.append(
        f"--proto_path={resources.files('grpc_tools').joinpath('_proto')}"
    )

    with tempfile.TemporaryDirectory() as directory:
        with chdir(directory):
            protoc_args.append('--python_out=.')
            protoc_args.append('--grpc_python_out=.')

            # Create a `FileDescriptorSet` that we can use as input to
            # calling `protoc`.
            file_descriptor_set = FileDescriptorSet()

            def add_file_descriptor(file_descriptor: FileDescriptor):
                file_descriptor_proto = FileDescriptorProto()
                file_descriptor.CopyToProto(file_descriptor_proto)

                if file_descriptor_proto in file_descriptor_set.file:
                    return

                for dependency in file_descriptor.dependencies:
                    add_file_descriptor(dependency)

                file_descriptor_set.file.append(file_descriptor_proto)

            add_file_descriptor(file)

            with open('file_descriptor_set', 'wb') as file_descriptor_set_file:
                file_descriptor_set_file.write(
                    file_descriptor_set.SerializeToString()
                )
                file_descriptor_set_file.close()

            protoc_args.append('--descriptor_set_in=file_descriptor_set')

            protoc_args.append(f'{file.name}')

            returncode = grpc_tools_protoc.main(protoc_args)

            if returncode != 0:
                print(
                    'Failed to generate protobuf and gRPC code for Python adaptor',
                    file=sys.stderr,
                )
                sys.exit(-1)

            with open(
                f"{file.name.replace('.proto', '_pb2.py')}",
                "r",
            ) as pb2_py, open(
                f"{file.name.replace('.proto', '_pb2_grpc.py')}",
                "r",
            ) as pb2_grpc_py:
                return (pb2_py.read(), pb2_grpc_py.read())


NodejsType = str


@dataclass
class NodejsMethodOptions(BaseMethodOptions):
    errors: dict[ProtoType, NodejsType]


@dataclass
class NodejsMethod(BaseMethod):
    options: NodejsMethodOptions
    input_type: NodejsType
    output_type: NodejsType
    # Nested messages have different types in Python and JS, since we are doing
    # pybind under the covers, we need the Python type to call the correct
    # instance.
    python_input_type: PythonType
    # We pass the request message to Python adaptor, so if the message is
    # described not in the same proto file (for example google.protobuf.* or any
    # other user specified), we want to import the message from the correct
    # Python module.
    python_request_message_module: Optional[str]


@dataclass
class NodejsService(BaseService):
    methods: Sequence[NodejsMethod]


@dataclass
class NodejsFile(BaseFile):
    services: Sequence[NodejsService]
    # Dictionary where the key is the relative path to the
    # file and the value is the unique name of the file.
    imports: dict[str, str]
    # A dict of:
    # key: a unique id including the full file path
    # value: the full file path, with .proto swapped for _rsm
    import_ids: dict[str, str]
    # The name of the ES module, which contains the generated protobuf
    # messages ("*_pb.js").
    pb_name: str
    # The name of the Resemble Python generated module ("*_rsm.py").
    rsm_name: str
    # Set of messages that are used in the file and should be imported from
    # '@bufbuild/protobuf'.
    google_protobuf_used_messages: set[str]
    # We embed the the `*_pb2.py`, `*_pb2_grpc.py`, and `*_rsm.py`
    # "files" as encoded strings in the generated `*_rsm.ts` file
    # so that they can be imported into Python when at runtime.
    base64_gzip_pb2_py: str
    base64_gzip_pb2_grpc_py: str
    base64_gzip_rsm_py: str
    # The name of the Python file generated by the Python Resemble protoc
    # plugin, we need that as we embed the Python file in the NodeJS file.
    pb2_name: str
    pb2_grpc_name: str


class NodejsResembleProtocPlugin(TypescriptResembleProtocPlugin):

    @staticmethod
    def plugin_specific_data() -> PluginSpecificData:
        return PluginSpecificData(
            template_filename="resemble.ts.j2",
            output_filename_suffix="_rsm.ts",
            supported_features=[
                "reader", "writer", "transaction", "workflow", "error"
            ],
            only_generates_with_resemble_services=False,
        )

    @classmethod
    def get_python_external_module(
        cls, message: Descriptor, current_package: str
    ) -> Optional[str]:
        message_package = message.file.package
        if message_package == current_package:
            return None

        python_type = PythonResembleProtocPlugin._get_python_type_from_proto_type(
            message
        )

        python_module = python_type.rsplit('.', 1)[0]

        return python_module

    def plugin_template_data(
        self, proto_file: FileDescriptorProto
    ) -> BaseFile:
        file = self.pool.FindFileByName(proto_file.name)

        state_names = self._proto_state_names(file)

        resemble_services = self._proto_resemble_services(
            file,
            self._proto_state_names(file),
        )

        proto = self._analyze_proto_file(file)

        services: Sequence[NodejsService] = [
            NodejsService(
                proto=self._analyze_proto_service(
                    service,
                    file.services_by_name[service.name],
                ),
                methods=[
                    NodejsMethod(
                        proto=self._analyze_proto_method(method),
                        options=NodejsMethodOptions(
                            proto=self._analyze_proto_method_options(
                                file.services_by_name[
                                    service.name].methods_by_name[method.name],
                                method.client_streaming or
                                method.server_streaming
                            ),
                            errors=self._analyze_errors(
                                file.services_by_name[
                                    service.name].methods_by_name[method.name],
                                state_names=state_names,
                            ),
                        ),
                        input_type=self._get_typescript_type_from_proto_type(
                            file.services_by_name[service.name].
                            methods_by_name[method.name].input_type,
                            file,
                            state_names=state_names,
                            messages_and_enums=proto.messages_and_enums,
                        ),
                        output_type=self._get_typescript_type_from_proto_type(
                            file.services_by_name[service.name].
                            methods_by_name[method.name].output_type,
                            file,
                            state_names=state_names,
                            messages_and_enums=proto.messages_and_enums,
                        ),
                        python_input_type=PythonResembleProtocPlugin.
                        _py_type_name(
                            file.services_by_name[service.name].
                            methods_by_name[method.name].input_type,
                        ),
                        python_request_message_module=self.
                        get_python_external_module(
                            file.services_by_name[service.name].
                            methods_by_name[method.name].input_type,
                            file.package,
                        ),
                    ) for method in service.method
                ],
                options=BaseServiceOptions(
                    proto=self._analyze_proto_service_options(
                        file.services_by_name[service.name]
                    ),
                ),
            ) for service in resemble_services
        ]

        base64_gzip_rsm_py = ""

        if len(services) != 0:
            # If there are at least one Resemble service in the proto file,
            # then '*_rsm.py' file should be generated and embedded in the
            # generated '*_rsm.ts' file.
            # It is tricky to pass the Resemble Python protoc plugin binary to
            # the NodeJS plugin in the context of Bazel tests, so we are just
            # invoking the Resemble Python plugin explicitly here.
            python_resemble_plugin = PythonResembleProtocPlugin(self.pool)

            python_template_data = python_resemble_plugin.template_data(
                proto_file
            )

            assert python_template_data is not None

            base64_gzip_rsm_py = base64.b64encode(
                gzip.compress(
                    python_resemble_plugin.
                    template_render(python_template_data).encode('utf-8'),
                    # Override timestamp, mtime, so .compress is deterministic.
                    mtime=0
                )
            ).decode('utf-8')

        pb2_py, pb2_grpc_py = protoc(file)

        nodejs_file: BaseFile = NodejsFile(
            proto=proto,
            services=services,
            imports=self._analyze_imports(file),
            import_ids=self._unique_import_aliases(file),
            pb_name=self._get_pb_file_name(file),
            google_protobuf_used_messages=self.
            _get_google_protobuf_messages(file),
            rsm_name=self.rsm_module_name(file),
            pb2_name=PythonResembleProtocPlugin._get_pb2_file_name(file),
            pb2_grpc_name=PythonResembleProtocPlugin._get_pb2_file_name(file) +
            '_grpc',
            base64_gzip_pb2_py=base64.b64encode(
                # Override timestamp, mtime, so .compress is deterministic.
                gzip.compress(pb2_py.encode('utf-8'), mtime=0)
            ).decode('utf-8'),
            base64_gzip_pb2_grpc_py=base64.b64encode(
                # Override timestamp, mtime, so .compress is deterministic.
                gzip.compress(pb2_grpc_py.encode('utf-8'), mtime=0)
            ).decode('utf-8'),
            # Leaving it empty for now, since we can handle a proto file which
            # doesn't contain a Resemble service.
            base64_gzip_rsm_py=base64_gzip_rsm_py,
        )

        return nodejs_file

    @classmethod
    def rsm_module_name(cls, file: FileDescriptor) -> str:
        """Get Resemble Python generated module name from file descriptor name
        and package.
        """
        file_name = os.path.basename(file.name).removesuffix('.proto')
        return file.package + '.' + file_name + '_rsm'


# This is a separate function (rather than just being in `__main__`) so that we
# can refer to it as a `script` in our `pyproject.rsm.toml` file.
def main():
    try:
        NodejsResembleProtocPlugin.execute()
    except UserProtoError as error:
        terminal.fail(str(error))


if __name__ == '__main__':
    main()
