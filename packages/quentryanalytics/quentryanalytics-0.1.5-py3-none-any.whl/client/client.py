import boto3
import awswrangler as wr
import base64
import pandas as pd
import warnings
import re


class QuentryAnalyticsClient:
    def __init__(self, auth_token) -> None:
        plaintext_auth_token = base64.b64decode(auth_token)
        self._bucket_name = "poc-data-for-google-colab"
        self._boto3_session = boto3.Session(
            # this is very bad practice and is only temporary.
            aws_access_key_id=plaintext_auth_token.split(";")[1],
            aws_secret_access_key=plaintext_auth_token.split(";")[2]
        )
        
    def getDataFrame(self, filename, tab) -> pd.DataFrame:
        file_url = f"s3://{self._bucket_name}/{filename}"
        warnings.filterwarnings('ignore', category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
        return wr.s3.read_excel(file_url, sheet_name=tab, boto3_session=self._boto3_session)