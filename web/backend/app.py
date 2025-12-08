import os
from datetime import datetime
from werkzeug.utils import secure_filename


from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from .db import get_db


app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../static')
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

UPLOAD_FOLDER = os.path.join(os.path.dirname(app.root_path), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    filename = secure_filename(file_storage.filename)
    name, ext = os.path.splitext(filename)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename = f"{name}_{ts}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(filepath)
    return url_for("static", filename=f"uploads/{filename}")


_db = get_db()
users = _db["users"]
pets = _db["pets"]
diary_posts = _db["diary_posts"]


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    try:
        return users.find_one({"_id": ObjectId(uid)})
    except Exception:
        return None


@app.route("/", methods=["GET"])
def index():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("sign-up.html")

    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not email or not password:
        flash("All fields are required.")
        return redirect(url_for("signup"))

    existing = users.find_one({"email": email})
    if existing:
        flash("This email is already registered.")
        return redirect(url_for("signup"))

    password_hash = generate_password_hash(password)
    now = datetime.utcnow()
    result = users.insert_one(
        {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "bio": "",
            "created_at": now,
            "member_since": now,
        }
    )

    session["user_id"] = str(result.inserted_id)
    return redirect(url_for("profile"))


@app.route("/login", methods=["POST"])
def login():
    identifier = request.form.get("email") or request.form.get("username")
    password = request.form.get("password", "")

    if not identifier or not password:
        flash("Please enter email and password.")
        return redirect(url_for("index"))

    identifier = identifier.strip().lower()
    user = users.find_one({"email": identifier}) or users.find_one(
        {"username": identifier}
    )
    if not user or not check_password_hash(user["password_hash"], password):
        flash("Incorrect email or password.")
        return redirect(url_for("index"))

    session["user_id"] = str(user["_id"])
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/profile")
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    if not user.get("member_since") and user.get("created_at"):
        user["member_since"] = user["created_at"]

    user_pets = []
    cursor = pets.find({"owner_id": user["_id"]})
    for p in cursor:
        p["id"] = str(p["_id"])
        user_pets.append(p)

    return render_template("profile.html", user=user, pets=user_pets)


@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("edit-profile.html", user=user)

    bio = request.form.get("bio", "")
    username = request.form.get("username", "").strip() or user["username"]
    phone_number = request.form.get("phone", "").strip()
    full_name = request.form.get("full_name", "").strip()
    avatar_file = request.files.get("avatar")
    avatar_url = save_image(avatar_file)

    update = {
        "bio": bio,
        "username": username,
        "phone_number": phone_number,
        "full_name": full_name,
    }
    if avatar_url:
        update["avatar_url"] = avatar_url

    users.update_one(
        {"_id": user["_id"]},
        {"$set": update},
    )
    return redirect(url_for("profile"))


@app.route("/pets/new", methods=["GET", "POST"])
def add_pet():
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("addPet.html")

    name = request.form.get("name", "").strip()
    pet_type = request.form.get("pet_type", "").strip().lower()
    age_raw = request.form.get("age", "0")
    weight_raw = request.form.get("weight", "")
    breed = request.form.get("breed", "").strip()
    tags = request.form.getlist("tags")

    try:
        age = int(age_raw)
    except ValueError:
        age = 0

    try:
        weight = float(weight_raw) if weight_raw else None
    except ValueError:
        weight = None

    photo_file = request.files.get("photo")
    photo_url = save_image(photo_file)

    if not name or not pet_type:
        flash("Please fill in required fields.")
        return redirect(url_for("add_pet"))

    pet_doc = {
        "owner_id": user["_id"],
        "name": name,
        "pet_type": pet_type,
        "age": age,
        "weight": weight,
        "breed": breed,
        "tags": tags,
        "photo_url": photo_url,
        "fact": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = pets.insert_one(pet_doc)
    return redirect(url_for("pet_detail", pet_id=str(result.inserted_id)))


@app.route("/pets/<pet_id>/edit", methods=["GET", "POST"])
def edit_pet(pet_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    try:
        pet = pets.find_one({"_id": ObjectId(pet_id), "owner_id": user["_id"]})
    except Exception:
        pet = None

    if not pet:
        flash("Pet not found.")
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("editPet.html", pet=pet, pet_id=pet_id)

    name = request.form.get("name", "").strip()
    pet_type = request.form.get("pet_type", "").strip().lower()
    age_raw = request.form.get("age", "")
    weight_raw = request.form.get("weight", "")
    breed = request.form.get("breed", "").strip()
    tags = request.form.getlist("tags")
    photo_file = request.files.get("photo")

    try:
        age = int(age_raw) if age_raw else pet.get("age", 0)
    except ValueError:
        age = pet.get("age", 0)

    try:
        weight = float(weight_raw) if weight_raw else pet.get("weight")
    except ValueError:
        weight = pet.get("weight")

    update = {
        "name": name or pet["name"],
        "pet_type": pet_type or pet.get("pet_type", ""),
        "age": age,
        "weight": weight,
        "breed": breed or pet.get("breed", ""),
        "tags": tags or pet.get("tags", []),
        "updated_at": datetime.utcnow(),
    }

    new_photo_url = save_image(photo_file)
    if new_photo_url:
        update["photo_url"] = new_photo_url

    pets.update_one({"_id": pet["_id"]}, {"$set": update})
    return redirect(url_for("pet_detail", pet_id=pet_id))


@app.route("/pets/<pet_id>")
def pet_detail(pet_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    try:
        pet = pets.find_one({"_id": ObjectId(pet_id), "owner_id": user["_id"]})
    except Exception:
        pet = None

    if not pet:
        flash("Pet not found.")
        return redirect(url_for("profile"))

    pet_type = (pet.get("pet_type") or "").lower()
    pet["_id"] = str(pet["_id"])

    template_name = "hamsterpet.html"
    if pet_type == "dog":
        template_name = "dogpet.html"
    elif pet_type == "cat":
        template_name = "catpet.html"
    elif pet_type == "hamster":
        template_name = "hamsterpet.html"
    elif pet_type == "rabbit":
        template_name = "rabbitpet.html"
    elif pet_type == "bird":
        template_name = "birdpet.html"

    # Get reminders from database, or use default ones if not set
    if "reminders" in pet and pet["reminders"]:
        reminders = pet["reminders"]
    else:
        base_reminders = []
        if pet_type == "dog":
            base_reminders = [
                "Morning walk",
                "Refill water bowl",
                "Give flea medication",
                "Schedule vet checkup",
            ]
        elif pet_type == "cat":
            base_reminders = [
                "Scoop the litter box",
                "Get cat treats",
                "Clean the ears",
                "Give flea/tick treatment",
            ]
        elif pet_type == "rabbit":
            base_reminders = [
                "Clean cage",
                "Refill hay",
                "Trim nails",
                "Check teeth",
            ]
        elif pet_type == "bird":
            base_reminders = [
                "Clean cage",
                "Refresh seeds and water",
                "Spray bath",
                "Check feathers",
            ]
        elif pet_type == "hamster":
            base_reminders = [
                "Clean cage",
                "Refill food bowl",
                "Change bedding",
            ]
        reminders = [{"text": text} for text in base_reminders]

    ctx = {"pet": pet, "pet_id": pet_id, "reminders": reminders}

    if template_name == "hamsterpet.html":
        fact_text = (
            "Hamsters have cheek pouches that can extend all the way back to their shoulders, "
            "allowing them to store a surprising amount of food."
        )
        ctx["fact_text"] = fact_text

    return render_template(template_name, **ctx)


@app.route("/pets/<pet_id>/reminders", methods=["POST"])
def save_reminders(pet_id):
    user = current_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    try:
        pet_oid = ObjectId(pet_id)
    except:
        return jsonify({"error": "Invalid pet ID"}), 400

    pet = pets.find_one({"_id": pet_oid, "owner_id": user["_id"]})
    if not pet:
        return jsonify({"error": "Pet not found"}), 404

    data = request.get_json()
    reminders_list = data.get("reminders", [])

    pets.update_one(
        {"_id": pet_oid},
        {"$set": {"reminders": reminders_list}}
    )

    return jsonify({"success": True})


@app.route("/pets/<pet_id>/diary", methods=["GET"])
def pet_diary_list(pet_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    try:
        pet = pets.find_one({"_id": ObjectId(pet_id), "owner_id": user["_id"]})
    except Exception:
        pet = None

    if not pet:
        flash("Pet not found.")
        return redirect(url_for("profile"))

    pet_id_str = str(pet["_id"])
    posts = list(
        diary_posts.find({"pet_id": pet_id_str}).sort("created_at", -1)
    )

    return render_template(
        "pet-diary-list.html",
        pet=pet,
        posts=posts,
        pet_id=pet_id_str,
        str=str,
    )


@app.route("/pets/<pet_id>/diary/new", methods=["GET", "POST"])
def add_diary_post(pet_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    try:
        pet = pets.find_one({"_id": ObjectId(pet_id), "owner_id": user["_id"]})
    except Exception:
        pet = None

    if not pet:
        flash("Pet not found.")
        return redirect(url_for("profile"))

    if request.method == "GET":
        pet["_id"] = str(pet["_id"])
        return render_template("addPost.html", pet=pet, pet_id=pet["_id"])

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    photo_file = request.files.get("photo")
    uploaded_url = save_image(photo_file)
    fallback_url = request.form.get("photo_url", "").strip()
    photo_url = uploaded_url or (fallback_url or None)

    if not title:
        flash("Title is required.")
        return redirect(url_for("add_diary_post", pet_id=pet_id))

    post = {
        "pet_id": str(pet["_id"]),
        "owner_id": str(user["_id"]),
        "title": title,
        "description": description,
        "photo_url": photo_url,
        "created_at": datetime.utcnow(),
        "is_public": True,
    }
    result = diary_posts.insert_one(post)
    return redirect(url_for("diary_detail", post_id=str(result.inserted_id)))


@app.route("/pets/<pet_id>/delete", methods=["POST"])
def delete_pet(pet_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    try:
        pet = pets.find_one({"_id": ObjectId(pet_id), "owner_id": user["_id"]})
    except Exception:
        pet = None
    if not pet:
        flash("Pet not found.")
        return redirect(url_for("profile"))
    pets.delete_one({"_id": pet["_id"]})
    diary_posts.delete_many({"pet_id": str(pet["_id"])})
    return redirect(url_for("profile"))


@app.route("/diary/<post_id>")
def diary_detail(post_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    try:
        post = diary_posts.find_one({"_id": ObjectId(post_id)})
    except Exception:
        post = None

    if not post:
        flash("Post not found.")
        return redirect(url_for("profile"))

    pet = pets.find_one({"_id": ObjectId(post["pet_id"])})
    owner = (
        users.find_one({"_id": ObjectId(post["owner_id"])})
        if post.get("owner_id")
        else None
    )

    if pet:
        pet["_id"] = str(pet["_id"])

    return render_template("postDetail.html", post=post, pet=pet, owner=owner)


@app.route("/diary/<post_id>/delete", methods=["POST"])
def delete_diary_post(post_id):
    user = current_user()
    if not user:
        return redirect(url_for("index"))

    try:
        post = diary_posts.find_one({"_id": ObjectId(post_id)})
    except Exception:
        post = None

    if not post:
        flash("Post not found.")
        return redirect(url_for("profile"))

    if str(post.get("owner_id")) != str(user["_id"]):
        flash("You cannot delete this post.")
        return redirect(url_for("profile"))

    diary_posts.delete_one({"_id": ObjectId(post_id)})

    pet_id = post.get("pet_id")
    if pet_id:
        return redirect(url_for("pet_diary_list", pet_id=pet_id))

    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True)
