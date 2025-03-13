from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy()

db.init_app(app)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=True, nullable=False)
    last_name = db.Column(db.String(20), unique=False, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Custom string representation of the Profile object
    def __repr__(self):
        return f"Profile(id={self.id}, Name: {self.first_name} {self.last_name}, Age: {self.age})"


@app.route('/userget', methods=['GET'])
def get_users():
    # Retrieve data from the database
    profiles = Profile.query.all()

    # Convert profile data to a list of dictionaries
    profiles_list = [
        {"id": profile.id, "first_name": profile.first_name, "last_name": profile.last_name, "age": profile.age} for
        profile in profiles]

    print(profiles_list)
    return jsonify(profiles_list)


@app.route('/adduser', methods=['POST'])
def add_user():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    age = data.get('age')

    if not first_name or not last_name or not age:
        return jsonify({"error": "Missing profile details"}), 400

    try:
        profile = Profile(first_name=first_name, last_name=last_name, age=age)

        existing_user = Profile.query.filter_by(first_name=first_name).first()
        if existing_user:
            return jsonify({"message": "user already exist please try"}), 400

        db.session.add(profile)
        db.session.commit()

        return jsonify({"message": "user created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/updateuser/<int:id>', methods=['PUT', 'PATCH'])
def update_user(id):
    try:
        profile = Profile.query.get(id)

        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        age = data.get('age')

        if request.method == "PUT":

            if not first_name or not last_name or not age:
                return jsonify({"message": "Missiong some details"}), 200

            profile.first_name = first_name
            profile.last_name = last_name
            profile.age = age

        elif request.method == "PATCH":

            if first_name:
                profile.first_name = first_name

            if last_name:
                profile.last_name = last_name

            elif age is not None:
                profile.age = age

        db.session.commit()

        return jsonify({"message": "profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/deleteuser/<int:id>', methods=["DELETE"])
def delete(id):
    try:

        profile = Profile.query.get(id)

        if profile:
            db.session.delete(profile)
            db.session.commit()
            return jsonify({"message": "Profile is deleted"}), 200

        return jsonify({"message": "Profile not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)