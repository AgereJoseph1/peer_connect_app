# preferences_controller.py

from app import db
from flask import current_app as app
from app.models import User, Ambiance, Cuisine, DietaryRestriction, BudgetPreference
from sqlalchemy.orm.exc import NoResultFound
from collections import Counter
from sqlalchemy.sql import func

class PreferencesController:
    
    @staticmethod
    def update_user_preferences(user_id, ambiance_ids, cuisine_ids, dietary_ids, budget_ids):
        # Find the user
        user = User.query.get(user_id)
        
        # Clear the current preferences
        user.ambiances.clear()
        user.cuisines.clear()
        user.dietary_restrictions.clear()
        user.budget_preferences.clear()  # Corrected from budgets to budget_preferences
        
        # Update preferences
        if ambiance_ids:
            user.ambiances = Ambiance.query.filter(Ambiance.id.in_(ambiance_ids)).all()
        if cuisine_ids:
            user.cuisines = Cuisine.query.filter(Cuisine.id.in_(cuisine_ids)).all()
        if dietary_ids:
            user.dietary_restrictions = DietaryRestriction.query.filter(DietaryRestriction.id.in_(dietary_ids)).all()
        if budget_ids:
            user.budget_preferences = BudgetPreference.query.filter(BudgetPreference.id.in_(budget_ids)).all()  # Corrected from budgets to budget_preferences
        
        # Commit the changes
        db.session.commit()

    @staticmethod
    def aggregate_preferences(user_ids):
        """
        Aggregate preferences for a list of users and find the most common ones.

        :param user_ids: List of user IDs
        :return: A dictionary with the most common preferences in each category
        """

        # Query for most common ambiance preferences
        ambiance_counts = Counter(
            name for name, in db.session.query(Ambiance.name)
            .join(User.ambiances)
            .filter(User.id.in_(user_ids))
            .group_by(Ambiance.name)
            .order_by(func.count(Ambiance.id).desc())
            .all()
        )

        # Query for most common cuisine preferences
        cuisine_counts = Counter(
            name for name, in db.session.query(Cuisine.name)
            .join(User.cuisines)
            .filter(User.id.in_(user_ids))
            .group_by(Cuisine.name)
            .order_by(func.count(Cuisine.id).desc())
            .all()
        )

        # Query for most common dietary restrictions
        dietary_counts = Counter(
            name for name, in db.session.query(DietaryRestriction.name)
            .join(User.dietary_restrictions)
            .filter(User.id.in_(user_ids))
            .group_by(DietaryRestriction.name)
            .order_by(func.count(DietaryRestriction.id).desc())
            .all()
        )

        # Query for most common budget preferences
        budget_counts = Counter(
            name for name, in db.session.query(BudgetPreference.name)
            .join(User.budget_preferences)
            .filter(User.id.in_(user_ids))
            .group_by(BudgetPreference.name)
            .order_by(func.count(BudgetPreference.id).desc())
            .all()
        )

        # Determine the most common preference in each category
        common_ambiance = ambiance_counts.most_common(1)[0] if ambiance_counts else (None,)
        common_cuisine = cuisine_counts.most_common(1)[0] if cuisine_counts else (None,)
        common_dietary = dietary_counts.most_common(1)[0] if dietary_counts else (None,)
        common_budget = budget_counts.most_common(1)[0] if budget_counts else (None,)

        # Return the most common preferences
        return {
            'ambiance': common_ambiance[0],
            'cuisine': common_cuisine[0],
            'dietary': common_dietary[0],
            'budget': common_budget[0]
        }
