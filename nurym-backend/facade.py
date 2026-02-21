from sqlalchemy.orm import Session
from application.register_user.register_user_application_service import UserRegistrationData
from application.register_user.register_user_application_service import execute as execute_user_registration

def register_user(params: UserRegistrationData, db: Session):
    return execute_user_registration(params, db)