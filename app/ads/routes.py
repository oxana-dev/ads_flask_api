from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Ad

ads_bp = Blueprint("ads", __name__, url_prefix="/ads")


def _current_user_id() -> int:
    return int(get_jwt_identity())


@ads_bp.get("/")
def list_ads():
    ads = Ad.query.order_by(Ad.created_at.desc()).all()
    return jsonify([ad.to_dict() for ad in ads]), 200


@ads_bp.get("/<int:ad_id>")
def get_ad(ad_id: int):
    ad = db.session.get(Ad, ad_id)
    if ad is None:
        return jsonify({"error": "Ad not found"}), 404
    return jsonify(ad.to_dict()), 200


@ads_bp.post("/")
@jwt_required()
def create_ad():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()

    if not title or not description:
        return jsonify({"error": "title and description are required"}), 400

    ad = Ad(title=title, description=description, owner_id=_current_user_id())
    db.session.add(ad)
    db.session.commit()
    return jsonify(ad.to_dict()), 201


@ads_bp.patch("/<int:ad_id>")
@jwt_required()
def update_ad(ad_id: int):
    ad = db.session.get(Ad, ad_id)
    if ad is None:
        return jsonify({"error": "Ad not found"}), 404
    if ad.owner_id != _current_user_id():
        return jsonify({"error": "You are not the owner of this ad"}), 403

    data = request.get_json(silent=True) or {}
    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        ad.title = title
    if "description" in data:
        description = (data.get("description") or "").strip()
        if not description:
            return jsonify({"error": "description cannot be empty"}), 400
        ad.description = description

    db.session.commit()
    return jsonify(ad.to_dict()), 200


@ads_bp.delete("/<int:ad_id>")
@jwt_required()
def delete_ad(ad_id: int):
    ad = db.session.get(Ad, ad_id)
    if ad is None:
        return jsonify({"error": "Ad not found"}), 404
    if ad.owner_id != _current_user_id():
        return jsonify({"error": "You are not the owner of this ad"}), 403

    db.session.delete(ad)
    db.session.commit()
    return "", 204