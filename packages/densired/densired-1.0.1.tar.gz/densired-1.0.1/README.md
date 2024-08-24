# DENSIRED

This package provides a data generator for density-based data, described in the ECML PKDD 24 paper "Data with Density-Based Clusters: A Generator for Systematic Evaluation of Clustering Algorithms" by Philipp Jahn$^{1,2}$ , Christian M. M. Frey$^{3}$, Anna Beer$^{4}$, Collin Leiber$^{1,2}$, and Thomas Seidl$^{1,2,3}$.

(1 LMU Munich, Munich, Germany; 2 Munich Center for Machine Learning (MCML), Munich, Germany; 3 Fraunhofer IIS, Erlangen, Germany; 4 University of Vienna, Vienna, Austria.)

## pip installation

The current stable version can be installed by the following command:

pip install densired

## How to use

Use the following code to generate a skeleton. Parameters are listed at our Github Repository (https://github.com/PhilJahn/DENSIRED).

```
skeleton = datagen.densityDataGen()
```

Use the following code to obtain a dataset with *n* points from a skeleton. There are additional parameters, that are also listed below.

```
data = skeleton.generate_data(n)
datax = data[:,0:-1]
datay = data[:,-1]
```

To visualize the skeleton, call the following code. For higher-dimensionalities, either specify *dcount* to get all pairs of the *dc* most spread out dimensions or specify the desired dimensions directly with *dims*.
```
skeleton.display_cores(dims=[d1,d2,...], dcount=dc)
```

To visualize a dataset, call the following. Give the dataset as *data*. The flags *show_radius* and *show_core* decide whether to display the core radii and core centers, respectively. For higher-dimensionalities, as with dispaly_cores, either specify *dcount* to get all pairs of the *dc* most spread out dimensions or specify the desired dimensions directly with *dims*.
```
skeleton.display_data(data, show_radius=False, show_core=False, dims=[d1,d2,...], dcount=dc)
```

To initialize a stream, call the following function. The *command*-String controls the stream behavior. The *default_duration* is the default duration of a block of the stream. default_duration does not need to be specified, in which case it has a value of 1000. The *command*-String will be explained in more detail further below.
```
skeleton.init_stream(command=commandstring, default_duration = 1000)
```

In order to get an element from the stream, just use the skeleton as an iterator
```
x = skeleton.next()
```

To visualize a data stream, call the following.
```
skeleton.display_current_stream()
```

Alternatively, use this to set a stream command and display it in one command. Parameters are analogous to *init_stream*.
```
skeleton.display_stream(command=commandstring, default_duration = 1000)
```