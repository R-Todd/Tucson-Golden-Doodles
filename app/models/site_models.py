from . import db

# Site-wide metadata, intended for a single row of data
class SiteMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    social_facebook_url = db.Column(db.String(255))
    social_instagram_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<SiteMeta {self.id}>'

# --- Homepage Content Models ---

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(300))
    cta_text = db.Column(db.String(50))
    cta_link = db.Column(db.String(255))

    def __repr__(self):
        return f'<HeroSection {self.title}>'

class AboutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<AboutSection {self.title}>'

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<GalleryImage {self.id}>'