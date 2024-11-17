import pytest

import httpretty
import boto3
from botocore.exceptions import ClientError


@httpretty.activate(allow_net_connect=False, verbose=True)
def test_boto3():
    "#416 boto3 issue"
    httpretty.register_uri(
        httpretty.PUT,
        "https://foo-bucket.s3.amazonaws.com/foo-object",
        body="""<?xml version="1.0" encoding="UTF-8"?>
    <Error>
        <Code>AccessDenied</Code>
        <Message>Access Denied</Message>
        <RequestId>foo</RequestId>
        <HostId>foo</HostId>
    </Error>""",
        status=403
    )

    session = boto3.Session(aws_access_key_id="foo", aws_secret_access_key="foo")
    s3_client = session.client('s3')

    with pytest.raises(ClientError) as expect:
        s3_client.put_object(
            Bucket="foo-bucket",
            Key="foo-object",
            Body=b"foo"
        )

    assert expect.value.operation_name == 'PutObject'
    assert expect.value.response["Error"]["Code"] == 'AccessDenied'
    assert expect.value.response["Error"]["Message"] == 'Access Denied'
    assert expect.value.response["ResponseMetadata"]["HTTPStatusCode"] == 403
