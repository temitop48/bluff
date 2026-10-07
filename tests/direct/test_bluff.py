"""Direct-mode tests for the BLUFF Intelligent Contract."""

import pytest

from tests.direct.conftest import to_hex


CONTRACT_PATH = "contracts/bluff.py"

SCENARIO = """
You are trapped in a locked laboratory.

Available objects:
- metal chair
- glass bottle
- electrical cable

There is a ventilation opening near the ceiling.

Objective:
Escape the room without breaking the door.
"""

RULES = """
- Only listed objects may be used.
- The door cannot be broken.
- The solution must be physically plausible.
"""


def test_create_game(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice
    alice = to_hex(direct_alice)

    contract.create_game(
        "lab-001",
        SCENARIO,
        RULES,
    )

    game = contract.get_game("lab-001")

    assert game["id"] == "lab-001"
    assert game["creator"] == alice
    assert game["status"] == "OPEN"
    assert game["claim"] == ""
    assert game["verdict"] == ""


def test_submit_claim(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-001",
        SCENARIO,
        RULES,
    )

    contract.submit_claim(
        "lab-001",
        "I use the electrical cable to climb through the ventilation opening.",
    )

    game = contract.get_game("lab-001")

    assert game["status"] == "CLAIMED"
    assert game["claimant"] == to_hex(direct_alice)
    assert "electrical cable" in game["claim"]


def test_challenge_claim(
    direct_vm,
    direct_deploy,
    direct_alice,
    direct_bob,
):
    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-001",
        SCENARIO,
        RULES,
    )

    contract.submit_claim(
        "lab-001",
        "I use the electrical cable to climb through the ventilation opening.",
    )

    direct_vm.sender = direct_bob

    contract.challenge_claim("lab-001")

    game = contract.get_game("lab-001")

    assert game["status"] == "CHALLENGED"
    assert game["challenger"] == to_hex(direct_bob)


def test_claimant_cannot_challenge_own_claim(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-001",
        SCENARIO,
        RULES,
    )

    contract.submit_claim(
        "lab-001",
        "I climb through the ventilation opening.",
    )

    with direct_vm.expect_revert(
        "Claimant cannot challenge their own claim"
    ):
        contract.challenge_claim("lab-001")


def test_resolve_valid_claim(
    direct_vm,
    direct_deploy,
    direct_alice,
    direct_bob,
):
    direct_vm.mock_llm(
        r".*",
        '{"verdict":"VALID","reasoning":"The claim uses an available object and follows the rules."}',
    )

    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-valid",
        SCENARIO,
        RULES,
    )

    contract.submit_claim(
        "lab-valid",
        "I use the electrical cable to climb through the ventilation opening.",
    )

    direct_vm.sender = direct_bob

    contract.challenge_claim("lab-valid")

    contract.resolve_game("lab-valid")

    game = contract.get_game("lab-valid")

    assert game["status"] == "RESOLVED"
    assert game["verdict"] == "VALID"
    assert len(game["reasoning"]) > 0


def test_resolve_invalid_claim(
    direct_vm,
    direct_deploy,
    direct_alice,
    direct_bob,
):
    direct_vm.mock_llm(
        r".*",
        '{"verdict":"INVALID","reasoning":"The claim invents an object that is not present."}',
    )

    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-invalid",
        SCENARIO,
        RULES,
    )

    contract.submit_claim(
        "lab-invalid",
        "I use a laser cutter to cut through the wall.",
    )

    direct_vm.sender = direct_bob

    contract.challenge_claim("lab-invalid")

    contract.resolve_game("lab-invalid")

    game = contract.get_game("lab-invalid")

    assert game["status"] == "RESOLVED"
    assert game["verdict"] == "INVALID"


def test_duplicate_game_id_fails(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-001",
        SCENARIO,
        RULES,
    )

    with direct_vm.expect_revert("Game already exists"):
        contract.create_game(
            "lab-001",
            SCENARIO,
            RULES,
        )


def test_get_games(
    direct_vm,
    direct_deploy,
    direct_alice,
):
    contract = direct_deploy(CONTRACT_PATH)

    direct_vm.sender = direct_alice

    contract.create_game(
        "lab-001",
        SCENARIO,
        RULES,
    )

    contract.create_game(
        "lab-002",
        "You are stranded on an island.",
        "Only available natural resources may be used.",
    )

    games = contract.get_games()

    assert len(games) == 2
    assert games["lab-001"]["status"] == "OPEN"
    assert games["lab-002"]["status"] == "OPEN"
