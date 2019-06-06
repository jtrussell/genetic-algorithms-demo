from abc import ABCMeta, abstractmethod
from math import ceil, floor, inf
from itertools import chain
import random


class GAExperiment(metaclass = ABCMeta):
    def __init__(self,
        population_size = 1000,
        max_generations = 100,
        target_fitness = None):
        """Initialize the experiment

        Create a generation 0 or random individuals and initialize other
        experiment parameters.

        Some properties of note:
        - population: A list of tuples of the form (individual, fitness score).
          This list will be ordered by fitness in descending order (i.e. the
          most fit individual first, least fit last).

        Params:
        - self: The experiment
        - population_size: How many individuals should be in each generation.
          Depending on the generation, this may not be exact.
        - max_generations: Stop the experiment after this many generations
        - target_fitness: If not None, stop the experiment after we find an
          individual with at least this fitness score.
        """
        if population_size < 1:
            raise ValueError('population_size must be at least 1')
        self.population_size = population_size
        self.max_generations = max_generations
        self.target_fitness = target_fitness
        pop = [self.make_individual() for _ in range(self.population_size)]
        self.population = [(_, self.fitness(_)) for _ in pop]
        self.population.sort(key=lambda x: x[1], reverse=True)
        self.generation = 0
        self.mutate_probability = 1 / len(self.population[0][0])
        self.most_fit = None
        self.most_fit_score = -inf


    def run(self):
        """Run the experiment"""
        while self.generation < self.max_generations:
            self.hook_pre_generation()
            # Determine which individuals will pass on genetic info to the next
            # generation
            pool = self.sample_population()
            # Match up parents from the mating pool
            num_parents_needed = ceil(self.population_size / 2)
            parents = self.match_parents(pool, num_parents_needed)
            # Breed to generate the next generation
            children = self.breed(parents)
            # Sort by fitness (descending)
            children.sort(key=lambda x: x[1], reverse=True)
            self.population = children
            self.generation = self.generation + 1
            bits, score = self.population[0]
            if score > self.most_fit_score:
                self.most_fit = bits
                self.most_fit_score = score
            self.hook_post_generation()
            if self.target_fitness is not None:
                if self.population[0][1] >= self.target_fitness:
                    break


    @abstractmethod
    def fitness(self, individual):
        """Get a fitness score for the individual.

        This method is intended to be overwritten. It will be used to evaluate
        the population members of each generation.

        Params:
        - self: The experiment
        - individual: An sample/phenotype from the population.

        Returns:
        A fitness score. Used to rank individuals in a population.
        """
        pass


    @abstractmethod
    def make_individual():
        """Any random individual will do.

        This method is intended to be overwritten. It will be used to create
        individuals whenever new ones are needed.

        Returns:
        An individual.
        """
        pass


    def sample_population(self):
        """Return a sampling of the given population
        
        Individuals are selected for "breading" the next generation with
        probability (N - rank) / N. Where N is the size of the population and
        rank a given individuals relative fitness rank within it.
        """
        pop = self.population
        n = len(pop)
        r = [random.random() for _ in range(n)]
        return [pop[ix] for ix in range(n) if (n - ix)/n > r[ix]]


    def match_parents(self, pool, num_needed):
        """Return a list of parents for mating

        Params:
        - self: The experiment
        - pool: Individuals, i.e. potential parents
        - num_needed: How many pairs of parents we should make

        Returns:
        A list of paired individual
        """
        l = pool[:]
        random.shuffle(l)
        while len(l) < 2 * num_needed:
            _l = pool[:]
            random.shuffle(_l)
            l = l + _l
        return [(l[2 * ix], l[2 * ix + 1]) for ix in range(num_needed)]


    def breed(self, parents):
        """Produce new individuals based on the given list of parents.

        Each set of parents should yield two offspring.
        """
        num_noop = floor(0.1 * len(parents))
        num_mutations = floor(0.6 * len(parents))
        num_xover = len(parents) - num_noop - num_mutations
        noops = parents[:num_noop]
        ix = num_noop
        mutations = [self.mutate(a, b) for a, b in parents[ix:ix+num_mutations]]
        ix = ix + num_mutations
        xovers = [self.crossover(a, b) for a, b in parents[ix:ix+num_xover]]
        children = list(chain.from_iterable(noops))
        children = children + list(chain.from_iterable(mutations))
        children = children + list(chain.from_iterable(xovers))
        return children


    def crossover(self, a, b):
        """Combine two members of the population.

        Params:
        - self: The experiment
        - a: An individual
        - b: Another individual

        Returns:
        A mirrored pair of crossed-over individuals
        """
        return self.crossover_uniform(a, b,)


    def crossover_single_point(self, a, b):
        """A simple one point crossover

        AA + BB --> AB + BA

        Params:
        - self: The experiment
        - a: An individual
        - b: Another individual

        Returns:
        A mirrored pair of crossed-over individuals
        """
        bits_1, _ = a
        bits_2, _ = b
        ix = random.randint(0, len(bits_1) - 1)
        new_bits_1 = bits_1[:ix] + bits_2[ix:]
        new_bits_2 = bits_2[:ix] + bits_1[ix:]
        child_1 = new_bits_1, self.fitness(new_bits)
        child_2 = new_bits_2, self.fitness(new_bits)
        return child_1, child_2


    def crossover_uniform(self, a, b):
        """A uniform crossover

        Each child bit is equally likely to come from either parent.

        Params:
        - self: The experiment
        - a: An individual
        - b: Another individual

        Returns:
        A mirrored pair of crossed-over individual
        """
        bits_1, _ = a
        bits_2, _ = b
        num_bits = len(bits_1)
        randos = [random.random() for _ in range(num_bits)]
        new_bits_1 = ''.join([bits_1[ix] if randos[ix] > 0.5 else bits_2[ix] for ix in range(num_bits)])
        new_bits_2 = ''.join([bits_2[ix] if randos[ix] >= 0.5 else bits_1[ix] for ix in range(num_bits)])
        child_1 = new_bits_1, self.fitness(new_bits_1)
        child_2 = new_bits_2, self.fitness(new_bits_2)
        return child_1, child_2


    def mutate(self, a, b,):
        """Mutate and return a random member of the population

        Our stock mutate method with flip a given bit in the individual's
        chromosome bit string with probability 2/L where L is the length of the
        chromosome bit string.

        Params:
        - self: The experiment
        - a: An individual
        - b: Another individual
        
        Returns:
        A pair of mutated individuals
        """
        return self.mutate_one(a), self.mutate_one(b)


    def mutate_one(self, individual):
        """Mutate a single individual
        
        Meant as a helper for the mutate method that gets two individuals.

        Params:
        - self: The experiment
        - individual: A bits/fitness score pair

        Returns:
        An individual
        """
        bits, _ = individual
        n = len(bits)
        p = self.mutate_probability
        randos = [random.random() for _ in range(n)]
        flip = {'0': '1', '1': '0'}
        new_bit = lambda ix: bits[ix] if randos[ix] > p else flip[bits[ix]]
        bits = ''.join([new_bit(ix) for ix in range(n)])
        return bits, self.fitness(bits)


    def hook_pre_generation(self):
        """A hook you may implement to run some code just before a new
        generation is crated.

        Perhaps used to adjust internal parameters used by the fitness function.
        """
        pass


    def hook_post_generation(self):
        """A hook you may implement to run some code just after a new generation
        is created.

        Perhaps used for logging to track evolutionary progress.
        """
        pass
