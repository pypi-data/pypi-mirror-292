from typing import Any, Tuple, Dict

import torch

from rlvortex.replay_buffer import BaseReplayBuffer


class EpisodeReplayBuffer(BaseReplayBuffer):
    def __init__(
        self,
        *,
        num_envs: int,
        num_episodes: int,
        obs_dim: Tuple[int, ...],
        act_dim: Tuple[int, ...],
        device: torch.device,
    ) -> None:
        super().__init__(num_envs, device)
        assert (
            isinstance(num_episodes, int) and num_episodes > 0
        ), "batch_steps_per_env must be a positive integer"
        assert isinstance(device, torch.device), "device must be an instance of Device"
        self.num_episodes: int = num_episodes
        self._obs_dim: Tuple[int, ...] = obs_dim
        self._act_dim: Tuple[int, ...] = act_dim
        self.data_dict: Dict[str, torch.Tensor] = {
            "observations": torch.tensor([], device=device),
            "actions": torch.tensor([], device=device),
            "rewards": torch.tensor([], device=device),
            "dones": torch.tensor([], device=device),
            "returns": torch.tensor([], device=device),
        }
        self._episode_counter = 0

    @property
    def params(self) -> Dict[str, Any]:
        params_dict: Dict = super().params
        params_dict.update(
            {
                "num_episodes": self.num_episodes,
                "obs_dim": self._obs_dim,
                "act_dim": self._act_dim,
            }
        )
        return params_dict

    @property
    def is_full(self) -> bool:
        return self._episode_counter >= self.num_episodes

    @property
    def num_transitions(self) -> int:
        return self.data_dict["dones"].shape[0]

    def clear(self) -> None:
        self._episode_counter = 0
        self.data_dict: Dict[str, torch.Tensor] = {
            "observations": torch.tensor([], device=self.device),
            "actions": torch.tensor([], device=self.device),
            "rewards": torch.tensor([], device=self.device),
            "dones": torch.tensor([], device=self.device),
            "returns": torch.tensor([], device=self.device),
        }

    def append(
        self,
        observations: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        dones: torch.Tensor,
        step_info: Dict[str, torch.Tensor],
    ):
        assert not self.is_full, "replay buffer is full"
        assert torch.all(dones[-1] == 1), "last step of each episode must be done"
        self.data_dict["observations"] = torch.cat([self.data_dict["observations"], observations], dim=0)
        self.data_dict["actions"] = torch.cat([self.data_dict["actions"], actions], dim=0)
        self.data_dict["rewards"] = torch.cat([self.data_dict["rewards"], rewards], dim=0)
        self.data_dict["dones"] = torch.cat([self.data_dict["dones"], dones], dim=0)

        for key, value in step_info.items():
            assert key not in ["observations", "actions", "rewards", "dones"], (
                f"key must not be one of ['observations', 'actions', 'rewards', 'dones'], " f"but got {key}"
            )
            if key not in self.data_dict:
                self.data_dict[key] = torch.tensor([], device=self.device)
            self.data_dict[key] = torch.cat([self.data_dict[key], value], dim=0)
        self._episode_counter += dones.sum().item()
