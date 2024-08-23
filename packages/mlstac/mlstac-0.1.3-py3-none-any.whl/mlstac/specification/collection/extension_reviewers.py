from typing import List, Literal, Optional

import pydantic

from mlstac.specification.collection.extension_contacts import Contact


class Reviewer(pydantic.BaseModel):
    """This extension provides a way to define reviewers. Useful for
    measuring the quality of a dataset.

    Fields:
        name (str): Name of the reviewer.
        score (Literal[0, 1, 2, 3, 4, 5]): Score of the reviewer.
            The score must be between 0 and 5. Higher is better.
        url (str): A public url where to find more information about
            the review process. Usually is a link to a github issue.
    """

    reviewer: Contact
    score: Optional[Literal[0, 1, 2, 3, 4, 5]] = None


class Reviewers(pydantic.BaseModel):
    """This extension define a review process. Useful for
    measuring the quality of a dataset.
    """

    reviewers: Optional[List[Reviewer]] = None
