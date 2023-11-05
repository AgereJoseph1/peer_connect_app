# preferences_controller.py

from app  import db
from flask import current_app as app
from app.models import User, Ambiance, Cuisine, DietaryRestriction, BudgetPreference
from sqlalchemy.orm.exc import NoResultFound

class PreferencesController:
    
    @staticmethod
    def update_user_preferences(user_id, ambiance_ids, cuisine_ids, dietary_ids, budget_ids):
        # Find the user
        user = User.query.get(user_id)
        
        # Clear the current preferences
        user.ambiances.clear()
        user.cuisines.clear()
        user.dietary_restrictions.clear()
        user.budgets.clear()
        
        # Update preferences
        if ambiance_ids:
            user.ambiances = Ambiance.query.filter(Ambiance.id.in_(ambiance_ids)).all()
        if cuisine_ids:
            user.cuisines = Cuisine.query.filter(Cuisine.id.in_(cuisine_ids)).all()
        if dietary_ids:
            user.dietary_restrictions = DietaryRestriction.query.filter(DietaryRestriction.id.in_(dietary_ids)).all()
        if budget_ids:
            user.budgets = BudgetPreference.query.filter(BudgetPreference.id.in_(budget_ids)).all()
        
        # Commit the changes
        db.session.commit()
