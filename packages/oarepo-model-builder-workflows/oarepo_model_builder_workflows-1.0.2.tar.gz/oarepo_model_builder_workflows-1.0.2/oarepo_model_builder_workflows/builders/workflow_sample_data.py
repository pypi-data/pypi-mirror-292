from oarepo_model_builder.builders.json_base import JSONBaseBuilder
from oarepo_model_builder.outputs.yaml import YAMLOutput
from oarepo_model_builder.utils.dict import dict_get


class WorkflowSampleDataBuilder(JSONBaseBuilder):
    TYPE = "workflow_sample_data"
    output_file_type = "yaml"
    output_file_name = ["sample", "file"]
    parent_module_root_name = "jsonschemas"

    def begin(self, current_model, schema):
        output_name = dict_get(current_model.definition, self.output_file_name)
        path = self.builder.output_dir.joinpath(output_name)

        if path not in self.builder.outputs:
            # sample file does not exist, so skip json builder to not create an empty one
            super(JSONBaseBuilder, self).begin(current_model, schema)
            self.output = None
        else:
            super().begin(current_model, schema)

    def finish(self):
        output: YAMLOutput = self.output
        if output:
            # add parent: workflow: "default" to the sample data
            documents = output.documents
            for d in documents:
                d.setdefault("parent", {}).setdefault("workflow", "default")
            super().finish()
