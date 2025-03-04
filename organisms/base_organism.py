# Add this method to your base organism class or extend each individual organism class

class BaseOrganism:
    """Base class for all organisms."""
    id_counter = 0
    
    @classmethod
    def reset_id_counter(cls):
        """Reset the class's ID counter to 0."""
        cls.id_counter = 0
    
    # ...existing code...
