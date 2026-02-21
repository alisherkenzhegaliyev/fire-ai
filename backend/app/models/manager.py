# SQLAlchemy ORM model: managers table
# Columns (from CSV):
#   id (UUID PK), session_id (str, indexed), full_name, position (Specialist/SeniorSpecialist/ChiefSpecialist),
#   skills (ARRAY of str: VIP/ENG/KZ), business_unit (str → FK or name),
#   workload (Int, number of active tickets — incremented on each assignment)
