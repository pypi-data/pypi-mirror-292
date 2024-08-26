import logging
from .models import User, UserInDB

def create_user(username, hashed_password, email, full_name=None):
    # Add a new user
    user = User(username=username, email=email, full_name=full_name, disabled=False)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    user_in_db.save()
    return user_in_db

def read_user(user_pk: str):
  try:
     user = UserInDB.find(UserInDB.pk==user_pk).first()
     return user
  except Exception:
     logging.error(f"User {user_pk} not found.")


def read_user_by_name(username: str):
   try:
     user = UserInDB.find(UserInDB.username==username).first()
     return user
   except Exception:
     logging.error(f"User {username} not found.")
   
  

def update_user(user_pk: str, **kwargs):
   # Update user email or name
   try:
      user = read_user(user_pk)
      logging.info(f"Found user: {user.username}")
      if kwargs: 
         user.__dict__.update(kwargs)
         user.save()
         return user
   except Exception as e:
      logging.info(f"Error updating vacancy {pk}: {str(e)}")
  

def delete_user(user_pk: str):
  try:
      user = read_user(user_pk)
      if user:
         user.delete(user.pk)
         logging.info(f"User {user.username} deleted.")
      else:
         logging.error(f"User {user_pk} not found.")
  except Exception as e:
      logging.error(f"Error deleting user {user_pk}: {str(e)}")

def disable_user(user_pk: str):
  try:
      user = read_user(user_pk)
      if user: 
         user.disabled = True
         user.save()
         return user
      else:
         logging.error(f"User {user_pk} not found")
  except Exception as e:
      logging.error(f"Error disabling user {user_pk}: {str(e)}")


def enable_user(user_pk: str):
  try:
      user = read_user(user_pk)
      if user: 
         user.disabled = False
         user.save()
         return user
      else:
         logging.error(f"User {user_pk} not found")
  except Exception as e:
      logging.error(f"Error enabling user {user_pk}: {str(e)}")

