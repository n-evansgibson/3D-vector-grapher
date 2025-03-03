# 3D-vector-grapher

Hey there! Thanks for helping me contribute to my project in any way that you can.

Final project goal: 3D graphing calculator that specifically graphs vectors, curves, and vector fields. Program automatically 
recognizes the format for each type of input. If I ever figure out how to do this without crashing CMU graphics, I also hope to 
add surfaces or the level curves. 

Main required imports: CMU Graphics, shapely, numpy (any additional imports will be listed at the top of the code file)

Here are many parts that need to be worked on: 

1. _Scaling the graph_: Currently the graph only displays objects within a 4x4x4 grid. In the final product, the user will be able to
   "zoom in" and "zoom out" of the graph, using either a mouse scroller or on-screen adjustment, causing the scaling of the graph to
   change. See Desmos 3D graphing calculator as a reference.
2. _Gridlines and labels_: There are currently major gridlines without labels, and there are labels for the x, y, and z axes, but each
   axis should also be numerically labelled.  Gridlines and labels should change along with scaling the graph.
3. _Calculator improvements_: The calculator needs to actually be...written. See calculator code. Currently only support for basic
   arithmetic. In addition, the display of equations should ideally be in a format like LaTeX.
4. _Program speed_: The graph currently lags when rotating vector spaces due to the high number of objects. Any ways to speed up the
   program here?
5. _Curves_: I have already written the logic to recognize when a user inputs a point, a vector, and a vector field, but not yet curves.
   This is also something that needs to be worked on after the calculator is completely finished, as that way more complex curves can
   be displayed besides lines.
6. _Style_: it looks a bit ugly. A better color scheme, fonts, better object ratios, additional graphics, etc. could go a long way.
7. _Import Error_: I've been having a problem where some of my imports on VSCode are saying that they have not been imported. Any place
   where I received this error is marked with "type: ignore" in my code. This may only be an issue on my end. Otherwise, if you can find
   the issue, you are my hero. 

Thanks again! Feel free to reach out at nevansgi@andrew.cmu.edu if you have any questions about my code (its a mess lol)
   

