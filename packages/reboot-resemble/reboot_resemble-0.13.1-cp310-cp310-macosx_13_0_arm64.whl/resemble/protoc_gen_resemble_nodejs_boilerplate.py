import os
from dataclasses import dataclass
from google.protobuf.descriptor import FileDescriptor
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from resemble.cli import terminal
from resemble.protoc_gen_resemble_generic import (
    BaseFile,
    PluginSpecificData,
    UserProtoError,
)
from resemble.protoc_gen_resemble_nodejs import (
    NodejsFile,
    NodejsResembleProtocPlugin,
)


@dataclass
class NodejsBoilerplateFile(NodejsFile):
    # The `..._rsm` module name of the Resemble generated Nodejs code for this
    # proto file.
    nodejs_rsm_name: str
    has_reader_method: bool
    has_writer_method: bool
    has_transaction_method: bool
    has_workflow_method: bool


class NodejsResembleBoilerplateProtocPlugin(NodejsResembleProtocPlugin):

    @staticmethod
    def plugin_specific_data() -> PluginSpecificData:
        return PluginSpecificData(
            template_filename="servicer_boilerplate.ts.j2",
            output_filename_suffix="_servicer.ts",
            supported_features=[
                "reader",
                "writer",
                "transaction",
                "error",
                "streaming",
                "workflow",
            ],
        )

    def plugin_template_data(
        self, proto_file: FileDescriptorProto
    ) -> BaseFile:
        file = self.pool.FindFileByName(proto_file.name)
        nodejs_file = super().plugin_template_data(proto_file)

        assert isinstance(nodejs_file, NodejsFile)

        nodejs_boilerplate_file = NodejsBoilerplateFile(
            proto=nodejs_file.proto,
            services=nodejs_file.services,
            imports=nodejs_file.imports,
            import_ids=nodejs_file.import_ids,
            pb_name=nodejs_file.pb_name,
            rsm_name=self.rsm_module_name(file),
            google_protobuf_used_messages=nodejs_file.
            google_protobuf_used_messages,
            base64_gzip_pb2_py=nodejs_file.base64_gzip_pb2_py,
            base64_gzip_pb2_grpc_py=nodejs_file.base64_gzip_pb2_grpc_py,
            base64_gzip_rsm_py=nodejs_file.base64_gzip_rsm_py,
            pb2_name=nodejs_file.pb2_name,
            pb2_grpc_name=nodejs_file.pb2_grpc_name,
            nodejs_rsm_name=self.nodejs_rsm_module_name(file),
            has_reader_method=False,
            has_writer_method=False,
            has_transaction_method=False,
            has_workflow_method=False,
        )

        for service in nodejs_boilerplate_file.services:
            for method in service.methods:
                if method.options.proto.kind == "reader":
                    nodejs_boilerplate_file.has_reader_method = True
                elif method.options.proto.kind == "writer":
                    nodejs_boilerplate_file.has_writer_method = True
                elif method.options.proto.kind == "transaction":
                    nodejs_boilerplate_file.has_transaction_method = True
                elif method.options.proto.kind == "workflow":
                    nodejs_boilerplate_file.has_workflow_method = True

        return nodejs_boilerplate_file

    @classmethod
    def nodejs_rsm_module_name(cls, file: FileDescriptor) -> str:
        """Get Resemble Nodejs generated module name from file descriptor name
        and package.
        """
        file_name = os.path.basename(file.name).removesuffix('.proto')
        return file_name + '_rsm.js'


# This is a separate function (rather than just being in `__main__`) so that we
# can refer to it as a `script` in our `pip_package` BUILD targets.
def main():

    try:
        NodejsResembleBoilerplateProtocPlugin.execute()
    except UserProtoError as error:
        terminal.fail(str(error))


if __name__ == '__main__':
    main()
