"""
A demo experiment.

More fit inviduals have more 1s in their bit string. You get 1 point for every 1
in your bit string. UNLESS! Your string is all 0s, then you get extra points :).
"""

import random
from gaexperiment import GAExperiment
from math import ceil
from utils import right_pad


class Experiment(GAExperiment):
    def __init__(self,
                 population_size=1000,
                 max_generations=100,
                 target_fitness=None,
                 num_digits=51):
        self.num_digits = num_digits
        GAExperiment.__init__(self,
                              max_generations=max_generations,
                              population_size=population_size,
                              target_fitness=target_fitness)


    def fitness(self, individual):
        score = individual.count('1')
        return self.num_digits + 1 if score == 0 else score


    def make_individual(self):
        return ''.join(random.choice('01') for _ in range(self.num_digits))


    def hook_post_generation(self):
        gen = self.generation
        gen_check = ceil(self.max_generations / 25)
        if gen % gen_check == 0 or gen == self.max_generations:
            ix = ceil(len(self.population) / 2)
            bits, ptile_score = self.population[ix]
            agg_score = sum([_[1] for _ in self.population])
            mean_score = agg_score / len(self.population)
            print('{}{}{}'.format(right_pad(gen),
                                  right_pad(mean_score),
                                  right_pad(ptile_score)))


if __name__ == '__main__':
    num_digits = 51
    population_size = 100
    max_generations = 100
    print()
    print('Sequence length: {}'.format(num_digits))
    print('Population size: {}'.format(population_size))
    print('Max Generations: {}'.format(max_generations))
    print()
    exp = Experiment(population_size=population_size,
                     max_generations=max_generations,
                     target_fitness=num_digits,
                     num_digits=num_digits)
    print('{}{}{}'.format(right_pad('Generation'),
                          right_pad('Mean Score'),
                          right_pad('Median Score')))
    exp.run()
    print('\nMost fit {}'.format(exp.most_fit))
    print()
