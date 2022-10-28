from tests.sync.models import Sample


def test_replace_one(preset_documents):
    count_1_before = Sample.find_many(Sample.integer == 1).count()
    count_2_before = Sample.find_many(Sample.integer == 2).count()

    a_2 = Sample.find_one(Sample.integer == 2).run()
    Sample.find_one(Sample.integer == 1).replace_one(a_2)

    count_1_after = Sample.find_many(Sample.integer == 1).count()
    count_2_after = Sample.find_many(Sample.integer == 2).count()

    assert count_1_after == count_1_before - 1
    assert count_2_after == count_2_before + 1


def test_replace_self(preset_documents):
    count_1_before = Sample.find_many(Sample.integer == 1).count()
    count_2_before = Sample.find_many(Sample.integer == 2).count()

    a_1 = Sample.find_one(Sample.integer == 1).run()
    a_1.integer = 2
    a_1.replace()

    count_1_after = Sample.find_many(Sample.integer == 1).count()
    count_2_after = Sample.find_many(Sample.integer == 2).count()

    assert count_1_after == count_1_before - 1
    assert count_2_after == count_2_before + 1
