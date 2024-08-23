import requests
import os

from cabysis_mail_man.file_meta import FileMeta


def send_mail(
    subject: str,
    message: str,
    recipients: list[str],
    provider: str,
    api_key: str,
    files_meta: list[FileMeta] = None,
    is_local: bool = False,
):
    provider = provider.value
    print(provider)
    if not subject or not message or not recipients or not provider or not api_key:
        raise ValueError("All parameters are required")

    openned_files = []

    try:
        # Production URL
        url = "https://fc7uzf2hcc.us-east-1.awsapprunner.com/mailapi/sendmail"
        if is_local:
            url = "http://localhost:8080/mailapi/sendmail"

        files = []
        if files_meta is not None and len(files_meta) > 0:
            for file_meta in files_meta:
                buffer = file_meta.buffer
                if buffer is None:
                    buffer = open(file_meta.file_path, "rb")
                    openned_files.append(buffer)
                files.append(
                    (
                        "files",
                        (
                            (
                                os.path.basename(file_meta.file_path)
                                if file_meta.buffer is None
                                else file_meta.file_name
                            ),
                            buffer,
                            file_meta.file_type,
                        ),
                    )
                )

        body = {
            "message": message,
            "recipients": recipients,
            "subject": subject,
            "provider": provider,
        }
        print(body)

        if len(files) > 0:
            requests.post(
                url,
                data=body,
                files=files,
                headers={"Authorization": api_key},
            )
        else:
            requests.post(
                url,
                data=body,
                headers={"Authorization": api_key},
            )

    except Exception as e:
        raise Exception(f"Error sending email: {e}")
    finally:
        for file in openned_files:
            file.close()
