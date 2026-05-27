"""
HF Agents Course — Bonus Unit 3: Pokémon Battle Agent (smolagents flavor).

This file implements a custom `HFAgentsCoursePokemonAgent` that you can
drop into the official PShowdown/pokemon_agents Space:

  https://huggingface.co/spaces/PShowdown/pokemon_agents

Architecture:

  poke_env.Player
      └── LLMAgentBase         # battle-state formatting + tool dispatch + fallbacks
          └── HFAgentsCoursePokemonAgent   # _get_llm_decision via HF Inference Providers

The agent calls Qwen 2.5-Coder-32B (any tool-calling model would do) and
forces it to emit one of two tool calls per turn:
   - choose_move(move_name)
   - choose_switch(pokemon_name)
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

# poke_env imports — only required at battle time, kept inside try/except so
# the file remains importable from a notebook for inspection.
try:
    from poke_env.environment.battle import Battle
    from poke_env.environment.move import Move
    from poke_env.environment.pokemon import Pokemon
    from poke_env.player import Player
except Exception:  # noqa: BLE001
    Battle = Move = Pokemon = Player = object  # type: ignore[misc,assignment]


STANDARD_TOOL_SCHEMA: dict[str, Any] = {
    "choose_move": {
        "type": "function",
        "function": {
            "name": "choose_move",
            "description": "Use one of your available moves this turn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "move_name": {
                        "type": "string",
                        "description": (
                            "The id (preferred) or display-name of the move "
                            "to use this turn. Must be in `Available moves:` "
                            "in the battle state."
                        ),
                    }
                },
                "required": ["move_name"],
            },
        },
    },
    "choose_switch": {
        "type": "function",
        "function": {
            "name": "choose_switch",
            "description": "Switch out the active Pokemon for one on the bench.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pokemon_name": {
                        "type": "string",
                        "description": (
                            "The species name of the Pokemon to bring in. "
                            "Must be in `Available switches:`."
                        ),
                    }
                },
                "required": ["pokemon_name"],
            },
        },
    },
}


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


# ---------------------------------------------------------------------------
# Base (battle formatting, tool dispatch, fallbacks)
# ---------------------------------------------------------------------------

class LLMAgentBase(Player):  # type: ignore[misc]
    """Bridge between an LLM and poke-env. Subclass + implement
    `_get_llm_decision(battle_state_str) -> {"decision": {...}}`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.standard_tools = STANDARD_TOOL_SCHEMA
        self.battle_history: list[str] = []

    def _format_battle_state(self, battle: Battle) -> str:  # type: ignore[name-defined]
        active = battle.active_pokemon
        active_str = (
            f"Your active Pokemon: {active.species} "
            f"(Type: {'/'.join(map(str, active.types))}) "
            f"HP: {active.current_hp_fraction * 100:.1f}% "
            f"Status: {active.status.name if active.status else 'None'} "
            f"Boosts: {active.boosts}"
        )
        opp = battle.opponent_active_pokemon
        opp_str = "Unknown"
        if opp:
            opp_str = (
                f"{opp.species} (Type: {'/'.join(map(str, opp.types))}) "
                f"HP: {opp.current_hp_fraction * 100:.1f}% "
                f"Status: {opp.status.name if opp.status else 'None'} "
                f"Boosts: {opp.boosts}"
            )
        moves = (
            "\n".join(
                f"- {m.id} (Type: {m.type}, BP: {m.base_power}, "
                f"Acc: {m.accuracy}, PP: {m.current_pp}/{m.max_pp}, "
                f"Cat: {m.category.name})"
                for m in battle.available_moves
            )
            if battle.available_moves
            else "- None (Must switch or Struggle)"
        )
        switches = (
            "\n".join(
                f"- {p.species} (HP: {p.current_hp_fraction * 100:.1f}%, "
                f"Status: {p.status.name if p.status else 'None'})"
                for p in battle.available_switches
            )
            if battle.available_switches
            else "- None"
        )
        return (
            f"{active_str}\n"
            f"Opponent's active Pokemon: {opp_str}\n\n"
            f"Available moves:\n{moves}\n\n"
            f"Available switches:\n{switches}\n\n"
            f"Weather: {battle.weather}\n"
            f"Terrains: {battle.fields}\n"
            f"Your Side Conditions: {battle.side_conditions}\n"
            f"Opponent Side Conditions: {battle.opponent_side_conditions}"
        ).strip()

    def _find_move_by_name(self, battle: Battle, name: str) -> Move | None:  # type: ignore[name-defined]
        n = normalize_name(name)
        for m in battle.available_moves:
            if m.id == n:
                return m
        for m in battle.available_moves:
            if m.name.lower() == name.lower():
                return m
        return None

    def _find_pokemon_by_name(self, battle: Battle, name: str) -> Pokemon | None:  # type: ignore[name-defined]
        n = normalize_name(name)
        for p in battle.available_switches:
            if normalize_name(p.species) == n:
                return p
        return None

    async def choose_move(self, battle: Battle) -> str:  # type: ignore[name-defined,override]
        state = self._format_battle_state(battle)
        result = await self._get_llm_decision(state)
        decision = (result or {}).get("decision") or {}
        fn = decision.get("name")
        args = decision.get("arguments", {}) or {}

        if fn == "choose_move":
            move = self._find_move_by_name(battle, args.get("move_name", ""))
            if move and move in battle.available_moves:
                print(f"AI: choose_move '{move.id}'")
                return self.create_order(move)
        elif fn == "choose_switch":
            pkmn = self._find_pokemon_by_name(battle, args.get("pokemon_name", ""))
            if pkmn and pkmn in battle.available_switches:
                print(f"AI: choose_switch '{pkmn.species}'")
                return self.create_order(pkmn)

        # Fallback path
        err = (result or {}).get("error")
        print(f"AI fallback (decision={decision}, error={err}) → random.")
        if battle.available_moves or battle.available_switches:
            return self.choose_random_move(battle)
        return self.choose_default_move(battle)

    async def _get_llm_decision(self, battle_state: str) -> dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# HF Inference Providers flavor (tool-calling via OpenAI-compat /v1)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a competitive Pokémon battle agent. Each turn you receive the "
    "current battle state and MUST respond by calling exactly ONE of the "
    "available tools: choose_move or choose_switch. Pick the option that "
    "maximizes your expected damage / survival across the next 2–3 turns. "
    "Consider type matchups, status effects, accuracy, boosts, and switch "
    "opportunities. Do not narrate."
)


class HFAgentsCoursePokemonAgent(LLMAgentBase):
    """LLM-driven Pokémon agent backed by Hugging Face Inference Providers
    (OpenAI-compatible /v1 endpoint). Set HF_TOKEN in the environment."""

    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        from openai import OpenAI
        token = os.environ.get("HF_TOKEN")
        if not token:
            raise RuntimeError(
                "HF_TOKEN env var is required for HFAgentsCoursePokemonAgent."
            )
        self._client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=token,
        )
        self._model_id = model_id
        self._tools = list(self.standard_tools.values())

    async def _get_llm_decision(self, battle_state: str) -> dict[str, Any]:
        loop = asyncio.get_event_loop()
        try:
            resp = await loop.run_in_executor(None, self._completion, battle_state)
        except Exception as exc:  # noqa: BLE001
            return {"error": f"API error: {exc}"}

        msg = resp.choices[0].message
        tcs = getattr(msg, "tool_calls", None) or []
        if not tcs:
            return {"error": "LLM did not call a tool."}
        call = tcs[0]
        try:
            args = json.loads(call.function.arguments) if call.function.arguments else {}
        except json.JSONDecodeError:
            args = {}
        return {"decision": {"name": call.function.name, "arguments": args}}

    def _completion(self, battle_state: str) -> Any:  # type: ignore[override]
        return self._client.chat.completions.create(
            model=self._model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Battle state:\n{battle_state}"},
            ],
            tools=self._tools,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=256,
        )


# Quick local sanity-check against poke-env's RandomPlayer using the official
# play server. Requires PSHOWDOWN_HOST + PSHOWDOWN_TOKEN env vars (or a
# locally running Pokémon Showdown server). This won't run in the Space — it's
# a developer-side smoke test.
async def main() -> None:
    from poke_env.player import RandomPlayer
    agent = HFAgentsCoursePokemonAgent(battle_format="gen9randombattle")
    opp = RandomPlayer(battle_format="gen9randombattle")
    await agent.battle_against(opp, n_battles=1)
    print(f"Won {agent.n_won_battles}/{agent.n_finished_battles} battles.")


if __name__ == "__main__":
    asyncio.run(main())
