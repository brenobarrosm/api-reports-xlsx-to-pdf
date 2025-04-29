from fastapi import APIRouter, Query
from starlette import status

router = APIRouter(prefix='/users')


@router.get('')
def get_users():
    return {'message': 'Hello World'}
