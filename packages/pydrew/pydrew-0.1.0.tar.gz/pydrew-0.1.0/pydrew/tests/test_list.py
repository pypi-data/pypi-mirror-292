import pytest
from pydrew.modules.list import List


def test_init():
    lst = List([1, 2, 3])
    assert lst.to_list() == [1, 2, 3]


def test_init_empty():
    lst = List()
    assert lst.to_list() == []


def test_alternate_init():
    lst = List().concat([1, 2, 3])
    assert lst.to_list() == [1, 2, 3]


def test_concat():
    lst = List([1, 2, 3]).concat([4, 5, 6])
    assert lst.to_list() == [1, 2, 3, 4, 5, 6]


def test_add_concat():
    lst = List([1, 2, 3]) + List([4, 5, 6])
    assert lst.to_list() == [1, 2, 3, 4, 5, 6]


def test_subtract():
    lst = List([1, 2, 3, 4, 5, 6]) - List([4, 5, 6])
    assert lst.to_list() == [1, 2, 3]


def test_add_item():
    lst = List([1, 2, 3]).add(4)
    assert lst.to_list() == [1, 2, 3, 4]


def test_add_item_at():
    lst = List([1, 2, 3]).add(4, 1)
    assert lst.to_list() == [1, 4, 2, 3]


def test_add_item_at_end():
    lst = List([1, 2, 3])
    lst = lst.add(4, lst.count())
    assert lst.to_list() == [1, 2, 3, 4]


def test_add_item_out_of_bounds():
    lst = List([1, 2, 3])
    lst = lst.add(4, 10)
    assert lst.to_list() == [1, 2, 3, 4]


def test_remove_item():
    lst = List([1, 2, 3]).remove(2)
    assert lst.to_list() == [1, 3]


def test_remove_item_at():
    lst = List([1, 2, 3])
    removed = lst.remove_at(1)
    assert lst.to_list() == [1, 3] and removed == 2


def test_remove_item_out_of_bounds():
    with pytest.raises(IndexError):
        List([1, 2, 3]).remove_at(10)


def test_element_at_index():
    lst = List([1, 2, 3])
    assert lst.at_index(1) == 2


def test_element_at_index_out_of_bounds():
    with pytest.raises(IndexError):
        List([1, 2, 3]).at_index(10)


def test_first():
    lst = List([1, 2, 3])
    assert lst.first() == 1


def test_first_empty():
    lst = List()
    assert lst.first() is None


def test_last():
    lst = List([1, 2, 3])
    assert lst.last() == 3


def test_last_empty():
    lst = List()
    assert lst.last() is None


def test_where():
    lst = List([1, 2, 3, 4, 5, 6])
    assert lst.where(lambda x: x % 2 == 0).to_list() == [2, 4, 6]


def test_select():
    lst = List([1, 2, 3, 4, 5, 6])
    assert lst.select(lambda x: x * 2).to_list() == [2, 4, 6, 8, 10, 12]


def test_sort():
    lst = List([3, 1, 2, 5, 4])
    assert lst.sort(lambda x: x).to_list() == [1, 2, 3, 4, 5]


def test_group_by_func():
    lst = List([1, 2, 3, 4, 5, 6])
    lst = lst.group_by_func(lambda x: x % 2)
    assert lst.to_dict() == {0: [2, 4, 6], 1: [1, 3, 5]}


@pytest.mark.parametrize("key", ["name", "age", "not_exists"])
def test_group_by_key(key: str):
    if key == "not_exists":
        with pytest.raises(KeyError):
            List([{"name": "John", "age": 25}, {"name": "Jane",
                  "age": 25}, {"name": "Jack", "age": 30}]).group_by(key)
    else:
        lst = List([{"name": "John", "age": 25}, {"name": "Jane",
                                                  "age": 25}, {"name": "Jack", "age": 30}])
        grouped = lst.group_by("age")
        assert grouped.to_dict() == {25: [{"name": "John", "age": 25}, {
            "name": "Jane", "age": 25}], 30: [{"name": "Jack", "age": 30}]}


def reverse():
    lst = List([1, 2, 3, 4, 5])
    assert lst.reverse().to_list() == [5, 4, 3, 2, 1]


def test_count():
    lst = List([1, 2, 3, 4, 5])
    assert lst.count() == 5


def test_count_empty():
    lst = List()
    assert lst.count() == 0


def test_clear():
    lst = List([1, 2, 3, 4, 5])
    assert lst.clear().to_list() == []


def test_set_item():
    lst = List([1, 2, 3, 4, 5])
    lst[1] = 10
    assert lst.to_list() == [1, 10, 3, 4, 5]


def test_get_item():
    lst = List([1, 2, 3, 4, 5])
    assert lst[1] == 2


def test_del_item():
    lst = List([1, 2, 3, 4, 5])
    del lst[1]
    assert lst.to_list() == [1, 3, 4, 5]


def test_iter():
    lst = List([1, 2, 3, 4, 5])
    assert [x for x in lst] == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("val,expected", [([1, 2, 3, 4], True), ([], False)])
def test_bool(val: list[int], expected: bool):
    lst = List([1, 2, 3, 4, 5])
    assert bool(lst) is True


@pytest.mark.parametrize("lst1,lst2,expected", [([1, 2, 3], [1, 2, 3], True), ([1, 2, 3], [1, 2, 4], False)])
def test_equals(lst1: list[int], lst2: list[int], expected: bool):
    assert (lst1 == lst2) is expected


@pytest.mark.parametrize("lst1,lst2,expected", [([1, 2, 3], [1, 2, 3], False), ([1, 2, 3], [1, 2, 4], True)])
def test_not_equals(lst1: list[int], lst2: list[int], expected: bool):
    assert (lst1 != lst2) is expected
