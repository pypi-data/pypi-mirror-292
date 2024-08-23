# Email Sender Package

MailManSender package is a Python library for sending emails easily using SMTP created by CabySis.


## Installation

You can install the lastest version as:

```bash
    pip install cabysis-mail-man
```
## Usage

You can use this library after installation as this example:

```python
from cabysis_mail_man.file_meta import FileMeta
from cabysis_mail_man import sender
from cabysis_mail_man.providers import Providers # Enum class with all available providers

    files_meta = [
        FileMeta(file_path="path/file.txt"),    # Create file meta by file stored on path
        FileMeta(                               # Create file meta by buffer and file name
            buffer=b"file buffer example",
            file_name="file.txt",
        ),
    ]

    subject = "This is a subject"               # Define email subject
    message = "This is email body message."     # Define email body
    to_emails = [                               # Define the email receivers list
        "your_email@exmple.com"
    ]
    provider = Providers.MYPROVIDER            # Specify the provider
    api_key = "your_api_key"                    # Specify the api key 
    sender.send_mail(subject, message, to_emails, provider, api_key, files_meta)  # Send email with the provided data
```

