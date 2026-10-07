# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

import json
import genlayer as gl
from genlayer.storage import TreeMap


class Bluff(gl.contract.Contract):
    games: TreeMap[str, str]

    def __init__(self):
        pass

    def _load_game(self, game_id: str) -> dict:
        raw = self.games.get(game_id)

        if raw is None:
            raise gl.vm.UserError("Game does not exist")

        return json.loads(raw)

    def _save_game(self, game_id: str, game: dict) -> None:
        self.games[game_id] = json.dumps(game, sort_keys=True)

    def _judge_claim(
        self,
        scenario: str,
        rules: str,
        claim: str,
    ) -> dict:

        def adjudicate():
            task = f"""
You are the neutral adjudicator for a strategy game called BLUFF.

Your task is to determine whether a player's claim is valid.

SCENARIO:
{scenario}

RULES:
{rules}

PLAYER CLAIM:
{claim}

A claim is VALID only if:

1. It obeys every explicit rule.
2. It is reasonably possible within the scenario.
3. It does not invent essential objects, powers, facts, permissions,
   or capabilities that are not provided by the scenario.
4. The proposed action plausibly achieves what the player claims.

Otherwise, the claim is INVALID.

Do not reward creativity if the claim violates the scenario or rules.

Respond ONLY in JSON:

{{
    "verdict": "VALID" or "INVALID"
}}

Do not include markdown.
Do not include any text outside the JSON object.
"""

            result = gl.nondet.exec_prompt(
                task,
                response_format="json",
            )

            if not isinstance(result, dict):
                raise gl.vm.UserError("Malformed adjudication result")

            verdict = str(result.get("verdict", "INVALID")).upper()

            if verdict not in ("VALID", "INVALID"):
                verdict = "INVALID"

            return verdict

        verdict = gl.eq_principle.strict_eq(adjudicate)

        if verdict not in ("VALID", "INVALID"):
            raise gl.vm.UserError("Malformed adjudication verdict")

        reasoning = (
            "Claim accepted by GenLayer validator consensus."
            if verdict == "VALID"
            else "Claim rejected by GenLayer validator consensus."
        )

        return {
            "verdict": verdict,
            "reasoning": reasoning,
        }

    @gl.public.write
    def create_game(
        self,
        game_id: str,
        scenario: str,
        rules: str,
    ) -> None:

        if len(game_id.strip()) == 0:
            raise gl.vm.UserError("Game ID cannot be empty")

        if len(scenario.strip()) == 0:
            raise gl.vm.UserError("Scenario cannot be empty")

        if len(rules.strip()) == 0:
            raise gl.vm.UserError("Rules cannot be empty")

        if self.games.get(game_id) is not None:
            raise gl.vm.UserError("Game already exists")

        creator = gl.message.sender_address.as_hex

        game = {
            "id": game_id,
            "creator": creator,
            "scenario": scenario,
            "rules": rules,
            "claim": "",
            "claimant": "",
            "challenger": "",
            "status": "OPEN",
            "verdict": "",
            "reasoning": "",
        }

        self._save_game(game_id, game)

    @gl.public.write
    def submit_claim(
        self,
        game_id: str,
        claim: str,
    ) -> None:

        if len(claim.strip()) == 0:
            raise gl.vm.UserError("Claim cannot be empty")

        game = self._load_game(game_id)

        if game["status"] != "OPEN":
            raise gl.vm.UserError("Game is not open")

        game["claim"] = claim
        game["claimant"] = gl.message.sender_address.as_hex
        game["status"] = "CLAIMED"

        self._save_game(game_id, game)

    @gl.public.write
    def challenge_claim(
        self,
        game_id: str,
    ) -> None:

        game = self._load_game(game_id)

        if game["status"] != "CLAIMED":
            raise gl.vm.UserError("Game cannot be challenged")

        challenger = gl.message.sender_address.as_hex

        if challenger.lower() == game["claimant"].lower():
            raise gl.vm.UserError(
                "Claimant cannot challenge their own claim"
            )

        game["challenger"] = challenger
        game["status"] = "CHALLENGED"

        self._save_game(game_id, game)

    @gl.public.write
    def resolve_game(
        self,
        game_id: str,
    ) -> None:

        game = self._load_game(game_id)

        if game["status"] != "CHALLENGED":
            raise gl.vm.UserError(
                "Game must be challenged before resolution"
            )

        result = self._judge_claim(
            game["scenario"],
            game["rules"],
            game["claim"],
        )

        game["verdict"] = result["verdict"]
        game["reasoning"] = result["reasoning"]
        game["status"] = "RESOLVED"

        self._save_game(game_id, game)

    @gl.public.view
    def get_game(
        self,
        game_id: str,
    ) -> dict:

        return self._load_game(game_id)

    @gl.public.view
    def get_games(self) -> dict:

        result = {}

        for game_id, raw in self.games.items():
            game = json.loads(raw)

            result[game_id] = {
                "id": game["id"],
                "creator": game["creator"],
                "status": game["status"],
                "verdict": game["verdict"],
            }

        return result
