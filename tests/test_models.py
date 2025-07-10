from datetime import date
from app.models import Parent, Puppy, ParentRole, PuppyStatus, ParentImage

def test_parent_creation(db):
    """
    GIVEN a Parent model
    WHEN a new Parent is created
    THEN check the name, role, and breed fields are defined correctly
    """
    parent = Parent(name='Buddy', role=ParentRole.DAD, breed='Golden Retriever')
    db.session.add(parent)
    db.session.commit()

    assert parent.id is not None
    assert parent.name == 'Buddy'
    assert parent.role == ParentRole.DAD

def test_grouped_litters_property(db):
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
    assert litter_keys[0][0] == date(2023, 5, 5) # newest first
    assert len(grouped[litter_keys[1]]) == 2 # 2 puppies in the first litter

def test_parent_image_relationship(db):
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