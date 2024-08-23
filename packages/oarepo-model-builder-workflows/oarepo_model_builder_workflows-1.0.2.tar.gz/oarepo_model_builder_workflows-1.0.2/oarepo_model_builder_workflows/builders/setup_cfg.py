from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.outputs.cfg import CFGOutput


class WorkflowsSetupCfgBuilder(OutputBuilder):
    TYPE = "workflows_setup_cfg"

    def finish(self):
        super().finish()
        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")
        output.add_dependency("oarepo-workflows", ">=1.0.0")
