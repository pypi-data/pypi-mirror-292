from typing import List, Optional

import pydantic

from mlstac.specification.collection.extension_contacts import Contact


class Authors(pydantic.BaseModel):
    """This extension provides a way to define authors. Useful for
    measuring the quality of a dataset.

    Fields:
        authors (List[Contact]): A list of authors.
    """

    authors: Optional[List[Contact]] = None
