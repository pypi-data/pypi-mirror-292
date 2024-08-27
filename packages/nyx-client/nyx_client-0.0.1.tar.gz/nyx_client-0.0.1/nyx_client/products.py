"""
Module that manages individual Nyx products
"""

import urllib


class NyxProduct:
    """Represents a product in the Nyx system.

    This class encapsulates the information and functionality related to a product
    in the Nyx system, including its metadata and content retrieval.

    Attributes:
        title (str): The title of the product.
        url (str): The access URL of the product.
        org (str): The organization associated with the product.
        content (str): The downloaded content of the product (None if not yet downloaded).
    """

    def __init__(self, **kwargs):
        """Initialize a NyxProduct instance.

        Args:
            **kwargs: Keyword arguments containing product information.
                Required keys: 'accessUrl', 'title', 'org'

        Raises:
            KeyError: If any of the required fields are missing.
        """
        if not kwargs.get("accessUrl") or not kwargs.get("title") or not kwargs.get("org"):
            raise KeyError(
                f"Required fields are 'accessUrl', 'title', 'org', got the fields {', '.join(kwargs.keys())}"
            )
        self.title = kwargs.get("title")
        self.url = kwargs.get("accessUrl")
        self.org = kwargs.get("org")

        try:
            self.content_type = kwargs.get("mediaType").split("/")[-1]
        except Exception:
            self.content_type = "unknown"
        self.content = None

    def __repr__(self):
        """Return a string representation of the NyxProduct instance.

        Returns:
            str: A string representation of the product.
        """
        return f"Product({self.title}, {self.url}, {self.content_type})"

    def download(self):
        """Download the content of the product and populate the class content field.

        This method attempts to download the content from the product's URL
        and stores it in the `content` attribute.

        Returns:
            str: The downloaded content, or None if the download fails.

        Note:
            If the content has already been downloaded, this method returns
            the cached content without re-downloading.
        """
        if self.content:
            return self.content
        url = self.url + f"?buyer_org={self.org}"
        try:
            with urllib.request.urlopen(url) as f:
                self.content = f.read().decode("utf-8")
                return self.content
        except urllib.error.URLError:
            return None
