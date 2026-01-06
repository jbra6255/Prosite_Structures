from base_manager import DatabaseManager
from user_repo import UserRepository
from structure_repo import StructureRepository
from project_repo import ProjectRepository

# The order matters here. DatabaseManager should be last or initialized specifically.
class AppDataManager(UserRepository, StructureRepository, ProjectRepository, DatabaseManager):
    def __init__(self, db_path="structures.db"):
        # Initialize the base manager which sets up db_path and logger
        super().__init__(db_path)