# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from .auth.helper import decode_access_token
# from sqlalchemy.ext.asyncio import AsyncSession
# from .models import User
# from sqlalchemy.future import select
# from sqlalchemy.orm import sessionmaker


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     username: str = payload.get("sub")
#     if not username:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     result = await session.execute(select(User).where(User.username == username))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return user
