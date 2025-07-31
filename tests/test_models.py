from datetime import date
from app.models import (
    Parent, Puppy, ParentRole, PuppyStatus, ParentImage, SiteMeta,
    HeroSection, AboutSection, GalleryImage, Review
)

# By grouping tests into classes, the test suite becomes more organized
# and easier to read, especially as the number of models grows.

class TestSiteModels:
    """Tests for site content models like SiteMeta, HeroSection, etc."""

    def test_sitemeta_creation(self, db):
        meta = SiteMeta(phone_number='555-555-5555', email='test@example.com')
        db.session.add(meta)
        db.session.commit()
        assert meta.id is not None

    def test_herosection_creation(self, db):
        hero = HeroSection(main_title='Welcome', subtitle='To the test suite')
        db.session.add(hero)
        db.session.commit()
        assert hero.id is not None
        assert hero.main_title == 'Welcome'

    def test_aboutsection_creation(self, db):
        about = AboutSection(title='About Us', content_html='<p>Some text.</p>')
        db.session.add(about)
        db.session.commit()
        assert about.id is not None
        assert about.content_html == '<p>Some text.</p>'

    def test_galleryimage_creation(self, db):
        image = GalleryImage(image_url='img/gallery.jpg', caption='A test image', sort_order=1)
        db.session.add(image)
        db.session.commit()
        assert image.id is not None
        assert image.sort_order == 1


class TestParentModels:
    """Tests for Parent and ParentImage models and their relationships."""
    
    def test_parent_creation(self, db):
        parent = Parent(name='Buddy', role=ParentRole.DAD, breed='Golden Retriever', is_active=True)
        db.session.add(parent)
        db.session.commit()
        assert parent.id is not None
        assert parent.role == ParentRole.DAD

    def test_parent_image_relationship(self, db):
        parent = Parent(name='Bella', role=ParentRole.MOM, breed='Poodle')
        image = ParentImage(image_url='img/bella.jpg', caption='Bella smiling')
        parent.images.append(image)
        db.session.add(parent)
        db.session.commit()
        assert len(parent.images) == 1
        assert image.parent == parent

    def test_grouped_litters_property(self, db):
        mom = Parent(name='Daisy', role=ParentRole.MOM, breed='Poodle')
        dad = Parent(name='Rocky', role=ParentRole.DAD, breed='Golden Doodle')
        db.session.add_all([mom, dad])
        db.session.commit()
        p1 = Puppy(name='p1', birth_date=date(2023, 1, 1), mom_id=mom.id, dad_id=dad.id)
        p2 = Puppy(name='p2', birth_date=date(2023, 1, 1), mom_id=mom.id, dad_id=dad.id)
        p3 = Puppy(name='p3', birth_date=date(2023, 5, 5), mom_id=mom.id, dad_id=dad.id)
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        grouped = mom.grouped_litters
        assert len(grouped) == 2
        litter_keys = list(grouped.keys())
        assert litter_keys[0][0] == date(2023, 5, 5)
        assert len(grouped[litter_keys[0]]) == 1
        assert len(grouped[litter_keys[1]]) == 2


class TestPuppyModel:
    """Tests for the Puppy model and its relationships."""

    def test_puppy_creation_and_relationships(self, db):
        mom = Parent(name='Lucy', role=ParentRole.MOM)
        dad = Parent(name='Max', role=ParentRole.DAD)
        db.session.add_all([mom, dad])
        db.session.commit()
        puppy = Puppy(
            name='Red Collar', birth_date=date(2023, 12, 25),
            status=PuppyStatus.AVAILABLE, dad_id=dad.id, mom_id=mom.id
        )
        db.session.add(puppy)
        db.session.commit()
        assert puppy.id is not None
        assert puppy.dad == dad
        assert puppy in mom.litters.all()


class TestReviewModel:
    """Tests for the Review model."""

    def test_review_creation(self, db):
        review1 = Review(
            author_name='The Testers',
            testimonial_text='This was a great experience.',
            is_featured=True
        )
        review2 = Review(author_name='Another Tester', testimonial_text='Also good.')
        db.session.add_all([review1, review2])
        db.session.commit()
        assert review1.is_featured is True
        assert review2.is_featured is False

# --- NEW: Add a test class for the AnnouncementBanner model ---
class TestAnnouncementBannerModel:
    """Tests for the AnnouncementBanner model and its relationships."""

    def test_banner_creation_and_relationship(self, db):
        """
        GIVEN an AnnouncementBanner and a Puppy model
        WHEN the banner is linked to a puppy
        THEN check that the relationship is correctly established
        """
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([mom, dad])
        db.session.commit()

        puppy = Puppy(name='Featured Puppy', birth_date=date(2025, 1, 1), mom_id=mom.id, dad_id=dad.id)
        db.session.add(puppy)
        db.session.commit()

        banner = AnnouncementBanner(
            main_text="Test Banner",
            featured_puppy_id=puppy.id
        )
        db.session.add(banner)
        db.session.commit()

        assert banner.id is not None
        assert banner.main_text == "Test Banner"
        # Check that the relationship works correctly
        assert banner.featured_puppy == puppy
