from sagemaker_jupyterlab_extension_common.identity import SagemakerIdentityProvider

# https://jupyter-server.readthedocs.io/en/latest/operators/configuring-extensions.html

c.AiExtension.default_language_model = "amazon-q:Q-Developer"  # noqa: F821
c.ServerApp.identity_provider_class = SagemakerIdentityProvider  # noqa: F821
