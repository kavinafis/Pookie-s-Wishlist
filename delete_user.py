from app import app, db, User

def delete_user(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User '{username}' does not exist.")
            return
        db.session.delete(user)
        db.session.commit()
        print(f"User '{username}' deleted successfully.")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <username>")
    else:
        delete_user(sys.argv[1])
