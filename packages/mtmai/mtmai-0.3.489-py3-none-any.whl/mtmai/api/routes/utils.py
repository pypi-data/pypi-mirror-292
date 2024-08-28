import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic.networks import EmailStr

from mtmai.api.deps import get_current_active_superuser
from mtmai.models.models import Message
from mtmai.utils import generate_test_email, send_email

router = APIRouter()


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


class TestUrlReq(BaseModel):
    url: str


@router.post(
    "/test-url/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
async def test_url(req: TestUrlReq):
    client = httpx.AsyncClient()
    response = await client.get(req.url)
    content = response.text
    return content
