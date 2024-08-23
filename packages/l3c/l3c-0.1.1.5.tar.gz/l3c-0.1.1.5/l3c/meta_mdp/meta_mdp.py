"""
Gym Environment For Maze3D
"""
import numpy
import gym
import pygame
from numpy import random

from gym import error, spaces, utils
from gym.utils import seeding

class RandomWorldModel(object):
    def __init__(self, 
                 n_emb=16, # Embedding size of the vocabulary
                 n_hidden=64, # Hidden dimension 
                 n_vocab_obs=256, # Number of vocabulary for observation
                 n_vocab_act=64, # Number of vocabulary for action
                 n_tok_obs=4, # Number of tokens taken for each observation
                 n_tok_act=2, # Number of tokens taken for each action
                 T=None, # Temporature for sampling
                 seed=None, # Random seed
                 ):
        self.n_emb = n_emb
        self.n_hidden = n_hidden
        self.n_vocab_obs = n_vocab_obs
        self.n_vocab_act = n_vocab_act
        self.n_tok_obs = n_tok_obs
        self.n_tok_act = n_tok_act
        self.T = T

        self.emb_obs = numpy.random.normal(0, 1.0, size=(self.n_vocab_obs, self.n_emb))
        self.emb_act = numpy.random.normal(0, 1.0, size=(self.n_vocab_obs, self.n_emb))

        if(seed is not None):
            numpy.random.seed(seed)

        self.encoder_weights = numpy.random.normal(0, 1.0, size=(self.n_hidden, (self.n_tok_obs + self.n_tok_act) * self.n_emb))
        self.encoder_bias = numpy.random.normal(0, 1.0, size=(self.n_hidden,))
        self.rec_weights = numpy.random.normal(0, 1.0, size=(self.n_hidden, self.n_hidden + self.n_emb))
        self.rec_bias = numpy.random.normal(0, 1.0, size=(self.n_hidden,))

        self.output_obs = numpy.random.normal(0, 1.0, size=(self.n_emb, self.n_hidden))
        self.output_rew = numpy.random.normal(0, 1.0, size=(1, self.n_hidden))

    def softmax(self, x):
        e_x = numpy.exp(x - numpy.max(x, axis=-1, keepdims=True))
        return e_x / e_x.sum(axis=-1, keepdims=True)

    def forward(self, obs: numpy.ndarray, act: numpy.ndarray):
        ind = 0

        def mean_var_norm(i):
            m_i = numpy.mean(i)
            m_ii = numpy.mean(i * i)
            std = numpy.sqrt(m_ii - m_i * m_i)
            return (1.0 / std) * (i - m_i)

        assert obs.shape[0] == self.n_tok_obs and oct.shape[0] == self.n_tok_act
        obs_emb = self.emb_obs[obs]
        act_emb = self.emb_act[act]

        done = False
        while not done:
            ind += 1
            tok_emb = numpy.expand_dims(numpy.array(self.emb[idxes, cur_tok]), axis=1)
            tok_embs.append(tok_emb)
            del tok_embs[0]

class MetaMDP(gym.Env):
    def __init__(self, 
            max_steps = 5000,
            ):

        self.max_steps = max_steps

        # Turning Left/Right and go backward / forward
        self.
        self.action_space = spaces.Discrete(arms)

        # observation is the x, y coordinate of the grid
        self.observation_space = None 

        # expected ctr of each arms 
        self.exp_gains = None
        self.K = arms
        self.need_reset = True

        assert self.K > 1 and self.max_steps > 1

    def sample_task(self,
            distribution_settings="Classical",
            mean=0.50,
            dev=0.05,
            ):
        """
        Classical: 1 arm is mean + sqrt(K-1) dev, others are mean - dev / sqrt(K-1)
        Uniform:   each arm with expected gain being Uniform(mean - 1.732 * dev, mean + 1.732 * dev)
        Gaussian:   Gaussian(mean, dev)
        """
        if(distribution_settings == "Classical"):
            fac = numpy.sqrt(self.K - 1)
            exp_gains = numpy.full((self.K,), mean - dev / fac)
            sel_idx = random.randint(0, self.K - 1)
            exp_gains[sel_idx] = mean + fac * dev
            exp_gains = numpy.clip(exp_gains, 0.0, 1.0)
        elif(distribution_settings == "Uniform"):
            exp_gains = numpy.clip((random.random(shape=(self.K,)) - 0.50) * 3.464 + mean, 0.0, 1.0).tolist()
        elif(distribution_settings == "Gaussian"):
            exp_gains = numpy.clip(random.normal(loc=mean, scale=dev), 0.0, 1.0)
        else:
            raise Exception("No such distribution_settings: %s", distribution_settings)
        return exp_gains

    def set_task(self, task_config):
        self.exp_gains = task_config
        assert numpy.shape(self.exp_gains) == (self.K,)
        self.need_reset = True

    def reset(self):
        if(self.exp_gains is None):
            raise Exception("Must call \"set_task\" before reset")
        self.steps = 0
        self.need_reset = False
        return None

    def step(self, action):
        if(self.need_reset):
            raise Exception("Must \"reset\" before doing any actions")
        exp_gain = self.exp_gains[action]
        reward = 1 if random.random() < exp_gain else 0
        info = {"steps": self.steps, "expected_gain": exp_gain}
        self.steps += 1
        done = self.steps >= self.max_steps
        if(done):
            self.need_reset = True

        return None, reward, done, info

    def expected_upperbound(self):
        return self.max_steps * numpy.max(self.exp_gains)
