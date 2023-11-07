from app.models import InviteToken, GroupMember, db
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

class InviteTokenController:
    """
    Controller responsible for handling operations related to invite tokens,
    including their creation, validation, redemption, and revocation.
    """

    @staticmethod
    def generate_invite_token(group_id):
        """
        Generates a new invite token for a group.

        Parameters:
        - group_id: Integer ID of the group for which to generate the invite token.

        Returns:
        - String representing the generated invite token.

        Raises:
        - BadRequest: An error occurred during token generation, possibly due
                       to database issues.

        Note:
        - This method commits the new invite token to the database and
          rolls back the session in case of any exceptions.
        """
        try:
            invite_token = InviteToken(group_id=group_id)
            db.session.add(invite_token)
            db.session.commit()
            return invite_token.token
        except SQLAlchemyError as e:
            db.session.rollback()
            # Proper logging of the exception can be implemented here
            raise BadRequest("Could not generate invite token.")

    @staticmethod
    def validate_invite_token(token):
        """
        Validates an invite token.

        Parameters:
        - token: String token to validate.

        Returns:
        - Boolean indicating whether the token is valid.

        Note:
        - This method does not alter the database state.
        """
        invite_token = InviteToken.query.filter_by(token=token).first()
        return bool(invite_token and invite_token.is_valid())
    
    @staticmethod
    def redeem_invite_token(token, user_id):
        """
        Redeems an invite token to add a user as a member of the group associated with the token.

        Parameters:
        - token: String token to redeem.
        - user_id: Integer ID of the user redeeming the invite token.

        Returns:
        - The new GroupMember instance representing the user's membership in the group.

        Raises:
        - BadRequest: The invite token is invalid, expired, or the user is already a member of the group.

        Note:
        - Redeeming a token will remove it from the database.
        - This method handles the database transaction, including rollback in case of exceptions.
        """
        try:
            invite_token = InviteToken.query.filter_by(token=token).first()
            if not invite_token or not invite_token.is_valid():
                raise BadRequest("Invalid or expired invite token.")

            if GroupMember.query.filter_by(group_id=invite_token.group_id, user_id=user_id).first():
                raise BadRequest("User is already a member of this group.")

            new_member = GroupMember(group_id=invite_token.group_id, user_id=user_id)
            db.session.add(new_member)
            db.session.delete(invite_token)
            db.session.commit()
            return new_member
        except SQLAlchemyError as e:
            db.session.rollback()
            # Proper logging of the exception can be implemented here
            raise BadRequest("Could not redeem invite token.")
        
    @staticmethod
    def revoke_invite_token(token):
        """
        Revokes an invite token, rendering it unusable for future redemptions.

        Parameters:
        - token: String token to revoke.

        Raises:
        - NotFound: The invite token does not exist.
        - BadRequest: There was an issue with revoking the invite token.

        Note:
        - This method handles the database transaction, including rollback in case of exceptions.
        """
        try:
            invite_token = InviteToken.query.filter_by(token=token).first()
            if not invite_token:
                raise NotFound("Invite token not found.")

            db.session.delete(invite_token)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            # Proper logging of the exception can be implemented here
            raise BadRequest("Could not revoke invite token.")
