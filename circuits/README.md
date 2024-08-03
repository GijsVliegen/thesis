# dnf_countries

The instances of dnf_countries originate from a neuro-symbolic probabilistic inference pipeline.

Based on the paper below, Jaron Maene gave me 3 DNF formulas similar to those in the paper where 
inference is performed on a Countries knowledge graph.
```
Maene, Jaron, and Luc De Raedt. 
"Soft-unification in deep probabilistic logic." 
Advances in Neural Information Processing Systems 36 (2024).
```

The license of these instances are the same as the license of this repository.

# noisy_or

The instances of noisy_or originate from a probabilistic inference problem in a noisy-or Bayesian network model, with an increasing number of parent nodes.
The following ProbLog program (with abitrary probabilities that are ignored) was used
```
0.1::parent(X).
0.5::latent(X).
x :- parent(X), latent(X).
```
which encodes roughly the following formula
```
X is true \iff any(Parent is true and is cause for X to be true)
```

The license of these instances is the same as the license of this repository.
Created by Vincent Derkinderen

# problog_bnkr24

The instances of bnkr24 represents probabilistic inference queries in existing Bayesian network models.
The Bayesian networks originate from the [BNlearn repository](https://www.bnlearn.com/bnrepository/),
and were transformed into ProbLog programs using ProbLog's [conversion script](https://github.com/ML-KULeuven/problog/blob/master/conversions/bn2problog.py).
I manually added a query that would encompass many of the BN variables.

* alarm
* andes
* andes-noneg
* asia
* cancer
* child
* earthquake
* hailfinder
* insurance
* munin
* pathfinder
* pigs
* barley (query timed-out)
* mildew (query timed-out)

The license of these instances is the same as the license of this repository.
Consider citing the BN source, which can be found in the BNlearn repository.
Created by Vincent Derkinderen.


# problog_games

The instances of problog_games represent probabilistic inference queries over some game related ProbLog programs.

The license of these instances is the same as the license of this repository.
Created by Vincent Derkinderen.

# problog_powergrid_latour2019

The instances of problog_powergrid_latour2019 represent probabilistic inference queries over a powergrid structure of a state or country.
Please see the README in the data/problog/powergrid-reliability-latour2019 directory for more information and the appropriate license.


# smokers1

The instances of smokers1 represent probabilistic inference queries over a ProbLog program that 
models the influence and smoking habit of a group of people.

We used the following 'influence'-network of people from the networkx codebase:
* networkx.les_miserables_graph
* networkx.karate_club_graph
* networkx.florentine_families_graph
* networkx.krackhardt_kite_graph

Based on these graphs, the direction of influence is randomly assigned, generating multiple graphs.
A random person is then queried.

Consider citing the networkx source, which can be found in the networkx repository.
The license of these instances is the same as the license of this repository.
Created by Vincent Derkinderen.

# smokers2

The instances of smokers2 represent probabilistic inference queries over a ProbLog program that 
models the influence and smoking habit of a group of people.

From the networkx codebase, we used the `networkx.extended_barabasi_albert_graph` method to generate 
random undirected graphs. Based on this graph, the direction of influence is randomly assigned to obtain 
a directed graph. A random person is then queried.

The license of these instances is the same as the license of this repository.
Created by Vincent Derkinderen.


# verilo_jpsety

The instances of verilog_jpsety represent various circuits, converted from verilog files, 
downloaded from https://github.com/jpsety/verilog_benchmark_circuits .
Please see the README in the data/verilog_jpsety directory for more information and the appropriate license.

# raki benchmarks

The instances of raki represent (probabilistic) inference queries over (probabilistic) logic programs.
See the original source for more information: https://github.com/raki123/KC-benchmarking .

These instances were used in
```
Kiesel, Rafael, and Thomas Eiter. 
"Knowledge compilation and more with SharpSAT-TD." 
Proceedings of the International Conference on Principles of Knowledge Representation and Reasoning. Vol. 19. No. 1. 2023.
```

These instances are CNF formulas, annotated with auxiliary variables that represent Tseitin variables (cf. the paper above).
We skipped the following 95 lp2sat files since we were unable to detect the proper definition.

* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_100_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 3221
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_40_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1301
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_80_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2096
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_60_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1576
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_30_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 611
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_80_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2581
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_5_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 44
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_30_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 426
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_50_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 706
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_60_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 846
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_7_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 86
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_10_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 276
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_30_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 981
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_13_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 228
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_13_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 284
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_10_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 406
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_9_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 128
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_13_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 300
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_50_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1926
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_10_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 173
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_12_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 175
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_70_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2261
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_9_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 144
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_15_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 382
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_90_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2901
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_7_6_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 234
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_5_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 44
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_15_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 318
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_15_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 294
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_70_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 986
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_70_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1411
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_10_0.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 78
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_6_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 56
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_40_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1546
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_12_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 271
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_10_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 141
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_40_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 566
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_8_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 107
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_20_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 536
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_20_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 786
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_100_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2616
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_8_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 90
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_6_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 72
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_30_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 796
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_40_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 811
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_7_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 70
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_8_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 115
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_100_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1406
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_9_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 144
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_10_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 341
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_80_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 3066
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_4_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 30
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_8_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 107
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_90_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2356
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_60_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1211
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_14_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 225
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_12_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 231
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_80_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1126
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_90_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1811
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_8_7_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 299
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_12_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 247
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_50_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1621
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_14_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 353
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_10_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 165
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_100_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 3826
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_11_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 154
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_50_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1316
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_50_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1011
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_10_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 211
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_70_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1836
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_80_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1611
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_20_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 286
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_60_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2306
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_70_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2686
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_11_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 178
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_100_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 2011
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_15_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 254
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_20_2.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 411
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_14_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 257
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_7_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 78
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_13_2_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 196
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_7_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 86
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_40_3.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1056
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_20_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 661
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_6_3_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 64
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_10_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 189
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_90_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1266
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_60_4.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 1941
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_9_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 144
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_11_5_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 218
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_10_1.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 146
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_90_5.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 3446
* Skipping ./data/raki_aux_benchmarks/lp2sat/tree_30_5.lp.lp.cnf due to parsing error.
		Can not find definition of auxiliary variable 1166
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_11_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 202
* Skipping ./data/raki_aux_benchmarks/lp2sat/smokers_14_4_prob.lp.lp.cnf due to parsing error.
	Can not find definition of auxiliary variable 305

