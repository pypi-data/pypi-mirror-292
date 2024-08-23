from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components.model import (
    DefaultsModelComponent,
    PermissionsModelComponent,
    RecordMetadataModelComponent,
    RecordModelComponent,
    ServiceModelComponent,
)
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.utils.deepmerge import deepmerge
from oarepo_model_builder_drafts.datatypes.components import (
    DraftParentComponent,
    ParentMarshmallowComponent,
)


class WorkflowPermissionsComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    affects = [PermissionsModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "record":
            permissions = set_default(datatype, "permissions", {})
            permissions.setdefault("presets", ["workflow"])


class WorkflowComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [
        DefaultsModelComponent,
        RecordModelComponent,
        RecordMetadataModelComponent,
        ServiceModelComponent,
        ParentMarshmallowComponent,
        DraftParentComponent,
    ]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "record":
            datatype.definition["permissions"].setdefault("presets", ["workflow"])
            fields = datatype.definition["record"].setdefault("fields", {})
            fields.setdefault(
                "state",
                "{{oarepo_workflows.records.systemfields.state.RecordStateField}}(initial='published')",
            )

            datatype.definition["service-config"].setdefault("components", []).append(
                "{{oarepo_workflows.services.components.workflow.WorkflowComponent}}"
            )

            parent_fields = datatype.definition["draft-parent-record"].setdefault(
                "fields", {}
            )
            parent_fields.setdefault(
                "workflow",
                "{{oarepo_workflows.records.systemfields.workflow.WorkflowField}}()",
            )

            # add marshmallow-only field "state" to the parent schema
            deepmerge(
                datatype.definition["properties"].setdefault("state", {}),
                {
                    "type": "keyword",
                    "marshmallow": {"read": True, "write": False},
                    "ui": {"marshmallow": {"read": True, "write": False}},
                },
            )

        if datatype.root.profile == "draft":
            fields = datatype.definition["record"].setdefault("fields", {})
            fields.setdefault(
                "state",
                "{{oarepo_workflows.records.systemfields.state.RecordStateField}}()",
            )


class WorkflowOverrideDefaultsComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [
        DefaultsModelComponent,
    ]
    affects = [
        DraftParentComponent,
        ParentMarshmallowComponent,
    ]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "record":
            datatype.definition.setdefault(
                "draft-parent-record-metadata", {}
            ).setdefault(
                "base-classes",
                [
                    "oarepo_workflows.records.models.RecordWorkflowParentModelMixin",
                    "invenio_db.db{db.Model}",
                    "invenio_records.models.RecordMetadataBase",
                ],
            )

            datatype.definition.setdefault("parent-record-marshmallow", {}).setdefault(
                "base-classes",
                ["oarepo_workflows.services.records.schema.WorkflowParentSchema"],
            )
