import numpy as np
from agox.writer import agox_writer
from agox.samplers.ABC_sampler import SamplerBaseClass
from agox.observer import Observer

from typing import List
from agox.candidates import CandidateBaseClass as Candidate


class RateTracker:
    def __init__(self, sample_size: int):
        self.sample_size = sample_size
        self.acceptance = {i: list() for i in range(sample_size)}
        self.swap_up = {i: list() for i in range(sample_size)}
        self.swap_down = {i: list() for i in range(sample_size)}

    def update_acceptance(self, sample_index: int, value: int) -> None:
        self.acceptance[sample_index].append(value)

    def update_swap_up(self, sample_index: int, value: int) -> None:
        if sample_index < self.sample_size - 1:
            self.swap_up[sample_index].append(value)

    def update_swap_down(self, sample_index: int, value: int) -> None:
        if sample_index < self.sample_size:
            self.swap_down[sample_index].append(value)

    def get_acceptance_rate(
        self, sample_index: int, start=None, stop=None, step=None
    ) -> float:
        index_slice = slice(start, stop, step)
        return np.mean(self.acceptance[sample_index][index_slice])

    def get_swap_up_rate(
        self, sample_index: int, start=None, stop=None, step=None
    ) -> float:
        index_slice = slice(start, stop, step)
        return np.mean(self.swap_up[sample_index][index_slice])

    def get_swap_down_rate(
        self, sample_index: int, start=None, stop=None, step=None
    ) -> float:
        index_slice = slice(start, stop, step)
        return np.mean(self.swap_down[sample_index][index_slice])

    def get_swap_up(self, sample_index: int) -> bool:
        if len(self.swap_up[sample_index]) == 0:
            return False
        return bool(self.swap_up[sample_index][-1])

    def get_swap_down(self, sample_index: int) -> bool:
        if len(self.swap_down[sample_index]) == 0:
            return False
        return bool(self.swap_down[sample_index][-1])

    def get_acceptance(self, sample_index: int) -> bool:
        if len(self.acceptance[sample_index]) == 0:
            return False
        return bool(self.acceptance[sample_index][-1])


class ParallelTemperingSampler(SamplerBaseClass):
    name = "ParallelTempering"

    """
    Parallel tempering sampler for non-concurrent searches.

    Parameters
    ----------
    sample_size : int
        Number of members in the sample.
    swap : str
        Method for swapping members. Options are 'up' or 'down'.
    temperatures: List[float]
        List of temperatures to use.
    t_max : float
        Maximum temperature.
    t_min : float
    """

    def __init__(
        self,
        t_min=None,
        t_max=None,
        sample_size=5,
        swap="up",
        gets={"get_key": "candidates"},
        temperatures=None,
        swap_interval=10,
        always_accept=False,
        model=None,
        sets={"set_key": "candidates"},
        **kwargs,
    ):
        super().__init__(gets=gets, sets=sets, **kwargs)

        self.sample_size = sample_size
        self.swap_interval = swap_interval
        self.always_accept = always_accept
        self.model = model

        # Temperature logic:
        # Check that they are not all not none:
        if t_max is not None and t_min is not None and temperatures is not None:
            raise ValueError(
                "Either t_max and t_min or temperatures must be provided, not both."
            )
        elif (
            t_max is not None and t_min is not None
        ):  # If both are provided, generate the temperatures.
            self.temperatures = np.geomspace(t_min, t_max, sample_size)
        elif temperatures is not None:
            if len(temperatures) != sample_size:
                raise ValueError(
                    f"Length of temperatures ({len(temperatures)}) does not match sample size ({sample_size})."
                )
            else:
                self.temperatures = temperatures
        else:
            raise ValueError("Either t_max and t_min or temperatures must be provided.")

        self.reset_observer()  # We remove observers added by the base-class.
        self.add_observer_method(
            self.setup_sampler,
            gets=self.gets[0],
            sets=self.sets[0],
            order=self.order[0],
            handler_identifier="AGOX",
        )

        self.tracker = RateTracker(sample_size)

        if swap == "up":
            self.swap = self.swap_up
        elif swap == "down":
            self.swap = self.swap_down
        else:
            raise ValueError(
                f"Swap method '{swap}' not recognized. Use 'up' or 'down'."
            )

    @agox_writer
    @Observer.observer_method
    def setup_sampler(self, state):
        if self.do_check():
            evaluated_candidates = state.get_from_cache(self, self.get_key)
            evaluated_candidates = list(filter(None, evaluated_candidates))
            if len(evaluated_candidates) > 0:
                self.setup(evaluated_candidates)

        # Overwrite the candidates on the cache as the sampler may have updated meta information.
        state.add_to_cache(self, self.set_key, evaluated_candidates, mode="w")

    def setup(self, evaluated_candidates: List[Candidate]) -> None:
        if len(self.sample) != self.sample_size:
            self.setup_when_empty(evaluated_candidates)
            return

        self.update_sample(evaluated_candidates)

        iteration = self.get_iteration_counter()
        if self.decide_to_swap(iteration):
            self.swap()

        if iteration % 1 == 0:
            self.report_statistics()

    def update_sample(self, evaluated_candidates: List[Candidate]) -> None:
        for candidate in evaluated_candidates:
            sample_index = candidate.get_meta_information("walker_index")
            parent = self.sample[sample_index]
            temperature = self.temperatures[sample_index]

            # Determine if the candidate gets accepted:
            accepted = self.metropolis_check(candidate, parent, temperature)
            self.tracker.update_acceptance(sample_index, int(accepted))
            if accepted:
                self.sample[sample_index] = candidate

            candidate.add_meta_information("accepted", accepted)

    def metropolis_check(
        self, candidate: Candidate, parent: Candidate, temperature: float
    ) -> bool:
        if self.always_accept:
            return True

        E_candidate = self.get_potential_energy(candidate)
        E_parent = self.get_potential_energy(parent)

        if E_candidate < E_parent:
            accepted = True
        else:
            P = np.exp(-(E_candidate - E_parent) / temperature)
            accepted = P > np.random.rand()

        return accepted

    def swap_check(self, i, j):
        """
        Check if we should swap the i-th and j-th member of the sample.

        Parameters
        ----------
        i: int
            Index of the first member.
        j: int
            Index of the second member.

        Returns
        -------
        bool
            True if the swap is accepted, False otherwise.
        """
        E_i = self.get_potential_energy(self.sample[i]) 
        E_j = self.get_potential_energy(self.sample[j])
        beta_i = 1 / self.temperatures[i]
        beta_j = 1 / self.temperatures[j]

        P = np.min([1, np.exp((beta_i - beta_j) * (E_i - E_j))])

        return P > np.random.rand()

    def swap_up(self):
        self.writer("Swapping in 'up' mode")

        # Run over the sample starting from the bottom:
        for i in range(len(self.sample) - 1):
            swap_bool = self.swap_check(i, i + 1)

            self.tracker.update_swap_up(i, int(swap_bool))
            self.tracker.update_swap_down(i + 1, int(swap_bool))

            if swap_bool:
                self.sample[i], self.sample[i + 1] = self.sample[i + 1], self.sample[i]

    def swap_down(self):
        self.writer("Swapping in 'down' mode")

        # Run over the sample starting from the highest temperature:
        for i in range(len(self.sample) - 1, 0, -1):
            swap_bool = self.swap_check(i, i - 1)

            self.tracker.update_swap_up(i - 1, int(swap_bool))
            self.tracker.update_swap_down(i, int(swap_bool))

            if swap_bool:
                self.sample[i], self.sample[i - 1] = self.sample[i - 1], self.sample[i]

    def decide_to_swap(self, iteration_counter: int) -> bool:
        return iteration_counter % self.swap_interval == 0

    def setup_when_empty(self, evaluated_candidates: List[Candidate]) -> None:
        replace = len(evaluated_candidates) < self.sample_size
        indices = np.arange(len(evaluated_candidates))
        sample_indices = np.random.choice(
            indices, size=self.sample_size, replace=replace
        )
        self.sample = [evaluated_candidates[i] for i in sample_indices]

        if self.verbose:
            self.writer(
                "Initialized Metropolis Sampler with {}".format(len(self.sample))
            )

        for candidate in evaluated_candidates:
            candidate.add_meta_information("accepted", True)

    def report_statistics(self):
        self.writer(
            f'{"Member":^14s}|{"Energy":^10s}|{"Accept":^10s}|{"Up":^9s}|{"Down":^9s}|'
        )
        for i in range(self.sample_size):
            swap_up = self.get_swap_up_rate(i)
            swap_down = self.get_swap_down_rate(i)
            acceptance = self.get_acceptance_rate(i, start=-10)
            energy = self.sample[i].get_meta_information("pt_energy") or 0

            ati = "*" if self.tracker.get_acceptance(i) else ""
            iteration = self.get_iteration_counter()
            if self.decide_to_swap(iteration):
                suti = "*" if self.tracker.get_swap_up(i) else ""
                sdti = "*" if self.tracker.get_swap_down(i) else ""
            else:
                suti = ""
                sdti = ""

            try: 
                self.writer(
                    f"{i:^6d}({self.temperatures[i]:^02.3f}) |{energy:^10.3f}|{acceptance:^7.2f}{ati:^3s}|{swap_up:^6.2f}{suti:^3s}|{swap_down:^6.2f}{sdti:^3s}|"
                )
            except Exception as e:
                print(energy)
                print(e)

    def get_acceptance_rate(
        self, index: int, start=None, stop=None, step=None
    ) -> float:
        return self.tracker.get_acceptance_rate(index, start, stop, step)

    def get_swap_up_rate(self, index: int, start=None, stop=None, step=None) -> float:
        return self.tracker.get_swap_up_rate(index, start, stop, step)

    def get_swap_down_rate(self, index: int, start=None, stop=None, step=None) -> float:
        return self.tracker.get_swap_down_rate(index, start, stop, step)

    def get_potential_energy(self, candidate):
        if self.model is not None:
            E = self.model.predict_energy(candidate)
        elif hasattr(candidate, 'calc'):
            E = candidate.get_potential_energy()
        else:
            E = 0.0

        candidate.add_meta_information("pt_energy", float(E))
        return float(E)