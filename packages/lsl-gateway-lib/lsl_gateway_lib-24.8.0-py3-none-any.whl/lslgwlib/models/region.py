from pydantic import BaseModel, Field, field_validator
import re


class Region(BaseModel):
    __namePattern = re.compile("^[a-z0-9]+( [a-z0-9]+)?( [a-z0-9]+)?$", re.IGNORECASE)
    __locPattern = re.compile(
        r"^[a-z0-9]+( [a-z0-9]+)?( [a-z0-9]+)?\s*\(\s*\d+\s*\,\s*\d+\s*\)$",
        re.IGNORECASE,
    )
    name: str = Field(min_length=3, max_length=25, pattern=__namePattern)
    location: tuple[int, int]

    def __init__(self, *args, **kwargs) -> None:
        # constructor by str <Region name (0, 0)>
        if len(args):
            nm, xy = args[0].split("(")
            nm = nm.strip()
            x, y = xy.replace(")", "").strip().split(",")
            super().__init__(name=nm, location=(x, y))
        else:
            super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"{self.name} {self.location}"

    @field_validator("location")
    def location_validator(cls, location: tuple[int, int]):
        if location[0] < 0 or location[1] < 0:
            raise ValueError("Region.location must contains positive values")
        if location[0] % 256 or location[1] % 256:
            raise ValueError("Region.location must contains in 256x256 grid values")
        return location
