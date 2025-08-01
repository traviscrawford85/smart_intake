from fastapi import Depends, Request
from your_utils_module import recursive_normalize

async def normalized_body(request: Request):
    data = await request.json()
    return recursive_normalize(data)

# Usage in endpoint:
from .models import MatterResponse  # This inherits from ClioBaseModel

@app.post("/matters")
async def create_matter(
    payload = Depends(normalized_body)
):
    model = MatterResponse(**payload)
    # ...proceed with normalized data
