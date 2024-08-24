# Copyright 2024 Agnostiq Inc.
"""Blueprint that uses NVIDIA NIMs and a Snowflake database to implement
RAG."""

import covalent_cloud as cc
from covalent_blueprints import get_blueprint
from covalent_blueprints.blueprints.utilities import set_metadata

from covalent_blueprints_ai._prefix import PREFIX


def nvidia_llama_rag(
    user: str = "",
    password: str = "",
    account: str = "",
    warehouse_name: str = "nims_rag_warehouse",
    database_name: str = "nims_rag_database",
    schema_name: str = "nims_rag_schema",
    table_name: str = "nims_rag_table",
):
    """A blueprint that deploys three NVIDIA NIMs composed into a RAG model
    using a Snowflake database.

    The following NIMs are utilized by this blueprint:
    - nvcr.io/nim/meta/llama3-8b-instruct:1.0.0
    - nvcr.io/nim/snowflake/arctic-embed-l:1.0.1
    - nvcr.io/nim/nvidia/nv-rerankqa-mistral-4b-v3:1.0.1

    Args:
        user: Snowflake username. Defaults to "".
        password: Snowflake password. Defaults to "".
        account: Snowflake account, i.e. 'ORGID-USERID'. Defaults to "".
        warehouse_name: Snowflake warehouse name. Defaults to "nims_rag_warehouse".
        database_name: Snowflake database name. Defaults to "nims_rag_database".
        schema_name: Snowflake schema name. Defaults to "nims_rag_schema".
        table_name: Snowflake table name. Defaults to "nims_rag_table".

    Returns:
        Covalent blueprint that runs the composed RAG model.

    Example:
        ```
        import covalent_blueprints as cb

        # Save your NGC API key.
        cb.store_secret("NGC_API_KEY", "your-ngc-api-key")

        # Save your Snowflake credentials.
        cb.store_secret("SNOWFLAKE_USER", "your-username")
        cb.store_secret("SNOWFLAKE_PASSWORD", "your-password")
        cb.store_secret("SNOWFLAKE_ACCOUNT", "orgid-userid")

        # Create the blueprint.
        from covalent_blueprints_ai import nvidia_llama_rag

        # Obtain main rag client and clients individual services.
        rag_client, llama_client, emb_client, rr_client = bp.run()

        # Add data to the Snowflake table.
        ingested = rag_client.ingest_data(
            data=[
                "Agnostiq Inc. is a started founded in Toronto.",
                "Agnostic develops Covalent Cloud.",
                "Covalent Cloud\\'s website URL is covalent.xyz",
            ]
        )

        # Run the RAG model.
        response = rag_client.query_llama(prompt="What is Agnostiq Inc?")
        print(response["choices"][0]["message"]["content"])
        ```
    """

    account_secret_names = cc.list_secrets()

    if "NGC_API_KEY" not in account_secret_names:
        raise RuntimeError("""'NGC_API_KEY' does not exist as a secret in your account.
Use the following to store your NGC API Key

    from covalent_blueprints import store_secret
    store_secret('NGC_API_KEY', 'you-ngc-api-key')` to store it.

This will make `NGC_API_KEY` available as an environment variable for all tasks in this blueprint.
""")

    if not (
        "SNOWFLAKE_USER" in account_secret_names
        and "SNOWFLAKE_PASSWORD" in account_secret_names
        and "SNOWFLAKE_ACCOUNT" in account_secret_names
    ):
        if not (user and password and account):
            raise RuntimeError(
                "If the blueprints arguments `user`, `password`, and `account` "
                "are not provided, you must store the Snowflake credentials as "
                "secrets in your account, under 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', "
                "and 'SNOWFLAKE_ACCOUNT'."
            )

    bp = get_blueprint(f"{PREFIX}/nvidia_llama_rag")
    bp.set_default_inputs(
        user=user,
        password=password,
        account=account,
        warehouse_name=warehouse_name,
        database_name=database_name,
        schema_name=schema_name,
        table_name=table_name,
    )

    # Set description manually for blueprints sourced from jupyter notebook.
    bp.description = "Implements RAG using three NVIDIA NIMs and a Snowflake database."

    set_metadata(bp, nvidia_llama_rag)
    return bp
