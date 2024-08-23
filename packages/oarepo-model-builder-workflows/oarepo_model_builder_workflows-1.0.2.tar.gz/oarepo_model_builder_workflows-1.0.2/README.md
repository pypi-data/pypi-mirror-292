# OARepo model builder plugin for workflows

This plugin provides a model builder for the OARepo workflow service.
Use it to add support for workflows to your OARepo model.

## Installation and usage

To use the plugin, add the following to your model yaml file, section `plugins.packages`:

```yaml
plugins:
  packages:
  - oarepo-model-builder-worklows
```

Then recompile your model to generate the new code.

## Code added

The plugin adds the following code to your model:

- A new field `workflow` to the model's parent record. The workflow is thus shared
  across all the versions of the record.
- A new field `state` on the record. This field is used to store the current state
  of the record in the workflow. Each version of the record (published, draft, previous versions)
  has its own state.
- Marhmallow schema of the parent record is extended with `oarepo_workflows.services.records.schema.WorkflowParentSchema`
  class to allow passing the workflow to the record.
- DB table of the parent record is extended with `oarepo_workflows.records.models.RecordWorkflowParentModelMixin`
  to include the workflow field
- A workflow component (`oarepo_workflows.services.components.workflow.WorkflowComponent`) is added to model service components.

## Tests

Note: the tests generated with oarepo-model-builder-tests plugin are not compatible
with the workflow plugin. You need to write your own tests for the workflow.

## Usage remarks

The workflow module depends on the record and initial data passed to the permission policy.
In the current version invenio does not pass those.  
To circumvent this, you need to use the oarepo forks of the following invenio modules:

- invenio-records-resources
- invenio-drafts-resources

