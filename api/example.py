from fastapi import APIRouter

router = APIRouter()

# simple example endpoints, you can use these to allow other services to check if the bot is online etc.
# you can have the following methods: get, post, put, delete, patch

# Get requests are easy to test in a browser, just go to http://yourbotaddress/api/example/
@router.get("/")
async def home() :
	return {"message": "Welcome to Discord!"}


@router.get("/status")
async def status() :
	return {"status": "ok"}
