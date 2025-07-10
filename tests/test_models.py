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
        """
        GIVEN a SiteMeta model
        WHEN a new SiteMeta object is created
        THEN check the phone_number and email fields are defined correctly
        """
        meta = SiteMeta(phone_number='555-555-5555', email='test@example.com')
        db.session.add(meta)
        db.session.commit()

        assert meta.id is not None
        assert meta.phone_number == '555-555-5555'
        assert meta.email == 'test@example.com'

    def test_herosection_creation(self, db):
        """
        GIVEN a HeroSection model
        WHEN a new HeroSection object is created
        THEN check the title and subtitle fields are defined correctly
        """
        hero = HeroSection(title='Welcome', subtitle='To the test suite')
        db.session.add(hero)
        db.session.commit()

        assert hero.id is not None
        assert hero.title == 'Welcome'

    def test_aboutsection_creation(self, db):
        """
        GIVEN an AboutSection model
        WHEN a new AboutSection object is created
        THEN check the title and content_html fields are defined correctly
        """
        about = AboutSection(title='About Us', content_html='<p>Some text.</p>')
        db.session.add(about)
        db.session.commit()

        assert about.id is not None
        assert about.content_html == '<p>Some text.</p>'

    def test_galleryimage_creation(self, db):
        """
        GIVEN a GalleryImage model
        WHEN a new GalleryImage object is created
        THEN check the image_url and sort_order fields are defined correctly
        """
        image = GalleryImage(image_url='img/gallery.jpg', caption='A test image', sort_order=1)
        db.session.add(image)
        db.session.commit()

        assert image.id is not None
        assert image.sort_order == 1
        assert image.caption == 'A test image'


class TestParentModels:
    """Tests for Parent and ParentImage models and their relationships."""

    def test_parent_creation(self, db):
        """
        GIVEN a Parent model
        WHEN a new Parent is created
        THEN check the name, role, and is_active fields are defined correctly
        """
        parent = Parent(name='Buddy', role=ParentRole.DAD, breed='Golden Retriever', is_active=True)
        db.session.add(parent)
        db.session.commit()

        assert parent.id is not None
        assert parent.name == 'Buddy'
        assert parent.role == ParentRole.DAD
        assert parent.is_active is True

    def test_parent_image_relationship(self, db):
        """
        GIVEN a Parent and ParentImage model
        WHEN a ParentImage is added to a Parent's images list
        THEN check that the relationship is correctly established
        """
        parent = Parent(name='Bella', role=ParentRole.MOM, breed='Poodle')
        image = ParentImage(image_url='img/bella.jpg', caption='Bella smiling')

        parent.images.append(image)
        db.session.add(parent)
        db.session.commit()

        assert len(parent.images) == 1
        assert parent.images[0].caption == 'Bella smiling'
        assert image.parent == parent

    def test_grouped_litters_property(self, db):
        """
        GIVEN a Parent and several Puppy models
        WHEN the `grouped_litters` property is accessed
        THEN check that puppies are grouped correctly by birth date and parents
        """
        mom = Parent(name='Daisy', role=ParentRole.MOM, breed='Poodle')
        dad = Parent(name='Rocky', role=ParentRole.DAD, breed='Golden Doodle')
        db.session.add_all([mom, dad])
        db.session.commit()

        # Litter 1
        p1 = Puppy(name='p1', birth_date=date(2023, 1, 1), mom_id=mom.id, dad_id=dad.id)
        p2 = Puppy(name='p2', birth_date=date(2023, 1, 1), mom_id=mom.id, dad_id=dad.id)
        # Litter 2
        p3 = Puppy(name='p3', birth_date=date(2023, 5, 5), mom_id=mom.id, dad_id=dad.id)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        grouped = mom.grouped_litters
        assert len(grouped) == 2  # Should be two distinct litters

        litter_keys = list(grouped.keys())
        # The property should order litters by date descending
        assert litter_keys[0][0] == date(2023, 5, 5) # newest first
        assert len(grouped[litter_keys[0]]) == 1 # 1 puppy in the newest litter
        assert len(grouped[litter_keys[1]]) == 2 # 2 puppies in the older litter


class TestPuppyModel:
    """Tests for the Puppy model and its relationships."""

    def test_puppy_creation_and_relationships(self, db):
        """
        GIVEN a Puppy model
        WHEN a new Puppy is created with parent relationships
        THEN check its fields and that the back-references from parents work
        """
        mom = Parent(name='Lucy', role=ParentRole.MOM)
        dad = Parent(name='Max', role=ParentRole.DAD)
        db.session.add_all([mom, dad])
        db.session.commit()

        puppy = Puppy(
            name='Red Collar',
            birth_date=date(2023, 12, 25),
            status=PuppyStatus.AVAILABLE,
            dad_id=dad.id,
            mom_id=mom.id
        )
        db.session.add(puppy)
        db.session.commit()

        assert puppy.id is not None
        assert puppy.name == 'Red Collar'
        assert puppy.status == PuppyStatus.AVAILABLE
        assert puppy.dad == dad
        assert puppy.mom == mom
        assert puppy in dad.litters.all()
        assert puppy in mom.litters.all()


class TestReviewModel:
    """Tests for the Review model."""

    def test_review_creation(self, db):
        """
        GIVEN a Review model
        WHEN a new Review is created
        THEN check the author_name and is_featured fields are correct
        """
        # Test a featured review
        review1 = Review(
            author_name='The Testers',
            testimonial_text='This was a great experience.',
            is_featured=True
        )
        # Test a non-featured review (default value)
        review2 = Review(
            author_name='Another Tester',
            testimonial_text='Also good.'
        )
        db.session.add_all([review1, review2])
        db.session.commit()

        assert review1.id is not None
        assert review1.author_name == 'The Testers'
        assert review1.is_featured is True

        assert review2.id is not None
        assert review2.is_featured is False # Check default value