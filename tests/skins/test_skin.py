"""KS3 and KS4, a Skin's own validation, see docs/specs/skins/tests.md#skin."""

import unicodedata

import pytest

from paranoid.skins import Skin, SkinError, prompt_hash

BAD_VALUES = {
    "a name with a capital": {"name": "Bakery"},
    "an empty intro": {"intro": "  \r\n "},
    "three channels": {"channels": ("Ashford", "Brill", "Corran")},
    "a channel name with a comma": {"channels": ("Ashford", "Brill, East", "Corran", "Dunmore")},
    "a bet_word with a comma": {"bet_word": "sent,out"},
    "an empty reading_word": {"reading_word": " "},
    "two names equal ignoring case": {"channels": ("Ashford", "Brill", "Corran", "ASHFORD")},
    "a tool_name with a space": {"tool_name": "send bread"},
    "a tool_name of 65 characters": {"tool_name": "s" * 65},
    "a bets_name with a capital": {"bets_name": "Split"},
    "a notes_param with a space": {"notes_param": "my note"},
    "an empty compute_param": {"compute_param": ""},
    "a notes_name equal to tool_name": {"notes_name": "send_bread"},
}


@pytest.mark.parametrize("overrides", BAD_VALUES.values(), ids=BAD_VALUES.keys())
def test_ks3_each_bad_value_raises(overrides, make_skin):
    with pytest.raises(SkinError):
        make_skin(**overrides)


def test_ks3_a_bets_name_equal_to_tool_name_builds(make_skin):
    assert make_skin(bets_name="send_bread").bets_name == "send_bread"


def test_ks3_two_tools_may_share_a_parameter_name(make_skin):
    skin = make_skin(notes_param="words", compute_param="words")
    assert skin.notes_param == skin.compute_param == "words"


def test_ks3_the_longest_tool_name_builds(make_skin):
    assert make_skin(tool_name="s" * 64).tool_name == "s" * 64


@pytest.mark.parametrize(
    "overrides",
    [{"intro": 7}, {"channels": "Ashford"}, {"channels": ("Ashford", "Brill", "Corran", 4)}],
    ids=["an int field", "channels as one string", "an int channel"],
)
def test_ks3_a_value_that_is_not_text_raises(overrides, make_skin):
    with pytest.raises(SkinError):
        make_skin(**overrides)


def test_ks3_an_error_never_holds_the_skins_text(make_skin):
    with pytest.raises(SkinError) as caught:
        make_skin(channels=("Ashford", "Brill", "Corran,Secret", "Dunmore"))
    assert "channels[2]" in str(caught.value) and "Secret" not in str(caught.value)


def test_ks4_text_is_stored_normalised(make_skin):
    skin = make_skin(ask="  text  \r\nmore \r")
    assert skin.ask == "text\nmore"


def test_ks4_channels_are_stored_as_a_tuple(make_skin, clean):
    assert make_skin(channels=list(clean["channels"])).channels == clean["channels"]


def test_ks4_nfd_and_nfc_are_one_name(make_skin):
    nfc = unicodedata.normalize("NFC", "Zürich")
    nfd = unicodedata.normalize("NFD", "Zürich")
    assert nfc != nfd
    a = make_skin(channels=("Ashford", "Brill", "Corran", nfc))
    b = make_skin(channels=("Ashford", "Brill", "Corran", nfd))
    assert a.channels[3] == nfc and a == b


def test_ks4_skins_differing_only_in_whitespace_or_form_are_equal(make_skin, clean):
    plain = make_skin()
    messy = make_skin(
        intro=" " + clean["intro"].replace(" ", " \r\n", 1) + "\r\n",
        question=unicodedata.normalize("NFD", clean["question"]) + "   ",
    )
    tidy = make_skin(intro=clean["intro"].replace(" ", "\n", 1))
    assert messy == tidy and hash(messy) == hash(tidy) and prompt_hash(messy) == prompt_hash(tidy)
    assert plain == make_skin(question="\r\n" + clean["question"] + " \r")
    assert isinstance(plain, Skin)
