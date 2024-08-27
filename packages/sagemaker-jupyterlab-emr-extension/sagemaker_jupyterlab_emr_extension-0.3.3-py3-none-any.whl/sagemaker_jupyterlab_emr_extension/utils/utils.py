import botocore
import logging
import traceback


def get_credential(roleArn):
    session = botocore.session.get_session()
    sts_client = session.create_client("sts")
    try:
        credential = sts_client.assume_role(
            RoleArn=roleArn,
            RoleSessionName="SagemakerAssumableSession",
        )
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as error:
        logging.error(
            "Error in get credential in EMR {}".format(traceback.format_exc())
        )
        raise error
    return credential["Credentials"]
