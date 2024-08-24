from typing import Optional
from urllib.parse import quote_plus


def encode_text(text: str, single: bool = False) -> str:
    result = quote_plus(text)
    if not single:
        result = quote_plus(result)
    return result.replace("%", "$")


ENCODED_EQUAL = encode_text("=", single=True)
ENCODED_QUESTION = encode_text("?", single=True)
ENCODED_AMPERSAND = encode_text("&", single=True)


def create_url_log_group(*, region: str, log_group_name: str) -> str:
    """Returns CloudWatch Logs LogGroup URL

    :param region: AWS Region
    :param log_group_name: LogGroup Name
    :return: CloudWatch Logs LogGroup URL
    """
    return "".join(
        [
            "https://",
            region,
            ".console.aws.amazon.com/cloudwatch/home?region=",
            region,
            "#logsV2:log-groups/log-group/",
            encode_text(log_group_name),
        ]
    )


def create_url_log_events(
    *,
    region: str,
    log_group_name: str,
    log_stream_name: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    filter_pattern: Optional[str] = None,
) -> str:
    """Returns CloudWatch Logs LogEvents Url

    :param region: AWS Region
    :param log_group_name: LogGroup Name
    :param log_stream_name: LogStream Name
    :param start: The starting point of the period in milliseconds since UNIX epoch. To specify a relative time, provide a negative value in milliseconds. ex) The last 30 minutes = -1800000
    :param end: The ending point of the period in milliseconds since UNIX epoch.
    :param filter_pattern: FilterPattern
    :return: CloudWatch Logs LogEvents Url
    """
    url = (
        create_url_log_group(region=region, log_group_name=log_group_name)
        + "/log-events"
    )
    if log_stream_name:
        url += "/" + encode_text(log_stream_name)

    query = []
    if filter_pattern:
        query += [f"filterPattern{ENCODED_EQUAL}{encode_text(filter_pattern)}"]
    if start:
        query += [f"start{ENCODED_EQUAL}{encode_text(str(start))}"]
    if end:
        query += [f"end{ENCODED_EQUAL}{encode_text(str(end))}"]

    if query:
        url += encode_text("?", single=True) + encode_text("&", single=True).join(query)
    return url
