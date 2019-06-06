"""
A demo experiment.

More fit inviduals have more 1s in their bit string. You get 1 point for every 1
in your bit string. UNLESS! Your string is all 0s, then you get extra points :).
"""

import random
from gaexperiment import GAExperiment
from math import ceil


NUM_DIGITS = 51


class Experiment(GAExperiment):
    def fitness(self, individual):
        score = individual.count('1')
        return NUM_DIGITS + 1 if score == 0 else score


    def make_individual(self):
        return ''.join(random.choice('01') for _ in range(NUM_DIGITS))


    def hook_post_generation(self):
        gen = self.generation
        gen_check = ceil(self.max_generations / 25)
        if gen % gen_check == 0 or gen == self.max_generations:
            ix = ceil(len(self.population) / 2)
            bits, ptile_score = self.population[ix]
            agg_score = sum([_[1] for _ in self.population])
            mean_score = agg_score / len(self.population)
            print('{}\t{}\t{}'.format(gen, mean_score, ptile_score))
            print('{}'.format(self.population[0][0]))


if __name__ == '__main__':
    exp = Experiment(population_size=100,
                     max_generations=30,
                     target_fitness=NUM_DIGITS + 1)
    print('Generation\tMean score\tMedian score')
    exp.run()
    print('\nMost fit {}'.format(exp.most_fit))
