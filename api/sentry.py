from fastapi import APIRouter

router = APIRouter()

# this route is used to test Sentry error tracking, if you use sentry.
@router.get("/sentry-debug")
async def trigger_error() :
	division_by_zero = 1 / 0
