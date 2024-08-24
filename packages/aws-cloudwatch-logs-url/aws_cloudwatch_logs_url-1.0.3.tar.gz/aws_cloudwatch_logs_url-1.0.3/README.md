# aws-cloudwatch-logs-url

[![PypiBadge]][Pypi]
[![PepyAllDownloadBadge]][Pypi]
[![PepyMonthlyDownloadBadge]][Pepy]


[PypiBadge]: https://img.shields.io/pypi/v/aws-cloudwatch-logs-url
[Pypi]: https://pypi.org/project/aws-cloudwatch-logs-url/
[Pepy]: https://www.pepy.tech/projects/aws-cloudwatch-logs-url
[PepyAllDownloadBadge]: https://static.pepy.tech/badge/aws-cloudwatch-logs-url
[PepyMonthlyDownloadBadge]: https://static.pepy.tech/badge/aws-cloudwatch-logs-url/month


Generate AWS CloudWatch Logs URL

## Install

```bash
$ pip install aws-cloudwatch-logs-url
```

## How to use
### create_url_log_group()
```python
from aws_cloudwatch_logs_url import create_url_log_group
url = create_url_log_group(
    region="string",
    log_group_name="string"
)
```
- region (string)
  **[REQUIRED]**
  AWS Region
- log_group_name (string)
  **[REQUIRED]**
  LogGroup Name

### create_url_log_events()
```python
from aws_cloudwatch_logs_url import create_url_log_events
url = create_url_log_events(
  region="string",
  log_group_name="string",
  log_stream_name="string",
  start=123,
  end=123,
  filter_pattern="string"
)
```
- region (string)  
  **[REQUIRED]**  
  AWS Region
- log_group_name (string)  
  **[REQUIRED]**  
  LogGroup Name
- log_stream_name (string)  
  LogStream Name
- start (integer)  
  The starting point of the period in milliseconds since UNIX epoch. To specify a relative time, provide a negative value in milliseconds. ex) The last 30 minutes = -1800000
- end (integer)  
  The ending point of the period in milliseconds since UNIX epoch.
- filter_pattern (string)  
  FilterPattern

## License

MIT © sinofseven
