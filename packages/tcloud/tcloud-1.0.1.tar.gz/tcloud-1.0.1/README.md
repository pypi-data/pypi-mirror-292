# Tobiko Cloud CLI

## Configuration

The configuration for the `tcloud` CLI tool should be stored either in the `$HOME/.tcloud/tcloud.yml` file or in the `tcloud.yml` file located in the project folder.

Below is an example of `tcloud.yml` configuration:
```yaml
projects:
    <Project name>:
        url: <The project URL>
        token: <The access token>
        gateway: <The name of the SQLMesh gateway to use with this project>
        extras: <Optional - Any extras that should be installed with sqlmesh-enterprise>
default_project: <The name of a project to use by default>
```

Alternatively, the target project can be configured using the `TCLOUD_URL`, `TCLOUD_TOKEN`, `TCLOUD_GATEWAY`, and `TCLOUD_EXTRAS` environment variables.
