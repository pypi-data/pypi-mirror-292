import unittest
from unittest.mock import patch, mock_open
from mail.sender import send_mail
from mail.file_meta import FileMeta


class TestEmailSender(unittest.TestCase):

    @patch("requests.post")
    def test_send_mail_without_attachments(self, mock_post):
        subject = "Unit Test "
        message = "This is a test"
        recipients = ["stephanny.murillo@cabysis.com"]
        provider = "trendeats"
        api_key = "ToDo: api_key"  # ToDo: api_key

        send_mail(subject, message, recipients, provider, api_key)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("data", kwargs)
        body = kwargs["data"]
        self.assertEqual(body["message"], message)
        self.assertEqual(body["subject"], subject)
        self.assertEqual(body["recipients"], recipients)
        self.assertEqual(body["provider"], provider)
        self.assertEqual(kwargs["headers"]["Authorization"], api_key)

    @patch("requests.post")
    def test_send_mail_with_attachments(self, mock_post):
        subject = "Unit Test"
        message = "This is a test"
        recipients = ["stephanny.murillo@cabysis.com"]
        provider = "trendeats"
        api_key = "ToDo: api_key"  # ToDo: api_key

        # Mock file content
        file_content = b"Test file content"

        # Mock file meta data
        file_meta_list = [
            FileMeta(
                file_path="./mock_data/file.json",
            ),
        ]

        # Mock open calls for file reading
        mock_open_func = mock_open(read_data=file_content)
        with patch("builtins.open", mock_open_func):
            send_mail(
                subject,
                message,
                recipients,
                provider,
                api_key,
                files_meta=file_meta_list,
            )

        # Assertions
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("files", kwargs)
        files = kwargs["files"]
        self.assertEqual(len(files), 1)  # Check one attachment

        expected_file_name = "file.json"
        # Check asserts on  each attachment
        for i, file_meta in enumerate(file_meta_list):
            self.assertEqual(files[i][0], "files")
            self.assertEqual(files[i][1][0], expected_file_name)
            self.assertEqual(files[i][1][1].read(), file_content)

        # Check assets on request parameters
        self.assertIn("data", kwargs)
        body = kwargs["data"]
        self.assertEqual(body["message"], message)
        self.assertEqual(body["subject"], subject)
        self.assertEqual(body["recipients"], recipients)
        self.assertEqual(body["provider"], provider)
        self.assertEqual(kwargs["headers"]["Authorization"], api_key)

    def test_send_mail_missing_parameter(self):
        # Testing empty parameters
        with self.assertRaises(ValueError):
            send_mail(
                None,
                "This is a test",
                ["stephanny.murillo@cabysis.com"],
                "trendeats",
                "ToDo: api_key",  # ToDo: api_key,
            )

        with self.assertRaises(ValueError):
            send_mail(
                "Test Subject",
                None,
                ["stephanny.murillo@cabysis.com"],
                "trendeats",
                "ToDo: api_key",  # ToDo: api_key
            )

        with self.assertRaises(ValueError):
            send_mail(
                "Test Subject",
                "This is a test",
                None,
                "trendeats",
                "ToDo: api_key",  # ToDo: api_key
            )

        with self.assertRaises(ValueError):
            send_mail(
                "Test Subject",
                "This is a test",
                ["stephanny.murillo@cabysis.com"],
                None,
                "ToDo: api_key",  # ToDo: api_key,
            )

        with self.assertRaises(ValueError):
            send_mail(
                "Test Subject",
                "This is a test",
                ["stephanny.murillo@cabysis.com"],
                "trendeats",
                None,
            )


if __name__ == "__main__":
    unittest.main()
