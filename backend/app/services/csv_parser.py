# CSV Parser Service
# Responsibilities:
#   - parse_and_persist(file: UploadFile, session_id: str, db: Session) -> ParseResult
#       Uses pandas to read the uploaded CSV file
#       Expects three logical tables in a single CSV or three separate sheets:
#         1. Tickets: customer_guid, gender, date_of_birth, segment, description,
#                     attachments, country, region, city, street, building_number
#         2. Managers: full_name, position, skills (comma-separated), business_unit, workload
#         3. Business Units: name, address
#       Persists Ticket, Manager, BusinessUnit records to DB with the given session_id
#       Returns ParseResult: { ticket_count, manager_count, office_count }
#   - validate_row(row: dict, table: str) -> list[str]: returns list of validation errors
