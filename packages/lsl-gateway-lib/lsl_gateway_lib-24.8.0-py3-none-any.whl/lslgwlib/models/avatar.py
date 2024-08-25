from pydantic import BaseModel, Field
from uuid import UUID
import re


class Avatar(BaseModel):
    """Avatar model"""

    __namePattern = re.compile("^[a-z0-9]{1,31}$", re.IGNORECASE)
    __nameStrPattern = re.compile(
        r"^[a-z0-9]{1,31}((\ |\.)[a-z0-9]{1,31})?$", re.IGNORECASE
    )
    id: UUID
    firstName: str = Field(pattern=__namePattern)
    lastName: str | None = Field(default=None, pattern=__namePattern)

    def __init__(self, *args, **kwargs) -> None:
        # constructor by id:uuid, fullname:str
        if len(args) == 2:
            id, name = args
            try:
                fn, ln = name.replace(".", " ").split()
            except ValueError:
                fn = name
                ln = None
            if ln and ln.lower() == "resident":
                ln = None
            super().__init__(id=id, firstName=fn, lastName=ln)
        else:
            super().__init__(**kwargs)

    def __eq__(self, o) -> bool:
        return self.modernName() == o.modernName() and self.id == o.id

    def legacyName(self) -> str:
        """Get name in legacy format <Firstname Lastname>"""
        ln = self.lastName
        if not ln:
            ln = "Resident"
        return f"{self.firstName} {ln}"

    def modernName(self) -> str:
        """Get name in modern format <username.resident>"""
        ln = self.lastName
        if ln:
            ln = ln.lower()
        else:
            ln = "resident"
        return f"{self.firstName.lower()}.{ln}"
