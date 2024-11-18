from typing import Annotated

from pydantic import StringConstraints

carrier = Annotated[
    str, StringConstraints(to_upper=True, strip_whitespace=True)
]
package_size = Annotated[
    str, StringConstraints(to_upper=True, strip_whitespace=True)
]
