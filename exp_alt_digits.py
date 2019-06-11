"""
A demo experiment.

More fit individuals have alternating bits. You get 1 point everytime your bit
string has a 1 following a 0 or a 0 following a 1.
"""

import random
from gaexperiment import GAExperiment
from math import ceil


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
        score = 0
        for ix in range(1, len(individual)):
            if individual[ix] != individual[ix - 1]:
                score = score + 1
        return score


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
            print('{}\t{}\t{}'.format(gen, mean_score, ptile_score))


if __name__ == '__main__':
    num_digits = 8
    exp = Experiment(population_size=4,
                     max_generations=3,
                     target_fitness=num_digits - 1,
                     num_digits=num_digits)
    print('Generation\tMean score\tMedian score')
    exp.run()
    print('\nMost fit {}'.format(exp.most_fit))
