import io
from unittest.mock import MagicMock

from fastapi import UploadFile

from app.services import photo_service


def test_upload_to_cloudinary_saves_file_and_returns_local_url(tmp_path, monkeypatch):
    monkeypatch.setattr(photo_service, "UPLOAD_DIR", tmp_path)
    fichier = UploadFile(filename="chaise.jpg", file=io.BytesIO(b"fake-image-bytes"))

    url = photo_service.upload_to_cloudinary(fichier)

    assert url.startswith("http://localhost:")
    assert "/uploads/" in url
    saved_files = list(tmp_path.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"fake-image-bytes"


def test_attach_to_produit_creates_a_photo():
    db = MagicMock()

    photo = photo_service.attach_to_produit(db, produit_id=1, url="http://x/y.jpg", ordre=2)

    assert photo.produit_id == 1
    assert photo.url == "http://x/y.jpg"
    assert photo.ordre == 2
    assert photo.principale is False
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_delete_returns_false_when_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    result = photo_service.delete(db, 999)

    assert result is False


def test_delete_returns_true_when_found():
    db = MagicMock()
    photo = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = photo

    result = photo_service.delete(db, 1)

    assert result is True
    db.delete.assert_called_once_with(photo)


def test_set_principale_returns_none_when_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    result = photo_service.set_principale(db, 999)

    assert result is None


def test_set_principale_unsets_other_photos_for_same_produit():
    db = MagicMock()
    photo = MagicMock(id=5, produit_id=1)
    db.query.return_value.filter.return_value.first.return_value = photo

    result = photo_service.set_principale(db, 5)

    assert result is photo
    assert photo.principale is True
    # the bulk-unset query ran against the same produit_id
    update_call = db.query.return_value.filter.return_value.update
    update_call.assert_called_once_with({"principale": False}, synchronize_session=False)
    db.commit.assert_called_once()
