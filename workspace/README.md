# workspace

Commit your Microsoft Fabric item definitions here by using Fabric Git integration from the DEV workspace. `deploy.py` publishes the items in this folder. To use a different folder, set the `REPOSITORY_DIRECTORY` environment variable.

Example layout:

```text
SampleNotebook.Notebook/
  notebook-content.py
  .platform
```

fabric-cicd only deploys the item types listed in `item_type_in_scope` in `deploy.py`.
