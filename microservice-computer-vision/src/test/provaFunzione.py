#!/usr/bin/env python
"""
Sample script that uses the TriangolazionePrototipo module created using
MATLAB Compiler SDK.

Refer to the MATLAB Compiler SDK documentation for more information.
"""

import TriangolazionePrototipo
# Import the matlab module only after you have imported
# MATLAB Compiler SDK generated Python modules.
import matlab

import plotly.express as px
import numpy as np
import pandas as pd

my_TriangolazionePrototipo = TriangolazionePrototipo.initialize()

x = [18.318112860148, 14.2949817462715, 16.4380855350346, 12.2903853701921, 14.4579005366844, 10.2903642978411, 8.49189149682204, 6.49447171658257, 8.29483356036796, 12.473517040832, 10.4848751821667, 16.3042155724446]
y = [48.0759783968909, 47.9871977358879, 42.0386448286094, 47.9291209919643, 41.9894100214277, 47.8659036790991, 41.8037451937836, 41.7389113024907, 47.8005083348189, 41.9319164105607, 41.8690573815958, 48.0371512121282]
z = ["giallo", "giallo", "blu", "giallo", "blu", "giallo", "blu", "blu", "giallo", "blu", "blu", "giallo"]

xIn = matlab.double([18.318112860148, 14.2949817462715, 16.4380855350346, 12.2903853701921, 14.4579005366844, 10.2903642978411, 8.49189149682204, 6.49447171658257, 8.29483356036796, 12.473517040832, 10.4848751821667, 16.3042155724446], size=(1, 12))
yIn = matlab.double([48.0759783968909, 47.9871977358879, 42.0386448286094, 47.9291209919643, 41.9894100214277, 47.8659036790991, 41.8037451937836, 41.7389113024907, 47.8005083348189, 41.9319164105607, 41.8690573815958, 48.0371512121282], size=(1, 12))
zIn = ["giallo", "giallo", "blu", "giallo", "blu", "giallo", "blu", "blu", "giallo", "blu", "blu", "giallo"]
maxConesIn = matlab.double([6.0], size=(1, 1))
risOut, sOut = my_TriangolazionePrototipo.TriangolazionePrototipo(xIn, yIn, zIn, maxConesIn, nargout=2)
#print(risOut, sOut, sep='\n')



risarr = np.array(risOut)
risOutT = risarr.transpose()
xa = risOutT[0].tolist()
ya = risOutT[1].tolist()
#print("Array\n",xa,"\n",ya,"\n")
#print(x+xa)
out = int(sOut)
my_dataframe = {
    'x' : x + xa
    ,'y' : y + ya
    ,'colore' : z + out*["traiettoria"]
}


#print(my_dataframe)
df = pd.DataFrame(my_dataframe)


fig = px.scatter(df, x="x", y="y", color='colore')

#fig = px.scatter(x=xa,y=ya)
fig.show()


my_TriangolazionePrototipo.terminate()
