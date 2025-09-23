# app/routes/admin/views/breed_views.py

from ..views.base import AdminModelView
from app.models import Parent

class BreedAdminView(AdminModelView):
    """
    A custom admin view for the Breed model that displays associated parents
    and those without an assigned breed.
    """
    
    # --- Template Configuration ---
    # Point to the new custom list template we will create.
    list_template = 'admin/breed/list.html'
    
    # --- Column Configuration ---
    # Define the columns that will appear in the standard list view table.
    column_list = ('name', 'parents')
    
    # Provide a more user-friendly label for the 'parents' column.
    column_labels = {
        'name': 'Breed Name',
        'parents': 'Assigned Parents'
    }

    def list_view(self):
        """
        Overrides the default list view to inject additional data into the template.
        """
        # Get the default data from the parent class.
        self._template_args.update(self.get_list_template_args())

        # --- Custom Data Injection ---
        # 1. Fetch all parents that do not have a breed assigned.
        unassigned_parents = Parent.query.filter(Parent.breed_id == None).all()
        self._template_args['unassigned_parents'] = unassigned_parents
        
        # 2. Fetch all breeds and include their parent relationships.
        all_breeds = self.model.query.all()
        self._template_args['all_breeds'] = all_breeds

        return self.render(self.list_template, **self._template_args)